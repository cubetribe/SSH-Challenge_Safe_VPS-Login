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

Version `0.1.0` contains a framework-neutral Python reference implementation:

- canonical challenge creation
- OpenSSH signing and verification helpers
- in-memory challenge manager with expiry and replay protection
- CLI for creating, signing, and verifying challenges
- tests that exercise real OpenSSH signatures

Future work may add web framework adapters and deployment templates, but the
core package is intentionally dependency-free.

## Install

From a checkout:

```sh
python3 -m pip install -e .
```

For development:

```sh
python3 -m pip install -e ".[dev]"
pytest
ruff check .
```

OpenSSH must be available on `PATH` because signing and verification use
`ssh-keygen -Y sign` and `ssh-keygen -Y verify`.

## CLI quickstart

Create a challenge:

```sh
ssh-challenge-safe-vps-login create-challenge \
  --service my-vps-admin \
  --origin https://admin.example.com \
  --username operator \
  --json > challenge.json
```

Save the `message` value from that JSON as `challenge.txt`, then sign it on the
operator machine:

```sh
ssh-challenge-safe-vps-login sign \
  --key ~/.ssh/id_ed25519 \
  --message-file challenge.txt > challenge.sig
```

Verify against an OpenSSH allowed signers file:

```sh
ssh-challenge-safe-vps-login verify \
  --allowed-signers allowed_signers \
  --identity operator \
  --message-file challenge.txt \
  --signature-file challenge.sig
```

## Python quickstart

```python
from pathlib import Path

from ssh_challenge_safe_vps_login import ChallengeManager

manager = ChallengeManager(
    service="my-vps-admin",
    origin="https://admin.example.com",
    allowed_signers_path=Path("/etc/my-app/allowed_signers"),
    ttl_seconds=120,
)

challenge = manager.create(username="operator", client_ip="203.0.113.10")

# Show challenge.message() to the operator, then verify the posted signature.
result = manager.verify(
    challenge_id=challenge.challenge_id,
    username="operator",
    signature=posted_signature,
)

if not result.ok:
    raise PermissionError(result.reason)
```

See [docs/integration.md](docs/integration.md) and
[docs/security-model.md](docs/security-model.md) before using this in a
production admin surface.

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
