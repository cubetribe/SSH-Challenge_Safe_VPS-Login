from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from ssh_challenge_safe_vps_login import ChallengeManager, sign_message, verify_signature


def _allowed_signers(tmp_path: Path, public_key: str, identity: str = "operator") -> Path:
    path = tmp_path / "allowed_signers"
    path.write_text(f"{identity} {public_key}\n", encoding="utf-8")
    return path


def test_manager_verifies_signature_and_blocks_replay(
    tmp_path: Path,
    ssh_keypair: tuple[Path, str],
) -> None:
    key_path, public_key = ssh_keypair
    manager = ChallengeManager(
        service="demo-admin",
        origin="https://admin.example.test",
        allowed_signers_path=_allowed_signers(tmp_path, public_key),
        ttl_seconds=120,
    )
    challenge = manager.create(
        username="operator",
        client_ip="127.0.0.1",
        now=datetime(2026, 4, 24, 12, 0, tzinfo=UTC),
    )
    signature = sign_message(key_path=key_path, message=challenge.message())

    result = manager.verify(
        challenge_id=challenge.challenge_id,
        username="operator",
        signature=signature,
        now=datetime(2026, 4, 24, 12, 1, tzinfo=UTC),
    )
    replay = manager.verify(
        challenge_id=challenge.challenge_id,
        username="operator",
        signature=signature,
        now=datetime(2026, 4, 24, 12, 1, 1, tzinfo=UTC),
    )

    assert result.ok
    assert result.reason == "ok"
    assert not replay.ok
    assert replay.reason == "challenge_consumed"


def test_manager_rejects_expired_challenge(tmp_path: Path, ssh_keypair: tuple[Path, str]) -> None:
    key_path, public_key = ssh_keypair
    manager = ChallengeManager(
        service="demo-admin",
        origin="https://admin.example.test",
        allowed_signers_path=_allowed_signers(tmp_path, public_key),
        ttl_seconds=1,
    )
    issued_at = datetime(2026, 4, 24, 12, 0, tzinfo=UTC)
    challenge = manager.create(username="operator", now=issued_at)
    signature = sign_message(key_path=key_path, message=challenge.message())

    result = manager.verify(
        challenge_id=challenge.challenge_id,
        username="operator",
        signature=signature,
        now=issued_at + timedelta(seconds=1),
    )

    assert not result.ok
    assert result.reason == "challenge_expired"


def test_manager_rejects_username_mismatch(tmp_path: Path, ssh_keypair: tuple[Path, str]) -> None:
    key_path, public_key = ssh_keypair
    manager = ChallengeManager(
        service="demo-admin",
        origin="https://admin.example.test",
        allowed_signers_path=_allowed_signers(tmp_path, public_key),
    )
    challenge = manager.create(username="operator", now=datetime(2026, 4, 24, 12, 0, tzinfo=UTC))
    signature = sign_message(key_path=key_path, message=challenge.message())

    result = manager.verify(
        challenge_id=challenge.challenge_id,
        username="other",
        signature=signature,
        now=datetime(2026, 4, 24, 12, 1, tzinfo=UTC),
    )

    assert not result.ok
    assert result.reason == "username_mismatch"


def test_verify_signature_rejects_tampered_message(
    tmp_path: Path,
    ssh_keypair: tuple[Path, str],
) -> None:
    key_path, public_key = ssh_keypair
    allowed_signers = _allowed_signers(tmp_path, public_key)
    message = "SSH Challenge Safe VPS Login\nchallenge_id=1"
    signature = sign_message(key_path=key_path, message=message)

    assert not verify_signature(
        allowed_signers_path=allowed_signers,
        identity="operator",
        message=f"{message}\ntampered=true",
        signature=signature,
    )


def test_verify_signature_rejects_wrong_namespace(
    tmp_path: Path,
    ssh_keypair: tuple[Path, str],
) -> None:
    key_path, public_key = ssh_keypair
    message = "SSH Challenge Safe VPS Login\nchallenge_id=1"
    signature = sign_message(key_path=key_path, message=message, namespace="wrong-namespace")

    assert not verify_signature(
        allowed_signers_path=_allowed_signers(tmp_path, public_key),
        identity="operator",
        message=message,
        signature=signature,
    )


def test_verify_signature_rejects_unauthorized_signer(
    tmp_path: Path,
    ssh_keypair: tuple[Path, str],
) -> None:
    key_path, public_key = ssh_keypair
    message = "SSH Challenge Safe VPS Login\nchallenge_id=1"
    signature = sign_message(key_path=key_path, message=message)

    assert not verify_signature(
        allowed_signers_path=_allowed_signers(tmp_path, public_key, identity="someone-else"),
        identity="operator",
        message=message,
        signature=signature,
    )


def test_malformed_allowed_signers_fails_closed(
    tmp_path: Path,
    ssh_keypair: tuple[Path, str],
) -> None:
    key_path, _public_key = ssh_keypair
    allowed_signers = tmp_path / "allowed_signers"
    allowed_signers.write_text("this is not an allowed signers file\n", encoding="utf-8")
    message = "SSH Challenge Safe VPS Login\nchallenge_id=1"
    signature = sign_message(key_path=key_path, message=message)

    assert not verify_signature(
        allowed_signers_path=allowed_signers,
        identity="operator",
        message=message,
        signature=signature,
    )
