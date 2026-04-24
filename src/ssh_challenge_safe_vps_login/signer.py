from __future__ import annotations

import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .challenge import DEFAULT_NAMESPACE


class OpenSSHError(RuntimeError):
    """Raised when OpenSSH signing or verification cannot be completed."""


class OpenSSHUnavailableError(OpenSSHError):
    """Raised when `ssh-keygen` is not available."""


@dataclass(frozen=True)
class OpenSSHSigner:
    key_path: Path
    namespace: str = DEFAULT_NAMESPACE
    ssh_keygen: str = "ssh-keygen"

    def sign(self, message: str) -> str:
        return sign_message(
            key_path=self.key_path,
            message=message,
            namespace=self.namespace,
            ssh_keygen=self.ssh_keygen,
        )


@dataclass(frozen=True)
class OpenSSHVerifier:
    allowed_signers_path: Path
    namespace: str = DEFAULT_NAMESPACE
    ssh_keygen: str = "ssh-keygen"

    def verify(self, *, identity: str, message: str, signature: str) -> bool:
        return verify_signature(
            allowed_signers_path=self.allowed_signers_path,
            identity=identity,
            message=message,
            signature=signature,
            namespace=self.namespace,
            ssh_keygen=self.ssh_keygen,
        )


def sign_message(
    *,
    key_path: Path | str,
    message: str,
    namespace: str = DEFAULT_NAMESPACE,
    ssh_keygen: str = "ssh-keygen",
) -> str:
    key = Path(key_path).expanduser()
    if not key.is_file():
        raise OpenSSHError(f"SSH private key not found: {key}")

    with tempfile.TemporaryDirectory(prefix="ssh-challenge-sign-") as temp_dir:
        message_path = Path(temp_dir) / "challenge.txt"
        message_path.write_text(message, encoding="utf-8")
        process = _run(
            [
                ssh_keygen,
                "-Y",
                "sign",
                "-n",
                namespace,
                "-f",
                str(key),
                str(message_path),
            ],
            input_text=None,
        )
        if process.returncode != 0:
            detail = process.stderr.strip() or "OpenSSH signing failed."
            raise OpenSSHError(detail)

        signature_path = Path(f"{message_path}.sig")
        if not signature_path.is_file():
            raise OpenSSHError("OpenSSH did not create a signature file.")
        return signature_path.read_text(encoding="utf-8")


def verify_signature(
    *,
    allowed_signers_path: Path | str,
    identity: str,
    message: str,
    signature: str,
    namespace: str = DEFAULT_NAMESPACE,
    ssh_keygen: str = "ssh-keygen",
) -> bool:
    allowed_signers = Path(allowed_signers_path).expanduser()
    if not allowed_signers.is_file():
        return False

    with tempfile.TemporaryDirectory(prefix="ssh-challenge-verify-") as temp_dir:
        signature_path = Path(temp_dir) / "challenge.sig"
        signature_path.write_text(signature, encoding="utf-8")
        process = _run(
            [
                ssh_keygen,
                "-Y",
                "verify",
                "-f",
                str(allowed_signers),
                "-I",
                identity,
                "-n",
                namespace,
                "-s",
                str(signature_path),
            ],
            input_text=message,
        )
        return process.returncode == 0


def _run(args: list[str], *, input_text: str | None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            args,
            input=input_text,
            capture_output=True,
            check=False,
            env={**os.environ, "LC_ALL": "C"},
            text=True,
        )
    except FileNotFoundError as exc:
        raise OpenSSHUnavailableError("ssh-keygen is not available on PATH.") from exc

