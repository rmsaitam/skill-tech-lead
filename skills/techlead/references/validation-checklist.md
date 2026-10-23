# Validation Checklist

Use this checklist when the validator script cannot run.

## PRD

- [ ] The file starts with `<!-- techlead:artifact type=prd version=2 -->`.
- [ ] Status, date, owner, and artifact language are present.
- [ ] Required sections exist: `summary`, `problem`, `users`, `scope`, `success`, `functional`, `nonfunctional`, `constraints`, `assumptions`, `risks`, `dod`, `qa`, `traceability`.
- [ ] In-scope and out-of-scope lists are explicit.
- [ ] At least one `FR-xxx` and one `NFR-xxx` exist and are testable or measurable.
- [ ] The PRD does not define `TR-xxx`, architecture, Docker, or test commands.
- [ ] Success metrics have targets and measurement windows.
- [ ] At least eight interview question and answer pairs are recorded.
- [ ] The traceability table maps every FR and NFR to at least one TR in `SPEC.md`.
- [ ] No `TODO`, `TBD`, `FIXME`, `[insert`, or `<insert` placeholders remain.

## SPEC

- [ ] The file starts with `<!-- techlead:artifact type=spec version=2 -->`.
- [ ] Status, date, owner, artifact language, and coverage gate are present.
- [ ] Required sections exist: `context`, `architecture`, `components`, `data`, `interfaces`, `technical`, `security`, `environments`, `testing`, `observability`, `decisions`, `risks`, `traceability`, `dod`.
- [ ] At least one `TR-xxx` exists and is testable.
- [ ] The SPEC does not define new `FR-xxx` or `NFR-xxx` requirements.
- [ ] Security covers authentication, authorization, validation, secrets, audit, and scanning.
- [ ] The environments section has `<!-- techlead:env id=local -->` and `<!-- techlead:env id=production -->`.
- [ ] Local Docker covers development, tests, dependencies, healthchecks, and startup commands.
- [ ] Production Docker covers image hardening, non-root runtime, secrets, reverse proxy, TLS, host hardening, backups, monitoring, scanning, deployment, and rollback.
- [ ] Testing names the coverage command and states a gate of at least 80 percent.
- [ ] Every TR maps to at least one FR or NFR, and every FR/NFR appears in the traceability table.
- [ ] The definition of done contains checkboxes, mentions Docker, and states the 80 percent gate.

## PLAN

- [ ] The file starts with `<!-- techlead:artifact type=plan version=2 -->`.
- [ ] Source PRD, source SPEC, status, and artifact language are present.
- [ ] Required sections exist: `strategy`, `milestones`, `dependencies`, `risks`, `traceability`, `dod`.
- [ ] The launch strategy covers launch, rollout, go/no-go, rollback, communication, and metrics.
- [ ] At least two milestones exist unless a documented exception is approved.
- [ ] Milestone IDs match `M1`, `M2`, and so on, are unique, and are ordered.
- [ ] Every milestone has a goal, scope, requirements, exit criteria, launch gate, target, and evidence.
- [ ] Every FR, NFR, and TR belongs to at least one milestone.
- [ ] The traceability table maps every requirement to a milestone.
- [ ] The definition of done contains checkboxes, mentions Docker, and states the 80 percent gate.

## TASKS

- [ ] The file starts with `<!-- techlead:artifact type=tasks version=2 -->`.
- [ ] Source PRD, source SPEC, source PLAN, status, and execution order are present.
- [ ] Required sections exist: `rules`, `tasks`, `issue-format`, `traceability`, `dod`.
- [ ] At least six task markers exist.
- [ ] Task IDs are unique and in increasing order.
- [ ] Every task has dependencies, PRD references, SPEC references, a milestone, an issue title, labels, an estimate, acceptance, verification, and files.
- [ ] Labels include at least `type:*`, `area:*`, and `priority:*`.
- [ ] Issue titles are unique and at most 72 characters.
- [ ] Every task touches five files or fewer and is small enough for one work session.
- [ ] Every task belongs to a milestone that exists in `PLAN.md`.
- [ ] Every milestone has at least one task.
- [ ] Every FR, NFR, and TR from the PRD and SPEC appears in at least one task.
- [ ] The mandatory tags appear at least once: `docker-local`, `docker-production`, `coverage-gate`, `security`, `deployment`.
- [ ] The `issue-format` section documents `gh`, `glab`, labels, milestones, issue titles, estimates, and `export_issues.py`.
- [ ] The traceability section includes every requirement and milestone.
- [ ] The definition of done contains checkboxes, mentions Docker, and states the 80 percent gate.
- [ ] A final gate task verifies the complete definition of done.

## AGENTS

- [ ] The file starts with `<!-- techlead:artifact type=agents version=2 -->`.
- [ ] Required sections exist: `overview`, `stack`, `layout`, `commands`, `conventions`, `rules`, `decisions`, `dod`, `security`.
- [ ] It links to `PRD.md`, `SPEC.md`, `PLAN.md`, and `TASKS.md`.
- [ ] Commands are real and cover setup, dev, test, coverage, lint, build, deploy, and rollback.
- [ ] It states the 80 percent coverage gate and the secret-handling rules.

## README

- [ ] The file starts with `<!-- techlead:artifact type=readme version=2 -->`.
- [ ] Required sections exist: `overview`, `status`, `quickstart`, `commands`, `architecture`, `docs`, `testing`, `deployment`, `security`.
- [ ] It links to `PRD.md`, `SPEC.md`, `PLAN.md`, `TASKS.md`, and `AGENTS.md`.
- [ ] Quickstart uses Docker and real commands.
- [ ] It states the coverage gate of at least 80 percent.
- [ ] It documents deployment, smoke test, and rollback at a high level.

## Evidence

- [ ] The coverage command has been run or is explicitly scheduled in the coverage task.
- [ ] The local Docker start and test commands are documented.
- [ ] The production deployment, smoke test, and rollback commands are documented.
- [ ] The backup and restore procedure is documented.
- [ ] The security scanning step is documented.
- [ ] `export_issues.py --format json` succeeds in dry-run mode.
- [ ] No issues, commits, pushes, or deployments happened without explicit approval.
