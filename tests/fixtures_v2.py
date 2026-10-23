from __future__ import annotations

from textwrap import dedent


VALID_PRD = dedent(
    """\
    <!-- techlead:artifact type=prd version=2 -->
    # PRD: Review Queue

    - Status: Approved
    - Date: 2026-01-01
    - Owner: Operations team
    - Artifact language: English

    <!-- techlead:section id=summary -->
    ## Summary

    A review queue that lets operations staff decide requests and prove who approved them.

    <!-- techlead:section id=problem -->
    ## Problem

    Operators lack a reliable review queue and cannot prove who approved a request.
    The current spreadsheet process is slow, error-prone, and impossible to audit.

    <!-- techlead:section id=users -->
    ## Users

    Operations staff review requests and auditors inspect the decision history.
    Administrators manage reviewer roles and retention rules.

    <!-- techlead:section id=scope -->
    ## Scope

    ### In scope

    - Request submission, review, decision, and audit history.
    - Reviewer roles, immutable decisions, and exportable history.

    ### Out of scope

    - Billing, payments, and third-party marketplace integrations.

    <!-- techlead:section id=success -->
    ## Success Metrics

    - Review time drops below one business day within the first month.
    - Every decision is auditable with actor, timestamp, and reason.
    - No regression in request volume during the rollout.

    <!-- techlead:section id=functional -->
    ## Functional Requirements

    - **FR-001**: The operator can approve or reject a submitted request and sees the updated decision.
    - **FR-002**: The auditor can search the decision history by request, actor, and date.

    <!-- techlead:section id=nonfunctional -->
    ## Non-Functional Requirements

    - **NFR-001**: The service must be available for 99.5 percent of each calendar month.
    - **NFR-002**: Every decision must be recorded in the audit log within one second.

    <!-- techlead:section id=constraints -->
    ## Constraints and Assumptions

    - The first release serves a single operations team and runs on one VPS.
    - The team must keep the existing identity provider for authentication.

    ### Assumptions

    - The first release serves a single operations team.

    <!-- techlead:section id=assumptions -->
    ## Open Decisions and Risks

    ### Open decisions

    - The retention period is pending legal review and defaults to seven years.

    ### Product risks

    - Reviewers may resist the new queue if the migration is not announced early.

    <!-- techlead:section id=risks -->
    ## Business Risks and Mitigations

    | Risk | Probability | Impact | Mitigation | Owner |
    | --- | --- | --- | --- | --- |
    | Slow review | Medium | Medium | Add queue metrics and weekly review | Lead |
    | Low adoption | Medium | High | Run a pilot with two reviewers | Product |

    <!-- techlead:section id=dod -->
    ## Product Definition of Done

    - [ ] Every must-have acceptance criterion is met and demonstrated.
    - [ ] Every FR and NFR is accepted by the product owner.
    - [ ] Success metrics are instrumented and ready to be measured.
    - [ ] Out-of-scope items are confirmed and documented.
    - [ ] User-facing support material is ready.

    <!-- techlead:section id=qa -->
    ## Interview Answers

    ### Q-001

    - Question: What problem are we solving?
    - Answer: Operators need a reliable review queue and provable decisions.

    ### Q-002

    - Question: Who are the primary users?
    - Answer: Operations staff and auditors.

    ### Q-003

    - Question: What must the first release include?
    - Answer: Submission, review, decision, and audit history.

    ### Q-004

    - Question: What is explicitly out of scope?
    - Answer: Billing and marketplace integrations.

    ### Q-005

    - Question: How will we measure success?
    - Answer: Every decision is recorded and review time drops below one day.

    ### Q-006

    - Question: What security controls are required?
    - Answer: Identity provider login, reviewer authorization, and audit logging.

    ### Q-007

    - Question: How will the project run locally?
    - Answer: Docker Compose with a development image and a test service.

    ### Q-008

    - Question: How will the project run in production?
    - Answer: A hardened container on a VPS behind a TLS reverse proxy.

    <!-- techlead:section id=traceability -->
    ## Requirement Traceability

    | Requirement | Summary | SPEC coverage |
    | --- | --- | --- |
    | FR-001 | Review decision | TR-001, TR-004 |
    | FR-002 | Searchable audit history | TR-001, TR-004 |
    | NFR-001 | Availability target | TR-002 |
    | NFR-002 | Audit latency | TR-003 |

    Every FR and NFR maps to a technical requirement in SPEC.md.
    """
)


