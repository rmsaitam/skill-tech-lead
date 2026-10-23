---
name: techlead
description: Run a structured brainstorming interview and produce a traceable PRD.md, SPEC.md, PLAN.md, TASKS.md, AGENTS.md, and README.md. Use when the user asks for a tech lead, product requirements, architecture specification, launch plan, milestones, task breakdown, issue-ready tickets, a PRD, a SPEC, an implementation plan, or wants to turn an idea into executable engineering work with Docker environments and a test coverage gate of at least 80 percent.
license: MIT
metadata:
  author: TechLead contributors
  version: "0.2.0"
---

# TechLead

Turn an idea into a traceable planning set with six artifacts:

1. `PRD.md`: product and business source of truth.
2. `SPEC.md`: architecture and engineering source of truth.
3. `PLAN.md`: launch strategy and macro milestones.
4. `TASKS.md`: atomic technical tasks ready to become GitHub or GitLab issues.
5. `AGENTS.md`: project memory for AI coding agents.
6. `README.md`: onboarding for humans.

The plan is not complete until it defines how the project runs in local/test and production/VPS Docker environments, how tests reach at least 80 percent coverage, how milestones are launched and rolled back, and how the team proves the definition of done.

## When to use

Use this skill when the user:

- provides a product idea, feature request, or project brief;
- asks for a PRD, SPEC, roadmap, milestones, or task breakdown;
- wants a tech lead to challenge scope and organize delivery;
- wants issue-ready tasks for GitHub or GitLab;
- wants Docker local and VPS production requirements included in planning;
- wants project memory and onboarding documentation.

Do not use this skill for a single-line bug fix, a typo, or a change whose scope is already fully specified and contains no product or architecture decisions. For those, implement directly.

## Non-negotiable rules

- Ask before inventing. Record every answer in the artifacts.
- Separate confirmed decisions from assumptions. Ask the user to approve assumptions before generating artifacts.
- Keep the PRD product-only and the SPEC engineering-only. Do not mix responsibilities.
- Keep traceability intact: `FR/NFR -> TR -> Milestone -> TASK -> Issue`.
- Enforce a coverage gate of at least 80 percent. Do not lower it without an explicit user decision.
- Include Docker for local/test and production/VPS in the SPEC and in the task plan.
- Treat production as hostile: non-root runtime, secrets outside the image, TLS, firewall, backups, healthchecks, resource limits, vulnerability scanning, and rollback.
- Make every task atomic: one issue, one pull request, one work session, five files or fewer.
- Do not implement application code unless the user explicitly asks after the plan is approved.
- Do not create issues, commit, push, or deploy without explicit confirmation.
- Do not commit secrets. Do not put credentials in examples, Compose files, Dockerfiles, or artifacts.
- Preserve the machine-readable HTML markers in the templates.
- Write generated artifacts in the user's language. Default to English. Keep machine-readable keys, IDs, tags, labels, and marker values in English.

## Workflow

Follow these gates in order. Do not skip a gate.

### Gate 1: Context

Inspect the workspace before asking questions:

- existing `README.md`, `AGENTS.md`, `CLAUDE.md`, package manifests, source layout, and infrastructure files;
- existing `PRD.md`, `SPEC.md`, `PLAN.md`, or `TASKS.md`;
- Git remote, issue provider (GitHub or GitLab), and existing issue or label conventions;
- the user's current message and any attached brief.

Reuse facts already available. Do not ask the user to repeat information that the repository already answers. State what you found and ask only about gaps and decisions.

### Gate 2: Brainstorm

Conduct a focused interview using the question bank in [references/question-bank.md](references/question-bank.md).

