#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

from artifact_model import (
    AGENTS_SECTIONS,
    ANY_PERCENT_RE,
    CHECKBOX_RE,
    MANDATORY_LABEL_PREFIXES,
    MANDATORY_TAGS,
    MILESTONE_ID_RE,
    MIN_BULLET_LINES,
    PLAN_SECTIONS,
    PRD_SECTIONS,
    README_SECTIONS,
    SPEC_SECTIONS,
    TASK_ID_RE,
    TASK_SECTIONS,
    Issue,
    Milestone,
    Report,
    Requirement,
    Task,
    artifact_header,
    env_bodies,
    has_metadata,
    label_prefixes,
    nonempty_content_lines,
    parse_attributes,
    parse_milestones,
    parse_percentages,
    parse_questions,
    parse_requirements,
    parse_tasks,
    section_bodies,
    split_list,
    strip_comments,
    strip_fenced_code,
)


ESTIMATE_VALUES = {"XS", "S", "M", "L"}
PRD_METADATA = ("Status:", "Date:", "Owner:", "Artifact language:")
SPEC_METADATA = ("Status:", "Date:", "Owner:", "Artifact language:", "Coverage gate:")
PLAN_METADATA = ("Source PRD:", "Source SPEC:", "Status:", "Artifact language:")
TASKS_METADATA = ("Source PRD:", "Source SPEC:", "Source PLAN:", "Status:", "Execution order:")
READ_ARTIFACTS = (
    ("prd", "PRD"),
    ("spec", "SPEC"),
    ("plan", "PLAN"),
    ("tasks", "TASKS"),
    ("agents", "AGENTS"),
    ("readme", "README"),
)


def check_artifact_marker(text: str, expected_type: str, report: Report, label: str) -> None:
    header = artifact_header(text)
    if not header:
        report.error("missing-artifact-marker", f"{label}.md is missing the techlead artifact marker.", label)
        return
    if header.get("type") != expected_type:
        report.error("wrong-artifact-type", f"{label}.md artifact type must be {expected_type}.", label)
    if header.get("version") != "2":
        report.error(
            "unsupported-version",
            f"{label}.md must use artifact version=2. See the migration section in README.md.",
            label,
        )


def check_metadata(text: str, fields: Iterable[str], report: Report, label: str) -> None:
    for field in has_metadata(text, fields):
        report.error("missing-metadata", f"{label}.md is missing metadata field {field}", label)


def check_sections(text: str, required: Iterable[str], report: Report, label: str) -> dict[str, str]:
    sections = section_bodies(text)
    for section_id in required:
        if section_id not in sections:
            report.error("missing-section", f"{label}.md is missing section marker id={section_id}.", label)
            continue
        if not nonempty_content_lines(sections[section_id]):
            report.error("empty-section", f"{label}.md section {section_id} has no content.", label)
    return sections


def require_min_lines(
    sections: dict[str, str],
    section_id: str,
    minimum: int,
    report: Report,
    label: str,
) -> None:
    if section_id not in sections:
        return
    count = len(nonempty_content_lines(sections[section_id]))
    if count < minimum:
        report.error(
            "thin-section",
            f"{label}.md section {section_id} needs at least {minimum} substantive lines.",
            label,
        )


def check_scope(scope: str, report: Report, label: str) -> None:
    if not re.search(r"(?mi)^###\s+In scope\s*$", scope):
        report.error("missing-in-scope", f"{label}.md scope needs an 'In scope' subsection.", label)
    if not re.search(r"(?mi)^###\s+Out of scope\s*$", scope):
        report.error("missing-out-of-scope", f"{label}.md scope needs an 'Out of scope' subsection.", label)


def check_coverage_section(text: str, report: Report, label: str, coverage_gate: int) -> int | None:
    percentages = parse_percentages(text)
    if not percentages:
        report.error("missing-coverage-gate", f"{label}.md must state a coverage percentage.", label)
        return None
    maximum = max(percentages)
    if maximum < coverage_gate:
        report.error(
            "coverage-too-low",
            f"{label}.md coverage gate is {maximum} percent, below {coverage_gate} percent.",
            label,
        )
    return maximum


