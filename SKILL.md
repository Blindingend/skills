---
name: yx-workflow
description: Use when working with Yanxin's reusable Codex workflows, including agent work tracking, Obsidian work notes, weekly reports, development guidelines, Chinese writing, and personal automation routines.
---

# yx-workflow

`yx-workflow` is the top-level entry point for Yanxin's personal Codex workflows. It routes tasks to the closest bundled sub-skill and keeps shared workflow conventions in one discoverable place.

## Sub-skills

The bundled sub-skills live in `skills/`:

- `skills/agent-work-tracker/`
- `skills/conventional-commit-zh/`
- `skills/dev-machine-bootstrap/`
- `skills/development-guidelines/`
- `skills/efficient-semantic-implementation/`
- `skills/multi-repo-manager/`
- `skills/orchestrated-worktree-implementation/`
- `skills/trade-dev/`
- `skills/write-chinese/`
- `skills/write-like-xin/`

## Routing Rules

Choose the closest matching sub-skill:

- completed substantial task, project milestone, implementation, debugging session, deployment, CI fix, investigation, or plan that should be recorded for weekly reports -> `skills/agent-work-tracker/`
- generating or updating a weekly work report from tracked agent work -> `skills/agent-work-tracker/`
- drafting a Conventional Commits message with English type/scope and Chinese title/body -> `skills/conventional-commit-zh/`
- summarizing staged changes into a commit message or aligning with a repository's commit history -> `skills/conventional-commit-zh/`
- inspecting, planning, or applying a Linux developer terminal bootstrap for local or SSH hosts -> `skills/dev-machine-bootstrap/`
- classifying reusable dotfiles or preparing safe zsh, tmux, git, pixi, and alias setup -> `skills/dev-machine-bootstrap/`
- implementing, reviewing, refactoring, or naming code that should follow Xin's reusable development standards, including Boolean naming -> `skills/development-guidelines/`
- implementing non-trivial backend, C++, data pipeline, stateful, storage, cache, hot-path, or multi-step code where semantic modeling, planning, low-copy data reuse, efficient data structures, ownership, and existing component reuse matter -> `skills/efficient-semantic-implementation/`
- auditing, registering, advancing, closing, or bootstrapping a document-driven cross-repository requirement workspace with `requirements/`, `repos/` submodules, and repository-local development worktrees -> `skills/multi-repo-manager/`
- implementing an already designed coding task with subagents, isolated worktrees, review gates, merge, verification, and cleanup -> `skills/orchestrated-worktree-implementation/`
- implementing or reviewing trading-system behavior involving trade dates, offline replay, backtests, online market data, or date configuration -> `skills/trade-dev/`
- generating, rewriting, editing, reviewing, or polishing Chinese prose or UI copy with concise, concrete, non-exaggerated wording -> `skills/write-chinese/`
- drafting or revising Chinese content specifically in Xin's confirmed personal style -> `skills/write-like-xin/`

If a task clearly belongs to a bundled sub-skill, use that sub-skill and stop treating `yx-workflow` as the main procedure.
