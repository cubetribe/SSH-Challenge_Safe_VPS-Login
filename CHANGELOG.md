# Changelog

All notable changes to this project are documented here.

This project follows manual Semantic Versioning after the first implementation.

## 0.1.0 - 2026-04-24

### Added

- Initial Python reference package for SSH-key challenge login flows.
- Canonical challenge message creation with expiry, nonce, origin, operation,
  username, and signer namespace.
- OpenSSH signing and verification wrappers using `ssh-keygen -Y sign` and
  `ssh-keygen -Y verify`.
- In-memory challenge manager with username checks, expiry checks, and replay
  protection.
- CLI for creating, signing, and verifying challenges.
- Tests for valid signer, unknown signer, tampered message, expired challenge,
  replayed challenge, wrong namespace, and malformed allowed signers handling.
- Integration and security documentation.

