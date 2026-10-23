from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from artifact_model import parse_attributes, parse_milestones, parse_tasks, split_list
from fixtures_v2 import valid_texts
from validate_artifacts import main, validate_files, validate_texts


def run(**overrides: str | None):
    texts = valid_texts()
    texts.update({key: value for key, value in overrides.items() if value is not None})
    return validate_texts(
        texts["prd"],
        texts["tasks"],
        spec_text=texts["spec"],
        plan_text=texts["plan"],
        agents_text=texts["agents"],
        readme_text=texts["readme"],
    )


def codes(report) -> set[str]:
    return {issue.code for issue in report.errors}


def test_valid_artifacts_pass() -> None:
    report = run()
    assert report.ok, [issue.message for issue in report.errors]
    assert report.stats["tasks"] == 6
    assert report.stats["milestones"] == 2
    assert report.stats["functional_requirements"] == 2
    assert report.stats["nonfunctional_requirements"] == 2
    assert report.stats["technical_requirements"] == 4
    assert report.stats["interview_questions"] == 8
    assert report.stats.get("prd_coverage_gate") == 80 or report.stats.get("coverage_gate") == 80


def test_valid_artifacts_pass_strict() -> None:
    report = run()
    assert not report.warnings


def test_partial_validation_without_optional_artifacts() -> None:
    texts = valid_texts()
    report = validate_texts(texts["prd"], texts["tasks"])
    assert report.ok, [issue.message for issue in report.errors]


def test_placeholder_is_rejected() -> None:
    report = run(prd=valid_texts()["prd"].replace("audit history", "audit TODO history", 1))
    assert "placeholder" in codes(report)


def test_placeholder_in_optional_artifact_is_rejected() -> None:
    report = run(readme=valid_texts()["readme"].replace("Review Queue", "Review TBD Queue", 1))
    assert "placeholder" in codes(report)


def test_placeholder_inside_code_fence_is_ignored() -> None:
    prd = valid_texts()["prd"].replace(
        "A review queue that lets operations staff decide requests and prove who approved them.",
        "A review queue that lets operations staff decide requests and prove who approved them.\n\n```text\nTODO\n```",
    )
    report = run(prd=prd)
    assert report.ok, [issue.message for issue in report.errors]


def test_missing_section_is_rejected() -> None:
    report = run(prd=valid_texts()["prd"].replace("<!-- techlead:section id=risks -->", ""))
    assert "missing-section" in codes(report)


def test_unsupported_version_is_rejected() -> None:
    report = run(prd=valid_texts()["prd"].replace("version=2", "version=1", 1))
    assert "unsupported-version" in codes(report)


def test_wrong_artifact_type_is_rejected() -> None:
    report = run(spec=valid_texts()["spec"].replace("type=spec", "type=prd", 1))
    assert "wrong-artifact-type" in codes(report)


def test_missing_metadata_is_rejected() -> None:
    report = run(readme=valid_texts()["readme"])
    assert report.ok
    report = run(agents=valid_texts()["agents"].replace("- Source artifacts:", "- Sources:"))
    assert report.ok
    report = run(spec=valid_texts()["spec"].replace("- Coverage gate: >= 80 percent\n", "", 1))
    assert "missing-metadata" in codes(report)


def test_missing_docker_environment_is_rejected() -> None:
    report = run(spec=valid_texts()["spec"].replace("<!-- techlead:env id=production -->", ""))
    assert "missing-docker-environment" in codes(report)


def test_thin_docker_environment_is_rejected() -> None:
    lines = [
        "- A multi-stage image uses a pinned base version.",
        "- The runtime uses a non-root user and a read-only filesystem.",
        "- Capabilities are dropped and no-new-privileges is enabled.",
        "- Secrets are injected at runtime from the host secret store.",
        "- A reverse proxy terminates TLS and sets secure headers.",
    ]
    production = "\n".join(lines)
    spec = valid_texts()["spec"]
    start = spec.index("<!-- techlead:env id=production -->")
    end = spec.index("<!-- techlead:section id=testing -->")
    report = run(spec=spec[:start] + "<!-- techlead:env id=production -->\n" + production + "\n\n" + spec[end:])
    assert "thin-docker-environment" in codes(report)


