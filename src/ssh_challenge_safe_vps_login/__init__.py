"""OpenSSH challenge-response helpers for VPS admin login flows."""

__version__ = "0.1.0"

from .challenge import (
    DEFAULT_NAMESPACE,
    DEFAULT_TTL_SECONDS,
    Challenge,
    ChallengeError,
    create_challenge,
)
from .manager import ChallengeManager, ChallengeRecord, VerificationResult
from .signer import (
    OpenSSHError,
    OpenSSHSigner,
    OpenSSHUnavailableError,
    OpenSSHVerifier,
    sign_message,
    verify_signature,
)

__all__ = [
    "DEFAULT_NAMESPACE",
    "DEFAULT_TTL_SECONDS",
    "Challenge",
    "ChallengeError",
    "ChallengeManager",
    "ChallengeRecord",
    "OpenSSHError",
    "OpenSSHSigner",
    "OpenSSHUnavailableError",
    "OpenSSHVerifier",
    "VerificationResult",
    "create_challenge",
    "sign_message",
    "verify_signature",
]
