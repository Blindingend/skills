---
name: yx-workflow
description: Use when working with Yanxin's reusable Codex workflows, including agent work tracking, Obsidian work notes, weekly reports, and personal automation routines.
---

# yx-workflow

`yx-workflow` is the top-level entry point for Yanxin's personal Codex workflows. It routes tasks to the closest bundled sub-skill and keeps shared workflow conventions in one discoverable place.

## Sub-skills

The bundled sub-skills live in `skills/`:

- `skills/agent-work-tracker/`
- `skills/conventional-commit-zh/`
- `skills/dev-machine-bootstrap/`
- `skills/orchestrated-worktree-implementation/`

## Routing Rules

Choose the closest matching sub-skill:

- completed substantial task, project milestone, implementation, debugging session, deployment, CI fix, investigation, or plan that should be recorded for weekly reports -> `skills/agent-work-tracker/`
- generating or updating a weekly work report from tracked agent work -> `skills/agent-work-tracker/`
- drafting a Conventional Commits message with English type/scope and Chinese title/body -> `skills/conventional-commit-zh/`
- summarizing staged changes into a commit message or aligning with a repository's commit history -> `skills/conventional-commit-zh/`
- inspecting, planning, or applying a Linux developer terminal bootstrap for local or SSH hosts -> `skills/dev-machine-bootstrap/`
- classifying reusable dotfiles or preparing safe zsh, tmux, git, pixi, and alias setup -> `skills/dev-machine-bootstrap/`
- implementing an already designed coding task with subagents, isolated worktrees, review gates, merge, verification, and cleanup -> `skills/orchestrated-worktree-implementation/`

If a task clearly belongs to a bundled sub-skill, use that sub-skill and stop treating `yx-workflow` as the main procedure.