def test_low_coverage_is_rejected() -> None:
    spec = valid_texts()["spec"].replace(
        "- Coverage gate: >= 80 percent.\n- Unit tests",
        "- Coverage gate: >= 70 percent.\n- Unit tests",
        1,
    )
    report = run(spec=spec)
    assert "coverage-too-low" in codes(report)


def test_missing_coverage_percentage_is_rejected() -> None:
    spec = valid_texts()["spec"].replace(
        "- Coverage gate: >= 80 percent.\n- Unit tests",
        "- Coverage gate: mandatory.\n- Unit tests",
        1,
    )
    spec = spec.replace(
        "- Coverage command: pytest --cov --cov-branch --cov-fail-under=80.",
        "- Coverage command: pytest --cov --cov-branch.",
        1,
    )
    report = run(spec=spec)
    assert "missing-coverage-gate" in codes(report)


def test_missing_coverage_mention_is_rejected() -> None:
    spec = valid_texts()["spec"].replace(
        "- Coverage gate: >= 80 percent.\n- Unit tests cover validation, authorization, and decision rules.\n"
        "- Integration tests use a disposable database and exercise migrations.\n"
        "- End-to-end tests cover the review and audit journeys.\n"
        "- Coverage command: pytest --cov --cov-branch --cov-fail-under=80.",
        "- Quality gate: >= 80 percent.\n- Unit tests cover validation, authorization, and decision rules.\n"
        "- Integration tests use a disposable database and exercise migrations.\n"
        "- End-to-end tests cover the review and audit journeys.\n"
        "- Quality command: pytest --cov --cov-branch --cov-fail-under=80.",
        1,
    )
    report = run(spec=spec)
    assert "missing-coverage" in codes(report)


def test_insufficient_questions_is_rejected() -> None:
    prd = valid_texts()["prd"].split("### Q-008")[0] + "\n<!-- techlead:section id=traceability -->\n## Traceability\n\n| FR-001 | x | TR-001 |\n"
    report = run(prd=prd)
    assert "insufficient-interview" in codes(report)


def test_duplicate_requirement_is_rejected() -> None:
    prd = valid_texts()["prd"].replace(
        "- **NFR-002**: Every decision must be recorded in the audit log within one second.",
        "- **NFR-002**: Every decision must be recorded in the audit log within one second.\n"
        "- **NFR-002**: Duplicate definition.",
        1,
    )
    report = run(prd=prd)
    assert "duplicate-requirement" in codes(report)


def test_technical_requirement_in_prd_is_rejected() -> None:
    prd = valid_texts()["prd"].replace(
        "- **FR-002**: The auditor can search the decision history by request, actor, and date.",
        "- **FR-002**: The auditor can search the decision history by request, actor, and date.\n"
        "- **TR-009**: The API must validate every input against a schema.",
        1,
    )
    report = run(prd=prd)
    assert "technical-requirement-in-prd" in codes(report)


def test_product_requirement_in_spec_is_rejected() -> None:
    spec = valid_texts()["spec"].replace(
        "- **TR-001**: The API must validate every request body against a schema and return a typed error before persistence.",
        "- **TR-001**: The API must validate every request body against a schema and return a typed error before persistence.\n"
        "- **FR-009**: The user can do something testable.",
        1,
    )
    report = run(spec=spec)
    assert "product-requirement-in-spec" in codes(report)


def test_missing_technical_requirement_is_rejected() -> None:
    spec = valid_texts()["spec"]
    start = spec.index("<!-- techlead:section id=technical -->")
    end = spec.index("<!-- techlead:section id=security -->")
    spec = spec[:start] + "<!-- techlead:section id=technical -->\n## Technical Requirements\n\nNo requirements yet.\n\n" + spec[end:]
    report = run(spec=spec)
    assert "missing-technical-requirement" in codes(report)