def check_dod(
    dod: str,
    report: Report,
    label: str,
    coverage_gate: int,
    require_docker: bool = True,
) -> None:
    if len(CHECKBOX_RE.findall(dod)) < MIN_BULLET_LINES["dod"]:
        report.error("thin-dod", f"{label}.md definition of done needs at least five checkboxes.", label)
    check_coverage_section(dod, report, label, coverage_gate)
    if require_docker and "docker" not in dod.lower():
        report.error("missing-dod-docker", f"{label}.md definition of done must mention Docker.", label)


def check_risks_table(risks: str, report: Report, label: str) -> None:
    if "| Risk |" not in risks or "| ---" not in risks:
        report.error("missing-risk-table", f"{label}.md risks section needs a risk table.", label)


def validate_prd(
    prd_text: str,
    report: Report,
    min_questions: int,
) -> dict[str, Requirement]:
    check_artifact_marker(prd_text, "prd", report, "PRD")
    check_metadata(prd_text, PRD_METADATA, report, "PRD")
    sections = check_sections(prd_text, PRD_SECTIONS, report, "PRD")
    for section_id, minimum in (
        ("summary", 1),
        ("problem", 2),
        ("users", 2),
        ("success", 2),
        ("constraints", 2),
        ("assumptions", 1),
        ("risks", 3),
    ):
        require_min_lines(sections, section_id, minimum, report, "PRD")
    check_scope(sections.get("scope", ""), report, "PRD")
    check_risks_table(sections.get("risks", ""), report, "PRD")

    requirements = parse_requirements(prd_text, report, "PRD")
    technical = [requirement for requirement in requirements.values() if requirement.kind == "TR"]
    if technical:
        report.error(
            "technical-requirement-in-prd",
            "PRD.md must keep technical requirements (TR-xxx) in SPEC.md.",
            "PRD",
        )
    functional = [requirement for requirement in requirements.values() if requirement.kind == "FR"]
    nonfunctional = [requirement for requirement in requirements.values() if requirement.kind == "NFR"]
    if not functional:
        report.error("missing-functional-requirement", "PRD.md needs at least one FR requirement.", "PRD")
    if not nonfunctional:
        report.error("missing-nonfunctional-requirement", "PRD.md needs at least one NFR requirement.", "PRD")

    questions = parse_questions(prd_text)
    if len(questions) < min_questions:
        report.error(
            "insufficient-interview",
            f"PRD.md has {len(questions)} answered interview questions; at least {min_questions} are required.",
            "PRD",
        )

    traceability = sections.get("traceability", "")
    for key in sorted(requirement.key for requirement in requirements.values() if requirement.kind != "TR"):
        if key not in traceability:
            report.error("traceability-gap", f"PRD.md traceability table is missing {key}.", "PRD")
    if "TR-" not in traceability:
        report.error("missing-spec-traceability", "PRD.md traceability must map requirements to SPEC TR IDs.", "PRD")
    if "SPEC" not in traceability:
        report.error("missing-spec-link", "PRD.md traceability must reference SPEC.md.", "PRD")

    dod = sections.get("dod", "")
    if len(CHECKBOX_RE.findall(dod)) < MIN_BULLET_LINES["dod"]:
        report.error("thin-dod", "PRD.md definition of done needs at least five checkboxes.", "PRD")
    if "acceptance" not in dod.lower() and "criteria" not in dod.lower():
        report.error("missing-dod-acceptance", "PRD.md definition of done must mention acceptance criteria.", "PRD")

    report.stats.update(
        {
            "functional_requirements": len(functional),
            "nonfunctional_requirements": len(nonfunctional),
            "interview_questions": len(questions),
        }
    )
    return {key: requirement for key, requirement in requirements.items() if requirement.kind in {"FR", "NFR"}}


