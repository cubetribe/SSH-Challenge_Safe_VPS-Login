# Integration Guide

## Minimal server flow

1. Configure an OpenSSH allowed signers file on the server.
2. Create a `ChallengeManager` with service name, origin, signer file path, and
   a short TTL.
3. When an operator starts login, call `manager.create(...)` and show
   `challenge.message()` to the local operator machine.
4. The operator signs that exact message with the CLI or OpenSSH directly.
5. Submit the signature back to the server.
6. Call `manager.verify(...)`.
7. Issue your own short-lived web session only when verification returns
   `ok=True`.

## Example

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
print(challenge.message())

# After the browser posts the signature back:
result = manager.verify(
    challenge_id=challenge.challenge_id,
    username="operator",
    signature=posted_signature,
)

if not result.ok:
    raise PermissionError(result.reason)
```

## Signer file

The allowed signers file uses the OpenSSH format:

```text
operator ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... operator@example
```

Keep this file outside the web root. Do not store private keys on the server.

## Operator signing

The bundled CLI signs a message file:

```sh
ssh-challenge-safe-vps-login sign \
  --key ~/.ssh/id_ed25519 \
  --message-file challenge.txt > challenge.sig
```

Verification can be tested locally:

```sh
ssh-challenge-safe-vps-login verify \
  --allowed-signers allowed_signers \
  --identity operator \
  --message-file challenge.txt \
  --signature-file challenge.sig
```

## Web application requirements

This package only verifies the SSH signature. A production web application must
still provide:

- HTTPS
- secure, HTTP-only, same-site session cookies
- CSRF protection for browser mutations
- rate limiting on challenge creation and completion
- audit logging without writing private key material or full signatures
- signer rotation and offboarding procedures

