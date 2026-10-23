from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import export_issues
from export_issues import (
    ExportError,
    GitHubBackend,
    GitLabBackend,
    IssuePayload,
    MilestonePayload,
    apply_manifest,
    build_backend,
    build_manifest,
    dependency_block,
    label_color,
    main,
    replace_dependencies,
    render_body,
    shell_plan,
    shell_quote,
    split_files,
    task_labels,
)
from fixtures_v2 import VALID_PLAN, VALID_TASKS, valid_texts


def build(**overrides):
    texts = valid_texts()
    values = {
        "tasks_text": texts["tasks"],
        "plan_text": texts["plan"],
        "provider": "github",
        "repo": "owner/repo",
        "base_labels": ["techlead"],
        "id_prefix": True,
    }
    values.update(overrides)
    return build_manifest(**values)


def make_completed(command, returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(command, returncode, stdout=stdout, stderr=stderr)


class FakeRunner:
    def __init__(self, responses):
        self.responses = list(responses)
        self.commands = []

    def __call__(self, command, **kwargs):
        self.commands.append(command)
        response = self.responses.pop(0) if self.responses else make_completed(command)
        if isinstance(response, Exception):
            raise response
        return response


class FakeBackend:
    def __init__(self):
        self.labels = []
        self.milestones = []
        self.created = []
        self.updated = []
        self._next = 100

    def ensure_label(self, label):
        self.labels.append(label)

    def ensure_milestone(self, milestone):
        self.milestones.append(milestone.milestone_id)

    def create_issue(self, issue):
        self._next += 1
        self.created.append(issue.task_id)
        return self._next

    def update_issue(self, number, issue):
        self.updated.append((number, issue.task_id, issue.body))


def test_build_manifest_from_valid_artifacts() -> None:
    manifest = build()
    assert manifest.provider == "github"
    assert manifest.repo == "owner/repo"
    assert [issue.task_id for issue in manifest.issues] == [f"TASK-00{index}" for index in range(1, 7)]
    assert manifest.issues[0].title == "[TASK-001] Bootstrap the API skeleton"
    assert manifest.issues[5].depends_on == ["TASK-005"]
    assert manifest.issues[0].files == ["src/main.py", "src/health.py", "tests/test_health.py"]
    assert manifest.issues[0].milestone == "M1 — Review decisions"
    assert manifest.issues[0].milestone_id == "M1"
    assert "## Dependencies\n\n- Depends on: TASK-001" in manifest.issues[1].body
    assert "## Traceability" in manifest.issues[0].body
    assert "techlead" in manifest.labels
    assert "techlead:foundation" in manifest.labels
    assert "type:chore" in manifest.labels
    assert [milestone.milestone_id for milestone in manifest.milestones] == ["M1", "M2"]
    assert "Goal: A reviewer can approve" in manifest.milestones[0].description
    assert "Exit criteria:" in manifest.milestones[0].description


def test_build_manifest_without_id_prefix_and_custom_labels() -> None:
    manifest = build(id_prefix=False, base_labels=["techlead", "team:ops"])
    assert manifest.issues[0].title == "Bootstrap the API skeleton"
    assert "team:ops" in manifest.labels


def test_build_manifest_to_dict_round_trips() -> None:
    payload = build().to_dict()
    assert payload["provider"] == "github"
    assert payload["issues"][0]["task_id"] == "TASK-001"
    assert payload["issues"][0]["number"] is None
    assert payload["milestones"][0]["id"] == "M1"
    assert json.loads(json.dumps(payload)) == payload


def test_build_manifest_requires_tasks() -> None:
    with pytest.raises(ExportError, match="no task markers"):
        build(tasks_text="# TASKS\n\nNo tasks.")


def test_build_manifest_requires_milestones() -> None:
    with pytest.raises(ExportError, match="no milestone markers"):
        build(plan_text="# PLAN\n\nNo milestones.")


def test_build_manifest_requires_milestone_per_task() -> None:
    tasks = VALID_TASKS.replace(" spec=TR-001 milestone=M1", " spec=TR-001", 1)
    tasks = tasks.replace("- Milestone: M1\n", "", 1)
    with pytest.raises(ExportError, match="TASK-001 has no milestone"):
        build(tasks_text=tasks)


def test_build_manifest_rejects_unknown_milestone() -> None:
    tasks = VALID_TASKS.replace("milestone=M1 tags=foundation", "milestone=M9 tags=foundation", 1)
    with pytest.raises(ExportError, match="unknown milestone M9"):
        build(tasks_text=tasks)


def test_build_manifest_requires_issue_title() -> None:
    tasks = VALID_TASKS.replace("- Issue title: Bootstrap the API skeleton\n", "", 1)
    with pytest.raises(ExportError, match="no issue title"):
        build(tasks_text=tasks)


def test_build_manifest_requires_estimate() -> None:
    tasks = VALID_TASKS.replace("- Estimate: S\n", "", 1)
    with pytest.raises(ExportError, match="no estimate"):
        build(tasks_text=tasks)


def test_build_manifest_requires_labels() -> None:
    tasks = VALID_TASKS.replace("labels=type:chore,area:infra,priority:p1", "labels=type:chore", 1)
    with pytest.raises(ExportError, match="incomplete labels"):
        build(tasks_text=tasks)


def test_build_manifest_requires_task_ids() -> None:
    tasks = VALID_TASKS.replace("<!-- techlead:task id=TASK-001 ", "<!-- techlead:task ", 1)
    with pytest.raises(ExportError, match="missing its id"):
        build(tasks_text=tasks)


def test_task_labels_deduplicates_and_sorts() -> None:
    manifest = build()
    labels = task_labels(export_issues.parse_tasks(VALID_TASKS)[5], ["techlead", "type:infra"])
    assert labels == sorted(set(labels))
    assert labels.count("techlead") == 1
    assert "techlead:final-gate" in labels
    assert manifest.labels == sorted(manifest.labels)


def test_dependency_block_variants() -> None:
    assert dependency_block([]) == "- None"
    assert dependency_block(["TASK-001"]) == "- Depends on: TASK-001"
    assert dependency_block(["TASK-001"], {"TASK-001": 12}) == "- Depends on: #12 (TASK-001)"


def test_replace_dependencies_existing_and_appended() -> None:
    existing = "## Dependencies\n\n- Depends on: TASK-001\n\n## Traceability\n\n- PRD: FR-001"
    replaced = replace_dependencies(existing, ["TASK-001"], {"TASK-001": 7})
    assert "- Depends on: #7 (TASK-001)" in replaced
    assert "TASK-001\n" not in replaced

    appended = replace_dependencies("## Traceability\n\n- PRD: FR-001", ["TASK-001"], {"TASK-001": 7})
    assert appended.endswith("## Dependencies\n\n- Depends on: #7 (TASK-001)\n")


def test_render_body_without_files() -> None:
    texts = valid_texts()
    task = export_issues.parse_tasks(texts["tasks"])[0]
    task.fields["files"] = ""
    milestone = export_issues.parse_milestones(texts["plan"])[0]
    body = render_body(task, milestone)
    assert "- See task verification" in body


def test_split_files_variants() -> None:
    assert split_files("") == []
    assert split_files(" a.py, b.py , ") == ["a.py", "b.py"]


def test_label_color_is_deterministic() -> None:
    assert label_color("techlead") == label_color("techlead")
    assert label_color("techlead") in export_issues.LABEL_COLORS


def test_shell_quote_quotes_spaces() -> None:
    assert shell_quote(["gh", "issue", "create", "--title", "Hello world"]) == "gh issue create --title 'Hello world'"


def test_shell_plan_github() -> None:
    script = shell_plan(build())
    assert script.startswith("#!/usr/bin/env bash\nset -euo pipefail")
    assert "gh label create techlead --repo owner/repo" in script
    assert "gh api repos/owner/repo/milestones" in script
    assert "gh issue create --repo owner/repo" in script
    assert "cat > .techlead-issues/TASK-001.md <<'TECHLEAD_ISSUE'" in script
    assert "--milestone 'M1 — Review decisions'" in script
    assert "--label techlead:foundation" in script


def test_shell_plan_gitlab() -> None:
    script = shell_plan(build(provider="gitlab"))
    assert "glab label create --name techlead" in script
    assert "glab milestone create --title 'M1 — Review decisions'" in script
    assert "glab issue create --title '[TASK-001] Bootstrap the API skeleton'" in script
    assert "--description" in script
    assert "gh " not in script


def test_backend_run_reports_missing_cli() -> None:
    backend = GitHubBackend("owner/repo", runner=FakeRunner([FileNotFoundError()]))
    with pytest.raises(ExportError, match="gh is not installed"):
        backend.run(["gh", "version"])


def test_backend_run_reports_failure() -> None:
    runner = FakeRunner([make_completed(["gh"], returncode=1, stderr="boom", stdout="stdout")])
    backend = GitHubBackend("owner/repo", runner=runner)
    with pytest.raises(ExportError, match="gh failed: boom"):
        backend.run(["gh"])

    runner = FakeRunner([make_completed(["gh"], returncode=1, stdout="stdout")])
    backend = GitHubBackend("owner/repo", runner=runner)
    with pytest.raises(ExportError, match="gh failed: stdout"):
        backend.run(["gh"])

    runner = FakeRunner([make_completed(["gh"], returncode=1)])
    backend = GitHubBackend("owner/repo", runner=runner)
    with pytest.raises(ExportError, match="gh failed: $"):
        backend.run(["gh"])


def test_backend_run_can_skip_check() -> None:
    runner = FakeRunner([make_completed(["gh"], returncode=1)])
    backend = GitHubBackend("owner/repo", runner=runner)
    assert backend.run(["gh"], check=False).returncode == 1


def test_parse_issue_number_variants() -> None:
    backend = GitHubBackend("owner/repo", runner=FakeRunner([]))
    assert backend.parse_issue_number("https://github.com/owner/repo/issues/42") == 42
    assert backend.parse_issue_number("https://gitlab.com/owner/repo/-/issues/7\n") == 7
    with pytest.raises(ExportError, match="Cannot parse issue number"):
        backend.parse_issue_number("no url here")


def test_github_ensure_label_and_update() -> None:
    runner = FakeRunner([make_completed(["gh"]), make_completed(["gh"])])
    backend = GitHubBackend("owner/repo", runner=runner)
    backend.ensure_label("techlead")
    issue = build().issues[0]
    backend.update_issue(10, issue)
    assert runner.commands[0][:4] == ["gh", "label", "create", "techlead"]
    assert runner.commands[1][:6] == ["gh", "issue", "edit", "10", "--repo", "owner/repo"]


def test_github_ensure_milestone_creates_when_missing() -> None:
    runner = FakeRunner([make_completed(["gh"], stdout="[]"), make_completed(["gh"])])
    backend = GitHubBackend("owner/repo", runner=runner)
    backend.ensure_milestone(MilestonePayload("M1", "M1 — Review decisions", "Goal"))
    assert runner.commands[0][:4] == ["gh", "api", "repos/owner/repo/milestones?state=all", "--paginate"]
    assert runner.commands[1][:4] == ["gh", "api", "repos/owner/repo/milestones", "--method"]


def test_github_ensure_milestone_skips_existing_and_rejects_invalid_json() -> None:
    runner = FakeRunner(
        [
            make_completed(["gh"], stdout='[{"title": "M1 — Review decisions"}]'),
            make_completed(["gh"], stdout="not json"),
        ]
    )
    backend = GitHubBackend("owner/repo", runner=runner)
    backend.ensure_milestone(MilestonePayload("M1", "M1 — Review decisions", "Goal"))
    with pytest.raises(ExportError, match="invalid JSON"):
        backend.ensure_milestone(MilestonePayload("M2", "M2 — Audit", "Goal"))
    assert len(runner.commands) == 2


def test_github_create_issue() -> None:
    runner = FakeRunner([make_completed(["gh"], stdout="https://github.com/owner/repo/issues/55\n")])
    backend = GitHubBackend("owner/repo", runner=runner)
    number = backend.create_issue(build().issues[0])
    assert number == 55
    command = runner.commands[0]
    assert command[:4] == ["gh", "issue", "create", "--repo"]
    assert "--body" in command
    assert "--milestone" in command
    assert "--label" in command


def test_gitlab_ensure_label_tolerates_existing_and_rejects_other_errors() -> None:
    runner = FakeRunner(
        [
            make_completed(["glab"], returncode=1, stderr="Label already exists"),
            make_completed(["glab"], returncode=1, stderr="permission denied"),
            make_completed(["glab"]),
        ]
    )
    backend = GitLabBackend("owner/repo", runner=runner)
    backend.ensure_label("techlead")
    with pytest.raises(ExportError, match="permission denied"):
        backend.ensure_label("techlead")
    backend.ensure_label("techlead")
    assert runner.commands[0][:5] == ["glab", "label", "create", "--name", "techlead"]


def test_gitlab_ensure_milestone_skips_existing_and_creates() -> None:
    runner = FakeRunner(
        [
            make_completed(["glab"], stdout="M1 — Review decisions | open\n"),
            make_completed(["glab"], stdout="Other milestone\n"),
            make_completed(["glab"]),
        ]
    )
    backend = GitLabBackend("owner/repo", runner=runner)
    backend.ensure_milestone(MilestonePayload("M1", "M1 — Review decisions", "Goal"))
    backend.ensure_milestone(MilestonePayload("M2", "M2 — Audit", "Goal"))
    assert len(runner.commands) == 3
    assert runner.commands[2][:4] == ["glab", "milestone", "create", "--title"]


def test_gitlab_create_and_update_issue() -> None:
    runner = FakeRunner(
        [
            make_completed(["glab"], stdout="https://gitlab.com/owner/repo/-/issues/9\n"),
            make_completed(["glab"]),
        ]
    )
    backend = GitLabBackend("owner/repo", runner=runner)
    issue = build(provider="gitlab").issues[0]
    assert backend.create_issue(issue) == 9
    backend.update_issue(9, issue)
    assert runner.commands[0][:4] == ["glab", "issue", "create", "--title"]
    assert runner.commands[1][:3] == ["glab", "issue", "update"]


def test_result_has_title_matches_whole_line() -> None:
    assert export_issues.result_has_title("M2 — Audit | open\n", "M2 — Audit")
    assert not export_issues.result_has_title("M2 — Audit plus extra\n", "M2 — Audit")


def test_build_backend_requires_cli(monkeypatch) -> None:
    monkeypatch.setattr(export_issues.shutil, "which", lambda name: None)
    with pytest.raises(ExportError, match="gh is required"):
        build_backend("github", "owner/repo")
    with pytest.raises(ExportError, match="glab is required"):
        build_backend("gitlab", "owner/repo")


def test_build_backend_returns_backends(monkeypatch) -> None:
    monkeypatch.setattr(export_issues.shutil, "which", lambda name: f"/usr/bin/{name}")
    assert isinstance(build_backend("github", "owner/repo"), GitHubBackend)
    assert isinstance(build_backend("gitlab", "owner/repo"), GitLabBackend)


def test_apply_manifest_resolves_dependencies() -> None:
    manifest = build()
    backend = FakeBackend()
    resolution = apply_manifest(manifest, backend)
    assert backend.labels == manifest.labels
    assert backend.milestones == ["M1", "M2"]
    assert backend.created == [f"TASK-00{index}" for index in range(1, 7)]
    assert resolution["TASK-001"] == 101
    assert len(backend.updated) == 5
    assert backend.updated[0][0] == 102
    assert "Depends on: #101 (TASK-001)" in backend.updated[0][2]


def test_main_dry_run_json(tmp_path: Path, capsys) -> None:
    tasks = tmp_path / "TASKS.md"
    plan = tmp_path / "PLAN.md"
    tasks.write_text(VALID_TASKS, encoding="utf-8")
    plan.write_text(VALID_PLAN, encoding="utf-8")
    output = tmp_path / "manifest.json"
    exit_code = main(
        ["--tasks", str(tasks), "--plan", str(plan), "--repo", "owner/repo", "--json-output", str(output)]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "dry-run"
    assert payload["manifest"]["issues"][0]["task_id"] == "TASK-001"
    assert json.loads(output.read_text(encoding="utf-8")) == payload


def test_main_dry_run_shell(tmp_path: Path, capsys) -> None:
    tasks = tmp_path / "TASKS.md"
    plan = tmp_path / "PLAN.md"
    tasks.write_text(VALID_TASKS, encoding="utf-8")
    plan.write_text(VALID_PLAN, encoding="utf-8")
    exit_code = main(["--tasks", str(tasks), "--plan", str(plan), "--provider", "gitlab", "--format", "shell"])
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "dry-run"
    assert "glab issue create" in payload["script"]


def test_main_apply_requires_repo(tmp_path: Path, capsys) -> None:
    tasks = tmp_path / "TASKS.md"
    plan = tmp_path / "PLAN.md"
    tasks.write_text(VALID_TASKS, encoding="utf-8")
    plan.write_text(VALID_PLAN, encoding="utf-8")
    exit_code = main(["--tasks", str(tasks), "--plan", str(plan), "--apply"])
    assert exit_code == 1
    assert "--repo is required" in capsys.readouterr().err


def test_main_apply_uses_backend(tmp_path: Path, capsys, monkeypatch) -> None:
    tasks = tmp_path / "TASKS.md"
    plan = tmp_path / "PLAN.md"
    tasks.write_text(VALID_TASKS, encoding="utf-8")
    plan.write_text(VALID_PLAN, encoding="utf-8")
    backend = FakeBackend()
    monkeypatch.setattr(export_issues, "build_backend", lambda provider, repo: backend)
    exit_code = main(["--tasks", str(tasks), "--plan", str(plan), "--apply", "--repo", "owner/repo"])
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "created"
    assert payload["issues"]["TASK-001"] == 101
    assert len(backend.created) == 6


def test_main_missing_files(tmp_path: Path, capsys) -> None:
    exit_code = main(["--tasks", str(tmp_path / "nope.md"), "--plan", str(tmp_path / "nope-plan.md")])
    assert exit_code == 1
    assert "Cannot read" in capsys.readouterr().err
