# README Template

Create or update the project `README.md` last, after all planning artifacts and commands are final. Preserve existing user content when it is still accurate. Do not document commands that do not exist.

```markdown
<!-- techlead:artifact type=readme version=2 -->
# Project Name

One sentence describing the product, the user, and the outcome.

<!-- techlead:section id=overview -->
## Overview

- The problem the product solves.
- The primary user and the main job to be done.
- The product promise and the current release scope.
- Links to `PRD.md` for product requirements and `SPEC.md` for architecture.

<!-- techlead:section id=status -->
## Status

- Current milestone from `PLAN.md` and the release stage.
- Known limitations and deferred scope.

<!-- techlead:section id=quickstart -->
## Quickstart

```bash
cp .env.example .env
docker compose -f compose.local.yml up --build
docker compose -f compose.local.yml run --rm tests
curl http://localhost:8080/health
```

- Document any prerequisite versions.
- Document the seed and reset commands.
- Never include real credentials or production secrets.

<!-- techlead:section id=commands -->
## Commands

- Start the local stack: `docker compose -f compose.local.yml up --build`.
- Run the test suite: `docker compose -f compose.local.yml run --rm tests`.
- Run the coverage gate: the command documented in `SPEC.md`.
- Run lint and typecheck: the commands documented in `AGENTS.md`.
- Build production: the command documented in `SPEC.md`.
- Deploy: the command documented in `PLAN.md`.
- Roll back: the command documented in `PLAN.md`.

<!-- techlead:section id=architecture -->
## Architecture

- Short summary of components, data stores, and interfaces.
- Link to `SPEC.md` for the full architecture, data model, and decisions.
- Link to `PLAN.md` for milestones and launch strategy.

<!-- techlead:section id=docs -->
## Documentation

- `PRD.md`: product scope, users, and requirements.
- `SPEC.md`: architecture, interfaces, security, Docker, and testing.
- `PLAN.md`: launch strategy and milestones.
- `TASKS.md`: atomic tasks and issue metadata.
- `AGENTS.md`: project memory and engineering conventions.

<!-- techlead:section id=testing -->
## Testing and Coverage

- Test levels used by the project.
- Coverage gate: at least 80 percent.
- Exact coverage command and CI gate.
- How to run a focused test file and the full suite.

<!-- techlead:section id=deployment -->
## Deployment

- Production Docker image and VPS target.
- Deployment command, smoke test, and rollback procedure.
- Required secrets and where they are injected.
- Backup and restore expectations.

<!-- techlead:section id=security -->
## Security

- Authentication and authorization summary.
- Secret handling and rotation.
- Vulnerability scanning and the policy for critical and high findings.
- How to report a security issue.

## License

MIT.
```
