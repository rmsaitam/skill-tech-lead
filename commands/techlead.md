---
description: Turn a product idea into a traceable PRD.md and ordered TASKS.md
argument-hint: Product idea or project brief
---

# TechLead Planning

Load and follow the `techlead` skill.

Host arguments: `$ARGUMENTS`

Use the host arguments as the product idea when they are present. Otherwise use the idea from the user's latest message. If no idea is available, ask for one sentence describing the problem and who has it.

Start with the context gate, then run the interview in rounds of at most five questions. Do not generate `PRD.md` or `TASKS.md` until the user approves the summary and assumptions.

After generating both files, run the bundled validator, fix every error, and report the validation result, the coverage gate, the highest-risk assumptions, and the recommended first task. Do not start implementation unless the user explicitly asks.
