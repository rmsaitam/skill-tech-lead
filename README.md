# TechLead

[![skills.sh](https://skills.sh/b/rmsaitam/skill-tech-lead)](https://skills.sh/rmsaitam/skill-tech-lead)

TechLead is a planning plugin for AI coding agents. It interviews the user about a product idea, captures every decision, and produces two traceable artifacts:

- `PRD.md`: the product requirements document, including the interview answers.
- `TASKS.md`: the implementation tasks in dependency order, with acceptance criteria and verification steps.

The generated plan always covers Docker for local/test and production/VPS, security hardening, and a definition of done that requires at least 80 percent test coverage.

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

The skill follows seven gates:

1. Inspect the workspace and reuse known facts.
2. Interview in rounds of at most five questions.
3. Present a compact plan and wait for approval.
4. Write or update `PRD.md`.
5. Write or update `TASKS.md`.
6. Validate both artifacts.
7. Report the result and stop before implementation.

Validate existing artifacts:

```text
/techlead-validate
/techlead-validate docs/PRD.md docs/TASKS.md
```

## Artifact contract

### PRD.md

The file starts with:

```html
<!-- techlead:artifact type=prd version=1 -->
```

It must contain section markers for `summary`, `problem`, `users`, `scope`, `functional`, `nonfunctional`, `assumptions`, `architecture`, `security`, `docker`, `testing`, `dod`, `risks`, `qa`, and `traceability`.

The Docker section must contain both environment markers:

```html
<!-- techlead:env id=local -->
<!-- techlead:env id=production -->
```

Requirements use stable IDs:

```markdown
- **FR-001**: The operator can approve a request and sees the updated decision.
- **NFR-001**: Test coverage remains at or above 80 percent.
```

Every question and answer from the interview appears in the `Interview Answers` section. At least eight answered questions are required by default.

### TASKS.md

The file starts with:

```html
<!-- techlead:artifact type=tasks version=1 -->
```

Every task uses a marker with an ID, dependencies, PRD references, and tags:

```html
<!-- techlead:task id=TASK-001 depends=none prd=FR-001,NFR-001 tags=foundation -->
```

Each task also contains a status checkbox and the fields `Depends on`, `PRD`, `Acceptance`, `Verify`, and `Files`.

The task list must include these tags:

- `docker-local`
- `docker-production`
- `coverage-gate`
- `security`
- `deployment`

A `final-gate` task is recommended and produces a warning when absent.

## Validation

Run the artifact validator:

```bash
python3 skills/techlead/scripts/validate_artifacts.py PRD.md TASKS.md --coverage 80
```

Options:

```text
--min-questions 8    Minimum answered interview questions.
--min-tasks 6        Minimum number of task markers.
--coverage 80        Minimum coverage percentage stated in the artifacts.
--strict             Treat warnings as failures.
--json               Emit a machine-readable report.
```

The validator uses only the Python standard library. It checks markers, sections, requirement IDs, Docker environments, coverage gates, task dependencies, mandatory tags, traceability, placeholders, and the definition of done.

If Python is unavailable, use `skills/techlead/references/validation-checklist.md`.

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

The test suite requires at least 80 percent branch coverage over both validator scripts.

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
├── skills/techlead/
│   ├── SKILL.md
│   ├── references/
│   └── scripts/validate_artifacts.py
├── scripts/validate_plugin.py
└── tests/
```

## Before publishing

- Run `make check`.
- Run the native plugin validator for each agent you publish to.
- Test installation from a clean environment.
- Confirm the marketplace source paths resolve to this repository root.

## Security

The plugin contains instructions, Markdown commands, and Python validators. It does not include MCP servers, hooks, network calls, telemetry, or credentials.

Generated projects must not commit secrets. Production requirements include runtime secret injection, a non-root container, TLS, host hardening, backups, vulnerability scanning, and rollback.

## License

MIT. See `LICENSE`.