VALID_SPEC = dedent(
    """\
    <!-- techlead:artifact type=spec version=2 -->
    # SPEC: Review Queue

    - Status: Approved
    - Date: 2026-01-01
    - Owner: Platform team
    - Artifact language: English
    - Coverage gate: >= 80 percent

    <!-- techlead:section id=context -->
    ## Technical Context

    The service is a web API with a relational database and a background audit writer.
    It inherits the single-VPS constraint, the identity provider, and the 99.5 percent availability target from the PRD.

    <!-- techlead:section id=architecture -->
    ## Architecture

    The application is a modular monolith with an API process and a worker process.
    The API validates requests, writes decisions in a transaction, and emits audit events.
    The worker consumes audit events and persists immutable records.

    <!-- techlead:section id=components -->
    ## Components

    | Component | Responsibility | Interface | Owner |
    | --- | --- | --- | --- |
    | API | Validate and record decisions | HTTPS JSON | Platform |
    | Audit worker | Persist immutable audit records | Queue event | Platform |
    | Database | Store requests and decisions | SQL | Platform |

    <!-- techlead:section id=data -->
    ## Data Model

    Requests, decisions, users, roles, and audit records are the main entities.
    Decisions are immutable and reference the request, actor, timestamp, and reason.
    Audit records are retained for seven years and exported on request.
    Migrations are transactional and support rollback to the previous version.

    <!-- techlead:section id=interfaces -->
    ## Interfaces and Contracts

    The API exposes request submission, decision, and audit search endpoints.
    Errors use a typed JSON envelope with a stable code and a human-readable message.
    Events are idempotent by decision ID, and retries use exponential backoff.
    The API version is part of the path and breaking changes require a new version.

    <!-- techlead:section id=technical -->
    ## Technical Requirements

    - **TR-001**: The API must validate every request body against a schema and return a typed error before persistence.
    - **TR-002**: The deployment must expose health and readiness endpoints used by Docker and the reverse proxy.
    - **TR-003**: The audit writer must persist every decision within one second under the expected load.
    - **TR-004**: The test suite must reach at least 80 percent line and branch coverage.

    <!-- techlead:section id=security -->
    ## Security Engineering

    - Authentication delegates to the organization identity provider with short-lived sessions.
    - Authorization limits decisions to the reviewer role and audit access to auditors.
    - Input validation and output encoding protect every endpoint against injection.
    - Secrets are injected at runtime and rotated on a defined schedule.
    - Audit logs exclude secrets, tokens, and personal data.

    <!-- techlead:section id=environments -->
    ## Docker and Environments

    <!-- techlead:env id=local -->
    ### Local and test environment

    - A development image runs the API with hot reload.
    - A Compose service starts the database with a persistent volume.
    - A dedicated test service runs the full suite with coverage.
    - A reset command removes local state safely.
    - Healthchecks gate the startup order.

    <!-- techlead:env id=production -->
    ### Production environment (VPS)

    - A multi-stage image uses a pinned base version.
    - The runtime uses a non-root user and a read-only filesystem.
    - Capabilities are dropped and no-new-privileges is enabled.
    - Secrets are injected at runtime from the host secret store.
    - A reverse proxy terminates TLS and sets secure headers.
    - The host uses key-only SSH and a restrictive firewall.
    - Backups, restore, image scanning, deployment, and rollback are documented.
    - Healthchecks, log rotation, metrics, and alerts are configured.

    <!-- techlead:section id=testing -->
    ## Testing Strategy

    - Coverage gate: >= 80 percent.
    - Unit tests cover validation, authorization, and decision rules.
    - Integration tests use a disposable database and exercise migrations.
    - End-to-end tests cover the review and audit journeys.
    - Coverage command: pytest --cov --cov-branch --cov-fail-under=80.

    <!-- techlead:section id=observability -->
    ## Observability

    - Structured logs include request IDs and exclude sensitive fields.
    - Metrics cover traffic, errors, latency, queue depth, and dependency health.
    - Alerts fire on availability, error rate, latency, and backup failure.
    - The audit worker exposes queue progress and dead-letter counts.

    <!-- techlead:section id=decisions -->
    ## Architecture Decisions

    ### ADR-001: Modular monolith

    - Status: Accepted
    - Context: The team is small and the first release runs on one VPS.
    - Decision: Use a modular monolith with a separate worker process.
    - Consequences: Deployment stays simple, but modules must not share persistence internals.

    ### ADR-002: Immutable audit records

    - Status: Accepted
    - Context: Auditors must prove who approved each request.
    - Decision: Write audit records once and never update them.
    - Consequences: Corrections require a new compensating record.

    <!-- techlead:section id=risks -->
    ## Technical Risks and Mitigations

    | Risk | Probability | Impact | Mitigation | Owner |
    | --- | --- | --- | --- | --- |
    | Audit lag | Medium | Medium | Add queue depth alerts | Platform |
    | Migration failure | Low | High | Test rollback on disposable data | Platform |

    <!-- techlead:section id=traceability -->
    ## Technical Traceability

    | Technical requirement | Summary | PRD coverage | Component |
    | --- | --- | --- | --- |
    | TR-001 | Input validation | FR-001, FR-002 | API |
    | TR-002 | Health endpoints | NFR-001 | API |
    | TR-003 | Audit latency | NFR-002 | Audit worker |
    | TR-004 | Coverage gate | FR-001, NFR-001 | Quality |

    Every TR maps to a PRD requirement.

    <!-- techlead:section id=dod -->
    ## Technical Definition of Done

    - [ ] Every technical requirement is implemented and covered by tests.
    - [ ] The test suite passes and coverage is at least 80 percent.
    - [ ] The local Docker environment starts and passes the suite.
    - [ ] The production image builds, scans clean, and deploys to the VPS.
    - [ ] Rollback and backup restore have been exercised.
    - [ ] No secrets are committed and no critical or high vulnerabilities remain.
    """
)


