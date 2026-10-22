---
description: Validate PRD.md and TASKS.md against the TechLead artifact contract
argument-hint: Optional PRD and TASKS paths
---

# Validate TechLead Artifacts

Load and follow the `techlead` skill for the artifact contract.

Host arguments: `$ARGUMENTS`

Use the host arguments as paths when provided. Otherwise default to `PRD.md` and `TASKS.md` in the current directory.

Resolve the validator script relative to the installed `techlead` skill and run:

```bash
python3 scripts/validate_artifacts.py PRD.md TASKS.md --coverage 80
```

Use the actual paths supplied by the user. Add `--strict` when the user wants warnings treated as errors. Add `--json` when a machine-readable report is useful.

Report errors first, then warnings, then the coverage gate and traceability summary. Do not edit the artifacts unless the user asks. If asked to fix them, update `PRD.md` first, then `TASKS.md`, and re-run validation until it passes.
