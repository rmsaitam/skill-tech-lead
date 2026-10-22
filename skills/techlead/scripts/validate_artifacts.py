#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


ARTIFACT_MARKER_RE = re.compile(r"<!--\s*techlead:artifact\s+([^>]*?)-->")
SECTION_MARKER_RE = re.compile(r"<!--\s*techlead:section\s+([^>]*?)-->")
ENV_MARKER_RE = re.compile(r"<!--\s*techlead:env\s+([^>]*?)-->")
TASK_MARKER_RE = re.compile(r"<!--\s*techlead:task\s+([^>]*?)-->")
ATTRIBUTE_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_-]*)=(\"[^\"]*\"|'[^']*'|[^\s]+)")
REQUIREMENT_RE = re.compile(
    r"(?m)^\s*[-*]\s*\*\*(FR|NFR)-(\d{3})\*\*\s*[:.\-]?\s*(.+?)\s*$"
)
REQUIREMENT_TABLE_RE = re.compile(r"(?m)^\s*\|\s*(FR|NFR)-(\d{3})\s*\|")
QUESTION_RE = re.compile(r"(?m)^###\s+Q-(\d{3})\s*$")
TASK_ID_RE = re.compile(r"^TASK-(\d{3})$")
COVERAGE_RE = re.compile(
    r"(?:>=|≥|at\s+least|minimum|min\.?)\s*(\d{1,3})\s*(?:%|percent\b|per\s+cent\b)",
    re.IGNORECASE,
)
ANY_PERCENT_RE = re.compile(r"(\d{1,3})\s*(?:%|percent\b|per\s+cent\b)", re.IGNORECASE)
CHECKBOX_RE = re.compile(r"(?m)^\s*-\s*\[[ xX]\]")
PLACEHOLDER_RE = re.compile(
    r"\b(?:TODO|TBD|FIXME)\b|\[insert\b|<insert\b|\[placeholder\b|<placeholder\b",
    re.IGNORECASE,
)
FIELD_PATTERNS = {
    "depends": re.compile(r"(?mi)^\s*-\s*Depends on:\s*(.+?)\s*$"),
    "prd": re.compile(r"(?mi)^\s*-\s*PRD:\s*(.+?)\s*$"),
    "acceptance": re.compile(r"(?mi)^\s*-\s*Acceptance:\s*(.+?)\s*$"),
    "verify": re.compile(r"(?mi)^\s*-\s*Verify:\s*(.+?)\s*$"),
    "files": re.compile(r"(?mi)^\s*-\s*Files:\s*(.+?)\s*$"),
}
TITLE_RE = re.compile(r"(?m)^#{2,4}\s+(.+?)\s*$")

PRD_REQUIRED_SECTIONS = (
    "summary",
    "problem",
    "users",
    "scope",
    "functional",
    "nonfunctional",
    "assumptions",
    "architecture",
    "security",
    "docker",
    "testing",
    "dod",
    "risks",
    "qa",
    "traceability",
)
TASKS_REQUIRED_SECTIONS = ("rules", "tasks", "traceability", "dod")
MANDATORY_TAGS = ("docker-local", "docker-production", "coverage-gate", "security", "deployment")
OPTIONAL_TAGS = ("final-gate",)
MIN_BULLET_LINES = {
    "local": 4,
    "production": 6,
    "security": 3,
    "testing": 4,
    "dod": 5,
}


@dataclass
class Issue:
    level: str
    code: str
    message: str
    location: str = ""


@dataclass
class Report:
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)
    stats: dict[str, object] = field(default_factory=dict)

    def error(self, code: str, message: str, location: str = "") -> None:
        self.errors.append(Issue("error", code, message, location))

    def warning(self, code: str, message: str, location: str = "") -> None:
        self.warnings.append(Issue("warning", code, message, location))

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "pass" if self.ok else "fail",
            "stats": self.stats,
            "errors": [issue.__dict__ for issue in self.errors],
            "warnings": [issue.__dict__ for issue in self.warnings],
        }


@dataclass
class Requirement:
    key: str
    kind: str
    number: int
    description: str


@dataclass
class Task:
    task_id: str
    attributes: dict[str, str]
    body: str
    title: str
    depends: list[str]
    prd_refs: list[str]
    tags: list[str]
    fields: dict[str, str]
    has_checkbox: bool


