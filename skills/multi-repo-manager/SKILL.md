---
name: multi-repo-manager
description: Use when a document-driven parent repository coordinates requirements across multiple Git repositories through requirements/, repos/ submodules, and nested worktrees.
---

# Multi-Repo Manager

## Core Model

The parent is a requirement control plane, not a business-code repository. Documents hold live state; gitlinks are cloneable entry points.

## Establish Authority And Mode

1. Read the request, parent instructions, README, template, requirements, `.gitmodules`, and Git/worktree state.
2. Read child instructions before choosing branches, tests, or delivery.
3. Classify the request as `bootstrap`, `audit`, `register`, `advance`, `close`,
   or `update-manager-state`.

User and local instructions override this skill. Report conflicts before mutation. Read-only requests cannot mutate files, refs, worktrees, commits, MRs, or remotes.

## Repository Boundaries

- Maintain parent `main` in its main checkout; create no parent branch, worktree, or MR.
- Keep business changes out of `repos/<repo>` submodule checkouts.
- Use a `reference` repository read-only from its submodule checkout.
- Create a `development` worktree at `repos/<repo>/.worktree/<requirement>/` from a fetched baseline.
- Follow each development repository's verification and delivery policy. Never propagate parent direct-main.
- Change a gitlink only for a requested shared entry point or baseline.

## Requirement Record

Keep `requirements/<requirement>/` as the durable status entry point. Use the local template. Record:

- background, goal, scope, non-goals, phase, and date
- each repository's role, responsibility, fetched base branch, and full base SHA
- development branch, worktree, commit, MR or repository-specific delivery state
- completed and pending work, blockers, decisions, verification evidence, and unverified scope

Do not write “latest” without a successful fetch. On fetch failure, record the blocker instead of treating a local remote-tracking ref as current.

## Lifecycle

### Bootstrap

When asked, align parent instructions, README, and `requirements/_template/README.md`. Preserve history and unrelated files. Do not add another state system unless requested.

### Audit

Compare requirement records with available parent and child Git state: roles, baselines, worktrees, HEADs, dirty files, and delivery. Report drift, stale evidence, and unverified remote state without reconciling it. Fetch only when authorized.

### Register

Update parent `main`. Evolve an existing matching scope instead of duplicating it; otherwise use the template. Assign roles, then fetch and record base SHAs before worktrees.

### Advance

Work only in development worktrees. Synchronize actual commits, reviews, verification, blockers, and delivery state. Distinguish planned from completed work.

### Close

Verify delivery against fetched targets. Record evidence and unverified scope. Mark eligible worktrees ready for cleanup; remove them only with separate explicit cleanup authorization. Preserve the requirement directory.

### Update Manager State

Treat an explicit request to "update the manager repo state" as authorization
to complete the related requirement's full local closeout:

1. Clean up local worktrees that are no longer needed.
2. Update the requirement record with delivered, pending, unverified, cleanup,
   and repository state.
3. Fast-forward each related submodule checkout to its recorded remote branch
   and stage the resulting gitlink update in the parent repository.

Before removing a worktree, resolve its exact registered path, verify that it is
clean, and confirm its commit is contained in the delivered target or is
patch-equivalent to an integrated commit. Preserve dirty worktrees and branches
with unique unmerged work, and record why they were not removed.

Before updating a submodule, fetch its recorded remote branch and verify that
the main checkout has no tracked or unrelated untracked changes that could
interfere. Registered `.worktree/` directories alone are not business changes.
Use a fast-forward-only update such as `git pull --ff-only origin <branch>`; do
not reset, force-update, or silently switch branches. Update only submodules
related to the requirement. Record the fetched full SHA and the final gitlink
in the requirement document.

The request authorizes removal of eligible related worktrees and updating the
related gitlinks. It does not authorize deleting local or remote branches,
cleaning unrelated worktrees, or changing unrelated submodules. If a worktree
or submodule cannot be updated safely, complete the other safe items and report
the exact remaining state.

## Delivery Safety

- Preserve unrelated dirty files. Stage only requirement-owned paths or hunks; if an authorized file overlaps unrelated edits that cannot be isolated safely, stop and report it.
- Do not overwrite existing branches or worktrees.
- Before cleanup, resolve the registered path and check dirty state, HEAD, and target containment. Do not use force or recursive deletion as routine cleanup.
- A request to update manager repo state is explicit cleanup and gitlink-update
  authorization only within the related requirement, as defined above.
- Parent commit/push is in scope only for an authorized mutating lifecycle action whose repository instructions require direct-main delivery.
- After delivery, verify the pushed remote SHA before reporting completion.
