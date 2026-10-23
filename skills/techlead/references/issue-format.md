# Issue Format

`TASKS.md` is both the execution plan and the source of truth for issue automation. Every task must be directly convertible into one GitHub or GitLab issue. Use `scripts/export_issues.py` to produce a dry-run manifest or to create labels, milestones, and issues.

## One task, one issue

- One task is one issue, one pull request, and one work session.
- A task touches at most five files. Split larger work.
- A task belongs to exactly one milestone from `PLAN.md`.
- Dependencies always point to earlier tasks.
- Acceptance and verification are observable and testable.

## Task marker

```html
<!-- techlead:task id=TASK-001 depends=none prd=FR-001,NFR-002 spec=TR-003 milestone=M1 tags=docker-local labels=type:feature,area:api,priority:p1 -->
```

The marker is machine-readable. The task body repeats the important fields for humans.

## Required fields

| Field | Purpose | Rule |
| --- | --- | --- |
| `Issue title` | Issue title without the ID prefix | Imperative, 8 to 72 characters, unique |
| `Labels` | Issue labels | At least `type:*`, `area:*`, and `priority:*` |
| `Estimate` | Relative size | `XS`, `S`, `M`, `L`, or 1 to 8 points |
| `Milestone` | Milestone from `PLAN.md` | Must exist in the plan |
| `PRD` | Product requirements | At least one FR or NFR |
| `SPEC` | Technical requirements | At least one TR |
| `Acceptance` | Completion condition | Observable outcome |
| `Verify` | Proof command or check | Exact command or manual check |
| `Files` | Expected changed paths | Comma-separated, five or fewer |

## Labels

Use a stable taxonomy:

- `type:feature`
- `type:bug`
- `type:chore`
- `type:test`
- `type:docs`
- `type:security`
- `type:infra`
- `area:api`, `area:web`, `area:data`, `area:infra`, or project-specific areas
- `priority:p0`, `priority:p1`, `priority:p2`, `priority:p3`
- `techlead:docker-local`, `techlead:docker-production`, `techlead:coverage-gate`, `techlead:security`, `techlead:deployment`, `techlead:final-gate`

The exporter adds the base `techlead` label and one `techlead:<tag>` label for every task tag.

## Issue title

The default title is `[TASK-001] <Issue title>`. The task ID prefix keeps traceability between the issue, the task, and the pull request. Use `--no-id-prefix` only when the project has another traceability mechanism.

## Milestones

Create one native milestone per marker in `PLAN.md`. The milestone title is `<M1> — <Milestone outcome>`. The description contains the goal, scope, exit criteria, and launch gate.

## Issue body

The exporter generates:

```markdown
<!-- techlead:task id=TASK-001 milestone=M1 -->
## Context

- Milestone: M1 — Milestone outcome
- PRD: FR-001, NFR-002
- SPEC: TR-003
- Estimate: S

## Acceptance

Observable completion condition.

## Verification

Exact command or manual check.

## Files

- src/api/handler.py
- tests/api/test_handler.py

## Dependencies

- Depends on: #12 (TASK-000)

## Traceability

- PRD: FR-001, NFR-002
- SPEC: TR-003
- Milestone: M1
```

## Export commands

Preview the manifest without side effects:

```bash
python3 scripts/export_issues.py --tasks TASKS.md --plan PLAN.md --provider github --repo owner/name --format json
```

Preview a shell script:

```bash
python3 scripts/export_issues.py --tasks TASKS.md --plan PLAN.md --provider gitlab --repo group/project --format shell
```

Create labels, milestones, and issues only after explicit approval:

```bash
python3 scripts/export_issues.py --tasks TASKS.md --plan PLAN.md --provider github --repo owner/name --apply
python3 scripts/export_issues.py --tasks TASKS.md --plan PLAN.md --provider gitlab --repo group/project --apply
```

The default is a dry-run. `--apply` requires the matching CLI (`gh` or `glab`) and an explicit repository. Dependencies are resolved in a second pass after issue numbers exist.