def parse_attributes(raw: str) -> dict[str, str]:
    attributes: dict[str, str] = {}
    for match in ATTRIBUTE_RE.finditer(raw):
        key = match.group(1).lower()
        value = match.group(2)
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        attributes[key] = value.strip()
    return attributes


def split_list(value: str) -> list[str]:
    normalized = value.strip()
    if not normalized or normalized.lower() in {"none", "n/a", "na", "-"}:
        return []
    return [item.strip() for item in normalized.split(",") if item.strip()]


def strip_fenced_code(text: str) -> str:
    return re.sub(r"(?ms)^```.*?^```\s*$", "", text)


def strip_comments(text: str) -> str:
    return re.sub(r"(?s)<!--.*?-->", "", text)


def marker_positions(text: str, pattern: re.Pattern[str]) -> list[tuple[int, int, dict[str, str]]]:
    matches: list[tuple[int, int, dict[str, str]]] = []
    for match in pattern.finditer(text):
        matches.append((match.start(), match.end(), parse_attributes(match.group(1))))
    return matches


def section_bodies(text: str) -> dict[str, str]:
    markers = marker_positions(text, SECTION_MARKER_RE)
    bodies: dict[str, str] = {}
    for index, (_, end, attributes) in enumerate(markers):
        section_id = attributes.get("id", "")
        next_start = markers[index + 1][0] if index + 1 < len(markers) else len(text)
        bodies[section_id] = text[end:next_start]
    return bodies


def env_bodies(text: str) -> dict[str, str]:
    markers = marker_positions(text, ENV_MARKER_RE)
    sections = marker_positions(text, SECTION_MARKER_RE)
    boundaries = sorted([position for position, _, _ in markers + sections])
    bodies: dict[str, str] = {}
    for _, end, attributes in markers:
        next_start = next((position for position in boundaries if position >= end), len(text))
        env_id = attributes.get("id", "")
        bodies[env_id] = text[end:next_start]
    return bodies


def nonempty_content_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if re.fullmatch(r"<!--.*?-->", line):
            continue
        if line.startswith("#"):
            continue
        lines.append(line)
    return lines


def parse_percentages(text: str) -> list[int]:
    values = [int(value) for value in COVERAGE_RE.findall(text)]
    if values:
        return values
    return [int(value) for value in ANY_PERCENT_RE.findall(text)]


def parse_requirements(prd_text: str, report: Report) -> dict[str, Requirement]:
    requirements: dict[str, Requirement] = {}
    duplicates: set[str] = set()
    for match in REQUIREMENT_RE.finditer(prd_text):
        kind, number, description = match.groups()
        key = f"{kind}-{number}"
        if key in requirements:
            duplicates.add(key)
            continue
        requirements[key] = Requirement(key, kind, int(number), description.strip())
    for match in REQUIREMENT_TABLE_RE.finditer(prd_text):
        kind, number = match.groups()
        key = f"{kind}-{number}"
        requirements.setdefault(key, Requirement(key, kind, int(number), ""))
    for key in sorted(duplicates):
        report.error("duplicate-requirement", f"Requirement {key} is defined more than once.", "PRD")
    for requirement in requirements.values():
        if len(requirement.description) < 10:
            report.error(
                "weak-requirement",
                f"Requirement {requirement.key} needs a testable description.",
                "PRD",
            )
    return requirements


def parse_questions(prd_text: str) -> list[tuple[str, str]]:
    matches = list(QUESTION_RE.finditer(prd_text))
    questions: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(prd_text)
        block = prd_text[start:end]
        question_match = re.search(r"(?mi)^\s*-\s*Question:\s*(.+?)\s*$", block)
        answer_match = re.search(r"(?mi)^\s*-\s*Answer:\s*(.+?)\s*$", block)
        question = question_match.group(1).strip() if question_match else ""
        answer = answer_match.group(1).strip() if answer_match else ""
        if question and answer:
            questions.append((question, answer))
    return questions


