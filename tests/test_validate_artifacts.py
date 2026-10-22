from __future__ import annotations

import json
from textwrap import dedent

import pytest

from validate_artifacts import (
    main,
    parse_attributes,
    split_list,
    validate_files,
    validate_texts,
)


VALID_PRD = dedent(
    """\
    <!-- techlead:artifact type=prd version=1 -->
    # PRD: Example

    - Status: Approved
    - Date: 2026-01-01
    - Owner: Example team
    - Artifact language: English
    - Coverage gate: >= 80 percent

    <!-- techlead:section id=summary -->
    ## Summary

    A small service that lets operators review requests and audit decisions.

    <!-- techlead:section id=problem -->
    ## Problem

    Operators lack a reliable review queue and cannot prove who approved a request.

    <!-- techlead:section id=users -->
    ## Users

    Operations staff review requests and auditors inspect the decision history.

    <!-- techlead:section id=scope -->
    ## Scope

    ### In scope

    - Request submission, review, decision, and audit history.

    ### Out of scope

    - Billing and third-party marketplace integrations.

    <!-- techlead:section id=functional -->
    ## Functional Requirements

    - **FR-001**: The operator can approve or reject a submitted request and sees the updated decision.

    <!-- techlead:section id=nonfunctional -->
    ## Non-Functional Requirements

    - **NFR-001**: The test suite must keep line and branch coverage at or above 80 percent.
    - **NFR-002**: All decisions must be immutable and recorded in the audit log within one second.

    <!-- techlead:section id=assumptions -->
    ## Assumptions

    - The first release serves a single operations team.

    <!-- techlead:section id=architecture -->
    ## Architecture

    The service uses a web API, a relational database, and a background audit writer.

    <!-- techlead:section id=security -->
    ## Security

    - Authentication uses the organization identity provider.
    - Authorization limits decisions to the reviewer role.
    - Audit records exclude secrets and personal data.

    <!-- techlead:section id=docker -->
    ## Docker

    <!-- techlead:env id=local -->
    ### Local and test environment

    - A development image runs the API with hot reload.
    - A Compose service starts the database.
    - A dedicated test service runs the full suite.
    - A reset command removes local state safely.

    <!-- techlead:env id=production -->
    ### Production environment (VPS)

    - A multi-stage image uses a pinned base version.
    - The runtime uses a non-root user and a read-only filesystem.
    - Secrets are injected at runtime.
    - A reverse proxy terminates TLS and sets secure headers.
    - The host uses key-only SSH and a restrictive firewall.
    - Backups, restore, image scanning, deployment, and rollback are documented.

    <!-- techlead:section id=testing -->
    ## Testing

    - Coverage gate: >= 80 percent.
    - Unit tests cover validation and decision rules.
    - Integration tests use a disposable database.
    - End-to-end tests cover the review journey.
    - Coverage command: pytest --cov --cov-branch --cov-fail-under=80.

    <!-- techlead:section id=dod -->
    ## Definition of Done

    - [ ] Every task is complete and verified.
    - [ ] Every requirement is covered by a task.
    - [ ] Test coverage is at least 80 percent.
    - [ ] The local Docker environment passes the test suite.
    - [ ] The production image deploys and passes the smoke test.
    - [ ] Rollback and restore have been exercised.

    <!-- techlead:section id=risks -->
    ## Risks

    | Risk | Probability | Impact | Mitigation | Owner |
    | --- | --- | --- | --- | --- |
    | Slow review | Medium | Medium | Add queue metrics | Lead |

    <!-- techlead:section id=qa -->
    ## Interview Answers

    ### Q-001

    - Question: What problem are we solving?
    - Answer: Operators need a reliable review queue.

    ### Q-002

    - Question: Who are the primary users?
    - Answer: Operations staff and auditors.

    ### Q-003

    - Question: What must the first release include?
    - Answer: Submission, review, decision, and audit history.

    ### Q-004

    - Question: What is explicitly out of scope?
    - Answer: Billing and marketplace integrations.

    ### Q-005

    - Question: How will we measure success?
    - Answer: Every decision is recorded and review time drops below one day.

    ### Q-006

    - Question: What security controls are required?
    - Answer: Identity provider login, reviewer authorization, and audit logging.

    ### Q-007

    - Question: How will the project run locally?
    - Answer: Docker Compose with a development image and a test service.

    ### Q-008

    - Question: How will the project run in production?
    - Answer: A hardened container on a VPS behind a TLS reverse proxy.

    <!-- techlead:section id=traceability -->
    ## Traceability

    | Requirement | Summary | Delivered by |
    | --- | --- | --- |
    | FR-001 | Review decision | TASK-001, TASK-006 |
    | NFR-001 | Coverage gate | TASK-004 |
    | NFR-002 | Audit latency | TASK-003 |
    """
)