def validate_spec(
    spec_text: str,
    prd_requirements: dict[str, Requirement],
    report: Report,
    coverage_gate: int,
) -> dict[str, Requirement]:
    check_artifact_marker(spec_text, "spec", report, "SPEC")
    check_metadata(spec_text, SPEC_METADATA, report, "SPEC")
    sections = check_sections(spec_text, SPEC_SECTIONS, report, "SPEC")
    for section_id, minimum in (
        ("context", 2),
        ("architecture", 3),
        ("components", 3),
        ("data", 3),
        ("interfaces", 3),
        ("security", MIN_BULLET_LINES["security"]),
        ("testing", MIN_BULLET_LINES["testing"]),
        ("observability", 3),
        ("decisions", 2),
        ("risks", 3),
    ):
        require_min_lines(sections, section_id, minimum, report, "SPEC")
    check_risks_table(sections.get("risks", ""), report, "SPEC")

    technical = sections.get("technical", "")
    if not re.search(r"\*\*TR-\d{3}\*\*", technical):
        report.error(
            "missing-technical-requirement",
            "SPEC.md technical section needs at least one TR-xxx requirement.",
            "SPEC",
        )
    requirements = parse_requirements(spec_text, report, "SPEC")
    product = [requirement for requirement in requirements.values() if requirement.kind in {"FR", "NFR"}]
    if product:
        report.error(
            "product-requirement-in-spec",
            "SPEC.md must keep FR/NFR requirements in PRD.md.",
            "SPEC",
        )
    technical_requirements = [requirement for requirement in requirements.values() if requirement.kind == "TR"]
    if not technical_requirements:
        report.error("missing-technical-requirement", "SPEC.md needs at least one TR requirement.", "SPEC")

    envs = env_bodies(spec_text)
    for env_id, minimum in (("local", MIN_BULLET_LINES["local"]), ("production", MIN_BULLET_LINES["production"])):
        body = envs.get(env_id, "")
        if env_id not in envs:
            report.error(
                "missing-docker-environment",
                f"SPEC.md environments section needs an environment marker id={env_id}.",
                "SPEC",
            )
        elif len(nonempty_content_lines(body)) < minimum:
            report.error(
                "thin-docker-environment",
                f"SPEC.md Docker environment {env_id} needs at least {minimum} substantive lines.",
                "SPEC",
            )
    environments = sections.get("environments", "")
    if "docker" not in environments.lower():
        report.error("docker-content", "SPEC.md environments section must mention Docker.", "SPEC")

    testing = sections.get("testing", "")
    if "coverage" not in testing.lower() and "cobertura" not in testing.lower():
        report.error("missing-coverage", "SPEC.md testing strategy must mention coverage.", "SPEC")
    spec_gate = check_coverage_section(testing, report, "SPEC", coverage_gate)
    check_dod(sections.get("dod", ""), report, "SPEC", coverage_gate)

    traceability = sections.get("traceability", "")
    for key in sorted(prd_requirements):
        if key not in traceability:
            report.error("traceability-gap", f"SPEC.md traceability table is missing {key}.", "SPEC")
    for key in sorted(requirement.key for requirement in technical_requirements):
        if key not in traceability:
            report.error("traceability-gap", f"SPEC.md traceability table is missing {key}.", "SPEC")
    if "PRD" not in traceability:
        report.error("missing-prd-link", "SPEC.md traceability must reference PRD.md.", "SPEC")

    report.stats.update(
        {
            "technical_requirements": len(technical_requirements),
            "spec_coverage_gate": spec_gate,
        }
    )
    return {key: requirement for key, requirement in requirements.items() if requirement.kind == "TR"}


