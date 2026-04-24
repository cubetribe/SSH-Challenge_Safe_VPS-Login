from __future__ import annotations

import json
from pathlib import Path

from ssh_challenge_safe_vps_login.cli import main


def test_create_challenge_json_outputs_message(capsys) -> None:
    result = main(
        [
            "create-challenge",
            "--service",
            "demo",
            "--origin",
            "https://example.test",
            "--username",
            "operator",
            "--json",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["username"] == "operator"
    assert payload["message"].startswith("SSH Challenge Safe VPS Login\n")


def test_cli_sign_and_verify_round_trip(
    tmp_path: Path,
    ssh_keypair: tuple[Path, str],
    capsys,
) -> None:
    key_path, public_key = ssh_keypair
    message_path = tmp_path / "challenge.txt"
    signature_path = tmp_path / "challenge.sig"
    allowed_signers_path = tmp_path / "allowed_signers"
    message_path.write_text("SSH Challenge Safe VPS Login\nchallenge_id=1", encoding="utf-8")
    allowed_signers_path.write_text(f"operator {public_key}\n", encoding="utf-8")

    sign_result = main(["sign", "--key", str(key_path), "--message-file", str(message_path)])
    signature = capsys.readouterr().out
    signature_path.write_text(signature, encoding="utf-8")
    verify_result = main(
        [
            "verify",
            "--allowed-signers",
            str(allowed_signers_path),
            "--identity",
            "operator",
            "--message-file",
            str(message_path),
            "--signature-file",
            str(signature_path),
        ]
    )

    assert sign_result == 0
    assert verify_result == 0
    assert capsys.readouterr().out == "valid\n"