VALID_TASKS = dedent(
    """\
    <!-- techlead:artifact type=tasks version=1 -->
    # TASKS: Example

    - Source PRD: `./PRD.md`
    - Status: Approved
    - Execution order: top to bottom, respecting dependencies

    <!-- techlead:section id=rules -->
    ## Execution Rules

    - Work in task order and verify each task before continuing.

    <!-- techlead:section id=tasks -->
    ## Tasks

    <!-- techlead:task id=TASK-001 depends=none prd=FR-001 tags=foundation -->
    ### TASK-001: Create the data model

    - [ ] Status
    - Depends on: none
    - PRD: FR-001
    - Acceptance: The request and decision entities exist with the approved relationships.
    - Verify: Run the migration test and inspect the schema.
    - Files: migrations, models, and schema tests.

    <!-- techlead:task id=TASK-002 depends=TASK-001 prd=FR-001 tags=core -->
    ### TASK-002: Implement the review API

    - [ ] Status
    - Depends on: TASK-001
    - PRD: FR-001
    - Acceptance: A reviewer can approve or reject a request and observe the new decision.
    - Verify: Run the review API integration tests.
    - Files: api handlers, services, and integration tests.

    <!-- techlead:task id=TASK-003 depends=TASK-002 prd=NFR-002 tags=security -->
    ### TASK-003: Implement authorization and audit

    - [ ] Status
    - Depends on: TASK-002
    - PRD: NFR-002
    - Acceptance: Only reviewers can decide, and every decision is written to the audit log.
    - Verify: Run security tests and inspect the audit records.
    - Files: authorization rules, audit writer, and security tests.

    <!-- techlead:task id=TASK-004 depends=TASK-002 prd=NFR-001 tags=coverage-gate -->
    ### TASK-004: Reach the coverage gate

    - [ ] Status
    - Depends on: TASK-002
    - PRD: NFR-001
    - Acceptance: Unit, integration, and end-to-end tests cover primary and failure paths at or above 80 percent.
    - Verify: Run pytest --cov --cov-branch --cov-fail-under=80.
    - Files: tests, fixtures, and coverage configuration.

    <!-- techlead:task id=TASK-005 depends=TASK-003,TASK-004 prd=NFR-001 tags=docker-local,docker-production -->
    ### TASK-005: Build the Docker environments

    - [ ] Status
    - Depends on: TASK-003, TASK-004
    - PRD: NFR-001
    - Acceptance: Local Compose and the hardened production image both build and pass their checks.
    - Verify: Start the local stack, run the tests, build the production image, and scan it.
    - Files: Dockerfiles, Compose files, proxy config, and scripts.

    <!-- techlead:task id=TASK-006 depends=TASK-005 prd=FR-001,NFR-002 tags=deployment,final-gate -->
    ### TASK-006: Deploy and verify the definition of done

    - [ ] Status
    - Depends on: TASK-005
    - PRD: FR-001, NFR-002
    - Acceptance: The VPS deployment passes the smoke test, rollback works, and all evidence is recorded.
    - Verify: Deploy, run the smoke test, roll back, and review the evidence.
    - Files: deployment workflow, runbook, and release notes.

    <!-- techlead:section id=traceability -->
    ## Traceability

    | Requirement | Tasks |
    | --- | --- |
    | FR-001 | TASK-001, TASK-002, TASK-006 |
    | NFR-001 | TASK-004, TASK-005 |
    | NFR-002 | TASK-003, TASK-006 |

    <!-- techlead:section id=dod -->
    ## Definition of Done

    - [ ] Every task is checked and verified.
    - [ ] Every requirement is covered by a task.
    - [ ] Test coverage is at least 80 percent.
    - [ ] The local Docker stack passes the test suite.
    - [ ] The production image scans clean and passes the smoke test.
    - [ ] Rollback and restore have been exercised.
    """
)