def test_missing_spec_traceability_is_rejected() -> None:
    spec = valid_texts()["spec"].replace("| NFR-002 | Audit latency | NFR-002 | Audit worker |\n", "", 1)
    spec = spec.replace("| TR-003 | Audit latency | NFR-002 | Audit worker |\n", "", 1)
    report = run(spec=spec)
    assert "traceability-gap" in codes(report)


def test_scope_subsections_are_required() -> None:
    prd = valid_texts()["prd"].replace("### Out of scope", "### Excluded", 1)
    report = run(prd=prd)
    assert "missing-out-of-scope" in codes(report)


def test_risk_table_is_required() -> None:
    plan = valid_texts()["plan"].replace("| Risk | Probability | Impact | Mitigation | Owner |", "Risk list", 1)
    report = run(plan=plan)
    assert "missing-risk-table" in codes(report)


def test_missing_milestone_is_rejected() -> None:
    plan = valid_texts()["plan"].replace("<!-- techlead:milestone id=M1 order=1 depends=none covers=FR-001,NFR-001,TR-001 -->", "")
    report = run(plan=plan)
    assert "unknown-milestone-requirement" in codes(report) or "uncovered-requirements" in codes(report)


def test_duplicate_milestone_id_is_rejected() -> None:
    plan = valid_texts()["plan"].replace(
        "<!-- techlead:milestone id=M2 order=2 depends=M1", "<!-- techlead:milestone id=M1 order=2 depends=M1", 1
    )
    report = run(plan=plan)
    assert "duplicate-milestone-id" in codes(report)


def test_milestone_order_is_rejected() -> None:
    plan = valid_texts()["plan"].replace(
        "<!-- techlead:milestone id=M2 order=2 depends=M1", "<!-- techlead:milestone id=M2 order=1 depends=M1", 1
    )
    report = run(plan=plan)
    assert "milestone-order" in codes(report)


def test_unknown_milestone_requirement_is_rejected() -> None:
    plan = valid_texts()["plan"].replace("covers=FR-002,NFR-002", "covers=FR-999,NFR-002", 1)
    report = run(plan=plan)
    assert "unknown-milestone-requirement" in codes(report)


def test_uncovered_requirement_is_rejected() -> None:
    plan = valid_texts()["plan"].replace("covers=FR-002,NFR-002", "covers=NFR-002", 1)
    report = run(plan=plan)
    assert "uncovered-requirements" in codes(report)


def test_missing_milestone_field_is_rejected() -> None:
    plan = valid_texts()["plan"].replace("- Exit criteria: Search works, audit latency is within one second, and production passes the smoke test.\n", "", 1)
    report = run(plan=plan)
    assert "missing-milestone-exit" in codes(report)


def test_unknown_milestone_dependency_is_rejected() -> None:
    plan = valid_texts()["plan"].replace("depends=M1 covers=FR-002", "depends=M9 covers=FR-002", 1)
    report = run(plan=plan)
    assert "unknown-milestone-dependency" in codes(report)


def test_incomplete_launch_strategy_is_rejected() -> None:
    plan = valid_texts()["plan"].replace(
        "- Rollback restores the previous image within ten minutes and keeps audit data intact.",
        "- Recovery restores the previous image within ten minutes and keeps audit data intact.",
        1,
    )
    report = run(plan=plan)
    assert "incomplete-strategy" in codes(report)


def test_single_milestone_is_a_warning() -> None:
    plan = valid_texts()["plan"]
    start = plan.index("<!-- techlead:milestone id=M2")
    end = plan.index("<!-- techlead:section id=dependencies -->")
    plan = plan[:start] + plan[end:]
    plan = plan.replace("covers=FR-001,NFR-001,TR-001", "covers=FR-001,FR-002,NFR-001,NFR-002,TR-001,TR-002,TR-003,TR-004", 1)
    plan = plan.replace("| FR-002 | M2 |\n", "| FR-002 | M1 |\n", 1)
    plan = plan.replace("| NFR-002 | M2 |\n", "| NFR-002 | M1 |\n", 1)
    plan = plan.replace("| TR-002 | M2 |\n", "| TR-002 | M1 |\n", 1)
    plan = plan.replace("| TR-003 | M2 |\n", "| TR-003 | M1 |\n", 1)
    plan = plan.replace("| TR-004 | M2 |\n", "| TR-004 | M1 |\n", 1)
    report = run(plan=plan)
    assert "single-milestone" in {issue.code for issue in report.warnings}


