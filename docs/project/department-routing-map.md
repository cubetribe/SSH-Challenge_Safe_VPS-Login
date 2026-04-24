# Department Routing Map

## Selected departments

| Department | Scope | Active for bootstrap |
| --- | --- | --- |
| `workspace_governance` | Repo-local rules, release law, Git safety | Yes |
| `docs_dx` | README, license, contribution, security docs | Yes |
| `workflow_design` | Intake, routing, write-scope, orchestration state | Yes |
| `quality_operations` | Validation commands and readiness checks | Validation only |

## Staff offices

| Office | Bootstrap role |
| --- | --- |
| `architect` | Keep first project shape minimal and extensible |
| `validator` | Check repository consistency and staged diff |
| `tester` | Run scope-matched validation; docs-only at bootstrap |
| `github_manager` | Remote, branch, commit, and push gate |

## Blockers before broader implementation

- Choose first implementation stack.
- Define package layout and public API.
- Decide whether commercial licensing needs a contributor agreement before
  accepting outside code.
- Decide when the GitHub repository should be made public.
