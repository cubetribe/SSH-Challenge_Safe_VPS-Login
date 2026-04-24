from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def ssh_keygen_available() -> None:
    if shutil.which("ssh-keygen") is None:
        pytest.skip("ssh-keygen is required for OpenSSH integration tests")


@pytest.fixture
def ssh_keypair(tmp_path: Path, ssh_keygen_available: None) -> tuple[Path, str]:
    key_path = tmp_path / "id_operator"
    subprocess.run(
        [
            "ssh-keygen",
            "-q",
            "-t",
            "ed25519",
            "-N",
            "",
            "-C",
            "operator@test",
            "-f",
            str(key_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    public_key = key_path.with_suffix(".pub").read_text(encoding="utf-8").strip()
    return key_path, public_key

