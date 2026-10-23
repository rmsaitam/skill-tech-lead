---
description: Validate PRD, SPEC, PLAN, TASKS, AGENTS, and README against the TechLead v2 contract
argument-hint: Optional PRD and TASKS paths
---

# Validate TechLead Artifacts

Load and follow the `techlead` skill for the artifact contract.

Host arguments: `$ARGUMENTS`

Use the host arguments as paths when provided. Otherwise default to `PRD.md` and `TASKS.md` in the current directory.

Resolve the validator script relative to the installed `techlead` skill and run:

```bash
python3 scripts/validate_artifacts.py PRD.md TASKS.md --all --coverage 80
```

`--all` loads `SPEC.md`, `PLAN.md`, `AGENTS.md`, and `README.md` next to the PRD. Pass `--spec`, `--plan`, `--agents`, or `--readme` when the files live elsewhere.

Use the actual paths supplied by the user. Add `--strict` when the user wants warnings treated as errors. Add `--json` when a machine-readable report is useful.

Report errors first, then warnings, then the coverage gate, milestone coverage, and traceability summary. Do not edit the artifacts unless the user asks. If asked to fix them, update `PRD.md` and `SPEC.md` first, then `PLAN.md`, then `TASKS.md`, then `AGENTS.md` and `README.md`, and re-run validation until it passes.
