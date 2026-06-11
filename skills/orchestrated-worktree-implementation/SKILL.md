---
name: orchestrated-worktree-implementation
description: Orchestrate implementation of an already designed coding task using subagents, isolated git worktrees, review gates, branch merging, and cleanup. Use when Codex is asked to execute a multi-step implementation plan or design document and should act mainly as manager/reviewer while parallel subagents implement independent parts without conflicting in the same worktree.
---

# Orchestrated Worktree Implementation

Use this skill to turn a prepared design, plan, or checklist into code with controlled parallelism. The main agent owns planning, dispatch, review, verification, merge, and cleanup. Subagents own scoped implementation in isolated worktrees.

## Core Rules

- Keep changes as small as possible while satisfying the plan.
- Do not expand requirements, add speculative abstractions, or solve adjacent problems.
- Do not run subagents in the current worktree.
- Do not parallelize tasks that touch the same files, shared contracts, migration order, or test targets in ways likely to conflict.
- Do not merge a subagent branch until the main agent has reviewed design, correctness, performance, tests, and diff scope.
- Do not claim success without verification evidence from the relevant worktree and, after merge, from the main worktree.

## Workflow

1. Read the design document or implementation plan completely.
2. Inspect repository state: current branch, dirty files, build/test commands, and existing worktree conventions.
3. Split work into dependency-aware tasks:
   - Parallelize only independent tasks with disjoint files or stable interfaces.
   - Serialize foundational API changes, schema/contract changes, and broad rewiring.
   - Prefer smaller reviewable branches over one large branch.
4. For each task, create or assign a dedicated worktree and branch from the current base branch.
5. Dispatch each subagent with a narrow contract:
   - exact task scope and files likely involved
   - branch/worktree path
   - required tests/build commands
   - commit and push requirement
   - instruction to avoid unrelated refactors and over-design
6. Track each subagent branch to completion. A completed subagent must provide:
   - branch name and worktree path
   - commit hash
   - pushed remote branch
   - summary of changes
   - commands run and results
   - known risks or skipped checks
7. Review each branch before merge.
8. Merge approved branches into the main worktree branch in dependency order.
9. Run post-merge verification in the main worktree.
10. Clean up merged worktrees and local/remote task branches when safe.

## Worktree And Branch Discipline

- Use branch names that make ownership clear, such as `codex/<topic>-<task>`.
- Put task worktrees under the repository's existing worktree location when one exists, commonly `.worktrees/<task>`.
- Check for dirty files before creating, merging, or deleting worktrees.
- Never delete a worktree or branch with unmerged or unexplained changes.
- Push subagent branches before review so the main agent can inspect the exact branch state.

## Dispatch Contract

Give each subagent enough context to implement safely, but do not ask it to redesign the whole project. Use this shape:

```text
Implement Task <N> from <plan path> in worktree <absolute path> on branch <branch>.
Scope: <specific behavior and files>.
Do not touch unrelated files or broaden the design.
Run: <focused tests/build commands>.
Commit your changes with a clear message and push the branch.
Report commit hash, test output summary, risks, and any skipped checks.
```

If a task depends on another branch, do not dispatch it until that dependency is merged or until the dependent branch can be based on the prerequisite branch without creating merge ambiguity.

## Review Gate

Review from the main agent's global perspective, not only whether the local feature appears to work.

Check:

- Design fit: implementation preserves the plan's architecture and contracts.
- Scope control: no unrelated refactors, style churn, hidden behavior changes, or speculative flexibility.
- Correctness: edge cases, error handling, ordering guarantees, lifecycle, cleanup, and failure modes.
- Performance: hot paths avoid unnecessary allocations, blocking, contention, avoidable maps, or repeated expensive work.
- Integration: shared APIs, async boundaries, schema/metadata compatibility, and downstream assumptions remain coherent.
- Tests: focused tests cover the new contract and fail-fast cases; skipped tests are justified.
- Maintainability: code is readable, locally idiomatic, and avoids premature abstractions.

If review fails, write concrete review criteria and send the branch back for another iteration. Keep the feedback tied to observable defects, risks, or mismatches with the plan. Repeat until the branch passes or the work is genuinely blocked.

## Merge And Verification

- Merge approved branches one at a time in dependency order.
- Resolve conflicts by preserving the plan's architecture, not by keeping whichever branch touched code last.
- After each risky merge, run the smallest relevant verification before continuing.
- After all merges, run the plan's final focused tests and build commands from the main worktree.
- Inspect `git diff --check` and the final diff scope before declaring completion.

## Cleanup

After merged work is verified:

- Remove task worktrees that are clean and no longer needed.
- Delete merged local task branches.
- Delete merged remote task branches when the workflow allows it.
- Keep branches/worktrees if tests failed, review is unresolved, or the user may need to inspect them.

## When Subagents Are Unavailable

If the environment cannot create subagents or isolated worktrees, do not simulate parallel ownership in the current worktree. Explain the limitation and either proceed serially in separate worktrees yourself or ask the user how to continue when that choice affects risk.
