# SSH Challenge Safe VPS Login

SSH Challenge Safe VPS Login is a reusable pattern for protecting VPS-hosted
admin surfaces with a local SSH key instead of a username/password login.

The server creates a short-lived challenge, the operator signs it on their own
machine with an existing SSH private key, and the server verifies the OpenSSH
signature against an allowlist of public keys. The private key never leaves the
operator machine.

## Why this exists

Admin dashboards, deployment controls, and emergency operations often end up
behind passwords or long-lived bearer tokens. That is risky on small VPS setups:
passwords can be reused, copied into environment files, entered into browsers,
or leaked through logs and support tooling.

This project extracts an approach that has already been used in private
projects: use the SSH key that already controls trusted operator access, but
apply it to browser-based and API-based admin approval flows.

## Core flow

1. The operator opens a protected admin page.
2. The server creates a one-time challenge containing values such as origin,
   challenge id, username, client IP, and expiry.
3. The browser shows a local command for the operator machine.
4. The operator signs the challenge locally with OpenSSH:

   ```sh
   ssh-keygen -Y sign -n ssh-challenge-safe-vps-login -f ~/.ssh/id_ed25519 challenge.txt
   ```

5. The signature is sent back to the server.
6. The server verifies the signature with `ssh-keygen -Y verify` and a configured
   public-key allowlist.
7. On success, the server issues a short-lived session for the admin workflow.

## Intended use cases

- VPS admin dashboards
- deployment approval gates
- operator-only maintenance actions
- emergency lock or unlock flows
- internal tools where password login is not acceptable

## Security goals

- No password-based admin login for protected operator surfaces.
- No private SSH key material on the server.
- Short-lived, one-time challenges to reduce replay risk.
- Explicit signer allowlist controlled by the server operator.
- Clear separation between browser session handling and SSH signature
  verification.

## Non-goals

- This is not a replacement for SSH daemon hardening.
- This does not remove the need for HTTPS, CSRF protection, secure cookies, rate
  limiting, logging, and server patching.
- This is not a general identity provider.
- This does not make a compromised operator machine safe.

## Project status

Bootstrap stage. The repository currently contains project governance,
licensing, and the security model. Reference implementation code will be added
in a later step.

Planned work:

- language-neutral protocol specification
- reference implementation for a Python/FastAPI admin flow
- CLI helper for signing challenges
- signer file format and rotation guidance
- deployment examples for VPS-hosted services
- integration tests around replay, expiry, namespace, and signer failures

## License

Copyright (c) 2026 Dennis Westermann.

Private and non-commercial use is free under the terms in
[LICENSE.md](LICENSE.md). Commercial use requires a separate written license.
Contact Dennis Westermann at <hey@dennis-westermann.de>.

Because commercial use is restricted, this repository is source-available for
review and non-commercial use, but it is not distributed under an OSI-approved
open-source license.

## Contact

Dennis Westermann
<hey@dennis-westermann.de>