def validate_plan(
    plan_text: str,
    requirements: dict[str, Requirement],
    report: Report,
    coverage_gate: int,
) -> list[Milestone]:
    check_artifact_marker(plan_text, "plan", report, "PLAN")
    check_metadata(plan_text, PLAN_METADATA, report, "PLAN")
    sections = check_sections(plan_text, PLAN_SECTIONS, report, "PLAN")
    for section_id, minimum in (
        ("strategy", 5),
        ("milestones", 3),
        ("dependencies", 2),
        ("risks", 3),
    ):
        require_min_lines(sections, section_id, minimum, report, "PLAN")
    check_risks_table(sections.get("risks", ""), report, "PLAN")

    strategy = sections.get("strategy", "").lower()
    for token in ("launch", "rollback", "metric"):
        if token not in strategy:
            report.error(
                "incomplete-strategy",
                f"PLAN.md launch strategy must address {token}.",
                "PLAN",
            )

    milestones = parse_milestones(plan_text)
    if not milestones:
        report.error("missing-milestone", "PLAN.md needs at least one milestone marker.", "PLAN")
    if len(milestones) < 2:
        report.warning("single-milestone", "PLAN.md should define more than one milestone.", "PLAN")

    seen_ids: set[str] = set()
    previous_order = 0
    covered: set[str] = set()
    for milestone in milestones:
        location = milestone.milestone_id or "PLAN"
        if not milestone.milestone_id:
            report.error("missing-milestone-id", "A milestone marker is missing its id.", "PLAN")
            continue
        if not MILESTONE_ID_RE.match(milestone.milestone_id):
            report.error("invalid-milestone-id", f"Milestone ID {milestone.milestone_id} must match M1, M2, ...", location)
            continue
        if milestone.milestone_id in seen_ids:
            report.error("duplicate-milestone-id", f"Milestone ID {milestone.milestone_id} is duplicated.", location)
        seen_ids.add(milestone.milestone_id)
        if milestone.order <= previous_order:
            report.error("milestone-order", f"Milestone {milestone.milestone_id} is not in increasing order.", location)
        previous_order = milestone.order
        if not milestone.title:
            report.error("missing-milestone-title", f"Milestone {milestone.milestone_id} needs a title.", location)
        for field_name, minimum in (
            ("goal", 10),
            ("scope", 10),
            ("exit", 10),
            ("launch", 3),
            ("target", 3),
            ("evidence", 6),
        ):
            if len(milestone.fields.get(field_name, "")) < minimum:
                report.error(
                    f"missing-milestone-{field_name}",
                    f"Milestone {milestone.milestone_id} needs a substantive {field_name} field.",
                    location,
                )
        if not milestone.requirements:
            report.error("missing-milestone-requirements", f"Milestone {milestone.milestone_id} needs requirements.", location)
        for requirement in milestone.requirements:
            if requirements and requirement not in requirements:
                report.error(
                    "unknown-milestone-requirement",
                    f"Milestone {milestone.milestone_id} references unknown requirement {requirement}.",
                    location,
                )
            else:
                covered.add(requirement)
        for dependency in milestone.depends:
            if dependency == milestone.milestone_id:
                report.error("self-milestone-dependency", f"Milestone {milestone.milestone_id} depends on itself.", location)
            elif dependency not in seen_ids:
                report.error(
                    "unknown-milestone-dependency",
                    f"Milestone {milestone.milestone_id} depends on unknown or later milestone {dependency}.",
                    location,
                )

    uncovered = sorted(set(requirements) - covered)
    if uncovered:
        report.error(
            "uncovered-requirements",
            f"Requirements without a milestone: {', '.join(uncovered)}.",
            "PLAN",
        )

    traceability = sections.get("traceability", "")
    for key in sorted(requirements):
        if key not in traceability:
            report.error("traceability-gap", f"PLAN.md traceability table is missing {key}.", "PLAN")
    if requirements and "M" not in traceability:
        report.error("traceability-milestones", "PLAN.md traceability must map requirements to milestones.", "PLAN")
    check_dod(sections.get("dod", ""), report, "PLAN", coverage_gate, require_docker=True)

    report.stats["milestones"] = len(milestones)
    return milestones


