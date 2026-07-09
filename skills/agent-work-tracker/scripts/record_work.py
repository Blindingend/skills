#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


DEFAULT_VAULT_ROOT = Path("/home/yanxin/personal/ObsidianNotes")
DEFAULT_TRACKING_REL = Path("Note/Work/TianYan/AgentTracking")
DEFAULT_PROJECT_DOC_REL = Path("Note/Work/TianYan/项目文档")
DEFAULT_WEEKLY_REPORT_REL = Path("Note/Work/TianYan/工作周报")
COMMIT_MESSAGE = "docs: 记录 agent 工作进展"
DIRTY_POLICY_APPEND_TRACKING_SKIP_PROJECT = "append_tracking_skip_project"
DIRTY_POLICY_STRICT = "strict"
DIRTY_TARGET_POLICIES = {
    DIRTY_POLICY_APPEND_TRACKING_SKIP_PROJECT,
    DIRTY_POLICY_STRICT,
}


class WorkRecord:
    def __init__(
        self,
        title: str,
        summary: str,
        status: str = "completed",
        repo: str = "",
        project: str = "",
        outputs: Optional[List[str]] = None,
        verification: Optional[List[str]] = None,
        next_steps: Optional[List[str]] = None,
        week_report_candidates: Optional[List[str]] = None,
    ) -> None:
        self.title = title
        self.summary = summary
        self.status = status
        self.repo = repo
        self.project = project
        self.outputs = outputs or []
        self.verification = verification or []
        self.next_steps = next_steps or []
        self.week_report_candidates = week_report_candidates or []

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "WorkRecord":
        title = clean_scalar(data.get("title"))
        summary = clean_scalar(data.get("summary"))
        if not title:
            raise ValueError("record requires a non-empty title")
        if not summary:
            raise ValueError("record requires a non-empty summary")

        return cls(
            title=title,
            summary=summary,
            status=clean_scalar(data.get("status")) or "completed",
            repo=clean_scalar(data.get("repo")),
            project=clean_scalar(data.get("project")),
            outputs=clean_list(data.get("outputs")),
            verification=clean_list(data.get("verification")),
            next_steps=clean_list(data.get("next_steps")),
            week_report_candidates=clean_list(data.get("week_report_candidates")),
        )


class SubprocessGit:
    def run(
        self,
        repo: Path,
        args: Sequence[str],
        check: bool = True,
        capture_output: bool = False,
    ) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git"] + list(args),
            cwd=str(repo),
            check=check,
            text=True,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None,
        )


class TrackerConfig:
    def __init__(
        self,
        vault_root: Path = DEFAULT_VAULT_ROOT,
        tracking_dir: Optional[Path] = None,
        project_doc_dir: Optional[Path] = None,
        weekly_report_dir: Optional[Path] = None,
        git_sync: bool = True,
        commit_message: str = COMMIT_MESSAGE,
        dirty_target_policy: str = DIRTY_POLICY_APPEND_TRACKING_SKIP_PROJECT,
    ) -> None:
        self.vault_root = vault_root
        self.tracking_dir = tracking_dir or vault_root / DEFAULT_TRACKING_REL
        self.project_doc_dir = project_doc_dir or vault_root / DEFAULT_PROJECT_DOC_REL
        self.weekly_report_dir = weekly_report_dir or vault_root / DEFAULT_WEEKLY_REPORT_REL
        self.git_sync = git_sync
        self.commit_message = commit_message
        self.dirty_target_policy = dirty_target_policy


def clean_scalar(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def clean_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, Iterable):
        return [clean_scalar(item) for item in value if clean_scalar(item)]
    return [clean_scalar(value)]


def week_ending_friday(day: date) -> date:
    friday = 4
    days_until_friday = (friday - day.weekday()) % 7
    return day + timedelta(days=days_until_friday)


def normalize_name(value: str) -> str:
    return re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]+", "", value).lower()


