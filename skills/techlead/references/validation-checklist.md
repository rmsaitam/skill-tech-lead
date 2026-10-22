# Validation Checklist

Use this checklist when the validator script cannot run.

## PRD

- [ ] The file starts with `<!-- techlead:artifact type=prd version=1 -->`.
- [ ] Status, date, owner, artifact language, and coverage gate are present.
- [ ] Every required section marker exists:
  - `summary`
  - `problem`
  - `users`
  - `scope`
  - `functional`
  - `nonfunctional`
  - `assumptions`
  - `architecture`
  - `security`
  - `docker`
  - `testing`
  - `dod`
  - `risks`
  - `qa`
  - `traceability`
- [ ] In-scope and out-of-scope lists are explicit.
- [ ] At least one `FR-xxx` and one `NFR-xxx` exist.
- [ ] Requirement IDs are unique and every requirement is testable or measurable.
- [ ] The Docker section has `<!-- techlead:env id=local -->` and `<!-- techlead:env id=production -->`.
- [ ] Local Docker covers development, tests, dependencies, healthchecks, and startup commands.
- [ ] Production Docker covers the image, non-root runtime, secrets, reverse proxy, TLS, host hardening, backups, monitoring, scanning, deployment, and rollback.
- [ ] The testing strategy names the coverage command and states a gate of at least 80 percent.
- [ ] The definition of done contains checkboxes for tasks, requirements, coverage, local Docker, production image, VPS smoke test, rollback, documentation, and secrets.
- [ ] The interview answers section has at least eight question and answer pairs.
- [ ] The traceability table maps requirements to tasks.
- [ ] No `TODO`, `TBD`, `FIXME`, `[insert`, or `<insert` placeholders remain.

## TASKS

- [ ] The file starts with `<!-- techlead:artifact type=tasks version=1 -->`.
- [ ] Source PRD, status, and execution order are present.
- [ ] Required sections exist: `rules`, `tasks`, `traceability`, `dod`.
- [ ] At least six task markers exist.
- [ ] Task IDs are unique and in increasing order.
- [ ] Every task has dependencies, at least one PRD reference, acceptance criteria, verification, and files.
- [ ] Dependencies refer to earlier tasks or `none`.
- [ ] No task is left with a placeholder.
- [ ] The mandatory tags appear at least once: `docker-local`, `docker-production`, `coverage-gate`, `security`, `deployment`.
- [ ] Every `FR-xxx` and `NFR-xxx` from the PRD appears in at least one task.
- [ ] The traceability table includes every requirement.
- [ ] The definition of done contains checkboxes and states the 80 percent coverage gate.
- [ ] A final gate task verifies the complete definition of done.

## Evidence

- [ ] The coverage command has been run or is explicitly scheduled in the coverage task.
- [ ] The local Docker start and test commands are documented.
- [ ] The production deployment, smoke test, and rollback commands are documented.
- [ ] The backup and restore procedure is documented.
- [ ] The security scanning step is documented.
- [ ] The release evidence requirements are documented.
