# SSH Challenge Safe VPS Login - Local Project Rules

## Project purpose

This repository extracts a reusable SSH-key challenge-response login pattern
for VPS-hosted admin surfaces and operator-only workflows. The intended
security property is that the private SSH key stays on the operator machine
while the server verifies a short-lived OpenSSH signature against configured
public keys.

## Local working rules

- Keep the repository safe to publish. Do not commit real private keys,
  production public signer lists, tokens, `.env` files, hostnames that are not
  intended to be public, logs, challenge payloads, or generated signatures.
- Prefer a small, auditable core with explicit security boundaries over broad
  framework integration.
- Treat the protocol and verification behavior as security-sensitive public
  contracts once implementation begins.
- Keep docs and examples framework-neutral unless a specific reference
  implementation is being added.
- Record assumptions in docs when implementation language, package layout, or
  release entrypoints are not established yet.

## Governance and ownership

- `README.md`, `LICENSE.md`, `CONTRIBUTING.md`, and `SECURITY.md` define the
  public project surface.
- `docs/security-model.md` owns protocol goals, non-goals, and threat model.
- `docs/project/**` and `state/**` hold workflow state, routing, and planning
  artifacts.
- Future source code must live under an explicit language or package root
  chosen in a later architecture step.

## Release law

- Current release state: manual SemVer package starting at `0.1.0`.
- Release model: manual SemVer after the first implementation exists.
- Keep `pyproject.toml`, `src/ssh_challenge_safe_vps_login/__init__.py`, and
  `CHANGELOG.md` aligned when preparing release commits.
- Do not create Git tags or GitHub releases unless the user explicitly asks for
  a release publication step.
- Classify work as:
  - `major`: breaking protocol, API, CLI, config, or verification behavior
  - `minor`: backward-compatible feature or new integration
  - `patch`: backward-compatible fix
  - `none`: docs, governance, planning, or internal-only workflow changes

## Validation

- For docs-only work, run `git diff --check` and inspect `git status`.
- For code work, run `python3 -m compileall src tests`, `pytest`, and
  `ruff check .` when available.
- Keep tests around challenge creation, signature verification, replay
  protection, expiry, signer parsing, and session handling.
- Any auth behavior change must include negative tests for invalid signer,
  expired challenge, replayed challenge, wrong namespace, and tampered message.

## Git and GitHub

- Initial repository bootstrap may establish `main` because the remote starts
  empty and has no default branch.
- After the initial default branch exists, use short topic branches and pull
  requests for changes.
- Never commit private material or generated runtime artifacts.
- Never force-push shared branches or rewrite shared history.
- Never push without explicit user approval in the current thread.
