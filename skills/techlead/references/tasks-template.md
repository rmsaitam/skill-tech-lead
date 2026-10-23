# TASKS Template

Copy this structure into `TASKS.md`. Every task is atomic, technical, and directly convertible into one GitHub or GitLab issue. The task must belong to a milestone in `PLAN.md` and trace to `PRD.md` and `SPEC.md`.

Preserve every HTML marker exactly. The prose may be translated; marker IDs, field keys, requirement IDs, task IDs, labels, and tags stay in English.

```markdown
<!-- techlead:artifact type=tasks version=2 -->
# TASKS: Project Name

- Source PRD: `./PRD.md`
- Source SPEC: `./SPEC.md`
- Source PLAN: `./PLAN.md`
- Status: Approved
- Execution order: top to bottom, respecting dependencies

<!-- techlead:section id=rules -->
## Execution Rules

- Work in task order unless all dependencies for parallel work are complete.
- Do not start a task until every task in its `Depends on` field is done and verified.
- One task equals one issue, one pull request, and one work session.
- Update the checkbox only after the verification step passes.
- Keep each task to five files or fewer. Split larger work.
- If scope changes, update `PRD.md` and `SPEC.md` first, then `PLAN.md`, then this file.
- Re-run artifact validation and the issue dry-run after any change.

<!-- techlead:section id=tasks -->
## Tasks

### Phase 1: Foundation (M1)

<!-- techlead:task id=TASK-001 depends=none prd=FR-001,NFR-001 spec=TR-001 milestone=M1 tags=foundation labels=type:chore,area:infra,priority:p1 -->
### TASK-001: Bootstrap the application skeleton

- [ ] Status
- Depends on: none
- PRD: FR-001, NFR-001
- SPEC: TR-001
- Milestone: M1
- Issue title: Bootstrap the application skeleton
- Labels: type:chore, area:infra, priority:p1
- Estimate: S
- Acceptance: The application starts locally with the approved runtime and exposes a health endpoint.
- Verify: Run the documented start command and call the health endpoint.
- Files: src/main.py, src/health.py, tests/test_health.py, pyproject.toml

<!-- techlead:task id=TASK-002 depends=TASK-001 prd=FR-001,NFR-003 spec=TR-001,TR-003 milestone=M1 tags=foundation labels=type:feature,area:api,priority:p1 -->
### TASK-002: Implement the primary domain model

- [ ] Status
- Depends on: TASK-001
- PRD: FR-001, NFR-003
- SPEC: TR-001, TR-003
- Milestone: M1
- Issue title: Implement the primary domain model
- Labels: type:feature, area:api, priority:p1
- Estimate: M
- Acceptance: The primary entity, validation rules, and invariants are implemented and covered by unit tests.
- Verify: Run the unit test suite for the domain module.
- Files: src/domain/models.py, src/domain/validation.py, tests/domain/test_models.py

<!-- techlead:task id=TASK-003 depends=TASK-002 prd=FR-001,NFR-002 spec=TR-002 milestone=M1 tags=docker-local,security labels=type:infra,area:data,priority:p1 -->
### TASK-003: Add persistence and migrations

- [ ] Status
- Depends on: TASK-002
- PRD: FR-001, NFR-002
- SPEC: TR-002
- Milestone: M1
- Issue title: Add persistence and migrations
- Labels: type:infra, area:data, priority:p1
- Estimate: M
- Acceptance: The schema is created by a reversible migration and repository tests pass against a disposable database.
- Verify: Run migrations up and down, then run the integration tests.
- Files: migrations/001_initial.sql, src/repository.py, tests/integration/test_repository.py

### Phase 2: Core behavior (M2)

<!-- techlead:task id=TASK-004 depends=TASK-003 prd=FR-002 spec=TR-001,TR-003 milestone=M2 tags=security labels=type:feature,area:api,priority:p1 -->
### TASK-004: Implement the primary user journey

- [ ] Status
- Depends on: TASK-003
- PRD: FR-002
- SPEC: TR-001, TR-003
- Milestone: M2
- Issue title: Implement the primary user journey
- Labels: type:feature, area:api, priority:p1
- Estimate: M
- Acceptance: The user completes the primary journey and observes the approved outcome, including validation errors.
- Verify: Run the end-to-end test for the primary journey.
- Files: src/api/routes.py, src/api/handlers.py, tests/e2e/test_primary_journey.py

<!-- techlead:task id=TASK-005 depends=TASK-004 prd=FR-003,NFR-003 spec=TR-004 milestone=M2 tags=security labels=type:security,area:api,priority:p1 -->
### TASK-005: Enforce authorization and audit logging

- [ ] Status
- Depends on: TASK-004
- PRD: FR-003, NFR-003
- SPEC: TR-004
- Milestone: M2
- Issue title: Enforce authorization and audit logging
- Labels: type:security, area:api, priority:p1
- Estimate: M
- Acceptance: Only authorized roles perform protected actions, and every decision is recorded without sensitive fields.
- Verify: Run the authorization and audit test suites and inspect a sample audit record.
- Files: src/security/authorization.py, src/security/audit.py, tests/security/test_authorization.py

### Phase 3: Quality and delivery (M3)

<!-- techlead:task id=TASK-006 depends=TASK-005 prd=NFR-001,NFR-005 spec=TR-004 milestone=M3 tags=coverage-gate labels=type:test,area:quality,priority:p1 -->
### TASK-006: Reach the coverage gate

- [ ] Status
- Depends on: TASK-005
- PRD: NFR-001, NFR-005
- SPEC: TR-004
- Milestone: M3
- Issue title: Reach the coverage gate
- Labels: type:test, area:quality, priority:p1
- Estimate: M
- Acceptance: Unit, integration, contract, and end-to-end tests cover the primary flows and total coverage is at least 80 percent.
- Verify: Run the coverage command and confirm the total is at least 80 percent.
- Files: tests/conftest.py, tests/unit, tests/integration, tests/e2e, pyproject.toml

<!-- techlead:task id=TASK-007 depends=TASK-006 prd=NFR-001 spec=TR-003 milestone=M3 tags=docker-local,docker-production,security labels=type:infra,area:infra,priority:p1 -->
### TASK-007: Build local and production Docker environments

- [ ] Status
- Depends on: TASK-006
- PRD: NFR-001
- SPEC: TR-003
- Milestone: M3
- Issue title: Build local and production Docker environments
- Labels: type:infra, area:infra, priority:p1
- Estimate: M
- Acceptance: The local stack starts from a clean checkout, the test service passes, and the production image is multi-stage, pinned, non-root, and scans clean.
- Verify: Start the local stack, run the test service, build the production image, and run the image scan.
- Files: Dockerfile, Dockerfile.dev, compose.local.yml, compose.production.yml, .dockerignore

<!-- techlead:task id=TASK-008 depends=TASK-007 prd=NFR-002,NFR-003 spec=TR-003 milestone=M3 tags=deployment,security labels=type:infra,area:deploy,priority:p1 -->
### TASK-008: Deploy to the VPS with smoke test and rollback

- [ ] Status
- Depends on: TASK-007
- PRD: NFR-002, NFR-003
- SPEC: TR-003
- Milestone: M3
- Issue title: Deploy to the VPS with smoke test and rollback
- Labels: type:infra, area:deploy, priority:p1
- Estimate: M
- Acceptance: The deployment publishes the image, applies migrations, passes the smoke test, and rolls back to the previous image.
- Verify: Deploy to staging, run the smoke test, execute rollback, and confirm the previous version serves traffic.
- Files: deploy.sh, docs/runbook.md, scripts/smoke.sh, compose.production.yml

<!-- techlead:task id=TASK-009 depends=TASK-008 prd=FR-001,FR-002,FR-003,NFR-001,NFR-002,NFR-003,NFR-005 spec=TR-001,TR-002,TR-003,TR-004 milestone=M3 tags=final-gate labels=type:chore,area:quality,priority:p1 -->
### TASK-009: Verify the definition of done

- [ ] Status
- Depends on: TASK-008
- PRD: FR-001, FR-002, FR-003, NFR-001, NFR-002, NFR-003, NFR-005
- SPEC: TR-001, TR-002, TR-003, TR-004
- Milestone: M3
- Issue title: Verify the definition of done
- Labels: type:chore, area:quality, priority:p1
- Estimate: S
- Acceptance: Every task, requirement, coverage gate, Docker environment, deployment step, rollback, and documentation check passes.
- Verify: Re-run the complete acceptance suite and attach evidence to the release record.
- Files: docs/release-evidence.md, docs/runbook.md, tests/acceptance

<!-- techlead:section id=issue-format -->
## Issue Format

- Every task marker maps to one issue title, one milestone, and a label set.
- Issue title convention: `[TASK-001] <Issue title>`; keep the title imperative and unique.
- Labels must include `type:*`, `area:*`, and `priority:*`; task tags become `techlead:<tag>` labels.
- Estimate is `XS`, `S`, `M`, `L`, or 1 to 8 points.
- Milestone must exist in `PLAN.md`; the exporter creates native milestones.
- Dependencies are resolved after issue creation and written as `Depends on: #N`.
- Dry-run with `scripts/export_issues.py --format json` before creating anything.
- Create issues with `gh` for GitHub or `glab` for GitLab only after explicit approval.
- The full issue body template is documented in `references/issue-format.md`.