def test_missing_task_spec_reference_is_rejected() -> None:
    tasks = valid_texts()["tasks"].replace(" spec=TR-001 milestone=M1", " milestone=M1", 1)
    tasks = tasks.replace("- SPEC: TR-001\n- Milestone: M1", "- Milestone: M1", 1)
    report = run(tasks=tasks)
    assert "missing-spec-reference" in codes(report)


def test_unknown_task_spec_reference_is_rejected() -> None:
    tasks = valid_texts()["tasks"].replace("spec=TR-001 milestone=M1", "spec=TR-999 milestone=M1", 1)
    tasks = tasks.replace("- SPEC: TR-001\n- Milestone: M1", "- SPEC: TR-999\n- Milestone: M1", 1)
    report = run(tasks=tasks)
    assert "unknown-spec-reference" in codes(report)


def test_missing_task_milestone_is_rejected() -> None:
    tasks = valid_texts()["tasks"].replace(" spec=TR-001 milestone=M1", " spec=TR-001", 1)
    tasks = tasks.replace("- SPEC: TR-001\n- Milestone: M1", "- SPEC: TR-001", 1)
    report = run(tasks=tasks)
    assert "missing-task-milestone" in codes(report)


def test_unknown_task_milestone_is_rejected() -> None:
    tasks = valid_texts()["tasks"].replace("milestone=M1 tags=foundation", "milestone=M9 tags=foundation", 1)
    tasks = tasks.replace("- Milestone: M1\n- Issue title: Bootstrap the API skeleton", "- Milestone: M9\n- Issue title: Bootstrap the API skeleton", 1)
    report = run(tasks=tasks)
    assert "unknown-task-milestone" in codes(report)


def test_missing_labels_and_prefix_are_rejected() -> None:
    tasks = valid_texts()["tasks"].replace("labels=type:chore,area:infra,priority:p1", "labels=type:chore,area:infra", 1)
    tasks = tasks.replace("- Labels: type:chore, area:infra, priority:p1", "- Labels: type:chore, area:infra", 1)
    report = run(tasks=tasks)
    assert "missing-labels" in codes(report)
    assert "missing-label-prefix" in codes(report)


def test_invalid_estimate_is_rejected() -> None:
    tasks = valid_texts()["tasks"].replace("- Estimate: S\n- Acceptance: The API starts", "- Estimate: XL\n- Acceptance: The API starts", 1)
    report = run(tasks=tasks)
    assert "invalid-estimate" in codes(report)


def test_long_issue_title_is_rejected() -> None:
    tasks = valid_texts()["tasks"].replace(
        "- Issue title: Bootstrap the API skeleton",
        f"- Issue title: {'Bootstrap the API skeleton with a very long descriptive title that exceeds the limit'}",
        1,
    )
    report = run(tasks=tasks)
    assert "long-issue-title" in codes(report)


def test_duplicate_issue_title_is_rejected() -> None:
    tasks = valid_texts()["tasks"].replace(
        "- Issue title: Implement the decision endpoint",
        "- Issue title: Bootstrap the API skeleton",
        1,
    )
    report = run(tasks=tasks)
    assert "duplicate-issue-title" in codes(report)


def test_task_too_large_is_rejected() -> None:
    tasks = valid_texts()["tasks"].replace(
        "- Files: src/main.py, src/health.py, tests/test_health.py",
        "- Files: a.py, b.py, c.py, d.py, e.py, f.py",
        1,
    )
    report = run(tasks=tasks)
    assert "task-too-large" in codes(report)