- Ask at most five questions per round.
- Prefer multiple-choice questions when the host supports structured questions.
- Otherwise use numbered questions and wait for answers.
- Start with the problem, users, outcome, and scope. Do not start with technology.
- Challenge the scope: ask what is explicitly out of scope, what can be cut from the first release, and what happens if the project does nothing.
- Ask for measurable success criteria, not adjectives.
- Ask about data, authentication, integrations, security, privacy, operations, and the VPS only when they are relevant to the idea.
- Cover every required category in the question bank across the rounds. If a category does not apply, record why.
- Cover launch strategy, milestones, issue tracker, label taxonomy, and AGENTS/README expectations before closing the interview.
- Stop interviewing when the answers are sufficient to make testable decisions. Do not ask questions for completeness alone.

After each round, summarize:

- confirmed answers;
- decisions made;
- assumptions you are making;
- open questions.

Ask the user to correct the summary before continuing.

### Gate 3: Approval

Before writing the artifacts, present a compact plan covering:

- the one-sentence product promise;
- primary users and the top jobs to be done;
- must-have and out-of-scope scope;
- measurable success criteria;
- proposed architecture and stack;
- security and data constraints;
- local/test and production/VPS approach;
- test strategy and the 80 percent coverage gate;
- launch strategy and the proposed milestone outline;
- issue tracker, label taxonomy, and issue automation approach;
- the main risks and trade-offs.

Ask the user to approve or correct it. Only generate the artifacts after approval. If the user says to proceed with assumptions, mark each assumption explicitly.

### Gate 4: PRD and SPEC

Create or update `PRD.md` and `SPEC.md` at the same time. They are a pair, not sequential drafts.

Use [references/prd-template.md](references/prd-template.md) and [references/spec-template.md](references/spec-template.md).

PRD requirements:

- Preserve the artifact marker and every required section marker.
- Keep product scope, users, success metrics, functional requirements, and business NFRs.
- Include every interview answer in the `Interview Answers` section.
- Use stable requirement IDs: `FR-001`, `FR-002`, `NFR-001`, and so on.
- Make every functional requirement testable. Include the actor, action, and observable outcome.
- Make every non-functional requirement measurable. Include a target and measurement method.
- State what is in scope and what is out of scope.
- Record assumptions, constraints, dependencies, and open decisions.
- Map every FR and NFR to at least one TR in the traceability section.
- Do not include architecture, Docker, or test commands.

SPEC requirements:

- Preserve the artifact marker and every required section marker.
- Cover context, architecture, components, data, interfaces, technical requirements, security, environments, testing, observability, decisions, risks, traceability, and definition of done.
- Use stable technical requirement IDs: `TR-001`, `TR-002`, and so on.
- Trace every TR back to at least one FR or NFR.
- Include the local and production Docker environment markers.
- Include the concrete coverage command and the 80 percent gate.
- Record architecture decisions and trade-offs.
- Do not redefine product scope or invent new FR/NFR requirements.

After writing both files, run a consistency pass:

- every FR and NFR appears in the SPEC traceability table;
- every TR maps to an existing FR or NFR;
- no technical requirement leaked into the PRD;
- no product scope leaked into the SPEC;
- IDs, names, and terms are consistent across both files.

### Gate 5: PLAN

Create or update `PLAN.md` using [references/plan-template.md](references/plan-template.md). The PLAN is the union of product and engineering.

Requirements:

- Preserve the artifact marker and every required section marker.
- Define the launch strategy: release model, rollout, go/no-go, rollback, communication, metrics, support, and on-call.
- Break the work into outcome-based milestones with stable IDs `M1`, `M2`, and so on.
- Give every milestone a goal, scope, requirements, exit criteria, launch gate, dependencies, target, and evidence.
- Map every FR, NFR, and TR to at least one milestone.
- Do not invent requirements. If a gap is found, update the PRD and SPEC first.
- Keep milestones shippable and user-visible, not technical layers.

Present the milestone outline to the user before generating `TASKS.md`. Correct the PLAN first if the milestones are wrong.

### Gate 6: TASKS

Create or update `TASKS.md` using [references/tasks-template.md](references/tasks-template.md) and [references/issue-format.md](references/issue-format.md).

Requirements:

- Preserve the artifact marker and every required section marker.
- Decompose every milestone into atomic technical tasks.
- Give every task a stable ID: `TASK-001`, `TASK-002`, and so on.
- Order tasks by milestone and dependency, from foundation to production verification.
- Keep each task focused enough for one work session and five files or fewer.
- Give every task at least one PRD reference, at least one SPEC reference, a milestone, dependencies, acceptance criteria, a verification step, and the files it touches.
- Add issue metadata to every task: `Issue title`, `Labels`, and `Estimate`.
- Use the label taxonomy: `type:*`, `area:*`, `priority:*`, plus the mandatory tags.
- Include tasks for data model and migrations, core functionality, error and edge cases, tests, local Docker, CI, production Docker, security hardening, observability, deployment, rollback, and documentation.
- Include the mandatory tags: `docker-local`, `docker-production`, `coverage-gate`, `security`, `deployment`.
- Include a final gate task tagged `final-gate`.
- Map every FR, NFR, TR, and milestone in the traceability section.
- Run the issue export in dry-run mode to prove that every task produces a valid issue payload. Do not create issues.

### Gate 7: Project Memory

Create or update `AGENTS.md` and `README.md` last, using [references/agents-template.md](references/agents-template.md) and [references/readme-template.md](references/readme-template.md).

Requirements:

- Preserve existing accurate content. Merge instead of overwriting user documentation.
- Use only commands and paths that exist in the final artifacts.
- `AGENTS.md` covers overview, stack, layout, commands, conventions, engineering rules, decisions, definition of done, and security.
- `README.md` covers overview, status, Docker quickstart, commands, architecture summary, documentation index, testing, deployment, and security.
- Link both files to `PRD.md`, `SPEC.md`, `PLAN.md`, and `TASKS.md` where relevant.
- Do not add speculative commands or future features.
- Do not include secrets or real credentials.

### Gate 8: Validation

Resolve the validator path relative to this `SKILL.md` and run:

```bash
python3 scripts/validate_artifacts.py PRD.md TASKS.md --all --coverage 80
```

`--all` loads `SPEC.md`, `PLAN.md`, `AGENTS.md`, and `README.md` next to the PRD. Pass explicit paths when the artifacts live elsewhere.

If the host installed the plugin elsewhere, use the absolute path to the bundled script. Add `--strict` when the user wants warnings treated as errors. Add `--json` when a machine-readable report is useful.

Then run the issue export in dry-run mode:

```bash
python3 scripts/export_issues.py --tasks TASKS.md --plan PLAN.md --provider github --format json
python3 scripts/export_issues.py --tasks TASKS.md --plan PLAN.md --provider gitlab --format json
```

If Python is unavailable, perform the manual checklist in [references/validation-checklist.md](references/validation-checklist.md).

Fix every error. Re-run validation until it passes. Do not deliver artifacts that fail validation.

### Gate 9: Handoff

Report:

- where the six artifacts were written;
- the validation result and coverage gate;
- the milestone summary and launch strategy;
- the highest-risk assumptions;
- the recommended first task and issue;
- the dry-run issue count and the exact command to apply it;
- that implementation and issue creation have not started.

Offer to begin `TASK-001` or create the issues, but do not start unless the user asks.

## Artifact contract

All artifacts use version 2 markers.

- `PRD.md`: `<!-- techlead:artifact type=prd version=2 -->`
- `SPEC.md`: `<!-- techlead:artifact type=spec version=2 -->`
- `PLAN.md`: `<!-- techlead:artifact type=plan version=2 -->`
- `TASKS.md`: `<!-- techlead:artifact type=tasks version=2 -->`
- `AGENTS.md`: `<!-- techlead:artifact type=agents version=2 -->`
- `README.md`: `<!-- techlead:artifact type=readme version=2 -->`

Requirements:

- `FR-xxx` and `NFR-xxx` are defined only in the PRD.
- `TR-xxx` is defined only in the SPEC.
- Milestones use `<!-- techlead:milestone id=M1 order=1 depends=none covers=FR-001,TR-001 -->`.
- Tasks use `<!-- techlead:task id=TASK-001 depends=none prd=FR-001 spec=TR-001 milestone=M1 tags=foundation labels=type:feature,area:api,priority:p1 -->`.

