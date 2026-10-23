#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from artifact_model import Milestone, Task, parse_milestones, parse_tasks


TASK_URL_RE = re.compile(r"/issues/(\d+)/?$")
LABEL_COLORS = ("0E8A16", "1D76DB", "5319E7", "B60205", "D93F0B", "FBCA04", "006B75", "C2E0C6")


class ExportError(RuntimeError):
    pass


@dataclass
class IssuePayload:
    task_id: str
    title: str
    body: str
    labels: list[str]
    milestone: str
    milestone_id: str
    depends_on: list[str]
    estimate: str
    prd_refs: list[str]
    spec_refs: list[str]
    files: list[str]
    number: int | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "body": self.body,
            "labels": self.labels,
            "milestone": self.milestone,
            "milestone_id": self.milestone_id,
            "depends_on": self.depends_on,
            "estimate": self.estimate,
            "prd": self.prd_refs,
            "spec": self.spec_refs,
            "files": self.files,
            "number": self.number,
        }


@dataclass
class MilestonePayload:
    milestone_id: str
    title: str
    description: str


@dataclass
class ExportManifest:
    provider: str
    repo: str
    labels: list[str]
    milestones: list[MilestonePayload]
    issues: list[IssuePayload] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "provider": self.provider,
            "repo": self.repo,
            "labels": self.labels,
            "milestones": [
                {
                    "id": milestone.milestone_id,
                    "title": milestone.title,
                    "description": milestone.description,
                }
                for milestone in self.milestones
            ],
            "issues": [issue.to_dict() for issue in self.issues],
        }


def milestone_title(milestone: Milestone) -> str:
    title = re.sub(
        rf"^{re.escape(milestone.milestone_id)}\s*[:—-]\s*",
        "",
        milestone.title,
    )
    return f"{milestone.milestone_id} — {title}"


def milestone_description(milestone: Milestone) -> str:
    return "\n".join(
        [
            f"Goal: {milestone.fields.get('goal', '')}",
            f"Scope: {milestone.fields.get('scope', '')}",
            f"Exit criteria: {milestone.fields.get('exit', '')}",
            f"Launch gate: {milestone.fields.get('launch', '')}",
        ]
    )


def task_labels(task: Task, base_labels: Iterable[str]) -> list[str]:
    labels = list(base_labels)
    labels.extend(f"techlead:{tag}" for tag in task.tags if tag)
    labels.extend(task.labels)
    return sorted(dict.fromkeys(label for label in labels if label))


def dependency_block(depends: Iterable[str], resolution: dict[str, int] | None = None) -> str:
    dependencies = list(depends)
    if not dependencies:
        return "- None"
    lines: list[str] = []
    for dependency in dependencies:
        if resolution and dependency in resolution:
            lines.append(f"- Depends on: #{resolution[dependency]} ({dependency})")
        else:
            lines.append(f"- Depends on: {dependency}")
    return "\n".join(lines)


def render_dependencies(task: Task, resolution: dict[str, int] | None = None) -> str:
    return dependency_block(task.depends, resolution)


def replace_dependencies(body: str, depends: Iterable[str], resolution: dict[str, int]) -> str:
    block = dependency_block(depends, resolution)
    pattern = re.compile(r"(## Dependencies\n\n)(.*?)(\n\n## Traceability)", re.DOTALL)
    if pattern.search(body):
        return pattern.sub(lambda match: match.group(1) + block + match.group(3), body, count=1)
    return body.rstrip() + "\n\n## Dependencies\n\n" + block + "\n"


def render_body(task: Task, milestone: Milestone, resolution: dict[str, int] | None = None) -> str:
    files = "\n".join(f"- {item}" for item in split_files(task.fields.get("files", "")))
    if not files:
        files = "- See task verification"
    return "\n".join(
        [
            f"<!-- techlead:task id={task.task_id} milestone={milestone.milestone_id} -->",
            "## Context",
            "",
            f"- Milestone: {milestone_title(milestone)}",
            f"- PRD: {', '.join(task.prd_refs)}",
            f"- SPEC: {', '.join(task.spec_refs)}",
            f"- Estimate: {task.fields.get('estimate', '')}",
            "",
            "## Acceptance",
            "",
            task.fields.get("acceptance", ""),
            "",
            "## Verification",
            "",
            task.fields.get("verify", ""),
            "",
            "## Files",
            "",
            files,
            "",
            "## Dependencies",
            "",
            render_dependencies(task, resolution),
            "",
            "## Traceability",
            "",
            f"- PRD: {', '.join(task.prd_refs)}",
            f"- SPEC: {', '.join(task.spec_refs)}",
            f"- Milestone: {milestone.milestone_id}",
            "",
        ]
    )