<!-- techlead:section id=traceability -->
## Traceability

| Requirement | Tasks |
| --- | --- |
| FR-001 | TASK-001, TASK-002, TASK-009 |
| FR-002 | TASK-004, TASK-009 |
| FR-003 | TASK-005, TASK-009 |
| NFR-001 | TASK-001, TASK-006, TASK-007, TASK-009 |
| NFR-002 | TASK-003, TASK-008, TASK-009 |
| NFR-003 | TASK-002, TASK-005, TASK-008, TASK-009 |
| NFR-005 | TASK-006, TASK-009 |
| TR-001 | TASK-001, TASK-002, TASK-004, TASK-009 |
| TR-002 | TASK-003, TASK-009 |
| TR-003 | TASK-002, TASK-004, TASK-007, TASK-008, TASK-009 |
| TR-004 | TASK-005, TASK-006, TASK-009 |

| Milestone | Tasks |
| --- | --- |
| M1 | TASK-001, TASK-002, TASK-003 |
| M2 | TASK-004, TASK-005 |
| M3 | TASK-006, TASK-007, TASK-008, TASK-009 |

Every requirement and milestone must appear in this section. A requirement with no task is a planning defect.

<!-- techlead:section id=dod -->
## Definition of Done

- [ ] Every task above is checked and its verification step passed.
- [ ] Every FR, NFR, and TR is implemented and covered by at least one task.
- [ ] Test coverage is at least 80 percent.
- [ ] The local/test Docker environment starts cleanly and passes the test suite.
- [ ] The production image builds, scans clean, and passes the VPS smoke test.
- [ ] Rollback and backup restore have been exercised.
- [ ] Security, privacy, and operational documentation are current.
- [ ] No secrets are committed and no critical or high vulnerabilities remain.
- [ ] Every task dry-runs successfully as a GitHub or GitLab issue.
```
