# Security Model

## Goal

The project protects VPS-hosted operator surfaces by replacing password login
with a local SSH-key signature challenge.

The server must be able to verify that an operator controls an approved SSH
private key without ever receiving that private key.

## Protocol sketch

1. The server creates a random challenge id and a message with:
   - project or service name
   - origin
   - username or signer identity
   - client IP when useful
   - expiry timestamp
   - random nonce or challenge id
2. The server stores the challenge as pending and unconsumed.
3. The operator signs the exact message locally with OpenSSH:

   ```sh
   ssh-keygen -Y sign -n ssh-challenge-safe-vps-login -f ~/.ssh/id_ed25519 challenge.txt
   ```

4. The server verifies the signature with OpenSSH:

   ```sh
   ssh-keygen -Y verify -f allowed_signers -I operator -n ssh-challenge-safe-vps-login -s challenge.sig
   ```

5. The server consumes the challenge and issues a short-lived session.

## Required controls

- The challenge must expire quickly.
- A challenge must be single-use.
- The signed message must bind the signature to the intended origin and
  operation.
- The signature namespace must be project-specific.
- The server must verify against an explicit signer allowlist.
- Session cookies must be secure, HTTP-only, same-site, and short-lived.
- Mutating browser routes still need CSRF protection.
- API routes used by automation need an explicit non-browser auth mechanism.

## Threats this helps with

- reused or weak admin passwords
- leaked browser passwords
- accidental password entry into the wrong form
- long-lived admin tokens copied into local notes or deployment files
- remote server compromise that does not include the operator's local SSH key

## Threats this does not solve alone

- compromised operator machine or stolen private SSH key
- malicious server returning a misleading challenge
- missing HTTPS
- server-side command injection or application bugs after login
- weak session cookie handling
- public exposure of admin routes without rate limiting

## Implementation requirements

Reference implementations must test at least:

- valid signer succeeds
- unknown signer fails
- tampered message fails
- expired challenge fails
- replayed challenge fails
- wrong namespace fails
- malformed allowed signers file fails closed

The Python package added in version `0.1.0` covers these cases with integration
tests that call the local OpenSSH `ssh-keygen` binary.