VALID_PLAN = dedent(
    """\
    <!-- techlead:artifact type=plan version=2 -->
    # PLAN: Review Queue

    - Source PRD: `./PRD.md`
    - Source SPEC: `./SPEC.md`
    - Status: Approved
    - Artifact language: English

    <!-- techlead:section id=strategy -->
    ## Launch Strategy

    - Release model: private beta with two operations teams, then general availability.
    - The first useful release proves that a request can be reviewed and audited.
    - Rollout uses a feature flag for the new queue while the spreadsheet remains available.
    - Go/no-go requires passing tests, a clean image scan, and a successful smoke test.
    - Rollback restores the previous image within ten minutes and keeps audit data intact.
    - Communication covers reviewers, support, and the audit team before each stage.
    - Success metrics are reviewed one week and one month after launch.

    <!-- techlead:section id=milestones -->
    ## Milestones

    <!-- techlead:milestone id=M1 order=1 depends=none covers=FR-001,NFR-001,TR-001 -->
    ### M1: Review decisions

    - Goal: A reviewer can approve or reject a request with an auditable decision.
    - Scope: Decision API, database schema, reviewer authorization, and local Docker.
    - Requirements: FR-001, NFR-001, TR-001
    - Exit criteria: The primary journey passes end-to-end and the audit record is visible.
    - Launch gate: Internal demo approval by the product owner.
    - Depends on: none
    - Target: First release window.
    - Evidence: Test report, demo recording, and audit record sample.

    <!-- techlead:milestone id=M2 order=2 depends=M1 covers=FR-002,NFR-002,TR-002,TR-003,TR-004 -->
    ### M2: Audit and production release

    - Goal: Auditors can search history and the service runs in production on the VPS.
    - Scope: Audit search, observability, hardened production image, deployment, and rollback.
    - Requirements: FR-002, NFR-002, TR-002, TR-003, TR-004
    - Exit criteria: Search works, audit latency is within one second, and production passes the smoke test.
    - Launch gate: General availability approval after a successful beta.
    - Depends on: M1
    - Target: Second release window.
    - Evidence: Beta metrics, coverage report, image scan, deployment and rollback records.

    <!-- techlead:section id=dependencies -->
    ## Cross-Milestone Dependencies

    - The identity provider configuration is required before M1 starts.
    - The VPS domain and TLS certificate are required before M2 deployment.
    - Legal approval for the retention period is required before general availability.

    <!-- techlead:section id=risks -->
    ## Launch Risks and Mitigations

    | Risk | Probability | Impact | Mitigation | Owner |
    | --- | --- | --- | --- | --- |
    | Beta adoption is low | Medium | Medium | Recruit two pilot teams | Product |
    | Deployment fails | Low | High | Rehearse rollback before launch | Platform |

    <!-- techlead:section id=traceability -->
    ## Milestone Traceability

    | Requirement | Milestone |
    | --- | --- |
    | FR-001 | M1 |
    | FR-002 | M2 |
    | NFR-001 | M1 |
    | NFR-002 | M2 |
    | TR-001 | M1 |
    | TR-002 | M2 |
    | TR-003 | M2 |
    | TR-004 | M2 |

    Every requirement belongs to a milestone.

    <!-- techlead:section id=dod -->
    ## Plan Definition of Done

    - [ ] Every milestone has an owner, exit criteria, and evidence.
    - [ ] Every FR, NFR, and TR is assigned to a milestone.
    - [ ] Every milestone is decomposed into atomic tasks in TASKS.md.
    - [ ] The launch strategy defines go/no-go and rollback.
    - [ ] The test suite passes and coverage is at least 80 percent.
    - [ ] The production image deploys to the VPS and passes the smoke test.
    - [ ] The local and production Docker environments are validated.
    """
)