def split_files(value: str) -> list[str]:
    normalized = value.strip()
    if not normalized:
        return []
    return [item.strip() for item in normalized.split(",") if item.strip()]


def issue_title(task: Task, prefix: bool) -> str:
    title = task.fields.get("issue_title", "").strip()
    return f"[{task.task_id}] {title}" if prefix else title


def build_manifest(
    tasks_text: str,
    plan_text: str,
    provider: str,
    repo: str,
    base_labels: Iterable[str],
    id_prefix: bool = True,
) -> ExportManifest:
    tasks = parse_tasks(tasks_text)
    milestones = parse_milestones(plan_text)
    milestone_index = {milestone.milestone_id: milestone for milestone in milestones}
    if not tasks:
        raise ExportError("TASKS.md contains no task markers.")
    if not milestone_index:
        raise ExportError("PLAN.md contains no milestone markers.")

    for task in tasks:
        if not task.task_id:
            raise ExportError("A task marker is missing its id.")
        if not task.milestone:
            raise ExportError(f"Task {task.task_id} has no milestone.")
        if task.milestone not in milestone_index:
            raise ExportError(f"Task {task.task_id} references unknown milestone {task.milestone}.")
        if not task.fields.get("issue_title", "").strip():
            raise ExportError(f"Task {task.task_id} has no issue title.")
        if not task.fields.get("estimate", "").strip():
            raise ExportError(f"Task {task.task_id} has no estimate.")
        if len(task.labels) < 3:
            raise ExportError(f"Task {task.task_id} has incomplete labels.")

    labels: set[str] = set(base_labels)
    issues: list[IssuePayload] = []
    milestone_payloads = [
        MilestonePayload(milestone.milestone_id, milestone_title(milestone), milestone_description(milestone))
        for milestone in milestones
    ]
    for task in tasks:
        milestone = milestone_index[task.milestone]
        labels.update(task_labels(task, base_labels))
        issues.append(
            IssuePayload(
                task_id=task.task_id,
                title=issue_title(task, id_prefix),
                body=render_body(task, milestone),
                labels=task_labels(task, base_labels),
                milestone=milestone_title(milestone),
                milestone_id=milestone.milestone_id,
                depends_on=list(task.depends),
                estimate=task.fields.get("estimate", ""),
                prd_refs=list(task.prd_refs),
                spec_refs=list(task.spec_refs),
                files=split_files(task.fields.get("files", "")),
            )
        )
    return ExportManifest(
        provider=provider,
        repo=repo,
        labels=sorted(labels),
        milestones=milestone_payloads,
        issues=issues,
    )


def label_color(label: str) -> str:
    return LABEL_COLORS[sum(ord(character) for character in label) % len(LABEL_COLORS)]


