# Orchestration State

## Current phase

GitHub CI and security hardening.

## Workspace

`/Volumes/2TB_CodingProjekte/Coding_Projekte/SSH-Challenge_Safe_VPS-Login`

## Remote

`https://github.com/cubetribe/SSH-Challenge_Safe_VPS-Login`

## Routing

- Top-level loop: `godmode-workflow`
- Requested staff office: `api_guardian`
- Active scopes: `workspace_governance`, `quality_operations`, `docs_dx`,
  `workflow_design`
- Quality gate: local validator and tester checks before any push gate

## Decisions

- Keep GitHub Actions CI-only; no server deployment workflow is in scope.
- Use least-privilege workflow permissions and immutable commit-SHA action pins.
- Add CodeQL, Dependency Review, Python audit, repo-local secret hygiene,
  Dependabot, and CODEOWNERS as the first hardening layer.
- Record branch/ruleset protection and GitHub security feature settings in
  `docs/project/github-security-baseline.md` because those controls require
  GitHub repository settings after the checks exist on `main`.

## Next required gate

Run compile, tests, lint, package build, security scans, whitespace checks, and
status inspection. Do not commit, push, or open a pull request until the user
answers the explicit push gate.
