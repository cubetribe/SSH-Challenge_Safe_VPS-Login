# Contributing

This project is in bootstrap stage. Contributions should keep the security model
small, explicit, and testable.

## Before contributing

- Do not submit private keys, production signer files, tokens, `.env` files,
  logs, signatures, or real challenge payloads.
- Keep changes focused and auditable.
- Include tests for any implementation behavior once code exists.
- Discuss large protocol, API, CLI, or license changes before opening a pull
  request.

## Security-sensitive changes

Authentication changes must include negative coverage for:

- expired challenges
- replayed challenges
- wrong signature namespace
- tampered challenge message
- unauthorized signer
- missing or malformed signer allowlist

## Contributor licensing

By submitting a contribution, you confirm that you have the right to contribute
it and that it may be distributed under this repository's current license.

Commercial licensing for third-party contributions may require an additional
written contributor agreement before merge.
