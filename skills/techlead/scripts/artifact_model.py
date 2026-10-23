#!/usr/bin/env python3
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable


ARTIFACT_MARKER_RE = re.compile(r"<!--\s*techlead:artifact\s+([^>]*?)-->")
SECTION_MARKER_RE = re.compile(r"<!--\s*techlead:section\s+([^>]*?)-->")
ENV_MARKER_RE = re.compile(r"<!--\s*techlead:env\s+([^>]*?)-->")
TASK_MARKER_RE = re.compile(r"<!--\s*techlead:task\s+([^>]*?)-->")
MILESTONE_MARKER_RE = re.compile(r"<!--\s*techlead:milestone\s+([^>]*?)-->")
ATTRIBUTE_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_-]*)=(\"[^\"]*\"|'[^']*'|[^\s]+)")
REQUIREMENT_RE = re.compile(
    r"(?m)^\s*[-*]\s*\*\*(FR|NFR|TR)-(\d{3})\*\*\s*[:.\-]?\s*(.+?)\s*$"
)
REQUIREMENT_TABLE_RE = re.compile(r"(?m)^\s*\|\s*(FR|NFR|TR)-(\d{3})\s*\|")
QUESTION_RE = re.compile(r"(?m)^###\s+Q-(\d{3})\s*$")
TASK_ID_RE = re.compile(r"^TASK-(\d{3})$")
MILESTONE_ID_RE = re.compile(r"^M(\d+)$")
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
    "spec": re.compile(r"(?mi)^\s*-\s*SPEC:\s*(.+?)\s*$"),
    "milestone": re.compile(r"(?mi)^\s*-\s*Milestone:\s*(.+?)\s*$"),
    "issue_title": re.compile(r"(?mi)^\s*-\s*Issue title:\s*(.+?)\s*$"),
    "labels": re.compile(r"(?mi)^\s*-\s*Labels:\s*(.+?)\s*$"),
    "estimate": re.compile(r"(?mi)^\s*-\s*Estimate:\s*(.+?)\s*$"),
    "acceptance": re.compile(r"(?mi)^\s*-\s*Acceptance:\s*(.+?)\s*$"),
    "verify": re.compile(r"(?mi)^\s*-\s*Verify:\s*(.+?)\s*$"),
    "files": re.compile(r"(?mi)^\s*-\s*Files:\s*(.+?)\s*$"),
}
MILESTONE_FIELD_PATTERNS = {
    "goal": re.compile(r"(?mi)^\s*-\s*Goal:\s*(.+?)\s*$"),
    "scope": re.compile(r"(?mi)^\s*-\s*Scope:\s*(.+?)\s*$"),
    "requirements": re.compile(r"(?mi)^\s*-\s*Requirements:\s*(.+?)\s*$"),
    "exit": re.compile(r"(?mi)^\s*-\s*Exit criteria:\s*(.+?)\s*$"),
    "launch": re.compile(r"(?mi)^\s*-\s*Launch gate:\s*(.+?)\s*$"),
    "depends": re.compile(r"(?mi)^\s*-\s*Depends on:\s*(.+?)\s*$"),
    "target": re.compile(r"(?mi)^\s*-\s*Target:\s*(.+?)\s*$"),
    "evidence": re.compile(r"(?mi)^\s*-\s*Evidence:\s*(.+?)\s*$"),
}
TITLE_RE = re.compile(r"(?m)^#{2,4}\s+(.+?)\s*$")

TASK_SECTIONS = ("rules", "tasks", "issue-format", "traceability", "dod")
PRD_SECTIONS = (
    "summary",
    "problem",
    "users",
    "scope",
    "success",
    "functional",
    "nonfunctional",
    "constraints",
    "assumptions",
    "risks",
    "dod",
    "qa",
    "traceability",
)
SPEC_SECTIONS = (
    "context",
    "architecture",
    "components",
    "data",
    "interfaces",
    "technical",
    "security",
    "environments",
    "testing",
    "observability",
    "decisions",
    "risks",
    "traceability",
    "dod",
)
PLAN_SECTIONS = ("strategy", "milestones", "dependencies", "risks", "traceability", "dod")
AGENTS_SECTIONS = (
    "overview",
    "stack",
    "layout",
    "commands",
    "conventions",
    "rules",
    "decisions",
    "dod",
    "security",
)
README_SECTIONS = (
    "overview",
    "status",
    "quickstart",
    "commands",
    "architecture",
    "docs",
    "testing",
    "deployment",
    "security",
)
MANDATORY_TAGS = ("docker-local", "docker-production", "coverage-gate", "security", "deployment")
OPTIONAL_TAGS = ("final-gate",)
MANDATORY_LABEL_PREFIXES = ("type:", "area:", "priority:")
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
    spec_refs: list[str]
    milestone: str
    tags: list[str]
    labels: list[str]
    fields: dict[str, str]
    has_checkbox: bool


