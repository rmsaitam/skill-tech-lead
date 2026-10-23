# SPEC Template

Copy this structure into `SPEC.md`. Replace every prompt with the approved engineering decision. Preserve every HTML marker exactly. The prose may be translated; marker IDs, requirement IDs, and marker attributes stay in English.

The SPEC owns architecture and engineering. It must not redefine product scope. Every technical requirement traces back to at least one FR or NFR in `PRD.md`.

```markdown
<!-- techlead:artifact type=spec version=2 -->
# SPEC: Project Name

- Status: Approved
- Date: YYYY-MM-DD
- Owner: Name or team
- Artifact language: English
- Coverage gate: >= 80%

<!-- techlead:section id=context -->
## 1. Technical Context

- Product constraints inherited from `PRD.md`.
- Existing systems, platforms, contracts, and non-negotiable stack choices.
- Expected traffic, data volume, growth, and latency targets.
- Technical risks that shape the architecture.

<!-- techlead:section id=architecture -->
## 2. Architecture

- System style: monolith, modular monolith, service, worker, CLI, static site, or combination.
- Runtime topology and the primary request or job flow.
- Trust boundaries and network zones.
- Key trade-offs and why the chosen design wins.

<!-- techlead:section id=components -->
## 3. Components

| Component | Responsibility | Interface | Owner |
| --- | --- | --- | --- |
| Component name | What it owns | API, event, CLI, or module boundary | Name or role |

<!-- techlead:section id=data -->
## 4. Data Model

- Main entities, attributes, relationships, and invariants.
- Source of truth for each important record.
- Retention, archival, export, and deletion rules.
- Migration strategy and rollback behavior.
- Sensitive data classification and storage controls.

<!-- techlead:section id=interfaces -->
## 5. Interfaces and Contracts

- HTTP or RPC endpoints with request, response, status codes, and error format.
- Events, queues, webhooks, and idempotency rules.
- CLI commands and exit codes.
- External integrations, timeouts, retries, and circuit-breaking behavior.
- Versioning and backward-compatibility policy.

<!-- techlead:section id=technical -->
## 6. Technical Requirements

- **TR-001**: The system must validate every input against a schema and return a typed error before persistence.
- **TR-002**: The persistence layer must run migrations in a transaction and support rollback to the previous version.
- **TR-003**: The service must expose health and readiness endpoints used by Docker and the reverse proxy.
- **TR-004**: The test suite must reach at least 80 percent line and branch coverage.

<!-- techlead:section id=security -->
## 7. Security Engineering

- Authentication mechanism, token or session lifecycle, and revocation.
- Authorization model and least-privilege rules per role and resource.
- Input validation, output encoding, and injection defenses.
- Secret storage, injection at runtime, and rotation.
- Audit logging and prohibited log fields.
- Threat model, dependency scanning, and image scanning.
- Backup, restore, and incident response.

<!-- techlead:section id=environments -->
## 8. Docker and Environments

<!-- techlead:env id=local -->
### Local and test environment

- Development image and Compose service with hot reload or fast rebuilds.
- Test service that runs the full suite with coverage.
- Local database, cache, and other dependencies with volumes.
- Seed data and a documented reset command.
- Healthchecks and startup order.
- One command to start the stack and one command to run tests.
- No production secrets or production data.

<!-- techlead:env id=production -->
### Production environment (VPS)

- Multi-stage image with pinned base versions or digests.
- Non-root runtime user, minimal image, and read-only filesystem where possible.
- Capability drop, no-new-privileges, and resource limits.
- Runtime secret injection and rotation.
- Reverse proxy with TLS, secure headers, and domain configuration.
- Host hardening, key-only SSH, firewall, and automatic security updates.
- Healthchecks, restart policy, log rotation, metrics, and alerts.
- Backup, restore, image scanning, deployment, smoke test, and rollback.

<!-- techlead:section id=testing -->
## 9. Testing Strategy

- Coverage gate: >= 80 percent. This gate is mandatory.
- Unit tests: scope, framework, and command.
- Integration tests: dependencies, disposable database, and command.
- Contract tests: interfaces, fixtures, and command.
- End-to-end tests: critical journeys, environment, and command.
- Security tests: authentication, authorization, validation, and scanning.
- Performance tests: load profile, dataset, percentile target, and command.
- Accessibility tests: standard, pages, and command.
- Coverage command: exact command used by CI.
- CI gates that block merge and release.

<!-- techlead:section id=observability -->
## 10. Observability

- Structured logs with request IDs and no sensitive fields.
- Metrics for traffic, errors, latency, saturation, queue depth, and dependency health.
- Traces for the primary request path and external calls.
- Alerts with thresholds, ownership, and runbook links.
- Dashboards or documented queries for the primary signals.

<!-- techlead:section id=decisions -->
## 11. Architecture Decisions

### ADR-001: Decision title

- Status: Accepted
- Context: Why the decision was needed.
- Decision: What was chosen.
- Consequences: What becomes easier, harder, or constrained.

### ADR-002: Decision title

- Status: Accepted
- Context: Why the decision was needed.
- Decision: What was chosen.
- Consequences: What becomes easier, harder, or constrained.

<!-- techlead:section id=risks -->
## 12. Technical Risks and Mitigations

| Risk | Probability | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Risk description | Low, Medium, or High | Low, Medium, or High | Concrete mitigation | Name or role |

<!-- techlead:section id=traceability -->
## 13. Technical Traceability

| Technical requirement | Summary | PRD coverage | Component |
| --- | --- | --- | --- |
| TR-001 | Input validation | FR-001, NFR-003 | API |
| TR-002 | Safe migrations | NFR-002 | Persistence |

Every TR must map to at least one FR or NFR. Every FR and NFR from the PRD must appear in this table.

<!-- techlead:section id=dod -->
## 14. Technical Definition of Done

- [ ] Every technical requirement is implemented and covered by tests.
- [ ] The test suite passes and coverage is at least 80 percent.
- [ ] The local/test Docker environment starts cleanly and passes the suite.
- [ ] The production image builds, scans clean, and deploys to the VPS.
- [ ] Healthchecks, observability, and alerts are active.
- [ ] Rollback and backup restore have been exercised.
- [ ] No secrets are committed and no critical or high vulnerabilities remain.
```
