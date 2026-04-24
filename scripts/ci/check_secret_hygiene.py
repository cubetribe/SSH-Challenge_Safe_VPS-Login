from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PRIVATE_OR_GENERATED_FILE_NAMES = {
    "authorized_signers",
    ".ops_authorized_signers",
}

PRIVATE_OR_GENERATED_SUFFIXES = {
    ".key",
    ".pem",
    ".p12",
    ".pfx",
    ".sig",
}

SENSITIVE_CONTENT_PATTERNS = [
    re.compile(r"-----BEGIN (?:OPENSSH |RSA |DSA |EC |PGP )?PRIVATE KEY(?: BLOCK)?-----"),
    re.compile(r"-----BEGIN SSH SIGNATURE-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b"),
]


def main() -> int:
    failures: list[str] = []
    for relative_path in tracked_files():
        path = Path(relative_path)
        inspect_path(path, failures)
        inspect_content(path, failures)

    if failures:
        print("Secret hygiene check failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Secret hygiene check passed.")
    return 0


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        capture_output=True,
        check=True,
        text=False,
    )
    return [path.decode("utf-8") for path in result.stdout.split(b"\0") if path]


def inspect_path(path: Path, failures: list[str]) -> None:
    name = path.name
    if name == ".env" or (name.startswith(".env.") and not name.endswith(".example")):
        failures.append(f"{path}: tracked environment file")
    if name.startswith("id_"):
        failures.append(f"{path}: tracked SSH private-key-style filename")
    if name in PRIVATE_OR_GENERATED_FILE_NAMES:
        failures.append(f"{path}: tracked production signer list filename")
    if path.suffix in PRIVATE_OR_GENERATED_SUFFIXES:
        failures.append(f"{path}: tracked private or generated credential-like suffix")


def inspect_content(path: Path, failures: list[str]) -> None:
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return

    for pattern in SENSITIVE_CONTENT_PATTERNS:
        match = pattern.search(content)
        if match is None:
            continue
        line_number = content.count("\n", 0, match.start()) + 1
        failures.append(f"{path}:{line_number}: matched {pattern.pattern}")


if __name__ == "__main__":
    raise SystemExit(main())