def test_missing_mandatory_tag_is_rejected() -> None:
    tasks = valid_texts()["tasks"].replace("tags=docker-local,security", "tags=security", 1)
    tasks = tasks.replace("tags=coverage-gate,docker-local", "tags=coverage-gate", 1)
    report = run(tasks=tasks)
    assert "missing-mandatory-tags" in codes(report)


def test_missing_final_gate_is_a_warning() -> None:
    tasks = valid_texts()["tasks"].replace("tags=docker-production,deployment,final-gate", "tags=docker-production,deployment", 1)
    report = run(tasks=tasks)
    assert report.ok
    assert "missing-final-gate" in {issue.code for issue in report.warnings}


def test_milestone_without_task_is_rejected() -> None:
    tasks = valid_texts()["tasks"]
    for task in ("TASK-004", "TASK-005", "TASK-006"):
        tasks = tasks.replace(f" milestone=M2 tags", f" milestone=M1 tags", 1)
    tasks = tasks.replace("- Milestone: M2", "- Milestone: M1")
    report = run(tasks=tasks)
    assert "milestone-without-task" in codes(report)


def test_uncovered_task_requirement_is_rejected() -> None:
    tasks = re.sub(r"\bprd=[^ ]+", "prd=FR-001", valid_texts()["tasks"])
    report = run(tasks=tasks)
    assert "uncovered-requirements" in codes(report)


def test_incomplete_issue_format_is_rejected() -> None:
    tasks = valid_texts()["tasks"]
    tasks = tasks.replace("- Create issues with `gh` for GitHub or `glab` for GitLab after approval.", "- Create issues after approval.", 1)
    tasks = tasks.replace("- Dry-run with `export_issues.py` before creating anything.", "- Dry-run before creating anything.", 1)
    report = run(tasks=tasks)
    assert "incomplete-issue-format" in codes(report)


def test_missing_task_traceability_is_rejected() -> None:
    tasks = valid_texts()["tasks"].replace("| M2 | TASK-004, TASK-005, TASK-006 |\n", "", 1)
    report = run(tasks=tasks)
    assert "traceability-milestone" in codes(report)


def test_missing_task_dod_docker_is_rejected() -> None:
    tasks = valid_texts()["tasks"].replace("- [ ] The local Docker environment passes the test suite.", "- [ ] The local environment passes the test suite.", 1)
    report = run(tasks=tasks)
    assert "missing-dod-docker" in codes(report)


def test_agents_missing_document_link_is_rejected() -> None:
    agents = valid_texts()["agents"].replace("PRD.md", "product brief")
    report = run(agents=agents)
    assert "missing-document-link" in codes(report)


def test_agents_missing_security_content_is_rejected() -> None:
    agents = valid_texts()["agents"]
    agents = agents.replace("secrets", "credentials").replace("Secrets", "Credentials").replace("secret", "credential")
    report = run(agents=agents)
    assert "missing-agents-content" in codes(report)


def test_readme_missing_document_link_is_rejected() -> None:
    readme = valid_texts()["readme"].replace("- AGENTS.md: project memory and engineering conventions.\n", "", 1)
    report = run(readme=readme)
    assert "missing-document-link" in codes(report)


def test_readme_missing_coverage_content_is_rejected() -> None:
    readme = re.sub(r"coverage", "tests", valid_texts()["readme"], flags=re.IGNORECASE)
    report = run(readme=readme)
    assert "missing-readme-content" in codes(report)


def test_parse_attributes_handles_quotes() -> None:
    attributes = parse_attributes('id=TASK-001 depends="TASK-002,TASK-003" tags=core')
    assert attributes == {
        "id": "TASK-001",
        "depends": "TASK-002,TASK-003",
        "tags": "core",
    }


def test_split_list_handles_none_and_values() -> None:
    assert split_list("none") == []
    assert split_list("N/A") == []
    assert split_list("TASK-001, TASK-002") == ["TASK-001", "TASK-002"]


