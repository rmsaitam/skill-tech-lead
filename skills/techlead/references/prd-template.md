# PRD Template

Copy this structure into `PRD.md`. Replace every prompt with the approved answer. Preserve every HTML marker exactly. The prose may be translated; marker IDs and requirement IDs stay in English.

```markdown
<!-- techlead:artifact type=prd version=1 -->
# PRD: Project Name

- Status: Approved
- Date: YYYY-MM-DD
- Owner: Name or team
- Artifact language: English
- Coverage gate: >= 80%

<!-- techlead:section id=summary -->
## 1. Executive Summary

One paragraph describing the product, the user, the problem, and the promised outcome.

<!-- techlead:section id=problem -->
## 2. Problem and Goals

### Problem

Describe the current pain, who feels it, and the cost of leaving it unsolved.

### Product promise

State the single outcome the product guarantees when it succeeds.

### Goals

- Goal 1 with a measurable target.
- Goal 2 with a measurable target.

### Non-goals

- Outcome this product will not pursue in this release.

<!-- techlead:section id=users -->
## 3. Users and Jobs to Be Done

### Primary users

- Persona, context, frequency, and main constraint.

### Secondary users and operators

- Persona, operational responsibility, and main constraint.

### Jobs to be done

- When [situation], I want to [motivation], so I can [outcome].

### Current alternatives

Describe what users do today and why it is insufficient.

<!-- techlead:section id=scope -->
## 4. Scope

### In scope

- Capability included in the approved release.

### Out of scope

- Capability explicitly excluded from this release and why.

### Deferred

- Capability intentionally postponed, with the condition that would bring it back.

<!-- techlead:section id=functional -->
## 5. Functional Requirements

- **FR-001**: The actor can perform an action and observes a specific result.
- **FR-002**: The system validates a condition and returns a defined response.
- **FR-003**: The operator can perform an administrative action with the required audit trail.

<!-- techlead:section id=nonfunctional -->
## 6. Non-Functional Requirements

- **NFR-001**: Performance. Target value, percentile, and measurement method.
- **NFR-002**: Availability. Target, measurement window, and recovery expectation.
- **NFR-003**: Security. Threat, control, and verification method.
- **NFR-004**: Accessibility. Standard, target level, and verification method.
- **NFR-005**: Observability. Required logs, metrics, traces, and alerts.

<!-- techlead:section id=assumptions -->
## 7. Assumptions and Constraints

### Assumptions

- Assumption that must remain true for the plan to hold.

### Constraints

- Technical, budget, deadline, contractual, or team constraint.

### Dependencies

- External system, team, credential, or decision required before delivery.

<!-- techlead:section id=architecture -->
## 8. Solution and Architecture

### Proposed stack

- Language, framework, runtime, database, and key libraries with versions where known.

### Components

- Component, responsibility, interface, and owner.

### Data model

- Main entities, relationships, retention, and source of truth.

### Primary flow

1. User action.
2. Validation and authorization.
3. State change and persistence.
4. Observable result.

### Failure behavior

- Timeout, retry, duplicate input, partial failure, and recovery behavior.

<!-- techlead:section id=security -->
## 9. Security, Privacy, and Compliance

- Authentication method and session lifecycle.
- Authorization roles and least-privilege rules.
- Sensitive data classification and retention.
- Input validation and output encoding.
- Secret storage and rotation.
- Audit logging and prohibited log fields.
- Backup, restore, and incident response.
- Applicable regulation or contractual control.

<!-- techlead:section id=docker -->
## 10. Docker and Environments

<!-- techlead:env id=local -->
### Local and test environment

- Development image and Compose service.
- Hot reload or fast rebuild strategy.
- Test service and coverage command.
- Local database, cache, or other dependencies.
- Seed data and reset procedure.
- Healthchecks and startup order.
- One command to start the stack and one command to run tests.

<!-- techlead:env id=production -->
### Production environment (VPS)

- Multi-stage production image and pinned base image versions.
- Non-root runtime user, minimal image, and read-only filesystem where possible.
- Capability drop, no-new-privileges, and resource limits.
- Runtime secret injection and secret rotation.
- Reverse proxy, TLS, secure headers, and domain.
- Host hardening, firewall, SSH policy, and security updates.
- Healthchecks, restart policy, log rotation, metrics, and alerts.
- Backup, restore, image scanning, deployment, smoke test, and rollback.

<!-- techlead:section id=testing -->
## 11. Testing Strategy

- Coverage gate: >= 80 percent. This gate is mandatory.
- Unit tests: scope, framework, and command.
- Integration tests: scope, dependencies, and command.
- End-to-end tests: critical journeys, environment, and command.
- Contract tests: external interfaces and command.
- Performance tests: target, load profile, and command.
- Accessibility tests: standard, pages, and command.
- Coverage command: exact command used by CI.
- CI gate: checks that block merge and release.

<!-- techlead:section id=dod -->
## 12. Definition of Done

- [ ] Every task in `TASKS.md` is complete and verified.
- [ ] Every FR and NFR is implemented and linked to at least one task.
- [ ] Test coverage is >= 80 percent.
- [ ] The local/test Docker environment starts cleanly and passes the test suite.
- [ ] The production image builds and passes vulnerability scanning.
- [ ] The production deployment passes the VPS smoke test.
- [ ] Rollback and backup restore have been exercised.
- [ ] Security, privacy, and operational documentation are current.
- [ ] No secrets are committed and no critical or high vulnerabilities remain.

<!-- techlead:section id=risks -->
## 13. Risks and Mitigations

| Risk | Probability | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Risk description | Low, Medium, or High | Low, Medium, or High | Concrete mitigation | Name or role |

<!-- techlead:section id=qa -->
## 14. Interview Answers

### Q-001

- Question: Exact question asked during the interview.
- Answer: Exact answer or approved decision.

### Q-002

- Question: Exact question asked during the interview.
- Answer: Exact answer or approved decision.

Add one entry for every question asked. If the user delegated a decision, write the chosen assumption and note that it was approved.

<!-- techlead:section id=traceability -->
## 15. Requirement Traceability

| Requirement | Summary | Delivered by |
| --- | --- | --- |
| FR-001 | Short requirement summary | TASK-001, TASK-004 |
| NFR-001 | Short requirement summary | TASK-007 |

Every requirement must appear in this table and in at least one task.
```