def validate_tasks(
    tasks_text: str,
    requirements: dict[str, Requirement],
    milestones: list[Milestone],
    report: Report,
    min_tasks: int,
    coverage_gate: int,
    spec_validated: bool,
) -> None:
    check_artifact_marker(tasks_text, "tasks", report, "TASKS")
    check_metadata(tasks_text, TASKS_METADATA, report, "TASKS")
    sections = check_sections(tasks_text, TASK_SECTIONS, report, "TASKS")

    issue_format = sections.get("issue-format", "").lower()
    for token in ("gh", "glab", "label", "milestone", "issue title", "estimate", "export_issues.py"):
        if token not in issue_format:
            report.error(
                "incomplete-issue-format",
                f"TASKS.md issue-format section must document {token}.",
                "TASKS",
            )

    tasks = parse_tasks(tasks_text)
    if len(tasks) < min_tasks:
        report.error(
            "insufficient-tasks",
            f"TASKS.md has {len(tasks)} tasks; at least {min_tasks} are required.",
            "TASKS",
        )

    seen_ids: set[str] = set()
    seen_titles: set[str] = set()
    previous_number = 0
    all_tags: set[str] = set()
    covered_requirements: set[str] = set()
    used_milestones: set[str] = set()

    for task in tasks:
        location = task.task_id or "TASKS"
        if not task.task_id:
            report.error("missing-task-id", "A task marker is missing its id.", "TASKS")
            continue
        match = TASK_ID_RE.match(task.task_id)
        if not match:
            report.error("invalid-task-id", f"Task ID {task.task_id} must match TASK-NNN.", location)
            continue
        number = int(match.group(1))
        if task.task_id in seen_ids:
            report.error("duplicate-task-id", f"Task ID {task.task_id} is duplicated.", location)
        seen_ids.add(task.task_id)
        if number <= previous_number:
            report.error("task-order", f"Task {task.task_id} is not in increasing order.", location)
        elif number != previous_number + 1:
            report.warning("task-gap", f"Task IDs jump from {previous_number:03d} to {number:03d}.", location)
        previous_number = number

        if not task.title:
            report.error("missing-task-title", f"Task {task.task_id} needs a title.", location)
        if not task.has_checkbox:
            report.error("missing-checkbox", f"Task {task.task_id} needs a status checkbox.", location)

        if not task.depends:
            depends_field = task.fields.get("depends", "").strip().lower()
            if depends_field not in {"none", "n/a", "na", "-"}:
                report.error(
                    "missing-dependencies",
                    f"Task {task.task_id} must declare dependencies or 'none'.",
                    location,
                )
        for dependency in task.depends:
            if dependency == task.task_id:
                report.error("self-dependency", f"Task {task.task_id} depends on itself.", location)
            elif dependency not in seen_ids:
                report.error(
                    "unknown-dependency",
                    f"Task {task.task_id} depends on unknown or later task {dependency}.",
                    location,
                )

        if not task.prd_refs:
            report.error("missing-prd-reference", f"Task {task.task_id} needs at least one PRD reference.", location)
        for reference in task.prd_refs:
            if reference not in requirements:
                report.error(
                    "unknown-prd-reference",
                    f"Task {task.task_id} references unknown requirement {reference}.",
                    location,
                )
            else:
                covered_requirements.add(reference)

        if not task.spec_refs:
            report.error("missing-spec-reference", f"Task {task.task_id} needs at least one SPEC reference.", location)
        for reference in task.spec_refs:
            if spec_validated and reference not in requirements:
                report.error(
                    "unknown-spec-reference",
                    f"Task {task.task_id} references unknown technical requirement {reference}.",
                    location,
                )
            elif reference in requirements:
                covered_requirements.add(reference)

        if not task.milestone:
            report.error("missing-task-milestone", f"Task {task.task_id} needs a milestone.", location)
        else:
            used_milestones.add(task.milestone)
            if milestones and task.milestone not in {milestone.milestone_id for milestone in milestones}:
                report.error(
                    "unknown-task-milestone",
                    f"Task {task.task_id} references unknown milestone {task.milestone}.",
                    location,
                )

        if len(task.labels) < 3:
            report.error("missing-labels", f"Task {task.task_id} needs at least type, area, and priority labels.", location)
        prefixes = label_prefixes(task.labels)
        for prefix in MANDATORY_LABEL_PREFIXES:
            if prefix not in prefixes:
                report.error(
                    "missing-label-prefix",
                    f"Task {task.task_id} labels need a {prefix}* label.",
                    location,
                )

        estimate = task.fields.get("estimate", "").strip()
        if not estimate:
            report.error("missing-estimate", f"Task {task.task_id} needs an estimate.", location)
        elif estimate.upper() not in ESTIMATE_VALUES and not re.match(r"^[1-8]\b", estimate):
            report.error(
                "invalid-estimate",
                f"Task {task.task_id} estimate must be XS, S, M, L, or 1-8 points.",
                location,
            )

        issue_title = task.fields.get("issue_title", "").strip()
        if len(issue_title) < 8:
            report.error("missing-issue-title", f"Task {task.task_id} needs a substantive issue title.", location)
        elif len(issue_title) > 72:
            report.error("long-issue-title", f"Task {task.task_id} issue title exceeds 72 characters.", location)
        elif issue_title.lower() in seen_titles:
            report.error("duplicate-issue-title", f"Task {task.task_id} issue title is duplicated.", location)
        seen_titles.add(issue_title.lower())

        for field_name in ("acceptance", "verify", "files"):
            if len(task.fields.get(field_name, "")) < 6:
                report.error(
                    f"missing-{field_name}",
                    f"Task {task.task_id} needs a substantive {field_name} field.",
                    location,
                )
        files = split_list(task.fields.get("files", ""))
        if len(files) > 5:
            report.error(
                "task-too-large",
                f"Task {task.task_id} touches {len(files)} files; split it to five or fewer.",
                location,
            )

        for tag in task.tags:
            all_tags.add(tag)

    missing_tags = [tag for tag in MANDATORY_TAGS if tag not in all_tags]
    if missing_tags:
        report.error(
            "missing-mandatory-tags",
            f"TASKS.md is missing mandatory task tags: {', '.join(missing_tags)}.",
            "TASKS",
        )
    if "final-gate" not in all_tags:
        report.warning("missing-final-gate", "TASKS.md has no task tagged final-gate.", "TASKS")

    uncovered = sorted(set(requirements) - covered_requirements)
    if uncovered:
        report.error(
            "uncovered-requirements",
            f"Requirements without a task: {', '.join(uncovered)}.",
            "TASKS",
        )

    if milestones:
        for milestone in milestones:
            if milestone.milestone_id not in used_milestones:
                report.error(
                    "milestone-without-task",
                    f"Milestone {milestone.milestone_id} has no task.",
                    "TASKS",
                )

    traceability = sections.get("traceability", "")
    for key in sorted(requirements):
        if key not in traceability:
            report.error("traceability-gap", f"TASKS.md traceability table is missing {key}.", "TASKS")
    for milestone in milestones:
        if milestone.milestone_id not in traceability:
            report.error(
                "traceability-milestone",
                f"TASKS.md traceability table is missing {milestone.milestone_id}.",
                "TASKS",
            )
    if requirements and "TASK-" not in traceability:
        report.error("traceability-tasks", "TASKS.md traceability table must map requirements to task IDs.", "TASKS")
    check_dod(sections.get("dod", ""), report, "TASKS", coverage_gate)

    report.stats.update(
        {
            "tasks": len(tasks),
            "covered_requirements": len(covered_requirements),
            "task_tags": sorted(all_tags),
        }
    )