VALID_TASKS = dedent(
    """\
    <!-- techlead:artifact type=tasks version=2 -->
    # TASKS: Review Queue

    - Source PRD: `./PRD.md`
    - Source SPEC: `./SPEC.md`
    - Source PLAN: `./PLAN.md`
    - Status: Approved
    - Execution order: top to bottom, respecting dependencies

    <!-- techlead:section id=rules -->
    ## Execution Rules

    - Work in task order unless dependencies are complete.
    - One task equals one issue and one pull request.
    - Update the checkbox only after verification passes.
    - Split tasks that touch more than five files.

    <!-- techlead:section id=tasks -->
    ## Tasks

    <!-- techlead:task id=TASK-001 depends=none prd=FR-001,NFR-001 spec=TR-001 milestone=M1 tags=foundation labels=type:chore,area:infra,priority:p1 -->
    ### TASK-001: Bootstrap the API skeleton

    - [ ] Status
    - Depends on: none
    - PRD: FR-001, NFR-001
    - SPEC: TR-001
    - Milestone: M1
    - Issue title: Bootstrap the API skeleton
    - Labels: type:chore, area:infra, priority:p1
    - Estimate: S
    - Acceptance: The API starts locally and exposes a health endpoint.
    - Verify: Run the start command and call the health endpoint.
    - Files: src/main.py, src/health.py, tests/test_health.py

    <!-- techlead:task id=TASK-002 depends=TASK-001 prd=FR-001 spec=TR-001,TR-002 milestone=M1 tags=security labels=type:feature,area:api,priority:p1 -->
    ### TASK-002: Implement the decision endpoint

    - [ ] Status
    - Depends on: TASK-001
    - PRD: FR-001
    - SPEC: TR-001, TR-002
    - Milestone: M1
    - Issue title: Implement the decision endpoint
    - Labels: type:feature, area:api, priority:p1
    - Estimate: M
    - Acceptance: A reviewer approves a request and the decision is persisted.
    - Verify: Run the decision endpoint integration tests.
    - Files: src/api/decisions.py, src/domain/decision.py, tests/integration/test_decisions.py

    <!-- techlead:task id=TASK-003 depends=TASK-002 prd=NFR-002 spec=TR-003 milestone=M1 tags=docker-local,security labels=type:infra,area:data,priority:p1 -->
    ### TASK-003: Persist immutable audit records

    - [ ] Status
    - Depends on: TASK-002
    - PRD: NFR-002
    - SPEC: TR-003
    - Milestone: M1
    - Issue title: Persist immutable audit records
    - Labels: type:infra, area:data, priority:p1
    - Estimate: M
    - Acceptance: Every decision produces an immutable audit record within one second.
    - Verify: Run the audit worker tests and inspect a sample record.
    - Files: src/audit/worker.py, migrations/002_audit.sql, tests/integration/test_audit.py

    <!-- techlead:task id=TASK-004 depends=TASK-003 prd=FR-002 spec=TR-001,TR-004 milestone=M2 tags=security labels=type:feature,area:api,priority:p1 -->
    ### TASK-004: Implement audit search

    - [ ] Status
    - Depends on: TASK-003
    - PRD: FR-002
    - SPEC: TR-001, TR-004
    - Milestone: M2
    - Issue title: Implement audit search
    - Labels: type:feature, area:api, priority:p1
    - Estimate: M
    - Acceptance: An auditor searches history by request, actor, and date.
    - Verify: Run the audit search integration tests.
    - Files: src/api/audit.py, src/domain/search.py, tests/integration/test_search.py

    <!-- techlead:task id=TASK-005 depends=TASK-004 prd=NFR-001,NFR-002 spec=TR-004 milestone=M2 tags=coverage-gate,docker-local labels=type:test,area:quality,priority:p1 -->
    ### TASK-005: Reach the coverage gate

    - [ ] Status
    - Depends on: TASK-004
    - PRD: NFR-001, NFR-002
    - SPEC: TR-004
    - Milestone: M2
    - Issue title: Reach the coverage gate
    - Labels: type:test, area:quality, priority:p1
    - Estimate: M
    - Acceptance: Unit, integration, and end-to-end tests keep coverage at or above 80 percent.
    - Verify: Run the coverage command and confirm the total.
    - Files: tests/conftest.py, tests/unit, tests/integration, pyproject.toml

    <!-- techlead:task id=TASK-006 depends=TASK-005 prd=FR-001,FR-002,NFR-001,NFR-002 spec=TR-001,TR-002,TR-003,TR-004 milestone=M2 tags=docker-production,deployment,final-gate labels=type:infra,area:deploy,priority:p1 -->
    ### TASK-006: Deploy and verify the definition of done

    - [ ] Status
    - Depends on: TASK-005
    - PRD: FR-001, FR-002, NFR-001, NFR-002
    - SPEC: TR-001, TR-002, TR-003, TR-004
    - Milestone: M2
    - Issue title: Deploy and verify the definition of done
    - Labels: type:infra, area:deploy, priority:p1
    - Estimate: M
    - Acceptance: The production image deploys, passes the smoke test, and rolls back cleanly.
    - Verify: Deploy to the VPS, run the smoke test, and execute rollback.
    - Files: Dockerfile, compose.production.yml, deploy.sh, docs/runbook.md

    <!-- techlead:section id=issue-format -->
    ## Issue Format

    - Every task maps to one issue title, one milestone, and a label set.
    - Issue title convention is `[TASK-001] <Issue title>`.
    - Labels include `type:*`, `area:*`, and `priority:*`.
    - Estimate is XS, S, M, L, or 1 to 8 points.
    - Milestone must exist in PLAN.md.
    - Dependencies are written as `Depends on: #N`.
    - Dry-run with `export_issues.py` before creating anything.
    - Create issues with `gh` for GitHub or `glab` for GitLab after approval.

    <!-- techlead:section id=traceability -->
    ## Traceability

    | Requirement | Tasks |
    | --- | --- |
    | FR-001 | TASK-001, TASK-002, TASK-006 |
    | FR-002 | TASK-004, TASK-006 |
    | NFR-001 | TASK-001, TASK-005, TASK-006 |
    | NFR-002 | TASK-003, TASK-005, TASK-006 |
    | TR-001 | TASK-001, TASK-002, TASK-004, TASK-006 |
    | TR-002 | TASK-002, TASK-006 |
    | TR-003 | TASK-003, TASK-006 |
    | TR-004 | TASK-004, TASK-005, TASK-006 |

    | Milestone | Tasks |
    | --- | --- |
    | M1 | TASK-001, TASK-002, TASK-003 |
    | M2 | TASK-004, TASK-005, TASK-006 |

    Every requirement and milestone appears in this table.

    <!-- techlead:section id=dod -->
    ## Definition of Done

    - [ ] Every task above is checked and verified.
    - [ ] Every FR, NFR, and TR is covered by a task.
    - [ ] Test coverage is at least 80 percent.
    - [ ] The local Docker environment passes the test suite.
    - [ ] The production image deploys and passes the smoke test.
    - [ ] Rollback and backup restore have been exercised.
    - [ ] Every task dry-runs successfully as an issue.
    """
)


