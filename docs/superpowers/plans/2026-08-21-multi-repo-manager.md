# Multi-Repo Manager Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a concise personal skill for document-driven multi-repository requirement workspaces.

**Architecture:** Keep the reusable lifecycle and safety invariants in one self-contained `SKILL.md`; keep project-specific facts in each manager repository. Register the sub-skill through the existing `yx-workflow` router and repository documentation.

**Tech Stack:** Markdown skill instructions, YAML UI metadata, Python `unittest` layout checks, skill-creator validator.

## Global Constraints

- Name the skill `multi-repo-manager`.
- Parent manager repositories use the main checkout of `main` without parent branches, worktrees, or MRs.
- Business development occurs only in participating development repositories' worktrees.
- Repository instructions and current Git state override generic skill defaults.
- Do not add scripts, bundled requirement templates, or YAML state files.
- Do not modify `scheduler-manager`, `carina`, or `monitor` in this implementation.

---

### Task 1: Add the failing skill layout contract

**Files:**
- Modify: `tests/test_skill_layout.py`

**Interfaces:**
- Consumes: existing `ROOT` path and `unittest` layout conventions.
- Produces: `test_multi_repo_manager_is_sub_skill`, which requires the skill entrypoint, UI metadata, and root router entry.

- [x] **Step 1: Add the failing test**

```python
def test_multi_repo_manager_is_sub_skill(self):
    skill = ROOT / "skills/multi-repo-manager"

    self.assertTrue((skill / "SKILL.md").is_file())
    self.assertTrue((skill / "agents/openai.yaml").is_file())
    self.assertIn("skills/multi-repo-manager/", (ROOT / "SKILL.md").read_text())
    self.assertFalse((ROOT / "multi-repo-manager/SKILL.md").exists())
```

- [x] **Step 2: Run the test and verify RED**

Run: `python3 -m unittest tests.test_skill_layout.SkillLayoutTests.test_multi_repo_manager_is_sub_skill -v`

Expected: FAIL because `skills/multi-repo-manager/SKILL.md` does not exist.

### Task 2: Implement and register the skill

**Files:**
- Create: `skills/multi-repo-manager/SKILL.md`
- Create: `skills/multi-repo-manager/agents/openai.yaml`
- Modify: `SKILL.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: local manager-repository instructions, `requirements/`, `repos/`, `.gitmodules`, and Git state.
- Produces: a discoverable `multi-repo-manager` workflow with bootstrap, audit, register, advance, and close modes.

- [x] **Step 1: Initialize the skill structure**

Run:

```bash
python3 /home/yanxin/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  multi-repo-manager \
  --path skills \
  --interface 'display_name=Multi-Repo Manager' \
  --interface 'short_description=管理文档驱动的跨仓库需求、基线、开发位置和交付状态' \
  --interface 'default_prompt=Use $multi-repo-manager to audit or advance this cross-repository requirement workspace.'
```

- [x] **Step 2: Write the minimal skill**

The entrypoint must define mode selection, repository authority, parent/subrepository boundaries, requirement state fields, lifecycle actions, and cleanup safeguards from the approved design.

- [x] **Step 3: Add UI metadata**

Set display name `Multi-Repo Manager`, a concise Chinese short description, and a default prompt that explicitly invokes `$multi-repo-manager`.

- [x] **Step 4: Register the sub-skill**

Add `skills/multi-repo-manager/` and its routing triggers to root `SKILL.md`; add a concise section and directory entry to `README.md`.

- [x] **Step 5: Run the layout test and verify GREEN**

Run: `python3 -m unittest tests.test_skill_layout.SkillLayoutTests.test_multi_repo_manager_is_sub_skill -v`

Expected: PASS.

### Task 3: Validate the completed skill

**Files:**
- Verify: `skills/multi-repo-manager/SKILL.md`
- Verify: `skills/multi-repo-manager/agents/openai.yaml`
- Verify: repository-wide changed files

**Interfaces:**
- Consumes: completed skill and repository validation commands.
- Produces: fresh evidence for layout, metadata, concise instructions, and clean diff scope.

- [x] **Step 1: Run all unit tests**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests pass.

- [x] **Step 2: Run skill validation**

Run: `python3 /home/yanxin/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/multi-repo-manager`

Expected: validation succeeds.

- [x] **Step 3: Validate metadata and scope**

Run YAML parsing for `agents/openai.yaml`, `wc -w skills/multi-repo-manager/SKILL.md`, `git diff --check`, and inspect `git diff --stat` plus the complete diff.

Expected: valid YAML, concise skill text, no whitespace errors, and only planned files changed.

- [x] **Step 4: Commit the implementation**

Use a Conventional Commit with English type/scope and a concise Chinese subject that matches the final diff.