def test_valid_artifacts_pass() -> None:
    report = validate_texts(VALID_PRD, VALID_TASKS)
    assert report.ok, [issue.message for issue in report.errors]
    assert report.stats["tasks"] == 6
    assert report.stats["functional_requirements"] == 1
    assert report.stats["nonfunctional_requirements"] == 2
    assert report.stats["interview_questions"] == 8
    assert report.stats["prd_coverage_gate"] == 80


def test_valid_artifacts_pass_strict() -> None:
    report = validate_texts(VALID_PRD, VALID_TASKS)
    assert not report.warnings


def test_placeholder_is_rejected() -> None:
    report = validate_texts(VALID_PRD.replace("audit decisions", "audit TODO decisions"), VALID_TASKS)
    assert any(issue.code == "placeholder" for issue in report.errors)


def test_placeholder_inside_code_fence_is_ignored() -> None:
    prd = VALID_PRD.replace(
        "A small service that lets operators review requests and audit decisions.",
        "A small service that lets operators review requests and audit decisions.\n\n```text\nTODO\n```",
    )
    report = validate_texts(prd, VALID_TASKS)
    assert report.ok, [issue.message for issue in report.errors]


def test_missing_section_is_rejected() -> None:
    prd = VALID_PRD.replace("<!-- techlead:section id=risks -->", "")
    report = validate_texts(prd, VALID_TASKS)
    assert any(issue.code == "missing-section" for issue in report.errors)


def test_missing_docker_environment_is_rejected() -> None:
    prd = VALID_PRD.replace("<!-- techlead:env id=production -->", "")
    report = validate_texts(prd, VALID_TASKS)
    assert any(issue.code == "missing-docker-environment" for issue in report.errors)


def test_low_coverage_is_rejected() -> None:
    prd = VALID_PRD.replace(
        "- Coverage gate: >= 80 percent.\n- Unit tests cover validation and decision rules.",
        "- Coverage gate: >= 70 percent.\n- Unit tests cover validation and decision rules.",
    )
    report = validate_texts(prd, VALID_TASKS)
    assert any(issue.code == "coverage-too-low" for issue in report.errors)


def test_missing_coverage_percentage_is_rejected() -> None:
    prd = VALID_PRD.replace("Coverage gate: >= 80 percent.", "Coverage gate: mandatory.", 1)
    report = validate_texts(prd, VALID_TASKS)
    assert any(issue.code == "missing-coverage-gate" for issue in report.errors)


def test_insufficient_questions_is_rejected() -> None:
    prd = VALID_PRD.split("### Q-008")[0] + VALID_PRD.split("<!-- techlead:section id=traceability -->")[1]
    report = validate_texts(prd, VALID_TASKS)
    assert any(issue.code == "insufficient-interview" for issue in report.errors)


def test_duplicate_requirement_is_rejected() -> None:
    prd = VALID_PRD.replace(
        "- **NFR-002**: All decisions must be immutable and recorded in the audit log within one second.",
        "- **NFR-002**: All decisions must be immutable and recorded in the audit log within one second.\n"
        "- **NFR-002**: Duplicate definition.",
    )
    report = validate_texts(prd, VALID_TASKS)
    assert any(issue.code == "duplicate-requirement" for issue in report.errors)


def test_missing_prd_reference_is_rejected() -> None:
    tasks = VALID_TASKS.replace("prd=FR-001 tags=foundation", "tags=foundation")
    tasks = tasks.replace("- PRD: FR-001\n", "", 1)
    report = validate_texts(VALID_PRD, tasks)
    assert any(issue.code == "missing-prd-reference" for issue in report.errors)


