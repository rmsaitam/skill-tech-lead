---
description: Turn a product idea into PRD, SPEC, PLAN, TASKS, AGENTS, and README
argument-hint: Product idea or project brief
---

# TechLead Planning

Load and follow the `techlead` skill.

Host arguments: `$ARGUMENTS`

Use the host arguments as the product idea when they are present. Otherwise use the idea from the user's latest message. If no idea is available, ask for one sentence describing the problem and who has it.

Start with the context gate, then run the interview in rounds of at most five questions. Do not generate artifacts until the user approves the summary, assumptions, architecture, milestone outline, and issue strategy.

After approval:

1. generate `PRD.md` and `SPEC.md` together and cross-check traceability;
2. generate `PLAN.md` with launch strategy and milestones;
3. generate `TASKS.md` with atomic issue-ready tasks;
4. generate `AGENTS.md` and `README.md` last;
5. run the bundled validator with `--all` and the issue export dry-run.

Fix every validation error. Report the artifacts, validation result, coverage gate, milestone summary, highest-risk assumptions, recommended first issue, and the exact dry-run export command.

Do not start implementation, create issues, commit, push, or deploy unless the user explicitly asks.