VALID_AGENTS = dedent(
    """\
    <!-- techlead:artifact type=agents version=2 -->
    # AGENTS: Review Queue

    - Source artifacts: `PRD.md`, `SPEC.md`, `PLAN.md`, `TASKS.md`

    <!-- techlead:section id=overview -->
    ## Project Overview

    The project is a review queue for operations staff and auditors.
    The current milestone is M1 from PLAN.md, and the product scope lives in PRD.md.

    <!-- techlead:section id=stack -->
    ## Stack and Architecture

    The service uses Python, a relational database, and a background audit worker.
    Architecture, interfaces, and decisions live in SPEC.md.

    <!-- techlead:section id=layout -->
    ## Repository Layout

    - `src/`: application code organized by component.
    - `tests/`: unit, integration, and end-to-end suites.
    - `docs/`: runbook and release evidence.
    - Generated planning artifacts live at the repository root.

    <!-- techlead:section id=commands -->
    ## Commands

    - Setup: `uv sync --extra dev`.
    - Development: `docker compose -f compose.local.yml up --build`.
    - Tests: `docker compose -f compose.local.yml run --rm tests`.
    - Coverage: `pytest --cov --cov-branch --cov-fail-under=80`.
    - Lint: `ruff check .`.
    - Build: `docker build -f Dockerfile -t review-queue .`.
    - Deploy: `./deploy.sh`.
    - Rollback: `./deploy.sh --rollback`.

    <!-- techlead:section id=conventions -->
    ## Conventions

    - Follow the existing code style and directory structure.
    - Branch names use the task ID and a short slug.
    - Commit messages are imperative and reference the task ID.
    - Update tests with every behavior change.

    <!-- techlead:section id=rules -->
    ## Engineering Rules

    - Keep test coverage at or above 80 percent.
    - Never commit secrets or real credentials.
    - Keep local and production Docker behavior aligned.
    - Do not create issues, commit, push, or deploy without approval.

    <!-- techlead:section id=decisions -->
    ## Decisions and Sources of Truth

    - Product scope: PRD.md.
    - Architecture and security: SPEC.md.
    - Milestones and launch strategy: PLAN.md.
    - Atomic execution and issue metadata: TASKS.md.

    <!-- techlead:section id=dod -->
    ## Definition of Done

    - Every task is complete and verified.
    - Every requirement is covered by a task.
    - Tests pass with at least 80 percent coverage.
    - The production image deploys and passes the smoke test.

    <!-- techlead:section id=security -->
    ## Security and Secrets

    - Secrets are injected at runtime and never written to the repository.
    - The runtime container uses a non-root user and drops capabilities.
    - Do not log credentials, tokens, or personal data.
    - Run dependency and image scanning before release.
    """
)


