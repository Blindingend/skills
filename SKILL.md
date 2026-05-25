---
name: yx-workflow
description: Use when working with Yanxin's reusable Codex workflows, including agent work tracking, Obsidian work notes, weekly reports, and personal automation routines.
---

# yx-workflow

`yx-workflow` is the top-level entry point for Yanxin's personal Codex workflows. It routes tasks to the closest bundled sub-skill and keeps shared workflow conventions in one discoverable place.

## Sub-skills

The bundled sub-skills live in `skills/`:

- `skills/agent-work-tracker/`

## Routing Rules

Choose the closest matching sub-skill:

- completed substantial task, project milestone, implementation, debugging session, deployment, CI fix, investigation, or plan that should be recorded for weekly reports -> `skills/agent-work-tracker/`
- generating or updating a weekly work report from tracked agent work -> `skills/agent-work-tracker/`

If a task clearly belongs to a bundled sub-skill, use that sub-skill and stop treating `yx-workflow` as the main procedure.

