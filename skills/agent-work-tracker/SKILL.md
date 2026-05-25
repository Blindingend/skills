---
name: agent-work-tracker
description: Use after completing a substantial task, project milestone, implementation, debugging session, deployment, CI fix, investigation, or plan to record a concise work summary into the user's Obsidian AgentTracking notes and, when clearly matched, an existing project document. Also use when asked to generate or update a weekly work report from tracked agent work.
---

# Agent Work Tracker

Record meaningful completed agent work so weekly reports can be generated from reliable notes instead of memory.

## When to Use

Use this skill at the end of any substantial completed task, including:

- implementation or refactoring work
- non-trivial debugging or CI fixes
- deployment or release work
- project investigation with concrete findings
- completed plans or design specs
- project milestones that should appear in a weekly report

Do not use it for short Q&A, tiny command outputs, or abandoned work with no useful result unless the user explicitly asks to record it.

## Configuration

The script reads configuration in this precedence order:

```text
CLI arguments > environment variables > config.toml > built-in defaults
```

Default config path:

```text
~/.config/yx-workflow/config.toml
```

Override config path:

```bash
python3 /home/yanxin/.codex/skills/yx-workflow/skills/agent-work-tracker/scripts/record_work.py --config /path/to/config.toml
```

Use `config.example.toml` as the template for a new machine.

Supported config:

```toml
[obsidian]
vault_root = "/home/yanxin/personal/ObsidianNotes"
agent_tracking_dir = "Note/Work/TianYan/AgentTracking"
project_doc_dir = "Note/Work/TianYan/项目文档"
weekly_report_dir = "Note/Work/TianYan/工作周报"

[git]
sync = true
commit_message = "docs: 记录 agent 工作进展"
```

Supported environment variables:

- `YX_WORKFLOW_CONFIG`
- `AGENT_WORK_TRACKER_VAULT`
- `AGENT_WORK_TRACKER_TRACKING_DIR`
- `AGENT_WORK_TRACKER_PROJECT_DOC_DIR`
- `AGENT_WORK_TRACKER_WEEKLY_REPORT_DIR`
- `AGENT_WORK_TRACKER_GIT_SYNC`
- `AGENT_WORK_TRACKER_COMMIT_MESSAGE`

## Default Paths

- Obsidian vault: `/home/yanxin/personal/ObsidianNotes`
- Raw tracking notes: `Note/Work/TianYan/AgentTracking/`
- Project docs: `Note/Work/TianYan/项目文档/`
- Weekly reports: `Note/Work/TianYan/工作周报/`

Tracking files use the Friday week-ending date:

```text
YYYY-MM-DD Agent Tracking.md
```

## Record Completed Work

Use `scripts/record_work.py` and pass a compact JSON object. Keep the summary factual and useful for a future weekly report.

Required fields:

- `title`
- `summary`

Optional fields:

- `status` defaults to `completed`
- `repo`
- `project`
- `outputs`
- `verification`
- `next_steps`
- `week_report_candidates`

Example:

```bash
python3 /home/yanxin/.codex/skills/yx-workflow/skills/agent-work-tracker/scripts/record_work.py <<'JSON'
{
  "title": "完成 Agent 工作追踪 skill",
  "status": "completed",
  "repo": "/home/yanxin/personal/skills",
  "project": "AgentTracking",
  "summary": "新增 agent-work-tracker skill、记录脚本、测试和全局触发指令。",
  "outputs": ["skills/agent-work-tracker/SKILL.md", "skills/agent-work-tracker/scripts/record_work.py"],
  "verification": ["python3 -m unittest discover -s tests -v"],
  "next_steps": ["重启 Codex 以加载新 skill"]
}
JSON
```

When Git sync is enabled, the script performs the required sync sequence:

1. `git pull --rebase --autostash`
2. write the weekly AgentTracking file and a matched existing project document
3. `git add` only touched files
4. `git commit -m "docs: 记录 agent 工作进展"`
5. `git pull --rebase --autostash`
6. `git push`

If a target file already has local changes before writing, stop and report the issue. Do not stage unrelated Obsidian changes.

## Project Document Policy

Only update a project document when `project` clearly matches one existing file under `Note/Work/TianYan/项目文档/`.

- exact filename stem match is clear
- unique normalized partial match is clear
- no match or multiple matches means only AgentTracking is updated

Never create a new project document automatically.

## Weekly Report Generation

When the user asks for a weekly report, read that week's AgentTracking file plus relevant project docs, then update the existing Friday-based weekly report file in `Note/Work/TianYan/工作周报/`.

Use the existing report style:

- `## 上周工作总结`
- `## 本周目标`
- `## 本周工作记录`
- `## 本周工作总结`

Keep raw task details in AgentTracking. The weekly report should group work by project/theme and use concise outcome-focused bullets.
