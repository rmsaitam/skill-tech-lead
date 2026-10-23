---
description: Export TechLead TASKS.md as GitHub or GitLab issues with labels and milestones
argument-hint: Optional provider, repository, or TASKS and PLAN paths
---

# Export TechLead Issues

Load and follow the `techlead` skill for the task and issue contract.

Host arguments: `$ARGUMENTS`

Resolve the exporter script relative to the installed `techlead` skill. Default to `TASKS.md` and `PLAN.md` in the current directory.

Always preview first:

```bash
python3 scripts/export_issues.py --tasks TASKS.md --plan PLAN.md --provider github --format json
python3 scripts/export_issues.py --tasks TASKS.md --plan PLAN.md --provider github --format shell
```

Use `--provider gitlab` for GitLab. Pass `--repo owner/name` or `--repo group/project` when the repository is not inferred.

Report the issue count, labels, milestones, dependencies, and any validation error. Then show the exact command that would create the issues:

```bash
python3 scripts/export_issues.py --tasks TASKS.md --plan PLAN.md --provider github --repo owner/name --apply
python3 scripts/export_issues.py --tasks TASKS.md --plan PLAN.md --provider gitlab --repo group/project --apply
```

Do not create issues without explicit user approval. Do not edit `TASKS.md` or `PLAN.md` unless the user asks. If the export fails, report the missing field or milestone and point to `references/issue-format.md`.
