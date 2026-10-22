---
name: techlead
description: Run a structured brainstorming interview for a product idea and produce a traceable PRD.md plus an ordered TASKS.md. Use when the user asks for a tech lead, product requirements, project planning, task breakdown, a PRD, an implementation plan, or wants to turn an idea into executable engineering work with Docker environments and a test coverage gate of at least 80 percent.
license: MIT
metadata:
  author: TechLead contributors
  version: "0.1.0"
---

# TechLead

Turn an idea into two engineering artifacts:

1. `PRD.md`: the product requirements document, including every interview answer.
2. `TASKS.md`: the implementation tasks in PRD dependency order, with acceptance criteria and verification steps.

The plan is not complete until it defines how the project will run in local/test and production/VPS Docker environments, how tests will reach at least 80 percent coverage, and how the team will prove the definition of done.

## When to use

Use this skill when the user:

- provides a product idea, feature request, or project brief;
- asks for a PRD, specification, roadmap, or task breakdown;
- wants a tech lead to challenge scope and organize delivery;
- wants implementation tasks with acceptance criteria and verification;
- wants Docker local and VPS production requirements included in planning.

Do not use this skill for a single-line bug fix, a typo, or a change whose scope is already fully specified and contains no product decisions. For those, implement directly.

## Non-negotiable rules

- Ask before inventing. Record every answer in `PRD.md`.
- Separate confirmed decisions from assumptions. Ask the user to approve assumptions before generating the PRD.
- Keep the PRD and TASKS traceable. Every task references at least one `FR-xxx` or `NFR-xxx`.
- Enforce a coverage gate of at least 80 percent. Do not lower it without an explicit user decision, and record the exception in the PRD.
- Include Docker for local/test and production/VPS in every PRD and task plan.
- Treat production as hostile: non-root runtime, secrets outside the image, TLS, firewall, backups, healthchecks, resource limits, vulnerability scanning, and rollback.
- Do not implement application code unless the user explicitly asks after the plan is approved.
- Do not commit secrets. Do not put credentials in examples, Compose files, Dockerfiles, or the PRD.
- Preserve the machine-readable HTML markers in the templates. They keep validation working when the prose is translated.
- Write `PRD.md` and `TASKS.md` in the user's language. Default to English. Keep machine-readable keys, IDs, tags, and marker values in English.

## Workflow

Follow these gates in order. Do not skip a gate.

### Gate 1: Context

Inspect the workspace before asking questions:

- existing `README`, `AGENTS.md`, `CLAUDE.md`, package manifests, source layout, and infrastructure files;
- existing `PRD.md` or `TASKS.md`, if present;
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
- the main risks and trade-offs.

Ask the user to approve or correct it. Only generate `PRD.md` after approval. If the user says to proceed with assumptions, mark each assumption explicitly in the PRD.

### Gate 4: PRD

Create or update `PRD.md` using [references/prd-template.md](references/prd-template.md).

Requirements:

- Preserve the artifact marker and every required section marker.
- Include every interview question and answer in the `Interview Answers` section.
- Use stable requirement IDs: `FR-001`, `FR-002`, `NFR-001`, and so on. Do not renumber approved requirements without recording the change.
- Make every functional requirement testable. Include the actor, action, and observable outcome.
- Make every non-functional requirement measurable. Include a target and, where relevant, the measurement method.
- State what is in scope and what is out of scope.
- Record assumptions, constraints, dependencies, and open decisions.
- Include a Docker section with explicit local/test and production/VPS subsections.
- Include a testing strategy with the concrete coverage command and the 80 percent gate.
- Include a definition of done with checkboxes.
- Include a requirement traceability section.
- Do not leave `TODO`, `TBD`, `FIXME`, or bracketed placeholders.

### Gate 5: TASKS

Create or update `TASKS.md` using [references/tasks-template.md](references/tasks-template.md).

Requirements:

- Preserve the artifact marker and every required section marker.
- Order tasks by dependency and PRD order, from foundation to production verification.
- Keep each task focused enough for one work session and roughly five files or fewer.
- Give every task a stable ID: `TASK-001`, `TASK-002`, and so on.
- Give every task at least one PRD reference, explicit dependencies, acceptance criteria, a verification step, and the files or modules it touches.
- Include critical tags so the validator can confirm coverage of non-negotiable work:
  - `docker-local`
  - `docker-production`
  - `coverage-gate`
  - `security`
  - `deployment`
- Include tasks for data model and migrations, core functionality, error and edge cases, tests, local Docker, CI, production Docker, security hardening, observability, deployment, rollback, and documentation.
- Include a final gate task that verifies every requirement and every definition-of-done item.
- Include a traceability section mapping every `FR-xxx` and `NFR-xxx` to at least one task.
- Do not leave `TODO`, `TBD`, `FIXME`, or bracketed placeholders.

### Gate 6: Validation

Resolve the validator path relative to this `SKILL.md` and run:

```bash
python3 scripts/validate_artifacts.py PRD.md TASKS.md --coverage 80
```

If the host installed the plugin elsewhere, use the absolute path to the bundled script. Add `--strict` when the user wants warnings treated as errors. Add `--json` when a machine-readable report is useful.

If Python is unavailable, perform the manual checklist in [references/validation-checklist.md](references/validation-checklist.md).

Fix every error. Re-run validation until it passes. Do not deliver artifacts that fail validation.

### Gate 7: Handoff

Report:

- where `PRD.md` and `TASKS.md` were written;
- the validation result and coverage gate;
- the highest-risk assumptions;
- the recommended first task;
- that implementation has not started.

Offer to begin `TASK-001`, but do not start it unless the user asks.

## Docker standard for generated projects

The PRD and TASKS must define both environments.

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

## Definition of done

The generated project is done only when:

- every task in `TASKS.md` is complete and verified;
- every `FR-xxx` and `NFR-xxx` is implemented and covered by at least one task;
- the test suite passes and coverage is at least 80 percent;
- the local/test Docker environment starts cleanly and passes the test suite;
- the production image builds, scans clean, deploys to the VPS, and passes a smoke test;
- rollback and backup restore have been exercised;
- security, privacy, and operational documentation are current;
- no secrets are committed and no critical or high vulnerabilities remain.

## Handling scope changes

If the user changes scope after approval:

1. update `PRD.md` first;
2. update requirement IDs and traceability;
3. update `TASKS.md` and dependencies;
4. re-run validation;
5. report what changed and what work is now obsolete.

Do not silently add features to the task list.

## Resources

- [Question bank](references/question-bank.md): interview categories and decision rules.
- [PRD template](references/prd-template.md): required PRD structure and markers.
- [TASKS template](references/tasks-template.md): required task structure and tags.
- [Docker baseline](references/docker-baseline.md): local/test and production/VPS requirements.
- [Testing baseline](references/testing-baseline.md): test levels, coverage commands, and CI gates.
- [Validation checklist](references/validation-checklist.md): manual fallback when the script cannot run.
- `scripts/validate_artifacts.py`: machine-readable validation for generated artifacts.