VALID_README = dedent(
    """\
    <!-- techlead:artifact type=readme version=2 -->
    # Review Queue

    A review queue for operations staff with an auditable decision history.

    <!-- techlead:section id=overview -->
    ## Overview

    The product helps operations staff review requests and gives auditors a reliable history.
    Product scope lives in PRD.md and the technical design lives in SPEC.md.

    <!-- techlead:section id=status -->
    ## Status

    Milestone M1 is in progress; general availability is planned for milestone M2.

    <!-- techlead:section id=quickstart -->
    ## Quickstart

    ```bash
    cp .env.example .env
    docker compose -f compose.local.yml up --build
    docker compose -f compose.local.yml run --rm tests
    curl http://localhost:8080/health
    ```

    The reset command removes local state safely.

    <!-- techlead:section id=commands -->
    ## Commands

    - Start the local stack: `docker compose -f compose.local.yml up --build`.
    - Run tests: `docker compose -f compose.local.yml run --rm tests`.
    - Run coverage: `pytest --cov --cov-branch --cov-fail-under=80`.
    - Run lint: `ruff check .`.
    - Build production: `docker build -f Dockerfile -t review-queue .`.
    - Deploy: `./deploy.sh`.

    <!-- techlead:section id=architecture -->
    ## Architecture

    The service is a modular monolith with an API process and an audit worker.
    See SPEC.md for components, data, interfaces, and decisions.
    See PLAN.md for milestones and the launch strategy.

    <!-- techlead:section id=docs -->
    ## Documentation

    - PRD.md: product scope, users, and requirements.
    - SPEC.md: architecture, interfaces, security, Docker, and testing.
    - PLAN.md: launch strategy and milestones.
    - TASKS.md: atomic tasks and issue metadata.
    - AGENTS.md: project memory and engineering conventions.

    <!-- techlead:section id=testing -->
    ## Testing and Coverage

    Unit, integration, and end-to-end tests run in Docker.
    Coverage gate: at least 80 percent.
    The coverage command is `pytest --cov --cov-branch --cov-fail-under=80`.

    <!-- techlead:section id=deployment -->
    ## Deployment

    The production image runs on a single VPS behind a TLS reverse proxy.
    Deploy with `./deploy.sh`, run the smoke test, and roll back with `./deploy.sh --rollback`.
    Secrets are injected at runtime by the host secret store.

    <!-- techlead:section id=security -->
    ## Security

    Authentication uses the organization identity provider and decisions require the reviewer role.
    Report security issues to the platform team and never include secrets in reports.

    ## License

    MIT.
    """
)


def valid_texts() -> dict[str, str]:
    return {
        "prd": VALID_PRD,
        "spec": VALID_SPEC,
        "plan": VALID_PLAN,
        "tasks": VALID_TASKS,
        "agents": VALID_AGENTS,
        "readme": VALID_README,
    }
