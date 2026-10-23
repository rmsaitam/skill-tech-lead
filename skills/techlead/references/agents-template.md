# AGENTS Template

Create or update `AGENTS.md` after `PRD.md`, `SPEC.md`, `PLAN.md`, and `TASKS.md` are approved. This file is the project memory for AI coding agents. Keep it short, factual, and tied to real commands and paths.

```markdown
<!-- techlead:artifact type=agents version=2 -->
# AGENTS: Project Name

- Source artifacts: `PRD.md`, `SPEC.md`, `PLAN.md`, `TASKS.md`

<!-- techlead:section id=overview -->
## Project Overview

- One paragraph describing the product, users, and primary outcome.
- Current milestone and release stage from `PLAN.md`.
- Link to `PRD.md` for product decisions and `SPEC.md` for engineering decisions.

<!-- techlead:section id=stack -->
## Stack and Architecture

- Language, framework, runtime, database, and key libraries with versions.
- Main components and their responsibilities.
- Link to `SPEC.md` for interfaces, data model, and architecture decisions.

<!-- techlead:section id=layout -->
## Repository Layout

- `src/`: application code organized by component.
- `tests/`: unit, integration, contract, and end-to-end suites.
- `docs/`: product, architecture, and operational documentation.
- Docker, Compose, CI, and deployment configuration paths.
- Generated artifacts: `PRD.md`, `SPEC.md`, `PLAN.md`, `TASKS.md`.

<!-- techlead:section id=commands -->
## Commands

- Setup: command that installs dependencies.
- Development: `docker compose -f compose.local.yml up --build`.
- Tests: `docker compose -f compose.local.yml run --rm tests`.
- Coverage: command that enforces the 80 percent gate.
- Lint and typecheck: commands that must pass before merge.
- Build: command that produces the production image.
- Deploy: documented command from `PLAN.md`.
- Rollback: documented command that restores the previous image.

<!-- techlead:section id=conventions -->
## Conventions

- Follow the existing code style and directory structure.
- One task equals one issue and one pull request.
- Branch names use the task ID, for example `task/TASK-001-short-title`.
- Commit messages are imperative and reference the task ID.
- Update tests with behavior changes and never weaken assertions.
- Update `PRD.md`, `SPEC.md`, and `PLAN.md` before changing scope.

<!-- techlead:section id=rules -->
## Engineering Rules

- Keep test coverage at or above 80 percent.
- Never commit secrets or real credentials.
- Keep local and production Docker behavior aligned.
- Keep traceability from requirement to milestone to task current.
- Do not create issues, commit, push, or deploy without explicit approval.
- Record architecture decisions in `SPEC.md`.

<!-- techlead:section id=decisions -->
## Decisions and Sources of Truth

- Product scope: `PRD.md`.
- Architecture, interfaces, data, and security: `SPEC.md`.
- Milestones and launch strategy: `PLAN.md`.
- Atomic execution tasks and issue metadata: `TASKS.md`.
- Architecture decision records: the decisions section of `SPEC.md`.

<!-- techlead:section id=dod -->
## Definition of Done

- Every task is complete and verified.
- Every requirement is covered by a task.
- Tests pass with at least 80 percent coverage.
- The local Docker stack passes the suite.
- The production image deploys and passes the smoke test.
- Rollback and backup restore have been exercised.

<!-- techlead:section id=security -->
## Security and Secrets

- Secrets are injected at runtime and never written to the repository.
- The runtime container uses a non-root user and drops capabilities.
- Do not log credentials, tokens, personal data, or sensitive payloads.
- Run dependency and image scanning before release.
- Report a suspected secret exposure immediately and rotate the credential.

<!-- techlead:section id=maintenance -->
## Maintaining This File

- Update this file when commands, layout, stack, or conventions change.
- Keep links to `PRD.md`, `SPEC.md`, `PLAN.md`, and `TASKS.md` valid.
- Do not add speculative commands that are not implemented in the repository.
```
