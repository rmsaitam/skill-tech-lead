# TechLead

[![skills.sh](https://skills.sh/b/rmsaitam/skill-tech-lead)](https://skills.sh/rmsaitam/skill-tech-lead)

TechLead is a planning plugin for AI coding agents. It interviews the user about a product idea, captures every decision, and produces a traceable set of six artifacts:

- `PRD.md`: product and business source of truth.
- `SPEC.md`: architecture and engineering source of truth.
- `PLAN.md`: launch strategy and macro milestones.
- `TASKS.md`: atomic technical tasks that become GitHub or GitLab issues.
- `AGENTS.md`: project memory for AI coding agents.
- `README.md`: onboarding for humans.

The generated plan always covers Docker for local/test and production/VPS, security hardening, launch and rollback strategy, issue automation, and a definition of done that requires at least 80 percent test coverage.

Repository: https://github.com/rmsaitam/skill-tech-lead

## Supported agents

| Agent | Manifest |
| --- | --- |
| Claude Code | `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` |
| Codex | `.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json` |
| Cursor | `.cursor-plugin/plugin.json` and `.cursor-plugin/marketplace.json` |
| GitHub Copilot CLI | `.github/plugin/marketplace.json` with the root `plugin.json` |
| Antigravity | root `plugin.json` |

All agents use the shared skill at `skills/techlead/SKILL.md` and the commands in `commands/`.

## Install

### skills.sh

The recommended way to install the skill across supported agents:

```bash
# Install into the current project after choosing the agents interactively
npx skills add rmsaitam/skill-tech-lead

# Install globally into the user home config for every project, skipping prompts
npx skills add rmsaitam/skill-tech-lead -g -y
```

The CLI prompts for the target agents. Node.js 22.20 or newer is required. List the available skill without installing:

```bash
npx skills add rmsaitam/skill-tech-lead --list
```

### Claude Code

From a published marketplace:

```text
/plugin marketplace add rmsaitam/skill-tech-lead
/plugin install techlead@techlead
```

From a local checkout:

```text
/plugin marketplace add /absolute/path/to/skill-techlead
/plugin install techlead@techlead
```

### Codex

```bash
codex plugin marketplace add rmsaitam/skill-tech-lead
codex plugin install techlead@techlead
```

For a local checkout, use the absolute path instead. Choose the TechLead plugin when prompted.

### GitHub Copilot CLI

```bash
copilot plugin marketplace add rmsaitam/skill-tech-lead
copilot plugin install techlead@techlead
```

### Cursor

Install the plugin from a marketplace that lists this repository, or point Cursor at a local plugin directory containing this repository. Cursor reads `.cursor-plugin/plugin.json`, the shared `skills/` directory, and `commands/`.

### Antigravity

Install the repository root as a plugin. Antigravity reads the root `plugin.json` directly.

Command syntax varies by agent version. When a command is unavailable, use the agent's plugin marketplace UI and select the `techlead` plugin.

## Usage

Start a planning session:

```text
/techlead Build a review queue for operations with an audit trail
```

The skill follows nine gates:

1. Inspect the workspace and reuse known facts.
2. Interview in rounds of at most five questions.
3. Present product, engineering, milestone, and issue plans and wait for approval.
4. Write or update `PRD.md` and `SPEC.md` together.
5. Write or update `PLAN.md` with launch strategy and milestones.
6. Write or update `TASKS.md` with atomic issue-ready tasks.
7. Write or update `AGENTS.md` and `README.md` last.
8. Validate every artifact and run the issue export dry-run.
9. Report the result and stop before implementation or issue creation.

Validate existing artifacts:

```text
/techlead-validate
/techlead-validate docs/PRD.md docs/TASKS.md
```

Export issues after explicit approval:

```text
/techlead-issues
/techlead-issues github owner/repo
```

## Artifact pipeline

```text
Brainstorm
  +-- PRD.md (product) + SPEC.md (engineering)     generated together
        +-- PLAN.md (launch strategy + Milestones)  macro planning
              +-- TASKS.md (atomic issue-ready work) micro execution
                    +-- AGENTS.md + README.md       project memory
                          +-- gh / glab issue export
```

Every requirement follows the same trace:

```text
FR/NFR -> TR -> Milestone -> TASK -> Issue
```

## Artifact contract (v2)

All six artifacts start with a machine-readable marker:

```html
<!-- techlead:artifact type=prd version=2 -->
<!-- techlead:artifact type=spec version=2 -->
<!-- techlead:artifact type=plan version=2 -->
<!-- techlead:artifact type=tasks version=2 -->
<!-- techlead:artifact type=agents version=2 -->
<!-- techlead:artifact type=readme version=2 -->
```

### PRD.md

Product-only. It contains the executive summary, problem, users, scope, success metrics, `FR-xxx`, business `NFR-xxx`, constraints, risks, interview answers, and product definition of done. It must not contain architecture, Docker, or test commands. The traceability table maps every FR and NFR to at least one `TR-xxx` in `SPEC.md`.

### SPEC.md

Engineering-only. It contains technical context, architecture, components, data model, interfaces, `TR-xxx`, security, Docker environments, testing, observability, architecture decisions, risks, traceability, and technical definition of done. The Docker section must contain both environment markers:

```html
<!-- techlead:env id=local -->
<!-- techlead:env id=production -->
```

Coverage command and the 80 percent gate live here.

### PLAN.md

The macro union of product and engineering. It defines the launch strategy, rollout, go/no-go, rollback, communication, metrics, support, and outcome-based milestones.

```html
<!-- techlead:milestone id=M1 order=1 depends=none covers=FR-001,TR-001 -->
```

Every milestone has a goal, scope, requirements, exit criteria, launch gate, dependencies, target, and evidence. Every FR, NFR, and TR must belong to at least one Milestone.

### TASKS.md

The micro execution layer. Every task is one issue, one pull request, and one work session, with five files or fewer.

```html
<!-- techlead:task id=TASK-001 depends=none prd=FR-001 spec=TR-001 milestone=M1 tags=foundation labels=type:feature,area:api,priority:p1 -->
```

Each task also contains `Depends on`, `PRD`, `SPEC`, `Milestone`, `Issue title`, `Labels`, `Estimate`, `Acceptance`, `Verify`, and `Files`.

Mandatory tags:

- `docker-local`
- `docker-production`
- `coverage-gate`
- `security`
- `deployment`
- `final-gate` is recommended and produces a warning when absent.

### AGENTS.md and README.md

`AGENTS.md` is the project memory: stack, layout, commands, conventions, engineering rules, decisions, definition of done, and security. `README.md` is the human onboarding: overview, status, Docker quickstart, commands, architecture summary, documentation index, testing, deployment, and security.

Both are generated last so commands and paths are final.

## Issue automation

`TASKS.md` is the source of truth for issue automation. Preview without side effects:

```bash
python3 skills/techlead/scripts/export_issues.py \
  --tasks TASKS.md --plan PLAN.md \
  --provider github --repo owner/name --format json
```

Preview a shell script:

```bash
python3 skills/techlead/scripts/export_issues.py \
  --tasks TASKS.md --plan PLAN.md \
  --provider gitlab --repo group/project --format shell
```

Create labels, milestones, and issues only after explicit approval:

```bash
python3 skills/techlead/scripts/export_issues.py \
  --tasks TASKS.md --plan PLAN.md \
  --provider github --repo owner/name --apply

python3 skills/techlead/scripts/export_issues.py \
  --tasks TASKS.md --plan PLAN.md \
  --provider gitlab --repo group/project --apply
```

The default is a dry-run. GitHub uses `gh`; GitLab uses `glab`. Dependencies are resolved in a second pass after issue numbers exist. The full format is in `skills/techlead/references/issue-format.md`.

## Validation

Run the artifact validator:

```bash
python3 skills/techlead/scripts/validate_artifacts.py PRD.md TASKS.md --all --coverage 80
```

`--all` loads `SPEC.md`, `PLAN.md`, `AGENTS.md`, and `README.md` next to the PRD. You can pass explicit paths:

```bash
python3 skills/techlead/scripts/validate_artifacts.py docs/PRD.md docs/TASKS.md \
  --spec docs/SPEC.md --plan docs/PLAN.md \
  --agents docs/AGENTS.md --readme docs/README.md --all
```

Options:

```text
--spec PATH          Path to SPEC.md.
--plan PATH          Path to PLAN.md.
--agents PATH        Path to AGENTS.md.
--readme PATH        Path to README.md.
--all                Require and validate all six artifacts.
--min-questions 8    Minimum answered interview questions.
--min-tasks 6        Minimum number of task markers.
--coverage 80        Minimum coverage percentage stated in the artifacts.
--strict             Treat warnings as failures.
--json               Emit a machine-readable report.
```

The validator uses only the Python standard library. It checks artifact markers, required sections, requirement IDs, Docker environments, coverage gates, milestone coverage, task dependencies, mandatory tags, issue metadata, traceability, placeholders, AGENTS, and README content.

If Python is unavailable, use `skills/techlead/references/validation-checklist.md`.

## Migration from v1

Version 0.2.0 replaces the v1 contract. Artifacts with `version=1` are rejected with an `unsupported-version` error. To migrate:

1. split the old `PRD.md` into a product-only `PRD.md` and an engineering `SPEC.md`;
2. convert technical requirements to `TR-xxx` in the SPEC;
3. add `PLAN.md` with milestones and map every requirement to a milestone;
4. add `Issue title`, `Labels`, `Estimate`, `SPEC`, and `Milestone` to every task;
5. add `AGENTS.md` and a user-facing `README.md`;
6. run the validator with `--all` and fix every error.

## Development

Prerequisites:

- Python 3.10 or newer.
- `uv` for the test environment.
- Docker when testing generated projects.

The published plugin has no Python runtime dependencies. Its validators use only the standard library, so end users do not need to create a virtual environment. For development, `uv` creates and manages an isolated `.venv` from `pyproject.toml` and resolves the lockfile locally (not committed):

```bash
uv sync --extra dev
```

The `.venv` directory is ignored by Git. Run commands through `uv run` or activate the environment explicitly:

```bash
source .venv/bin/activate
pytest -q
```

Run the tests and coverage gate:

```bash
make coverage
```

Validate the plugin structure:

```bash
make validate
```

Run everything:

```bash
make check
```

The test suite requires at least 80 percent branch coverage over the validator and exporter scripts.

## Repository layout

```text
.
├── plugin.json
├── .claude-plugin/
├── .codex-plugin/
├── .cursor-plugin/
├── .agents/plugins/
├── .github/
├── agents/openai.yaml
├── assets/
├── commands/
│   ├── techlead.md
│   ├── techlead-validate.md
│   └── techlead-issues.md
├── skills/techlead/
│   ├── SKILL.md
│   ├── references/
│   │   ├── prd-template.md
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   ├── tasks-template.md
│   │   ├── issue-format.md
│   │   ├── agents-template.md
│   │   └── readme-template.md
│   └── scripts/
│       ├── artifact_model.py
│       ├── validate_artifacts.py
│       └── export_issues.py
├── scripts/validate_plugin.py
└── tests/
```

## Before publishing

- Run `make check`.
- Run the native plugin validator for each agent you publish to.
- Test installation from a clean environment.
- Confirm the marketplace source paths resolve to this repository root.

## Security

The plugin contains instructions, Markdown commands, and Python scripts. It does not include MCP servers, hooks, network calls, telemetry, or credentials.

Generated projects must not commit secrets. Production requirements include runtime secret injection, a non-root container, TLS, host hardening, backups, vulnerability scanning, and rollback. Issue export is dry-run by default and never creates issues without explicit approval.

## License

MIT. See `LICENSE`.
