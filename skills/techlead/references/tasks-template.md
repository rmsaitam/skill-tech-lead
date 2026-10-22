# TASKS Template

Copy this structure into `TASKS.md`. Replace every prompt with an executable task. Preserve every HTML marker exactly. The prose may be translated; marker IDs, field keys, requirement IDs, task IDs, and tags stay in English.

```markdown
<!-- techlead:artifact type=tasks version=1 -->
# TASKS: Project Name

- Source PRD: `./PRD.md`
- Status: Approved
- Execution order: top to bottom, respecting dependencies

<!-- techlead:section id=rules -->
## Execution Rules

- Work in task order unless all dependencies for parallel work are complete.
- Do not start a task until every task in its `Depends on` field is done and verified.
- Update the checkbox only after the verification step passes.
- Keep each task focused. If a task grows beyond roughly five files, split it.
- If scope changes, update `PRD.md` first, then update this file and re-run validation.
- Record deviations and follow-up work in the PRD risk or open-decision section.

<!-- techlead:section id=tasks -->
## Tasks

### Phase 1: Foundation

<!-- techlead:task id=TASK-001 depends=none prd=FR-001,NFR-001 tags=foundation -->
### TASK-001: Task title

- [ ] Status
- Depends on: none
- PRD: FR-001, NFR-001
- Acceptance: Observable and testable condition that proves the task is complete.
- Verify: Exact command or manual check that proves acceptance.
- Files: Paths or modules expected to change.

<!-- techlead:task id=TASK-002 depends=TASK-001 prd=FR-002 tags=core -->
### TASK-002: Task title

- [ ] Status
- Depends on: TASK-001
- PRD: FR-002
- Acceptance: Observable and testable condition that proves the task is complete.
- Verify: Exact command or manual check that proves acceptance.
- Files: Paths or modules expected to change.

### Phase 2: Security and quality

<!-- techlead:task id=TASK-003 depends=TASK-002 prd=NFR-003 tags=security -->
### TASK-003: Implement and verify security controls

- [ ] Status
- Depends on: TASK-002
- PRD: NFR-003
- Acceptance: Required authentication, authorization, validation, secret handling, and audit controls are implemented and tested.
- Verify: Security tests, dependency scan, and configuration review pass.
- Files: Authentication, authorization, validation, and configuration paths.

<!-- techlead:task id=TASK-004 depends=TASK-002 tags=coverage-gate -->
### TASK-004: Reach the coverage gate

- [ ] Status
- Depends on: TASK-002
- PRD: NFR-001
- Acceptance: Unit, integration, and end-to-end tests cover the primary flows and failure paths, and total coverage is at least 80 percent.
- Verify: Run the coverage command and confirm the total is >= 80 percent.
- Files: Test suites, fixtures, and coverage configuration.

### Phase 3: Docker and delivery

<!-- techlead:task id=TASK-005 depends=TASK-003,TASK-004 tags=docker-local -->
### TASK-005: Build the local and test Docker environment

- [ ] Status
- Depends on: TASK-003, TASK-004
- PRD: NFR-001, NFR-003
- Acceptance: A documented Compose command starts the development stack, and the test service runs the full suite with coverage.
- Verify: Start the stack from a clean checkout, run the test service, and confirm healthchecks pass.
- Files: Development Dockerfile, local Compose file, environment example, and test scripts.

<!-- techlead:task id=TASK-006 depends=TASK-005 tags=docker-production,security -->
### TASK-006: Build the hardened production image

- [ ] Status
- Depends on: TASK-005
- PRD: NFR-003
- Acceptance: The production image is multi-stage, uses pinned bases, runs as non-root, drops capabilities, uses no baked secrets, and passes vulnerability scanning.
- Verify: Build the image, inspect its configuration, and run the image scan.
- Files: Production Dockerfile, Docker ignore file, Compose production file, and reverse proxy configuration.

<!-- techlead:task id=TASK-007 depends=TASK-006 tags=deployment -->
### TASK-007: Deploy to the VPS with rollback

- [ ] Status
- Depends on: TASK-006
- PRD: NFR-002, NFR-003
- Acceptance: The deployment command publishes the image, applies migrations, passes the smoke test, and can roll back to the previous image.
- Verify: Deploy to a staging or production VPS, run the smoke test, then execute and verify the rollback procedure.
- Files: Deployment workflow, server runbook, Compose production file, and smoke test script.

<!-- techlead:task id=TASK-008 depends=TASK-007 tags=observability,docs -->
### TASK-008: Add observability and operational documentation

- [ ] Status
- Depends on: TASK-007
- PRD: NFR-005
- Acceptance: Logs, metrics, alerts, backup, restore, and incident procedures are documented and exercised.
- Verify: Trigger a test alert, run a backup and restore, and review the runbook with the operator.
- Files: Monitoring configuration, runbook, backup scripts, and documentation.

### Phase 4: Final gate

<!-- techlead:task id=TASK-009 depends=TASK-008 tags=final-gate -->
### TASK-009: Verify the definition of done

- [ ] Status
- Depends on: TASK-008
- PRD: FR-001, FR-002, NFR-001, NFR-002, NFR-003, NFR-005
- Acceptance: Every task, requirement, coverage gate, Docker environment, deployment step, rollback, and documentation check passes.
- Verify: Re-run the complete acceptance suite and attach the evidence to the delivery record.
- Files: Verification report and release notes.

Mandatory tags and their purpose:

- `docker-local`: local/test Docker environment.
- `docker-production`: hardened production image and Compose configuration.
- `coverage-gate`: proof that coverage is at least 80 percent.
- `security`: authentication, authorization, validation, secrets, scanning, or audit controls.
- `deployment`: VPS deployment, smoke test, rollback, or release automation.
- `final-gate`: end-to-end verification of the definition of done.

<!-- techlead:section id=traceability -->
## Traceability

| Requirement | Tasks |
| --- | --- |
| FR-001 | TASK-001, TASK-009 |
| FR-002 | TASK-002, TASK-009 |
| NFR-001 | TASK-001, TASK-004, TASK-009 |
| NFR-002 | TASK-007, TASK-009 |
| NFR-003 | TASK-003, TASK-005, TASK-006, TASK-007, TASK-009 |
| NFR-005 | TASK-008, TASK-009 |

Add every requirement from the PRD. A requirement with no task is a planning defect.

<!-- techlead:section id=dod -->
## Definition of Done

- [ ] Every task above is checked and its verification step passed.
- [ ] Every FR and NFR is implemented and covered by at least one task.
- [ ] Test coverage is >= 80 percent.
- [ ] The local/test Docker environment starts cleanly and passes the test suite.
- [ ] The production image builds, scans clean, and passes the VPS smoke test.
- [ ] Rollback and backup restore have been exercised.
- [ ] Security, privacy, and operational documentation are current.
- [ ] No secrets are committed and no critical or high vulnerabilities remain.
```
