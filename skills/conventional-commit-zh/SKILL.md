---
name: conventional-commit-zh
description: "Generate Conventional Commits messages with an English type and optional scope, but Chinese title and Chinese body. Use when asked to draft a commit message, summarize staged changes into a commit, align with a repository's historical commit style, or decide the right `type(scope): subject` format before committing."
---

# Conventional Commit Zh

## Overview

Generate commit messages that satisfy the Conventional Commits 1.0.0 structure while matching the target repository's local style. Keep `type` and `scope` in English, then write the subject and body in concise Chinese.

## Workflow

1. Inspect commit context in this order:
   - `git diff --cached --stat` and `git diff --cached`
   - If nothing is staged, inspect `git status --short` and `git diff`
   - `git log --oneline -20` to learn repository style
2. Infer the dominant change intent. If the diff mixes unrelated intents, say so and recommend splitting the commit before drafting a message.
3. Choose `type` from the Conventional Commits spec:
   - `feat`: user-facing feature or behavior addition
   - `fix`: bug fix or behavior correction
   - `refactor`: internal restructuring without behavior change
   - `test`: test-only change
   - `docs`: documentation-only change
   - `ci`: CI, workflow, or build pipeline change
   - `chore`: maintenance change that fits none of the above
   - `perf`: measurable performance improvement
   - `build`: build system or dependency packaging change
4. Choose `scope` only when it adds signal. Prefer the repository's existing module names, usually lower-case identifiers such as `min_particle`, `compare_tool`, `ci`, or `test`.
5. Write the final message in Chinese:
   - Title format: `<type>(<scope>): 中文标题` or `<type>: 中文标题`
   - Body: Chinese only, 2-4 short lines, focused on what changed and why
   - Footer: add only when required, for example `BREAKING CHANGE: ...`

## Style Rules

- Follow the Conventional Commits structure exactly.
- Keep `type` English and lowercase.
- Keep `scope` English, lowercase, and repository-native.
- Keep the title concise and specific. Do not end it with punctuation.
- Prefer Chinese verbs that describe the actual change, not vague summaries like “更新代码”.
- Do not turn the body into a file inventory. Explain intent, behavior, or important implementation points.
- If the repository history already favors Chinese titles with English `type(scope)`, preserve that pattern.
- If the repo history is inconsistent, prefer the dominant recent pattern that is still valid Conventional Commits.

## Repository Alignment

When learning repository style from history, pay attention to:

- Whether `scope` is frequently used
- Whether the project prefers snake_case scopes such as `min_particle`
- Whether titles are terse fixes such as `fix(min_particle): 修复 ...`
- Whether the body is commonly omitted

When the user explicitly asks for a body, always provide one even if the repository often omits it.

## Output Format

Return only:

```text
<type>(<scope>): 中文标题

中文正文第一行
中文正文第二行
```

If `scope` is unnecessary:

```text
<type>: 中文标题

中文正文第一行
中文正文第二行
```

## Quality Bar

Before drafting, verify:

- The message matches the actual diff, not a guessed task name
- The selected `type` is justified by behavior, not by file path alone
- The title can stand on its own without reading the body
- The body adds useful context instead of repeating the title