def find_project_doc(project: str, project_dir: Path) -> Optional[Path]:
    project = project.strip()
    if not project or not project_dir.exists():
        return None

    docs = sorted(path for path in project_dir.glob("*.md") if path.is_file())
    normalized_project = normalize_name(project)

    exact = [path for path in docs if normalize_name(path.stem) == normalized_project]
    if len(exact) == 1:
        return exact[0]

    partial = [
        path
        for path in docs
        if normalized_project and normalized_project in normalize_name(path.stem)
    ]
    if len(partial) == 1:
        return partial[0]

    return None


def tracking_file_for(tracking_dir: Path, week_end: date) -> Path:
    return tracking_dir / ("%s Agent Tracking.md" % week_end.isoformat())


def markdown_list(items: Sequence[str]) -> str:
    if not items:
        return "- 无"
    return "\n".join("- %s" % item for item in items)


def render_tracking_header(week_end: date) -> str:
    return (
        "---\n"
        "created: %s\n"
        "tags:\n"
        "  - 工作\n"
        "  - agent-tracking\n"
        "  - year-%s\n"
        "aliases:\n"
        "  - %s Agent Tracking\n"
        "---\n\n"
        "# %s Agent Tracking\n\n"
        "本文件记录 agent 在本周完成的较大任务，供项目文档和周报汇总使用。\n"
    ) % (
        week_end.isoformat(),
        week_end.year,
        week_end.isoformat(),
        week_end.isoformat(),
    )


