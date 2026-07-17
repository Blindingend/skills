---
name: development-guidelines
description: Apply Xin's reusable software development conventions while implementing, reviewing, refactoring, or naming code. Use when code should follow personal development standards, including Boolean naming, or when adding and applying new guideline topics from this extensible development skill set.
---

# Development Guidelines

Apply the relevant personal development standards without loading unrelated guidance. Treat repository-specific conventions and explicit user requirements as higher priority.

## Apply the guidelines

1. Inspect the target repository's existing conventions and nearby code.
2. Select the relevant topic from the reference catalog below.
3. Read the matching reference before implementing or reviewing that topic.
4. Apply the guideline consistently across definitions, call sites, tests, and documentation in scope.
5. Preserve existing behavior unless the task explicitly requests a behavior change.
6. Validate with the repository's focused checks.

If a personal guideline conflicts with an explicit user requirement or an established repository contract, follow the explicit requirement or repository contract and state the conflict when it affects the result.

## Reference catalog

- Boolean variables, fields, parameters, predicates, and functions: read [references/boolean-naming.md](references/boolean-naming.md).

## Extend the skill set

Add each new development topic as one focused file under `references/`. Keep the main skill limited to the shared workflow and reference catalog. Avoid copying detailed rules into both places.