def parse_tasks(tasks_text: str) -> list[Task]:
    markers = marker_positions(tasks_text, TASK_MARKER_RE)
    tasks: list[Task] = []
    for index, (_, end, attributes) in enumerate(markers):
        next_start = markers[index + 1][0] if index + 1 < len(markers) else len(tasks_text)
        section_match = SECTION_MARKER_RE.search(tasks_text, end, next_start)
        if section_match:
            next_start = section_match.start()
        body = tasks_text[end:next_start]
        title_match = TITLE_RE.search(body)
        title = title_match.group(1).strip() if title_match else ""
        fields: dict[str, str] = {}
        for name, pattern in FIELD_PATTERNS.items():
            match = pattern.search(body)
            fields[name] = match.group(1).strip() if match else ""
        tasks.append(
            Task(
                task_id=attributes.get("id", ""),
                attributes=attributes,
                body=body,
                title=title,
                depends=split_list(attributes.get("depends", "") or fields["depends"]),
                prd_refs=split_list(attributes.get("prd", "") or fields["prd"]),
                tags=split_list(attributes.get("tags", "")),
                fields=fields,
                has_checkbox=bool(CHECKBOX_RE.search(body)),
            )
        )
    return tasks


def validate_prd(prd_text: str, report: Report, min_questions: int, coverage_gate: int) -> dict[str, Requirement]:
    artifact = ARTIFACT_MARKER_RE.search(prd_text)
    if not artifact:
        report.error("missing-artifact-marker", "PRD.md is missing the techlead artifact marker.", "PRD")
    else:
        attributes = parse_attributes(artifact.group(1))
        if attributes.get("type") != "prd":
            report.error("wrong-artifact-type", "PRD.md artifact type must be prd.", "PRD")
        if attributes.get("version") != "1":
            report.warning("artifact-version", "PRD.md uses an unknown artifact version.", "PRD")

    for required in ("Status:", "Date:", "Owner:", "Artifact language:", "Coverage gate:"):
        if required not in prd_text:
            report.error("missing-metadata", f"PRD.md is missing metadata field {required}", "PRD")

    sections = section_bodies(prd_text)
    for section_id in PRD_REQUIRED_SECTIONS:
        if section_id not in sections:
            report.error(
                "missing-section",
                f"PRD.md is missing section marker id={section_id}.",
                "PRD",
            )
            continue
        if not nonempty_content_lines(sections[section_id]):
            report.error(
                "empty-section",
                f"PRD.md section {section_id} has no content.",
                "PRD",
            )

    requirements = parse_requirements(prd_text, report)
    functional = [requirement for requirement in requirements.values() if requirement.kind == "FR"]
    nonfunctional = [requirement for requirement in requirements.values() if requirement.kind == "NFR"]
    if not functional:
        report.error("missing-functional-requirement", "PRD.md needs at least one FR requirement.", "PRD")
    if not nonfunctional:
        report.error("missing-nonfunctional-requirement", "PRD.md needs at least one NFR requirement.", "PRD")

    scope = sections.get("scope", "")
    if not re.search(r"(?mi)^###\s+In scope\s*$", scope):
        report.error("missing-in-scope", "PRD.md scope needs an 'In scope' subsection.", "PRD")
    if not re.search(r"(?mi)^###\s+Out of scope\s*$", scope):
        report.error("missing-out-of-scope", "PRD.md scope needs an 'Out of scope' subsection.", "PRD")

    envs = env_bodies(prd_text)
    for env_id, minimum in (("local", MIN_BULLET_LINES["local"]), ("production", MIN_BULLET_LINES["production"])):
        body = envs.get(env_id, "")
        if env_id not in envs:
            report.error(
                "missing-docker-environment",
                f"PRD.md Docker section needs an environment marker id={env_id}.",
                "PRD",
            )
        elif len(nonempty_content_lines(body)) < minimum:
            report.error(
                "thin-docker-environment",
                f"PRD.md Docker environment {env_id} needs at least {minimum} substantive lines.",
                "PRD",
            )

    docker_text = sections.get("docker", "")
    if "docker" not in docker_text.lower():
        report.error("docker-content", "PRD.md Docker section must mention Docker.", "PRD")

    security = sections.get("security", "")
    if len(nonempty_content_lines(security)) < MIN_BULLET_LINES["security"]:
        report.error(
            "thin-security",
            "PRD.md security section needs at least three substantive controls.",
            "PRD",
        )

    testing = sections.get("testing", "")
    if len(nonempty_content_lines(testing)) < MIN_BULLET_LINES["testing"]:
        report.error(
            "thin-testing",
            "PRD.md testing strategy needs at least four substantive lines.",
            "PRD",
        )
    if not re.search(r"coverage|cobbertura|cobertura", testing, re.IGNORECASE):
        report.error("missing-coverage", "PRD.md testing strategy must mention coverage.", "PRD")
    testing_percentages = parse_percentages(testing)
    if not testing_percentages:
        report.error("missing-coverage-gate", "PRD.md testing strategy must state a coverage percentage.", "PRD")
    elif max(testing_percentages) < coverage_gate:
        report.error(
            "coverage-too-low",
            f"PRD.md coverage gate is {max(testing_percentages)} percent, below {coverage_gate} percent.",
            "PRD",
        )

    dod = sections.get("dod", "")
    if len(CHECKBOX_RE.findall(dod)) < MIN_BULLET_LINES["dod"]:
        report.error("thin-dod", "PRD.md definition of done needs at least five checkboxes.", "PRD")
    dod_percentages = parse_percentages(dod)
    if not dod_percentages:
        report.error("missing-dod-coverage", "PRD.md definition of done must state the coverage gate.", "PRD")
    elif max(dod_percentages) < coverage_gate:
        report.error(
            "dod-coverage-too-low",
            f"PRD.md definition of done coverage is {max(dod_percentages)} percent, below {coverage_gate} percent.",
            "PRD",
        )
    if "docker" not in dod.lower():
        report.error("missing-dod-docker", "PRD.md definition of done must mention Docker.", "PRD")

    questions = parse_questions(prd_text)
    if len(questions) < min_questions:
        report.error(
            "insufficient-interview",
            f"PRD.md has {len(questions)} answered interview questions; at least {min_questions} are required.",
            "PRD",
        )

    traceability = sections.get("traceability", "")
    if requirements and not any(key in traceability for key in requirements):
        report.error(
            "empty-traceability",
            "PRD.md traceability section must reference requirement IDs.",
            "PRD",
        )
    if "TASK-" not in traceability:
        report.error(
            "missing-task-traceability",
            "PRD.md traceability section must map requirements to tasks.",
            "PRD",
        )

    report.stats.update(
        {
            "functional_requirements": len(functional),
            "nonfunctional_requirements": len(nonfunctional),
            "interview_questions": len(questions),
            "prd_coverage_gate": max(testing_percentages) if testing_percentages else None,
        }
    )
    return requirements


