from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from ssh_challenge_safe_vps_login import (
    DEFAULT_NAMESPACE,
    Challenge,
    ChallengeError,
    create_challenge,
)

UTC = timezone.utc


def test_create_challenge_builds_canonical_message() -> None:
    challenge = create_challenge(
        service="demo-admin",
        origin="https://admin.example.test",
        username="operator",
        operation="ops-login",
        client_ip="127.0.0.1",
        ttl_seconds=120,
        now=datetime(2026, 4, 24, 12, 0, tzinfo=UTC),
        challenge_id="challenge-1",
        nonce="nonce-1",
    )

    assert challenge.message() == "\n".join(
        [
            "SSH Challenge Safe VPS Login",
            "version=1",
            f"namespace={DEFAULT_NAMESPACE}",
            "service=demo-admin",
            "origin=https://admin.example.test",
            "operation=ops-login",
            "username=operator",
            "client_ip=127.0.0.1",
            "challenge_id=challenge-1",
            "nonce=nonce-1",
            "issued_at=2026-04-24T12:00:00Z",
            "expires_at=2026-04-24T12:02:00Z",
        ]
    )


def test_challenge_round_trip_dict() -> None:
    challenge = create_challenge(
        service="demo",
        origin="https://example.test",
        username="operator",
        now=datetime(2026, 4, 24, 12, 0, tzinfo=UTC),
        challenge_id="challenge-1",
        nonce="nonce-1",
    )

    restored = Challenge.from_dict(challenge.to_dict())

    assert restored == challenge
    assert restored.message() == challenge.message()


@pytest.mark.parametrize("field", ["service", "origin", "username", "operation", "namespace"])
def test_challenge_rejects_newline_in_required_fields(field: str) -> None:
    kwargs = {
        "service": "demo",
        "origin": "https://example.test",
        "username": "operator",
        "operation": "login",
        "namespace": DEFAULT_NAMESPACE,
    }
    kwargs[field] = "bad\nvalue"

    with pytest.raises(ChallengeError):
        create_challenge(**kwargs)


def test_challenge_rejects_naive_datetime() -> None:
    with pytest.raises(ChallengeError):
        create_challenge(
            service="demo",
            origin="https://example.test",
            username="operator",
            now=datetime(2026, 4, 24, 12, 0),
        )


def test_expiry_boundary_is_strict() -> None:
    issued_at = datetime(2026, 4, 24, 12, 0, tzinfo=UTC)
    challenge = create_challenge(
        service="demo",
        origin="https://example.test",
        username="operator",
        ttl_seconds=120,
        now=issued_at,
    )

    assert not challenge.is_expired(issued_at + timedelta(seconds=119))
    assert challenge.is_expired(issued_at + timedelta(seconds=120))