@dataclass
class Milestone:
    milestone_id: str
    attributes: dict[str, str]
    body: str
    title: str
    order: int
    depends: list[str]
    requirements: list[str]
    fields: dict[str, str]


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


def artifact_header(text: str) -> dict[str, str]:
    match = ARTIFACT_MARKER_RE.search(text)
    return parse_attributes(match.group(1)) if match else {}


def has_metadata(text: str, fields: Iterable[str]) -> list[str]:
    first_section = SECTION_MARKER_RE.search(text)
    metadata = text[: first_section.start()] if first_section else text
    return [field for field in fields if field not in metadata]


def parse_requirements(text: str, report: Report, label: str) -> dict[str, Requirement]:
    requirements: dict[str, Requirement] = {}
    duplicates: set[str] = set()
    for match in REQUIREMENT_RE.finditer(text):
        kind, number, description = match.groups()
        key = f"{kind}-{number}"
        if key in requirements:
            duplicates.add(key)
            continue
        requirements[key] = Requirement(key, kind, int(number), description.strip())
    for match in REQUIREMENT_TABLE_RE.finditer(text):
        kind, number = match.groups()
        key = f"{kind}-{number}"
        requirements.setdefault(key, Requirement(key, kind, int(number), ""))
    for key in sorted(duplicates):
        report.error("duplicate-requirement", f"Requirement {key} is defined more than once.", label)
    for requirement in requirements.values():
        if len(requirement.description) < 10:
            report.error(
                "weak-requirement",
                f"Requirement {requirement.key} needs a testable description.",
                label,
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
                spec_refs=split_list(attributes.get("spec", "") or fields["spec"]),
                milestone=attributes.get("milestone", "") or fields["milestone"],
                tags=split_list(attributes.get("tags", "")),
                labels=split_list(attributes.get("labels", "") or fields["labels"]),
                fields=fields,
                has_checkbox=bool(CHECKBOX_RE.search(body)),
            )
        )
    return tasks


def parse_milestones(plan_text: str) -> list[Milestone]:
    markers = marker_positions(plan_text, MILESTONE_MARKER_RE)
    milestones: list[Milestone] = []
    for index, (_, end, attributes) in enumerate(markers):
        next_start = markers[index + 1][0] if index + 1 < len(markers) else len(plan_text)
        section_match = SECTION_MARKER_RE.search(plan_text, end, next_start)
        if section_match:
            next_start = section_match.start()
        body = plan_text[end:next_start]
        title_match = TITLE_RE.search(body)
        title = title_match.group(1).strip() if title_match else ""
        fields: dict[str, str] = {}
        for name, pattern in MILESTONE_FIELD_PATTERNS.items():
            match = pattern.search(body)
            fields[name] = match.group(1).strip() if match else ""
        raw_order = attributes.get("order", "")
        try:
            order = int(raw_order)
        except ValueError:
            order = 0
        milestones.append(
            Milestone(
                milestone_id=attributes.get("id", ""),
                attributes=attributes,
                body=body,
                title=title,
                order=order,
                depends=split_list(attributes.get("depends", "") or fields["depends"]),
                requirements=split_list(attributes.get("covers", "") or fields["requirements"]),
                fields=fields,
            )
        )
    return milestones


def label_prefixes(labels: Iterable[str]) -> set[str]:
    prefixes: set[str] = set()
    for label in labels:
        if ":" in label:
            prefixes.add(label.split(":", 1)[0] + ":")
    return prefixes
