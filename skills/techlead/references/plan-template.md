# PLAN Template

Copy this structure into `PLAN.md`. The PLAN is the macro bridge between product and engineering. It combines `PRD.md` and `SPEC.md` into a launch strategy and outcome-based milestones. It must not invent requirements or scope.

Preserve every HTML marker exactly. Replace every prompt with an approved decision.

```markdown
<!-- techlead:artifact type=plan version=2 -->
# PLAN: Project Name

- Source PRD: `./PRD.md`
- Source SPEC: `./SPEC.md`
- Status: Approved
- Artifact language: English

<!-- techlead:section id=strategy -->
## 1. Launch Strategy

- Release model: internal, private beta, public beta, or general availability.
- First useful release and the smallest scope that proves the product promise.
- Rollout approach: feature flags, canary, blue-green, or staged percentage.
- Go/no-go checklist and the owner who signs it.
- Rollback trigger, rollback procedure, and maximum acceptable downtime.
- Communication plan for users, support, and stakeholders.
- Success metrics measured after launch and the review window.
- Support and on-call expectations during and after launch.

<!-- techlead:section id=milestones -->
## 2. Milestones

<!-- techlead:milestone id=M1 order=1 depends=none covers=FR-001,TR-001 -->
### M1: Milestone outcome

- Goal: The user-visible outcome this milestone delivers.
- Scope: Product and technical scope included in this milestone.
- Requirements: FR-001, TR-001
- Exit criteria: Observable conditions that prove the milestone is complete.
- Launch gate: Internal demo, beta, or general availability decision.
- Depends on: none
- Target: Release window or relative sequence.
- Evidence: Test results, demo, metrics, or deployment record required.

<!-- techlead:milestone id=M2 order=2 depends=M1 covers=FR-002,NFR-002,TR-002 -->
### M2: Milestone outcome

- Goal: The user-visible outcome this milestone delivers.
- Scope: Product and technical scope included in this milestone.
- Requirements: FR-002, NFR-002, TR-002
- Exit criteria: Observable conditions that prove the milestone is complete.
- Launch gate: Release decision for this milestone.
- Depends on: M1
- Target: Release window or relative sequence.
- Evidence: Test results, demo, metrics, or deployment record required.

<!-- techlead:section id=dependencies -->
## 3. Cross-Milestone Dependencies

- External systems, credentials, contracts, or approvals required before a milestone.
- Team dependencies and hand-offs.
- Ordering constraints that are not obvious from the milestone list.
- Decisions that must be made before the next milestone starts.

<!-- techlead:section id=risks -->
## 4. Launch Risks and Mitigations

| Risk | Probability | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Risk description | Low, Medium, or High | Low, Medium, or High | Concrete mitigation | Name or role |

<!-- techlead:section id=traceability -->
## 5. Milestone Traceability

| Requirement | Milestone |
| --- | --- |
| FR-001 | M1 |
| FR-002 | M2 |
| NFR-002 | M2 |
| TR-001 | M1 |
| TR-002 | M2 |

Every FR, NFR, and TR must appear in exactly one primary milestone and may be supported by later milestones.

<!-- techlead:section id=dod -->
## 6. Plan Definition of Done

- [ ] Every milestone has an owner, exit criteria, and evidence.
- [ ] Every FR, NFR, and TR is assigned to a milestone.
- [ ] Every milestone is decomposed into atomic tasks in `TASKS.md`.
- [ ] The launch strategy defines go/no-go and rollback.
- [ ] The test suite passes and coverage is at least 80 percent.
- [ ] The local/test Docker environment passes the suite.
- [ ] The production image deploys to the VPS and passes the smoke test.
- [ ] Rollback and backup restore have been exercised.
```