def validate_tasks(
    tasks_text: str,
    requirements: dict[str, Requirement],
    report: Report,
    min_tasks: int,
    coverage_gate: int,
) -> None:
    artifact = ARTIFACT_MARKER_RE.search(tasks_text)
    if not artifact:
        report.error("missing-artifact-marker", "TASKS.md is missing the techlead artifact marker.", "TASKS")
    else:
        attributes = parse_attributes(artifact.group(1))
        if attributes.get("type") != "tasks":
            report.error("wrong-artifact-type", "TASKS.md artifact type must be tasks.", "TASKS")
        if attributes.get("version") != "1":
            report.warning("artifact-version", "TASKS.md uses an unknown artifact version.", "TASKS")

    for required in ("Source PRD:", "Status:", "Execution order:"):
        if required not in tasks_text:
            report.error("missing-metadata", f"TASKS.md is missing metadata field {required}", "TASKS")

    sections = section_bodies(tasks_text)
    for section_id in TASKS_REQUIRED_SECTIONS:
        if section_id not in sections:
            report.error(
                "missing-section",
                f"TASKS.md is missing section marker id={section_id}.",
                "TASKS",
            )
        elif not nonempty_content_lines(sections[section_id]):
            report.error(
                "empty-section",
                f"TASKS.md section {section_id} has no content.",
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
    previous_number = 0
    all_tags: set[str] = set()
    covered_requirements: set[str] = set()

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

        for tag in task.tags:
            all_tags.add(tag)
        for field_name in ("acceptance", "verify", "files"):
            if len(task.fields.get(field_name, "")) < 6:
                report.error(
                    f"missing-{field_name}",
                    f"Task {task.task_id} needs a substantive {field_name} field.",
                    location,
                )

    missing_tags = [tag for tag in MANDATORY_TAGS if tag not in all_tags]
    if missing_tags:
        report.error(
            "missing-mandatory-tags",
            f"TASKS.md is missing mandatory task tags: {', '.join(missing_tags)}.",
            "TASKS",
        )
    if "final-gate" not in all_tags:
        report.warning(
            "missing-final-gate",
            "TASKS.md has no task tagged final-gate.",
            "TASKS",
        )

    uncovered = sorted(set(requirements) - covered_requirements)
    if uncovered:
        report.error(
            "uncovered-requirements",
            f"Requirements without a task: {', '.join(uncovered)}.",
            "TASKS",
        )

    traceability = sections.get("traceability", "")
    for key in sorted(requirements):
        if key not in traceability:
            report.error(
                "traceability-gap",
                f"TASKS.md traceability table is missing {key}.",
                "TASKS",
            )
    if requirements and "TASK-" not in traceability:
        report.error(
            "traceability-tasks",
            "TASKS.md traceability table must map requirements to task IDs.",
            "TASKS",
        )

    dod = sections.get("dod", "")
    if len(CHECKBOX_RE.findall(dod)) < MIN_BULLET_LINES["dod"]:
        report.error("thin-dod", "TASKS.md definition of done needs at least five checkboxes.", "TASKS")
    dod_percentages = parse_percentages(dod)
    if not dod_percentages:
        report.error("missing-dod-coverage", "TASKS.md definition of done must state the coverage gate.", "TASKS")
    elif max(dod_percentages) < coverage_gate:
        report.error(
            "dod-coverage-too-low",
            f"TASKS.md definition of done coverage is {max(dod_percentages)} percent, below {coverage_gate} percent.",
            "TASKS",
        )
    if "docker" not in dod.lower():
        report.error("missing-dod-docker", "TASKS.md definition of done must mention Docker.", "TASKS")

    report.stats.update(
        {
            "tasks": len(tasks),
            "covered_requirements": len(covered_requirements),
            "task_tags": sorted(all_tags),
        }
    )


def check_placeholders(text: str, name: str, report: Report) -> None:
    cleaned = strip_fenced_code(strip_comments(text))
    for match in PLACEHOLDER_RE.finditer(cleaned):
        line = cleaned.count("\n", 0, match.start()) + 1
        report.error(
            "placeholder",
            f"{name} contains unresolved placeholder {match.group(0)!r}.",
            f"{name}:{line}",
        )


def validate_texts(
    prd_text: str,
    tasks_text: str,
    min_questions: int = 8,
    min_tasks: int = 6,
    coverage_gate: int = 80,
) -> Report:
    report = Report()
    requirements = validate_prd(prd_text, report, min_questions, coverage_gate)
    validate_tasks(tasks_text, requirements, report, min_tasks, coverage_gate)
    check_placeholders(prd_text, "PRD.md", report)
    check_placeholders(tasks_text, "TASKS.md", report)
    report.stats["coverage_gate"] = coverage_gate
    return report


def validate_files(
    prd_path: Path,
    tasks_path: Path,
    min_questions: int = 8,
    min_tasks: int = 6,
    coverage_gate: int = 80,
) -> Report:
    report = Report()
    prd_text = ""
    tasks_text = ""
    if not prd_path.is_file():
        report.error("missing-file", f"PRD file not found: {prd_path}", str(prd_path))
    else:
        prd_text = prd_path.read_text(encoding="utf-8")
    if not tasks_path.is_file():
        report.error("missing-file", f"TASKS file not found: {tasks_path}", str(tasks_path))
    else:
        tasks_text = tasks_path.read_text(encoding="utf-8")
    if report.errors:
        return report
    result = validate_texts(prd_text, tasks_text, min_questions, min_tasks, coverage_gate)
    result.stats["prd_file"] = str(prd_path)
    result.stats["tasks_file"] = str(tasks_path)
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
        f"{stats.get('functional_requirements', 0)} functional requirements, "
        f"{stats.get('nonfunctional_requirements', 0)} non-functional requirements, "
        f"{stats.get('interview_questions', 0)} interview answers, "
        f"coverage gate {stats.get('coverage_gate', 'unknown')} percent."
    )
    print(f"Errors: {len(report.errors)}. Warnings: {len(report.warnings)}.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate TechLead PRD.md and TASKS.md artifacts.",
    )
    parser.add_argument("prd", nargs="?", default="PRD.md", help="Path to PRD.md")
    parser.add_argument("tasks", nargs="?", default="TASKS.md", help="Path to TASKS.md")
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
    report = validate_files(
        Path(args.prd),
        Path(args.tasks),
        min_questions=args.min_questions,
        min_tasks=args.min_tasks,
        coverage_gate=args.coverage,
    )
    print_report(report, args.json)
    if report.errors:
        return 1
    if args.strict and report.warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
