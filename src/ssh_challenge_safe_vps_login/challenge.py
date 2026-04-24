from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

DEFAULT_NAMESPACE = "ssh-challenge-safe-vps-login"
DEFAULT_TTL_SECONDS = 120


class ChallengeError(ValueError):
    """Raised when a challenge cannot be constructed safely."""


@dataclass(frozen=True)
class Challenge:
    service: str
    origin: str
    username: str
    challenge_id: str
    nonce: str
    operation: str
    issued_at: datetime
    expires_at: datetime
    namespace: str = DEFAULT_NAMESPACE
    client_ip: str | None = None

    def message(self) -> str:
        """Return the exact canonical message that must be signed."""

        fields = [
            ("version", "1"),
            ("namespace", self.namespace),
            ("service", self.service),
            ("origin", self.origin),
            ("operation", self.operation),
            ("username", self.username),
            ("client_ip", self.client_ip or ""),
            ("challenge_id", self.challenge_id),
            ("nonce", self.nonce),
            ("issued_at", _format_utc(self.issued_at)),
            ("expires_at", _format_utc(self.expires_at)),
        ]
        lines = ["SSH Challenge Safe VPS Login"]
        lines.extend(f"{key}={value}" for key, value in fields)
        return "\n".join(lines)

    def is_expired(self, now: datetime | None = None) -> bool:
        check_time = _coerce_utc(now or datetime.now(UTC))
        return check_time >= self.expires_at

    def to_dict(self) -> dict[str, str | None]:
        return {
            "service": self.service,
            "origin": self.origin,
            "username": self.username,
            "challenge_id": self.challenge_id,
            "nonce": self.nonce,
            "operation": self.operation,
            "issued_at": _format_utc(self.issued_at),
            "expires_at": _format_utc(self.expires_at),
            "namespace": self.namespace,
            "client_ip": self.client_ip,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Challenge:
        return cls(
            service=_required_text("service", payload.get("service")),
            origin=_required_text("origin", payload.get("origin")),
            username=_required_text("username", payload.get("username")),
            challenge_id=_required_text("challenge_id", payload.get("challenge_id")),
            nonce=_required_text("nonce", payload.get("nonce")),
            operation=_required_text("operation", payload.get("operation")),
            issued_at=_parse_utc(_required_text("issued_at", payload.get("issued_at"))),
            expires_at=_parse_utc(_required_text("expires_at", payload.get("expires_at"))),
            namespace=_required_text("namespace", payload.get("namespace", DEFAULT_NAMESPACE)),
            client_ip=_optional_text("client_ip", payload.get("client_ip")),
        )


def create_challenge(
    *,
    service: str,
    origin: str,
    username: str,
    operation: str = "login",
    client_ip: str | None = None,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    namespace: str = DEFAULT_NAMESPACE,
    now: datetime | None = None,
    challenge_id: str | None = None,
    nonce: str | None = None,
) -> Challenge:
    """Create a signed-message challenge with safe defaults."""

    ttl = _validate_ttl(ttl_seconds)
    issued_at = _coerce_utc(now or datetime.now(UTC)).replace(microsecond=0)
    return Challenge(
        service=_required_text("service", service),
        origin=_required_text("origin", origin),
        username=_required_text("username", username),
        challenge_id=_required_text("challenge_id", challenge_id or secrets.token_urlsafe(32)),
        nonce=_required_text("nonce", nonce or secrets.token_urlsafe(32)),
        operation=_required_text("operation", operation),
        issued_at=issued_at,
        expires_at=issued_at + timedelta(seconds=ttl),
        namespace=_required_text("namespace", namespace),
        client_ip=_optional_text("client_ip", client_ip),
    )


def _validate_ttl(ttl_seconds: int) -> int:
    if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, int):
        raise ChallengeError("ttl_seconds must be an integer.")
    if ttl_seconds < 1:
        raise ChallengeError("ttl_seconds must be at least 1.")
    return ttl_seconds


def _required_text(name: str, value: Any) -> str:
    if value is None:
        raise ChallengeError(f"{name} is required.")
    text = str(value).strip()
    if not text:
        raise ChallengeError(f"{name} is required.")
    _reject_control_chars(name, text)
    return text


def _optional_text(name: str, value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    _reject_control_chars(name, text)
    return text


def _reject_control_chars(name: str, value: str) -> None:
    if "\n" in value or "\r" in value or "\0" in value:
        raise ChallengeError(f"{name} must not contain newlines or NUL bytes.")


def _coerce_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ChallengeError("datetime values must include timezone information.")
    return value.astimezone(UTC)


def _format_utc(value: datetime) -> str:
    return _coerce_utc(value).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_utc(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    return _coerce_utc(datetime.fromisoformat(normalized))
