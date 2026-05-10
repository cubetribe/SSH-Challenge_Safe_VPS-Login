# GitHub Security Baseline

This repository has no deployment workflow. GitHub is used for CI, security
testing, supply-chain review, and protected pull-request integration.

## Repository settings to apply manually

Apply these settings after the hardening pull request is merged and the new
checks have run at least once on `main`.

### Branch or ruleset protection for `main`

- Require a pull request before merging.
- Require at least one approving review.
- Dismiss stale pull request approvals when new commits are pushed.
- Require review from Code Owners.
- Require conversation resolution before merging.
- Require signed commits.
- Require linear history.
- Require branches to be up to date before merging.
- Do not allow bypassing the above settings.
- Do not allow force pushes.
- Do not allow deletions.
- Allow squash merge only, then delete merged branches automatically.

### Required status checks

Require these checks from GitHub Actions:

- `CI / Lint`
- `CI / Tests (Python 3.10)`
- `CI / Tests (Python 3.11)`
- `CI / Tests (Python 3.12)`
- `CI / Tests (Python 3.13)`
- `CI / Tests (Python 3.14)`
- `CI / Package Build`
- `Security / CodeQL (Python)`
- `Security / Dependency Review`
- `Security / Python Audit`
- `Security / Secret Hygiene`
- `CodeQL`

### Actions policy

- Keep default workflow token permissions at read-only.
- Keep "Allow GitHub Actions to create and approve pull requests" disabled.
- For private forks, require approval for outside collaborator workflows and do
  not send write tokens or secrets to fork pull request workflows.
- Prefer allowing only GitHub-owned actions and explicitly selected third-party
  actions. This baseline currently uses only GitHub-owned actions:
  - `actions/checkout`
  - `actions/setup-python`
  - `github/codeql-action`
  - `actions/dependency-review-action`
- Keep workflow actions pinned to full commit SHAs and review Dependabot action
  update pull requests before merging.

### Code security features

- Enable Dependabot alerts.
- Enable Dependabot security updates.
- Enable Dependabot version updates from `.github/dependabot.yml`.
- Enable dependency graph.
- Enable code scanning with CodeQL.
- Enable secret scanning.
- Enable push protection.
- Enable non-provider secret patterns where available so private keys are
  scanned as secrets.
- Review and close all security alerts before cutting a release.

## Current assumptions

- The repository owner handle is `@cubetribe`; update `.github/CODEOWNERS` if
  ownership moves to another user or team.
- The package remains Python `>=3.10`; CI covers Python 3.10 through 3.14.
- This project intentionally shells out to `ssh-keygen` with an argv list and
  `shell=False`; Bandit exceptions are limited to that explicit OpenSSH boundary.
