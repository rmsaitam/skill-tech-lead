# PRD Template

Copy this structure into `PRD.md`. The PRD is the product and business source of truth. It must not contain architecture, Docker, or implementation detail; those belong in `SPEC.md`.

Preserve every HTML marker exactly. Replace every prompt with the approved answer. The prose may be translated; marker IDs, requirement IDs, and marker attributes stay in English.

```markdown
<!-- techlead:artifact type=prd version=2 -->
# PRD: Project Name

- Status: Approved
- Date: YYYY-MM-DD
- Owner: Name or team
- Artifact language: English

<!-- techlead:section id=summary -->
## 1. Executive Summary

One paragraph describing the product, the user, the problem, and the promised outcome.

<!-- techlead:section id=problem -->
## 2. Problem and Product Promise

### Problem

Describe the current pain, who feels it, and the cost of leaving it unsolved.

### Product promise

State the single outcome the product guarantees when it succeeds.

### Why now

Explain why this is worth solving now and what happens if the team does nothing.

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

<!-- techlead:section id=success -->
## 5. Success Metrics

- Primary measurable outcome, target value, and measurement window.
- Adoption or engagement metric with a target.
- Quality or satisfaction metric with a target.
- Metric that must not get worse.
- How and when the team will review the result after launch.

<!-- techlead:section id=functional -->
## 6. Functional Requirements

- **FR-001**: The actor can perform an action and observes a specific result.
- **FR-002**: The system validates a condition and returns a defined response.
- **FR-003**: The operator can perform an administrative action with the required audit trail.

Every FR states the actor, the action, and the observable outcome.

<!-- techlead:section id=nonfunctional -->
## 7. Non-Functional Requirements

- **NFR-001**: Availability. Target uptime, measurement window, and recovery expectation.
- **NFR-002**: Performance. User-visible latency target, percentile, and measurement method.
- **NFR-003**: Privacy and compliance. Data classification, retention, and applicable regulation.
- **NFR-004**: Accessibility. Standard, target level, and verification expectation.
- **NFR-005**: Supportability. Maximum acceptable incident response time and support window.

NFRs describe business or quality constraints. Technical mechanisms belong in `SPEC.md`.

<!-- techlead:section id=constraints -->
## 8. Constraints and Assumptions

### Constraints

- Budget, deadline, contractual, regulatory, or team constraint.
- Mandated platform, vendor, or integration.
- Production environment expectation, such as a VPS, region, domain, or TLS requirement.

### Assumptions

- Assumption that must remain true for the plan to hold.

### Dependencies

- External system, team, credential, or decision required before delivery.

<!-- techlead:section id=assumptions -->
## 9. Open Decisions and Risks

### Open decisions

- Decision still required, the owner, and the deadline.

### Product risks

- Adoption, scope, dependency, or go-to-market risk.

<!-- techlead:section id=risks -->
## 10. Business Risks and Mitigations

| Risk | Probability | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Risk description | Low, Medium, or High | Low, Medium, or High | Concrete mitigation | Name or role |

<!-- techlead:section id=dod -->
## 11. Product Definition of Done

- [ ] Every must-have acceptance criterion is met and demonstrated.
- [ ] Every FR and NFR is accepted by the product owner.
- [ ] Success metrics are instrumented and ready to be measured.
- [ ] Out-of-scope items are confirmed and documented.
- [ ] User-facing documentation and support material are ready.
- [ ] Launch go/no-go criteria in `PLAN.md` are satisfied.

<!-- techlead:section id=qa -->
## 12. Interview Answers

### Q-001

- Question: Exact question asked during the interview.
- Answer: Exact answer or approved decision.

### Q-002

- Question: Exact question asked during the interview.
- Answer: Exact answer or approved decision.

Add one entry for every question asked. If the user delegated a decision, write the chosen assumption and note that it was approved. At least eight answered questions are required.

<!-- techlead:section id=traceability -->
## 13. Requirement Traceability

| Requirement | Summary | SPEC coverage |
| --- | --- | --- |
| FR-001 | Short requirement summary | TR-001, TR-003 |
| NFR-001 | Short requirement summary | TR-002 |

Every FR and NFR must map to at least one TR in `SPEC.md`. The final requirement-to-milestone and requirement-to-task maps live in `PLAN.md` and `TASKS.md`.
```