def validate_agents(agents_text: str, report: Report) -> None:
    check_artifact_marker(agents_text, "agents", report, "AGENTS")
    sections = check_sections(agents_text, AGENTS_SECTIONS, report, "AGENTS")
    for section_id, minimum in (
        ("overview", 2),
        ("stack", 2),
        ("layout", 3),
        ("commands", 5),
        ("conventions", 3),
        ("rules", 3),
        ("decisions", 2),
        ("dod", 3),
        ("security", 3),
    ):
        require_min_lines(sections, section_id, minimum, report, "AGENTS")
    for document in ("PRD.md", "SPEC.md", "PLAN.md", "TASKS.md"):
        if document not in agents_text:
            report.error("missing-document-link", f"AGENTS.md must reference {document}.", "AGENTS")
    lowered = agents_text.lower()
    for token in ("docker", "80", "test", "secret"):
        if token not in lowered:
            report.error("missing-agents-content", f"AGENTS.md must mention {token}.", "AGENTS")


def validate_readme(readme_text: str, report: Report) -> None:
    check_artifact_marker(readme_text, "readme", report, "README")
    sections = check_sections(readme_text, README_SECTIONS, report, "README")
    for section_id, minimum in (
        ("overview", 2),
        ("status", 1),
        ("quickstart", 4),
        ("commands", 5),
        ("architecture", 2),
        ("docs", 5),
        ("testing", 3),
        ("deployment", 3),
        ("security", 2),
    ):
        require_min_lines(sections, section_id, minimum, report, "README")
    for document in ("PRD.md", "SPEC.md", "PLAN.md", "TASKS.md", "AGENTS.md"):
        if document not in readme_text:
            report.error("missing-document-link", f"README.md must reference {document}.", "README")
    lowered = readme_text.lower()
    for token in ("docker", "coverage", "80"):
        if token not in lowered:
            report.error("missing-readme-content", f"README.md must mention {token}.", "README")