def shell_quote(command: Iterable[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def shell_plan(manifest: ExportManifest) -> str:
    lines = ["#!/usr/bin/env bash", "set -euo pipefail", ""]
    if manifest.provider == "github":
        lines.append(f"REPO={shlex.quote(manifest.repo)}")
        lines.append("")
        lines.append("# Labels")
        for label in manifest.labels:
            lines.append(
                shell_quote(
                    [
                        "gh",
                        "label",
                        "create",
                        label,
                        "--repo",
                        manifest.repo,
                        "--force",
                        "--color",
                        label_color(label),
                    ]
                )
            )
        lines.append("")
        lines.append("# Milestones")
        for milestone in manifest.milestones:
            lines.append(
                shell_quote(
                    [
                        "gh",
                        "api",
                        f"repos/{manifest.repo}/milestones",
                        "--method",
                        "POST",
                        "-f",
                        f"title={milestone.title}",
                        "-f",
                        f"description={milestone.description}",
                    ]
                )
                + " || true"
            )
        lines.append("")
        lines.append("# Issues")
        for issue in manifest.issues:
            body_path = f".techlead-issues/{issue.task_id}.md"
            lines.append(f"mkdir -p .techlead-issues")
            lines.append(f"cat > {shlex.quote(body_path)} <<'TECHLEAD_ISSUE'")
            lines.append(issue.body.rstrip())
            lines.append("TECHLEAD_ISSUE")
            command = [
                "gh",
                "issue",
                "create",
                "--repo",
                manifest.repo,
                "--title",
                issue.title,
                "--body-file",
                body_path,
                "--milestone",
                issue.milestone,
            ]
            for label in issue.labels:
                command.extend(["--label", label])
            lines.append(shell_quote(command))
        return "\n".join(lines) + "\n"

    lines.append(f"REPO={shlex.quote(manifest.repo)}")
    lines.append("")
    lines.append("# Labels")
    for label in manifest.labels:
        lines.append(
            shell_quote(
                [
                    "glab",
                    "label",
                    "create",
                    "--name",
                    label,
                    "--color",
                    label_color(label),
                ]
            )
            + " || true"
        )
    lines.append("")
    lines.append("# Milestones")
    for milestone in manifest.milestones:
        lines.append(
            shell_quote(
                [
                    "glab",
                    "milestone",
                    "create",
                    "--title",
                    milestone.title,
                    "--description",
                    milestone.description,
                ]
            )
            + " || true"
        )
    lines.append("")
    lines.append("# Issues")
    for issue in manifest.issues:
        command = [
            "glab",
            "issue",
            "create",
            "--title",
            issue.title,
            "--description",
            issue.body,
            "--milestone",
            issue.milestone,
        ]
        for label in issue.labels:
            command.extend(["--label", label])
        lines.append(shell_quote(command))
    return "\n".join(lines) + "\n"


class Backend:
    name = ""
    cli = ""

    def __init__(self, repo: str, runner=None) -> None:
        self.repo = repo
        self.runner = runner or subprocess.run

    def run(self, command: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
        try:
            result = self.runner(command, capture_output=True, text=True, check=False)
        except FileNotFoundError as error:
            raise ExportError(f"{self.cli} is not installed.") from error
        if check and result.returncode != 0:
            message = (result.stderr or result.stdout or "").strip()
            raise ExportError(f"{shell_quote(command)} failed: {message}")
        return result

    def ensure_label(self, label: str) -> None:
        raise NotImplementedError

    def ensure_milestone(self, milestone: MilestonePayload) -> None:
        raise NotImplementedError

    def create_issue(self, issue: IssuePayload) -> int:
        raise NotImplementedError

    def update_issue(self, number: int, issue: IssuePayload) -> None:
        raise NotImplementedError

    def parse_issue_number(self, output: str) -> int:
        match = TASK_URL_RE.search(output.strip())
        if not match:
            raise ExportError(f"Cannot parse issue number from: {output.strip()}")
        return int(match.group(1))


class GitHubBackend(Backend):
    name = "github"
    cli = "gh"

    def ensure_label(self, label: str) -> None:
        self.run(
            [
                "gh",
                "label",
                "create",
                label,
                "--repo",
                self.repo,
                "--force",
                "--color",
                label_color(label),
            ]
        )

    def ensure_milestone(self, milestone: MilestonePayload) -> None:
        listing = self.run(
            ["gh", "api", f"repos/{self.repo}/milestones?state=all", "--paginate", "--slurp"],
        )
        try:
            milestones = json.loads(listing.stdout or "[]")
        except json.JSONDecodeError as error:
            raise ExportError("gh returned invalid JSON while listing milestones.") from error
        if not isinstance(milestones, list):
            raise ExportError("gh returned an invalid milestone list.")
        if milestones and all(isinstance(page, list) for page in milestones):
            milestones = [item for page in milestones for item in page]
        if not all(isinstance(item, dict) for item in milestones):
            raise ExportError("gh returned an invalid milestone list.")
        existing = [item.get("title", "") for item in milestones]
        if milestone.title in existing:
            return
        self.run(
            [
                "gh",
                "api",
                f"repos/{self.repo}/milestones",
                "--method",
                "POST",
                "-f",
                f"title={milestone.title}",
                "-f",
                f"description={milestone.description}",
            ]
        )

    def create_issue(self, issue: IssuePayload) -> int:
        command = [
            "gh",
            "issue",
            "create",
            "--repo",
            self.repo,
            "--title",
            issue.title,
            "--body",
            issue.body,
            "--milestone",
            issue.milestone,
        ]
        for label in issue.labels:
            command.extend(["--label", label])
        result = self.run(command)
        return self.parse_issue_number(result.stdout)

    def update_issue(self, number: int, issue: IssuePayload) -> None:
        self.run(
            [
                "gh",
                "issue",
                "edit",
                str(number),
                "--repo",
                self.repo,
                "--body",
                issue.body,
            ]
        )


class GitLabBackend(Backend):
    name = "gitlab"
    cli = "glab"

    def ensure_label(self, label: str) -> None:
        result = self.run(
            [
                "glab",
                "label",
                "create",
                "--name",
                label,
                "--color",
                f"#{label_color(label)}",
                "--description",
                "Managed by TechLead",
            ],
            check=False,
        )
        if result.returncode != 0 and "already" not in (result.stderr or "").lower():
            raise ExportError(f"glab label create failed for {label}: {(result.stderr or '').strip()}")

    def ensure_milestone(self, milestone: MilestonePayload) -> None:
        listing = self.run(["glab", "milestone", "list", "--per-page", "100"], check=False)
        if result_has_title(listing.stdout, milestone.title):
            return
        self.run(
            [
                "glab",
                "milestone",
                "create",
                "--title",
                milestone.title,
                "--description",
                milestone.description,
            ]
        )

    def create_issue(self, issue: IssuePayload) -> int:
        command = [
            "glab",
            "issue",
            "create",
            "--title",
            issue.title,
            "--description",
            issue.body,
            "--milestone",
            issue.milestone,
        ]
        for label in issue.labels:
            command.extend(["--label", label])
        result = self.run(command)
        return self.parse_issue_number(result.stdout)

    def update_issue(self, number: int, issue: IssuePayload) -> None:
        self.run(
            [
                "glab",
                "issue",
                "update",
                str(number),
                "--description",
                issue.body,
            ]
        )


def result_has_title(output: str, title: str) -> bool:
    return any(line.partition(" | ")[0].strip() == title for line in output.splitlines())


def build_backend(provider: str, repo: str, runner=None) -> Backend:
    backend = GitHubBackend if provider == "github" else GitLabBackend
    if not shutil.which(backend.cli):
        raise ExportError(f"{backend.cli} is required for --apply with provider {provider}.")
    return backend(repo, runner=runner)


def apply_manifest(manifest: ExportManifest, backend: Backend) -> dict[str, int]:
    for label in manifest.labels:
        backend.ensure_label(label)
    for milestone in manifest.milestones:
        backend.ensure_milestone(milestone)

    resolution: dict[str, int] = {}
    for issue in manifest.issues:
        number = backend.create_issue(issue)
        issue.number = number
        resolution[issue.task_id] = number

    for issue in manifest.issues:
        if not issue.depends_on:
            continue
        issue.body = replace_dependencies(issue.body, issue.depends_on, resolution)
        backend.update_issue(issue.number or 0, issue)
    return resolution


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        raise ExportError(f"Cannot read {path}: {error}") from error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export TechLead TASKS.md as GitHub or GitLab issues.",
    )
    parser.add_argument("--tasks", default="TASKS.md", help="Path to TASKS.md")
    parser.add_argument("--plan", default="PLAN.md", help="Path to PLAN.md")
    parser.add_argument("--provider", choices=("github", "gitlab"), default="github")
    parser.add_argument("--repo", default="", help="Repository in owner/name form")
    parser.add_argument("--format", choices=("json", "shell"), default="json")
    parser.add_argument("--base-label", action="append", default=[], help="Additional base label")
    parser.add_argument("--no-id-prefix", action="store_true", help="Do not prefix issue titles with the task ID")
    parser.add_argument("--apply", action="store_true", help="Create labels, milestones, and issues")
    parser.add_argument("--json-output", help="Write the manifest or resolution to this file")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        manifest = build_manifest(
            read_text(Path(args.tasks)),
            read_text(Path(args.plan)),
            provider=args.provider,
            repo=args.repo,
            base_labels=["techlead", *args.base_label],
            id_prefix=not args.no_id_prefix,
        )
        if args.apply:
            if not args.repo:
                raise ExportError("--repo is required with --apply.")
            backend = build_backend(args.provider, args.repo)
            resolution = apply_manifest(manifest, backend)
            payload: dict[str, object] = {
                "status": "created",
                "provider": args.provider,
                "repo": args.repo,
                "issues": resolution,
            }
        elif args.format == "shell":
            payload = {"status": "dry-run", "script": shell_plan(manifest)}
        else:
            payload = {"status": "dry-run", "manifest": manifest.to_dict()}
    except ExportError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.json_output:
        Path(args.json_output).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
