# Testing Baseline

Use this reference when writing the testing strategy in the SPEC and the coverage task in the TASKS. Adapt the commands to the selected stack. The coverage gate is at least 80 percent unless the user explicitly approves a documented exception.

## Coverage rules

- Measure line and branch coverage.
- Exclude generated code, vendor code, and bootstrap code only when the exclusion is justified in the SPEC.
- Do not exclude difficult business logic to reach the gate.
- Fail CI when total coverage is below 80 percent.
- Add focused tests for new logic before or with the implementation.
- Treat flaky tests as defects.
- Prefer testing behavior and observable outcomes over private implementation details.
- Do not weaken, skip, or delete assertions to make the gate pass.

## Test levels

### Unit tests

- Cover domain rules, validation, transformations, and pure functions.
- Run fast and without network access.
- Isolate time, randomness, and external services.
- Use table-driven or parameterized cases for boundaries and error paths.

### Integration tests

- Cover repositories, database queries, migrations, message handlers, and external adapters.
- Use a disposable database or container.
- Verify transaction boundaries and rollback behavior.
- Verify idempotency for retried operations.

### Contract tests

- Cover API request and response shapes, status codes, and error formats.
- Validate consumer expectations against provider behavior.
- Keep fixtures versioned with the contract.
- Fail when a breaking change is introduced.

### End-to-end tests

- Cover the critical user journeys and the most expensive failure paths.
- Run against a production-like environment.
- Avoid duplicating every unit case.
- Capture traces, screenshots, or logs on failure.
- Keep the suite small enough to run on every pull request or before release.

### Performance tests

- Define the load profile, dataset, duration, and target percentile.
- Measure throughput, latency, error rate, and resource saturation.
- Compare against the baseline and record regressions.
- Test the production image and production-like configuration.

### Security tests

- Test authentication, authorization, input validation, and sensitive-data handling.
- Test for injection, broken access control, and secret exposure where relevant.
- Run dependency and image scans in CI.
- Keep critical and high findings at zero before release, or document an approved exception.

### Accessibility tests

- Use automated checks for the required standard.
- Add manual keyboard and screen-reader checks for critical journeys.
- Record known exceptions with owner and target date.

## Coverage commands

Use the real command for the stack. Examples:

```bash
pytest --cov --cov-branch --cov-report=term-missing --cov-fail-under=80
npm test -- --coverage --coverageThreshold='{"global":{"lines":80,"branches":80}}'
go test ./... -coverprofile=coverage.out && go tool cover -func=coverage.out
mvn verify jacoco:report
gradle test jacocoTestReport
dotnet test --collect:"XPlat Code Coverage"
```

The SPEC must name the real command. The TASKS coverage task must use the same command.

## CI gates

At minimum, CI must run:

- formatting and lint checks;
- type checks when the language supports them;
- unit and integration tests;
- coverage with the 80 percent gate;
- dependency scanning;
- production image build;
- image vulnerability scanning;
- migration check against a disposable database;
- end-to-end or smoke tests for critical journeys;
- artifact retention for coverage and test reports.

Release must additionally verify:

- the production image digest;
- the deployment smoke test;
- rollback readiness;
- backup status;
- no unresolved critical or high vulnerabilities.

## Test data

- Use synthetic data by default.
- Never use production personal data in tests.
- Keep fixtures small and purpose-built.
- Seed deterministic data for end-to-end tests.
- Clean up or isolate state between tests.
- Do not put real credentials in fixtures or test configuration.

## Evidence

Record in the release or task verification:

- test command;
- total tests and pass or fail;
- coverage percentage;
- failed or skipped tests with justification;
- scan results;
- smoke test result;
- links to CI runs or artifacts.

## Common anti-patterns

- Testing only the happy path.
- Asserting that a function was called instead of asserting the outcome.
- Mocking the code under test.
- Using sleeps instead of condition-based waits.
- Sharing mutable state between tests.
- Excluding business logic from coverage.
- Treating snapshot updates as automatic approval.
- Running end-to-end tests only on the developer machine.
- Measuring coverage without a failing gate.