def check_placeholders(text: str, name: str, report: Report) -> None:
    cleaned = strip_fenced_code(strip_comments(text))
    for match in re.finditer(
        r"\b(?:TODO|TBD|FIXME)\b|\[insert\b|<insert\b|\[placeholder\b|<placeholder\b",
        cleaned,
        re.IGNORECASE,
    ):
        line = cleaned.count("\n", 0, match.start()) + 1
        report.error(
            "placeholder",
            f"{name} contains unresolved placeholder {match.group(0)!r}.",
            f"{name}:{line}",
        )


def validate_texts(
    prd_text: str,
    tasks_text: str,
    spec_text: str | None = None,
    plan_text: str | None = None,
    agents_text: str | None = None,
    readme_text: str | None = None,
    min_questions: int = 8,
    min_tasks: int = 6,
    coverage_gate: int = 80,
) -> Report:
    report = Report()
    prd_requirements = validate_prd(prd_text, report, min_questions)
    spec_requirements: dict[str, Requirement] = {}
    if spec_text is not None:
        spec_requirements = validate_spec(spec_text, prd_requirements, report, coverage_gate)
    requirements = {**prd_requirements, **spec_requirements}
    milestones: list[Milestone] = []
    if plan_text is not None:
        milestones = validate_plan(plan_text, requirements, report, coverage_gate)
    validate_tasks(
        tasks_text,
        requirements,
        milestones,
        report,
        min_tasks,
        coverage_gate,
        spec_validated=spec_text is not None,
    )
    if agents_text is not None:
        validate_agents(agents_text, report)
    if readme_text is not None:
        validate_readme(readme_text, report)
    check_placeholders(prd_text, "PRD.md", report)
    check_placeholders(tasks_text, "TASKS.md", report)
    if spec_text is not None:
        check_placeholders(spec_text, "SPEC.md", report)
    if plan_text is not None:
        check_placeholders(plan_text, "PLAN.md", report)
    if agents_text is not None:
        check_placeholders(agents_text, "AGENTS.md", report)
    if readme_text is not None:
        check_placeholders(readme_text, "README.md", report)
    report.stats["coverage_gate"] = coverage_gate
    report.stats["requirements"] = len(requirements)
    return report


def read_artifact(path: Path | None, report: Report, required: bool) -> str | None:
    if path is None:
        if required:
            report.error("missing-file", "A required artifact path was not provided.", "")
        return None
    if not path.is_file():
        report.error("missing-file", f"Artifact file not found: {path}", str(path))
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        report.error("unreadable-file", f"Cannot read {path}: {error}.", str(path))
        return None


def validate_files(
    prd_path: Path,
    tasks_path: Path,
    spec_path: Path | None = None,
    plan_path: Path | None = None,
    agents_path: Path | None = None,
    readme_path: Path | None = None,
    min_questions: int = 8,
    min_tasks: int = 6,
    coverage_gate: int = 80,
    require_all: bool = False,
) -> Report:
    report = Report()
    texts: dict[str, str] = {}
    paths = {
        "prd": prd_path,
        "spec": spec_path,
        "plan": plan_path,
        "tasks": tasks_path,
        "agents": agents_path,
        "readme": readme_path,
    }
    required = {key for key, _ in READ_ARTIFACTS} if require_all else {"prd", "tasks"}
    for key, _ in READ_ARTIFACTS:
        text = read_artifact(paths[key], report, key in required)
        if text is not None:
            texts[key] = text
    if report.errors:
        return report
    result = validate_texts(
        texts["prd"],
        texts["tasks"],
        spec_text=texts.get("spec"),
        plan_text=texts.get("plan"),
        agents_text=texts.get("agents"),
        readme_text=texts.get("readme"),
        min_questions=min_questions,
        min_tasks=min_tasks,
        coverage_gate=coverage_gate,
    )
    for key, path in paths.items():
        if path is not None:
            result.stats[f"{key}_file"] = str(path)
    return result