## Docker standard for generated projects

The SPEC and TASKS must define both environments.

### Local and test

- A development Dockerfile or Compose service with hot reload or fast rebuilds.
- A dedicated test service that runs the full test suite with coverage.
- Local database or dependencies with persistent volumes where appropriate.
- Seed data and a documented reset command.
- Healthchecks for long-running services.
- No production secrets and no production credentials.
- One documented command to start the stack and one to run tests.

### Production on a VPS

- A multi-stage production Dockerfile with pinned base image versions or digests.
- A non-root runtime user and a minimal final image.
- Read-only root filesystem where the runtime permits it, plus explicit writable mounts.
- `cap_drop: [ALL]`, `security_opt: [no-new-privileges:true]`, and resource limits.
- Secrets supplied at runtime, never baked into the image or committed to Git.
- Healthchecks, restart policy, log rotation, and centralized logs or metrics.
- A reverse proxy with TLS termination and secure headers.
- Host hardening: key-only SSH, firewall, automatic security updates, and intrusion protection.
- Backup and restore procedure, tested at least once.
- Image vulnerability scanning with no unresolved critical or high findings.
- A repeatable deployment command, a smoke test, and a tested rollback to the previous image.

Use [references/docker-baseline.md](references/docker-baseline.md) and [references/testing-baseline.md](references/testing-baseline.md) for the detailed checklists.

## Issue automation

Use `scripts/export_issues.py` to convert `TASKS.md` into issues.

- The default is a dry-run. Nothing is created without `--apply`.
- `--provider github` uses `gh`; `--provider gitlab` uses `glab`.
- The exporter creates missing labels and milestones, creates issues in task order, and resolves dependencies in a second pass.
- A task must have a unique issue title, a valid milestone, labels, an estimate, acceptance, verification, and files.
- Do not create issues until the user explicitly approves.

## Definition of done

The generated project is done only when:

- every task in `TASKS.md` is complete and verified;
- every FR, NFR, and TR is implemented and covered by at least one task;
- the test suite passes and coverage is at least 80 percent;
- the local/test Docker environment starts cleanly and passes the test suite;
- the production image builds, scans clean, deploys to the VPS, and passes a smoke test;
- rollback and backup restore have been exercised;
- security, privacy, and operational documentation are current;
- no secrets are committed and no critical or high vulnerabilities remain;
- every task dry-runs successfully as a GitHub or GitLab issue.

## Handling scope changes

If the user changes scope after approval:

1. update `PRD.md` and `SPEC.md` first;
2. update requirement IDs and traceability;
3. update `PLAN.md` milestones;
4. update `TASKS.md`, dependencies, labels, and issue metadata;
5. update `AGENTS.md` and `README.md` when commands or layout change;
6. re-run validation and the issue dry-run;
7. report what changed and what work is now obsolete.

Do not silently add features to the task list.

## Resources

- [Question bank](references/question-bank.md): interview categories and decision rules.
- [PRD template](references/prd-template.md): product structure and markers.
- [SPEC template](references/spec-template.md): architecture structure and markers.
- [PLAN template](references/plan-template.md): launch strategy and milestone structure.
- [TASKS template](references/tasks-template.md): atomic tasks and issue metadata.
- [Issue format](references/issue-format.md): labels, titles, bodies, and export commands.
- [AGENTS template](references/agents-template.md): project memory structure.
- [README template](references/readme-template.md): onboarding structure.
- [Docker baseline](references/docker-baseline.md): local/test and production/VPS requirements.
- [Testing baseline](references/testing-baseline.md): test levels, coverage commands, and CI gates.
- [Validation checklist](references/validation-checklist.md): manual fallback when the script cannot run.
- `scripts/validate_artifacts.py`: machine-readable validation for all artifacts.
- `scripts/export_issues.py`: GitHub and GitLab issue export with dry-run.