def test_unknown_prd_reference_is_rejected() -> None:
    tasks = VALID_TASKS.replace("prd=FR-001 tags=foundation", "prd=FR-999 tags=foundation")
    report = validate_texts(VALID_PRD, tasks)
    assert any(issue.code == "unknown-prd-reference" for issue in report.errors)


def test_uncovered_requirement_is_rejected() -> None:
    tasks = VALID_TASKS.replace("prd=NFR-002 tags=security", "prd=NFR-001 tags=security")
    tasks = tasks.replace("prd=FR-001,NFR-002 tags=deployment,final-gate", "prd=FR-001 tags=deployment,final-gate")
    report = validate_texts(VALID_PRD, tasks)
    assert any(issue.code == "uncovered-requirements" for issue in report.errors)


def test_unknown_dependency_is_rejected() -> None:
    tasks = VALID_TASKS.replace("depends=TASK-001 prd=FR-001", "depends=TASK-999 prd=FR-001")
    report = validate_texts(VALID_PRD, tasks)
    assert any(issue.code == "unknown-dependency" for issue in report.errors)


def test_duplicate_task_id_is_rejected() -> None:
    tasks = VALID_TASKS.replace("id=TASK-002", "id=TASK-001", 1)
    report = validate_texts(VALID_PRD, tasks)
    assert any(issue.code == "duplicate-task-id" for issue in report.errors)


def test_missing_mandatory_tag_is_rejected() -> None:
    tasks = VALID_TASKS.replace("tags=docker-local,docker-production", "tags=docker-local")
    report = validate_texts(VALID_PRD, tasks)
    assert any(issue.code == "missing-mandatory-tags" for issue in report.errors)


def test_missing_optional_final_gate_is_warning() -> None:
    tasks = VALID_TASKS.replace("tags=deployment,final-gate", "tags=deployment")
    report = validate_texts(VALID_PRD, tasks)
    assert report.ok
    assert any(issue.code == "missing-final-gate" for issue in report.warnings)


def test_missing_verify_field_is_rejected() -> None:
    tasks = VALID_TASKS.replace(
        "- Verify: Run the review API integration tests.\n",
        "",
    )
    report = validate_texts(VALID_PRD, tasks)
    assert any(issue.code == "missing-verify" for issue in report.errors)


def test_minimum_task_count_is_configurable() -> None:
    report = validate_texts(VALID_PRD, VALID_TASKS, min_tasks=10)
    assert any(issue.code == "insufficient-tasks" for issue in report.errors)


def test_minimum_question_count_is_configurable() -> None:
    report = validate_texts(VALID_PRD, VALID_TASKS, min_questions=9)
    assert any(issue.code == "insufficient-interview" for issue in report.errors)


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


def test_validate_files_reports_missing_files(tmp_path) -> None:
    report = validate_files(tmp_path / "missing-prd.md", tmp_path / "missing-tasks.md")
    assert len(report.errors) == 2
    assert all(issue.code == "missing-file" for issue in report.errors)


def test_cli_json_output(tmp_path, capsys) -> None:
    prd = tmp_path / "PRD.md"
    tasks = tmp_path / "TASKS.md"
    prd.write_text(VALID_PRD, encoding="utf-8")
    tasks.write_text(VALID_TASKS, encoding="utf-8")
    exit_code = main([str(prd), str(tasks), "--json"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["status"] == "pass"
    assert payload["stats"]["tasks"] == 6


def test_cli_strict_fails_on_warning(tmp_path, capsys) -> None:
    prd = tmp_path / "PRD.md"
    tasks = tmp_path / "TASKS.md"
    prd.write_text(VALID_PRD, encoding="utf-8")
    tasks.write_text(VALID_TASKS.replace("tags=deployment,final-gate", "tags=deployment"), encoding="utf-8")
    exit_code = main([str(prd), str(tasks), "--strict"])
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