def format_issue(issue: Issue) -> str:
    location = f" ({issue.location})" if issue.location else ""
    return f"[{issue.level.upper()}] {issue.code}: {issue.message}{location}"


def print_report(report: Report, as_json: bool) -> None:
    if as_json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        return
    for issue in report.errors:
        print(format_issue(issue), file=sys.stderr)
    for issue in report.warnings:
        print(format_issue(issue), file=sys.stderr)
    status = "PASS" if report.ok else "FAIL"
    stats = report.stats
    print(
        f"{status}: {stats.get('tasks', 0)} tasks, "
        f"{stats.get('milestones', 0)} milestones, "
        f"{stats.get('functional_requirements', 0)} functional requirements, "
        f"{stats.get('nonfunctional_requirements', 0)} non-functional requirements, "
        f"{stats.get('technical_requirements', 0)} technical requirements, "
        f"{stats.get('interview_questions', 0)} interview answers, "
        f"coverage gate {stats.get('coverage_gate', 'unknown')} percent."
    )
    print(f"Errors: {len(report.errors)}. Warnings: {len(report.warnings)}.")


def default_requirement_paths(prd_path: Path) -> dict[str, Path]:
    root = prd_path.parent
    return {
        "spec": root / "SPEC.md",
        "plan": root / "PLAN.md",
        "agents": root / "AGENTS.md",
        "readme": root / "README.md",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate TechLead v2 planning artifacts.",
    )
    parser.add_argument("prd", nargs="?", default="PRD.md", help="Path to PRD.md")
    parser.add_argument("tasks", nargs="?", default="TASKS.md", help="Path to TASKS.md")
    parser.add_argument("--spec", help="Path to SPEC.md")
    parser.add_argument("--plan", help="Path to PLAN.md")
    parser.add_argument("--agents", help="Path to AGENTS.md")
    parser.add_argument("--readme", help="Path to README.md")
    parser.add_argument("--all", action="store_true", help="Require and validate every artifact")
    parser.add_argument("--min-questions", type=int, default=8, help="Minimum answered interview questions")
    parser.add_argument("--min-tasks", type=int, default=6, help="Minimum number of tasks")
    parser.add_argument("--coverage", type=int, default=80, help="Minimum coverage percentage")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    parser.add_argument("--json", action="store_true", help="Emit a JSON report")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.coverage < 0 or args.coverage > 100:
        parser.error("--coverage must be between 0 and 100")
    if args.min_questions < 0:
        parser.error("--min-questions must be zero or greater")
    if args.min_tasks < 1:
        parser.error("--min-tasks must be at least one")
    prd_path = Path(args.prd)
    defaults = default_requirement_paths(prd_path) if args.all else {}
    spec_path = Path(args.spec) if args.spec else defaults.get("spec")
    plan_path = Path(args.plan) if args.plan else defaults.get("plan")
    agents_path = Path(args.agents) if args.agents else defaults.get("agents")
    readme_path = Path(args.readme) if args.readme else defaults.get("readme")
    report = validate_files(
        prd_path,
        Path(args.tasks),
        spec_path=spec_path,
        plan_path=plan_path,
        agents_path=agents_path,
        readme_path=readme_path,
        min_questions=args.min_questions,
        min_tasks=args.min_tasks,
        coverage_gate=args.coverage,
        require_all=args.all,
    )
    print_report(report, args.json)
    if report.errors:
        return 1
    if args.strict and report.warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