def render_tracking_entry(record: WorkRecord, recorded_at: str) -> str:
    lines = [
        "",
        "### %s %s" % (recorded_at, record.title),
        "",
        "- **状态**：%s" % record.status,
    ]
    if record.repo:
        lines.append("- **仓库**：`%s`" % record.repo)
    if record.project:
        lines.append("- **项目**：%s" % record.project)

    lines.extend(
        [
            "",
            "**工作总结**",
            "",
            record.summary,
            "",
            "**产出**",
            "",
            markdown_list(record.outputs),
            "",
            "**验证**",
            "",
            markdown_list(record.verification),
            "",
            "**后续事项**",
            "",
            markdown_list(record.next_steps),
        ]
    )
    if record.week_report_candidates:
        lines.extend(
            [
                "",
                "**周报候选表达**",
                "",
                markdown_list(record.week_report_candidates),
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def append_tracking_entry(
    tracking_file: Path,
    record: WorkRecord,
    recorded_at: str,
    week_end: date,
) -> None:
    tracking_file.parent.mkdir(parents=True, exist_ok=True)
    if tracking_file.exists():
        content = tracking_file.read_text(encoding="utf-8").rstrip() + "\n"
    else:
        content = render_tracking_header(week_end)

    content += render_tracking_entry(record, recorded_at)
    tracking_file.write_text(content, encoding="utf-8")


def render_project_entry(record: WorkRecord, recorded_at: str, tracking_file: Path) -> str:
    return (
        "\n"
        "- %s：%s。来源：[[%s]]\n"
        "  - 验证：%s\n"
        "  - 后续：%s\n"
    ) % (
        recorded_at,
        record.summary,
        tracking_file.stem,
        "；".join(record.verification) if record.verification else "未记录",
        "；".join(record.next_steps) if record.next_steps else "无",
    )


def append_project_progress(project_doc: Path, record: WorkRecord, recorded_at: str, tracking_file: Path) -> None:
    content = project_doc.read_text(encoding="utf-8") if project_doc.exists() else ""
    section = "\n## Agent Progress\n"
    if "## Agent Progress" not in content:
        content = content.rstrip() + "\n" + section
    else:
        content = content.rstrip() + "\n"
    content += render_project_entry(record, recorded_at, tracking_file)
    project_doc.write_text(content, encoding="utf-8")


def rel_paths(repo: Path, paths: Sequence[Path]) -> List[str]:
    return [str(path.resolve().relative_to(repo.resolve())) for path in paths]


def git_status_for_paths(repo: Path, target_files: Sequence[Path], git: SubprocessGit) -> str:
    if not target_files:
        return ""
    paths = rel_paths(repo, target_files)
    result = git.run(
        repo,
        ["-c", "core.quotePath=false", "status", "--porcelain", "--"] + paths,
        capture_output=True,
    )
    return (result.stdout or "").strip()


def dirty_paths_from_status(output: str) -> List[str]:
    paths = []
    for raw_line in output.splitlines():
        if not raw_line.strip():
            continue
        path = raw_line[3:] if len(raw_line) > 3 else raw_line.strip()
        if " -> " in path:
            path = path.rsplit(" -> ", 1)[1]
        paths.append(path)
    return paths


def ensure_targets_clean(repo: Path, target_files: Sequence[Path], git: Optional[SubprocessGit] = None) -> None:
    if not target_files:
        return
    git = git or SubprocessGit()
    output = git_status_for_paths(repo, target_files, git)
    if output:
        raise RuntimeError("target files already have local changes:\n%s" % output)


def validate_dirty_target_policy(value: str) -> str:
    policy = clean_scalar(value) or DIRTY_POLICY_APPEND_TRACKING_SKIP_PROJECT
    if policy not in DIRTY_TARGET_POLICIES:
        raise ValueError(
            "invalid dirty target policy %s; expected one of: %s"
            % (policy, ", ".join(sorted(DIRTY_TARGET_POLICIES)))
        )
    return policy


def project_doc_status_for(project_doc: Optional[Path], skipped_dirty: bool) -> str:
    if project_doc is None:
        return "not_matched"
    return "skipped_dirty" if skipped_dirty else "updated"


def resolve_write_targets(
    repo: Path,
    tracking_file: Path,
    project_doc: Optional[Path],
    git: SubprocessGit,
    dirty_target_policy: str,
) -> Dict[str, Any]:
    target_files = [tracking_file]
    if project_doc is not None:
        target_files.append(project_doc)

    policy = validate_dirty_target_policy(dirty_target_policy)
    if policy == DIRTY_POLICY_STRICT:
        ensure_targets_clean(repo, target_files, git=git)
        return {
            "target_files": target_files,
            "write_project_doc": project_doc is not None,
            "project_doc_status": project_doc_status_for(project_doc, skipped_dirty=False),
        }

    output = git_status_for_paths(repo, target_files, git)
    dirty_paths = set(dirty_paths_from_status(output))
    write_targets = [tracking_file]
    skip_project_doc = False
    if project_doc is not None:
        project_rel = rel_paths(repo, [project_doc])[0]
        skip_project_doc = project_rel in dirty_paths
        if not skip_project_doc:
            write_targets.append(project_doc)

    return {
        "target_files": write_targets,
        "write_project_doc": project_doc is not None and not skip_project_doc,
        "project_doc_status": project_doc_status_for(project_doc, skipped_dirty=skip_project_doc),
    }


def git_sync_write_commit_push(
    vault_root: Path,
    tracking_file: Path,
    project_doc: Optional[Path],
    write_fn,
    git: Optional[SubprocessGit] = None,
    commit_message: str = COMMIT_MESSAGE,
    dirty_target_policy: str = DIRTY_POLICY_APPEND_TRACKING_SKIP_PROJECT,
) -> Dict[str, str]:
    git = git or SubprocessGit()
    git.run(vault_root, ["pull", "--rebase", "--autostash"])
    target_plan = resolve_write_targets(
        vault_root,
        tracking_file,
        project_doc,
        git=git,
        dirty_target_policy=dirty_target_policy,
    )
    write_fn(target_plan["write_project_doc"])

    paths = rel_paths(vault_root, target_plan["target_files"])
    git.run(vault_root, ["add", "--"] + paths)
    diff = git.run(vault_root, ["diff", "--cached", "--quiet"], check=False)
    if diff.returncode == 0:
        return {
            "status": "no_changes",
            "project_doc_status": target_plan["project_doc_status"],
        }

    git.run(vault_root, ["commit", "-m", commit_message])
    git.run(vault_root, ["pull", "--rebase", "--autostash"])
    git.run(vault_root, ["push"])
    return {
        "status": "committed",
        "project_doc_status": target_plan["project_doc_status"],
    }


def no_git_project_doc_status(project_doc: Optional[Path]) -> str:
    return "updated" if project_doc is not None else "not_matched"


def record_workflow(
    payload: Mapping[str, Any],
    vault_root: Path = DEFAULT_VAULT_ROOT,
    tracking_dir: Optional[Path] = None,
    project_doc_dir: Optional[Path] = None,
    today: Optional[date] = None,
    recorded_at: Optional[str] = None,
    git: Optional[SubprocessGit] = None,
    use_git: bool = True,
    commit_message: str = COMMIT_MESSAGE,
    dirty_target_policy: str = DIRTY_POLICY_APPEND_TRACKING_SKIP_PROJECT,
) -> Dict[str, Any]:
    record = WorkRecord.from_mapping(payload)
    today = today or date.today()
    recorded_at = recorded_at or datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
    tracking_dir = tracking_dir or vault_root / DEFAULT_TRACKING_REL
    project_doc_dir = project_doc_dir or vault_root / DEFAULT_PROJECT_DOC_REL
    week_end = week_ending_friday(today)
    tracking_file = tracking_file_for(tracking_dir, week_end)
    project_doc = find_project_doc(record.project, project_doc_dir)

    def write_notes(write_project_doc: bool = True) -> None:
        append_tracking_entry(tracking_file, record, recorded_at=recorded_at, week_end=week_end)
        if project_doc is not None and write_project_doc:
            append_project_progress(project_doc, record, recorded_at, tracking_file)

    if use_git:
        sync_result = git_sync_write_commit_push(
            vault_root,
            tracking_file,
            project_doc,
            write_notes,
            git=git,
            commit_message=commit_message,
            dirty_target_policy=dirty_target_policy,
        )
        status = sync_result["status"]
        project_doc_status = sync_result["project_doc_status"]
    else:
        write_notes()
        status = "written"
        project_doc_status = no_git_project_doc_status(project_doc)

    return {
        "status": status,
        "tracking_file": str(tracking_file),
        "project_doc": str(project_doc) if project_doc is not None else None,
        "project_doc_status": project_doc_status,
    }


def parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    return date.fromisoformat(value)


def default_config_path() -> Path:
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        return Path(config_home) / "yx-workflow" / "config.toml"
    return Path.home() / ".config" / "yx-workflow" / "config.toml"


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = clean_scalar(value).lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    raise ValueError("invalid boolean value: %s" % value)


def parse_toml_subset(text: str) -> Dict[str, Dict[str, Any]]:
    config: Dict[str, Dict[str, Any]] = {}
    section: Optional[str] = None
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            if not section:
                raise ValueError("empty section at line %s" % line_number)
            config.setdefault(section, {})
            continue
        if "=" not in line or section is None:
            raise ValueError("invalid config line %s: %s" % (line_number, raw_line))
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            parsed: Any = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            parsed = value[1:-1]
        elif value.lower() in {"true", "false"}:
            parsed = value.lower() == "true"
        else:
            parsed = value
        config[section][key] = parsed
    return config


def load_config_file(path: Path) -> Dict[str, Dict[str, Any]]:
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    try:
        import tomllib  # type: ignore
    except ImportError:
        return parse_toml_subset(raw)
    return tomllib.loads(raw)


def env_value(name: str) -> Optional[str]:
    value = os.environ.get(name)
    return value if value not in {None, ""} else None


def resolve_path(value: Any, base: Optional[Path] = None) -> Optional[Path]:
    text = clean_scalar(value)
    if not text:
        return None
    path = Path(os.path.expandvars(text)).expanduser()
    if path.is_absolute() or base is None:
        return path
    return base / path


def env_bool(name: str) -> Optional[bool]:
    value = env_value(name)
    if value is None:
        return None
    return parse_bool(value)


def resolve_config(args: argparse.Namespace) -> TrackerConfig:
    config_path = resolve_path(args.config or env_value("YX_WORKFLOW_CONFIG")) or default_config_path()
    file_config = load_config_file(config_path)
    obsidian_config = file_config.get("obsidian", {})
    git_config = file_config.get("git", {})

    vault_root = (
        resolve_path(args.vault_root)
        or resolve_path(env_value("AGENT_WORK_TRACKER_VAULT"))
        or resolve_path(obsidian_config.get("vault_root"))
        or DEFAULT_VAULT_ROOT
    )

    tracking_dir = (
        resolve_path(args.tracking_dir, vault_root)
        or resolve_path(env_value("AGENT_WORK_TRACKER_TRACKING_DIR"), vault_root)
        or resolve_path(obsidian_config.get("agent_tracking_dir"), vault_root)
        or vault_root / DEFAULT_TRACKING_REL
    )
    project_doc_dir = (
        resolve_path(args.project_doc_dir, vault_root)
        or resolve_path(env_value("AGENT_WORK_TRACKER_PROJECT_DOC_DIR"), vault_root)
        or resolve_path(obsidian_config.get("project_doc_dir"), vault_root)
        or vault_root / DEFAULT_PROJECT_DOC_REL
    )
    weekly_report_dir = (
        resolve_path(env_value("AGENT_WORK_TRACKER_WEEKLY_REPORT_DIR"), vault_root)
        or resolve_path(obsidian_config.get("weekly_report_dir"), vault_root)
        or vault_root / DEFAULT_WEEKLY_REPORT_REL
    )

    git_sync = True
    if "sync" in git_config:
        git_sync = parse_bool(git_config["sync"])
    env_sync = env_bool("AGENT_WORK_TRACKER_GIT_SYNC")
    if env_sync is not None:
        git_sync = env_sync
    if args.no_git:
        git_sync = False

    commit_message = (
        clean_scalar(env_value("AGENT_WORK_TRACKER_COMMIT_MESSAGE"))
        or clean_scalar(git_config.get("commit_message"))
        or COMMIT_MESSAGE
    )
    dirty_target_policy = validate_dirty_target_policy(
        clean_scalar(args.dirty_target_policy)
        or clean_scalar(env_value("AGENT_WORK_TRACKER_DIRTY_TARGET_POLICY"))
        or clean_scalar(git_config.get("dirty_target_policy"))
        or DIRTY_POLICY_APPEND_TRACKING_SKIP_PROJECT
    )

    return TrackerConfig(
        vault_root=vault_root,
        tracking_dir=tracking_dir,
        project_doc_dir=project_doc_dir,
        weekly_report_dir=weekly_report_dir,
        git_sync=git_sync,
        commit_message=commit_message,
        dirty_target_policy=dirty_target_policy,
    )


def read_payload(args: argparse.Namespace, stdin) -> Dict[str, Any]:
    if args.input:
        raw = Path(args.input).read_text(encoding="utf-8")
    else:
        raw = stdin.read()
    return json.loads(raw)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record completed agent work into Obsidian.")
    parser.add_argument("--input", help="Path to JSON payload. Defaults to stdin.")
    parser.add_argument("--config", help="Path to yx-workflow config.toml.")
    parser.add_argument("--vault-root", default=None)
    parser.add_argument("--tracking-dir", default=None)
    parser.add_argument("--project-doc-dir", default=None)
    parser.add_argument("--today", default=None, help="YYYY-MM-DD override for tests or backfills.")
    parser.add_argument("--recorded-at", default=None, help="Displayed timestamp, e.g. 2026-05-22 18:30.")
    parser.add_argument("--no-git", action="store_true", help="Write files without pull/commit/push.")
    parser.add_argument(
        "--dirty-target-policy",
        choices=sorted(DIRTY_TARGET_POLICIES),
        default=None,
        help="How to handle target files that already have local changes before writing.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None, stdin=sys.stdin) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = resolve_config(args)

    result = record_workflow(
        read_payload(args, stdin),
        vault_root=config.vault_root,
        tracking_dir=config.tracking_dir,
        project_doc_dir=config.project_doc_dir,
        today=parse_date(args.today),
        recorded_at=args.recorded_at,
        use_git=config.git_sync,
        commit_message=config.commit_message,
        dirty_target_policy=config.dirty_target_policy,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
