from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from .challenge import DEFAULT_NAMESPACE, DEFAULT_TTL_SECONDS, Challenge, create_challenge
from .signer import OpenSSHVerifier


class SignatureVerifier(Protocol):
    def verify(self, *, identity: str, message: str, signature: str) -> bool:
        ...


@dataclass
class ChallengeRecord:
    challenge: Challenge
    consumed_at: datetime | None = None

    @property
    def consumed(self) -> bool:
        return self.consumed_at is not None


@dataclass(frozen=True)
class VerificationResult:
    ok: bool
    reason: str
    challenge_id: str
    username: str
    consumed_at: datetime | None = None


class ChallengeManager:
    """Small in-memory manager for one-time SSH signature challenges."""

    def __init__(
        self,
        *,
        service: str,
        origin: str,
        allowed_signers_path: Path | str | None = None,
        verifier: SignatureVerifier | None = None,
        namespace: str = DEFAULT_NAMESPACE,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
    ) -> None:
        if allowed_signers_path is None and verifier is None:
            raise ValueError("allowed_signers_path or verifier is required.")

        self.service = service
        self.origin = origin
        self.namespace = namespace
        self.ttl_seconds = ttl_seconds
        self._verifier = verifier or OpenSSHVerifier(
            allowed_signers_path=Path(allowed_signers_path or ""),
            namespace=namespace,
        )
        self._records: dict[str, ChallengeRecord] = {}

    def create(
        self,
        *,
        username: str,
        operation: str = "login",
        client_ip: str | None = None,
        now: datetime | None = None,
    ) -> Challenge:
        challenge = create_challenge(
            service=self.service,
            origin=self.origin,
            username=username,
            operation=operation,
            client_ip=client_ip,
            ttl_seconds=self.ttl_seconds,
            namespace=self.namespace,
            now=now,
        )
        self._records[challenge.challenge_id] = ChallengeRecord(challenge=challenge)
        return challenge

    def get_message(
        self,
        *,
        challenge_id: str,
        username: str,
        now: datetime | None = None,
    ) -> str | None:
        record = self._records.get(challenge_id)
        if record is None or record.challenge.username != username or record.consumed:
            return None
        if record.challenge.is_expired(now):
            return None
        return record.challenge.message()

    def verify(
        self,
        *,
        challenge_id: str,
        username: str,
        signature: str,
        now: datetime | None = None,
    ) -> VerificationResult:
        check_time = (now or datetime.now(UTC)).astimezone(UTC).replace(microsecond=0)
        record = self._records.get(challenge_id)
        if record is None:
            return self._failure("unknown_challenge", challenge_id, username)
        if record.challenge.username != username:
            return self._failure("username_mismatch", challenge_id, username)
        if record.consumed:
            return self._failure("challenge_consumed", challenge_id, username)
        if record.challenge.is_expired(check_time):
            return self._failure("challenge_expired", challenge_id, username)

        valid = self._verifier.verify(
            identity=username,
            message=record.challenge.message(),
            signature=signature,
        )
        if not valid:
            return self._failure("signature_rejected", challenge_id, username)

        record.consumed_at = check_time
        return VerificationResult(
            ok=True,
            reason="ok",
            challenge_id=challenge_id,
            username=username,
            consumed_at=check_time,
        )

    def cleanup(self, *, now: datetime | None = None) -> int:
        check_time = (now or datetime.now(UTC)).astimezone(UTC)
        expired_or_consumed = [
            challenge_id
            for challenge_id, record in self._records.items()
            if record.consumed or record.challenge.is_expired(check_time)
        ]
        for challenge_id in expired_or_consumed:
            self._records.pop(challenge_id, None)
        return len(expired_or_consumed)

    def _failure(self, reason: str, challenge_id: str, username: str) -> VerificationResult:
        return VerificationResult(
            ok=False,
            reason=reason,
            challenge_id=challenge_id,
            username=username,
            consumed_at=None,
        )
