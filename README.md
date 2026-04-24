# SSH Challenge Safe VPS Login

SSH Challenge Safe VPS Login is a reusable pattern for protecting VPS-hosted
admin surfaces with a local SSH key instead of a username/password login.

The server creates a short-lived challenge, the operator signs it on their own
machine with an existing SSH private key, and the server verifies the OpenSSH
signature against an allowlist of public keys. The private key never leaves the
operator machine.

## Copy-prompt for local coding assistants

Use this prompt when you want a local coding assistant to integrate the project
into another app:

```text
Integrate SSH Challenge Safe VPS Login into this project.

Source repository:
https://github.com/cubetribe/SSH-Challenge_Safe_VPS-Login

Goal:
- Protect the admin or operator area with an SSH-key challenge instead of a
  username/password login.
- Use the repository as the source of truth. Read README.md,
  docs/security-model.md, docs/integration.md, and the Python package under
  src/ssh_challenge_safe_vps_login.
- Add the dependency from the GitHub repository or vendor the package code into
  a clearly named internal module if the project cannot use Git dependencies.
- Keep private SSH keys on the operator machine only. Never commit private keys,
  production allowed-signers files, signatures, tokens, .env files, or real
  challenge payloads.
- Implement a flow where the server creates a short-lived one-time challenge,
  the operator signs the exact message locally with OpenSSH, and the server
  verifies the signature against an allowed-signers file.
- Add tests for: valid signer, unknown signer, expired challenge, replayed
  challenge, wrong namespace, tampered message, and malformed allowed signers.
- Keep existing app security in place: HTTPS, secure HTTP-only same-site
  cookies, CSRF protection for browser mutations, rate limiting, and audit logs
  without secret material.
- Update the target project's README, deployment notes, and environment examples
  so another developer can configure the signer file and session settings safely.

Before finishing:
- Run the target project's lint, tests, and any package/build checks.
- Show the changed files, validation commands, and remaining assumptions.
```

## Why this exists

Admin dashboards, deployment controls, and emergency operations often end up
behind passwords or long-lived bearer tokens. That is risky on small VPS setups:
passwords can be reused, copied into environment files, entered into browsers,
or leaked through logs and support tooling.

This project extracts an approach that has already been used in private
projects: use the SSH key that already controls trusted operator access, but
apply it to browser-based and API-based admin approval flows.

The project is intentionally small. It gives you the core challenge/sign/verify
building blocks, then lets your app keep responsibility for sessions, CSRF,
rate limiting, logging, and deployment policy.

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

OpenSSH must be available on `PATH` because signing and verification use
`ssh-keygen -Y sign` and `ssh-keygen -Y verify`.

For a first local test, clone the repository and install it in a virtual
environment:

```sh
git clone https://github.com/cubetribe/SSH-Challenge_Safe_VPS-Login.git
cd SSH-Challenge_Safe_VPS-Login
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

For development work, install the test and build tools too:

```sh
python -m pip install -e ".[dev]"
ruff check .
pytest
python -m build
```

If another project should depend on this package directly from GitHub, use a
Git dependency in that project's packaging config or install command:

```sh
python -m pip install \
  "ssh-challenge-safe-vps-login @ git+https://github.com/cubetribe/SSH-Challenge_Safe_VPS-Login.git@main"
```

For production, pin a commit SHA or release tag instead of tracking `main`.

## CLI quickstart

Create a challenge:

```sh
ssh-challenge-safe-vps-login create-challenge \
  --service my-vps-admin \
  --origin https://admin.example.com \
  --username operator \
  --json > challenge.json
```

Save the `message` value from that JSON as `challenge.txt`. The operator signs
that exact file on the machine that owns the SSH private key:

```sh
python - <<'PY'
import json
from pathlib import Path

payload = json.loads(Path("challenge.json").read_text(encoding="utf-8"))
Path("challenge.txt").write_text(payload["message"], encoding="utf-8")
PY
```

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

Use `ChallengeManager` inside your web app or operator service. The package
handles challenge creation and signature verification; your app still owns the
web session.

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

## Safe deployment checklist

- Store only public keys in the server-side allowed-signers file.
- Keep the allowed-signers file outside the web root.
- Use short challenge TTLs, for example 60 to 120 seconds.
- Mark a challenge consumed immediately after successful verification.
- Use HTTPS and secure, HTTP-only, same-site cookies for the browser session.
- Add CSRF protection for mutating browser routes.
- Rate-limit challenge creation and completion endpoints.
- Log decisions and reasons, but not private keys, full signatures, bearer
  tokens, or real challenge payloads.

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