def test_parse_tasks_and_milestones() -> None:
    texts = valid_texts()
    tasks = parse_tasks(texts["tasks"])
    milestones = parse_milestones(texts["plan"])
    assert tasks[0].task_id == "TASK-001"
    assert tasks[0].milestone == "M1"
    assert tasks[0].spec_refs == ["TR-001"]
    assert milestones[0].milestone_id == "M1"
    assert milestones[1].depends == ["M1"]


def test_validate_files_reports_missing_files(tmp_path: Path) -> None:
    report = validate_files(tmp_path / "missing-prd.md", tmp_path / "missing-tasks.md")
    assert len(report.errors) == 2
    assert all(issue.code == "missing-file" for issue in report.errors)


def write_all(tmp_path: Path) -> tuple[Path, Path]:
    texts = valid_texts()
    paths = {
        "prd": tmp_path / "PRD.md",
        "spec": tmp_path / "SPEC.md",
        "plan": tmp_path / "PLAN.md",
        "tasks": tmp_path / "TASKS.md",
        "agents": tmp_path / "AGENTS.md",
        "readme": tmp_path / "README.md",
    }
    for key, path in paths.items():
        path.write_text(texts[key], encoding="utf-8")
    return paths["prd"], paths["tasks"]


def test_cli_json_output(tmp_path: Path, capsys) -> None:
    prd, tasks = write_all(tmp_path)
    exit_code = main([str(prd), str(tasks), "--all", "--json"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["status"] == "pass"
    assert payload["stats"]["tasks"] == 6
    assert payload["stats"]["milestones"] == 2


def test_cli_all_reports_missing_siblings(tmp_path: Path, capsys) -> None:
    prd = tmp_path / "PRD.md"
    tasks = tmp_path / "TASKS.md"
    prd.write_text(valid_texts()["prd"], encoding="utf-8")
    tasks.write_text(valid_texts()["tasks"], encoding="utf-8")
    exit_code = main([str(prd), str(tasks), "--all"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.err.count("missing-file") == 4


def test_cli_explicit_paths(tmp_path: Path, capsys) -> None:
    prd, tasks = write_all(tmp_path)
    exit_code = main(
        [
            str(prd),
            str(tasks),
            "--spec",
            str(tmp_path / "SPEC.md"),
            "--plan",
            str(tmp_path / "PLAN.md"),
            "--agents",
            str(tmp_path / "AGENTS.md"),
            "--readme",
            str(tmp_path / "README.md"),
        ]
    )
    assert exit_code == 0, capsys.readouterr().err


def test_cli_strict_fails_on_warning(tmp_path: Path, capsys) -> None:
    prd, tasks = write_all(tmp_path)
    tasks.write_text(
        valid_texts()["tasks"].replace("tags=docker-production,deployment,final-gate", "tags=docker-production,deployment"),
        encoding="utf-8",
    )
    exit_code = main([str(prd), str(tasks), "--all", "--strict"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "missing-final-gate" in captured.err


@pytest.mark.parametrize(
    ("argument", "message"),
    [
        (["--coverage", "101"], "--coverage must be between 0 and 100"),
        (["--min-questions", "-1"], "--min-questions must be zero or greater"),
        (["--min-tasks", "0"], "--min-tasks must be at least one"),
    ],
)
def test_cli_rejects_invalid_limits(argument, message, capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        main(argument)
    assert exc.value.code == 2
    assert message in capsys.readouterr().err


def test_minimum_task_and_question_counts_are_configurable() -> None:
    report = run()
    assert report.ok
    report = validate_texts(
        valid_texts()["prd"],
        valid_texts()["tasks"],
        spec_text=valid_texts()["spec"],
        plan_text=valid_texts()["plan"],
        agents_text=valid_texts()["agents"],
        readme_text=valid_texts()["readme"],
        min_tasks=10,
        min_questions=9,
    )
    assert "insufficient-tasks" in codes(report)
    assert "insufficient-interview" in codes(report)
