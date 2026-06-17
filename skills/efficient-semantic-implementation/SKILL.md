---
name: efficient-semantic-implementation
description: Use before implementing non-trivial backend, C++, data pipeline, stateful operator, batch processor, storage sink, cache, performance-sensitive code, or any multi-step change. Guides planning, global flow review, semantic modeling, ownership design, low-copy data reuse, efficient data structures, reuse of existing components, explicit policies, and implementation hygiene.
---

# Efficient Semantic Implementation

Use this skill before substantial implementation work, especially when code touches shared data flow, hot paths, stateful logic, caches, storage sinks, output schemas, or multi-step changes.

The goal is to avoid code that is locally workable but globally awkward: wrong abstractions, unclear ownership, unnecessary data copies, inefficient containers, hidden policies, duplicated project logic, or implementations that follow an old plan without re-checking reality.

## Core Principle

Implement from this sequence:

1. Re-check the plan and the whole system flow.
2. Model the real domain concepts.
3. Decide ownership and data lifetime.
4. Design for data reuse and low-copy flow.
5. Choose data structures by access pattern and cost.
6. Reuse existing project components before adding new ones.
7. Make correctness policies explicit.
8. Validate semantics, integration, and performance.

Good code should make the correct model natural and the wrong model hard to express.

## Plan Before Large Changes

Before a large or multi-step modification, create or refresh a concrete plan. Do not execute an old spec mechanically; plans become stale as code, constraints, and understanding change.

The plan must cover:

- Goal: behavior or capability being changed.
- Scope: modules involved and intentionally excluded.
- Current flow: where data enters, transforms, batches, emits, persists, and gets consumed.
- Design: domain concepts, identities, ownership, reused components, and new code needed.
- Risks: compatibility, correctness, performance, lifecycle, and failure modes.
- Validation: tests, replay, benchmark, or inspection that proves the change.

## Re-Plan Before Each Subtask

For each meaningful subtask, do a small fresh design pass before editing.

Ask:

- What is this subtask changing?
- How does it fit the whole logic flow and data flow?
- Does the earlier plan still apply?
- Is there an existing type, helper, operator, cache, writer, config, or test utility to reuse?
- Will this local change create inconsistency upstream or downstream?
- What focused validation should run after this step?

If a subtask invalidates a plan assumption, update the plan before continuing.

## Trace The Whole Flow Before Local Fixes

Before changing code, trace the relevant flow end to end:

```text
source
  -> parsing / normalization
  -> canonical identity
  -> state / cache / operator
  -> transformation
  -> batch / message
  -> sink / output
  -> downstream contract
```

For each stage, understand:

- input and output shape
- identity used
- ownership and lifetime
- ordering and completeness guarantees
- edge-case policy
- downstream expectations

Do not patch a local symptom without checking the surrounding flow.

## Model Real Concepts First

Do not use implementation conveniences as domain concepts.

Bad signs:

- display labels used as internal identity
- file paths used as business keys
- strings used where stable typed IDs should exist
- timestamps formatted before core logic
- type names that do not match the real role

Rules:

- Identity, label, path, and serialization format must be separate.
- Internal keys must be lossless and stable.
- Human-readable formats belong at system boundaries.
- Type names must match business meaning.

## Decide Ownership Before Data Flow

For every large or shared object, answer:

- Who owns it?
- Who can mutate it?
- Who only reads it?
- How long is it valid?
- Can consumers keep references, views, handles, or only indices?
- What invalidates it?

Default preference:

- one clear owner
- many read-only borrowers
- immutable shared data where possible
- lightweight handles, ordinals, indices, references, or views instead of copies

Avoid unclear ownership where every layer keeps its own copy.

## Prefer Reuse Over Copy

Large data should usually be stored once and referenced cheaply.

Preferred patterns:

- Store canonical data in a central table, arena, cache, catalog, context, or global manager.
- Pass stable indices, ordinals, handles, references, or views between components.
- Use `std::span`, `std::string_view`, references, pointers, or typed IDs when lifetime is clear.
- Use move semantics when ownership is transferred.
- Use `shared_ptr` only when shared lifetime is real.

Rules:

- Do not copy vectors, strings, maps, or large structs across layers by habit.
- Do not duplicate per-record metadata that can be interned, indexed, or looked up from canonical storage.
- Do not repeatedly parse, normalize, or format the same key on the hot path.
- Prefer precomputed ordinals over repeated string lookup.

`shared_ptr` is an ownership tool, not a performance tool. It has reference-count overhead and can hide lifecycle problems. Prefer explicit owner plus borrowed view, handle, or index when possible.

## Use Index-Based Design For Shared Static Data

When many runtime records refer to the same static universe, prefer:

```text
canonical table:
  entity_key -> ordinal
  ordinal -> static fields
  ordinal -> output slot
  ordinal -> metadata

runtime state:
  ordinal
  mutable values
```

Instead of passing full strings or full static records everywhere.

Rules:

- Use stable integer IDs for repeated joins and lookups.
- Intern repeated strings.
- Keep static or canonical data immutable after initialization.
- If indices may become stale, use generation or version checks.

## Choose Data Structures By Access Pattern

Do not choose containers by habit.

Ask:

- Do I need ordering?
- Do I need fast lookup?
- Do I need contiguous iteration?
- Do I need pointer stability?
- How many elements?
- How often do I insert or erase?
- Is this on the hot path?

Default preferences:

- `std::vector` for dense indexed data and iteration.
- `std::array` for fixed small data.
- `std::unordered_map` or a flat hash map for lookup when ordering is not needed.
- sorted vector plus binary search for small mostly-static maps.
- bitset or compact flags for dense boolean state.
- arena or pool allocation when many same-lifetime objects are created.

Avoid by default on hot paths:

- `std::map`
- `std::set`
- linked lists
- string keys
- per-record heap allocation
- repeated formatting or parsing
- deep object graphs
- owning containers inside every small state object

Use `std::map` only when sorted traversal, iterator stability, or ordered `lower_bound` semantics are actually required.

## Make Hot-Path Costs Explicit

Before implementation, write the cost model.

Per input record:

- allocations
- hash or tree lookups
- string operations
- copies
- branches
- expected complexity

Per active state:

- memory
- object count
- cache locality
- cleanup cost

Per emit or flush:

- rows scanned
- rows copied
- sorting cost
- serialization cost

Rules:

- Hot paths should avoid allocation.
- Hot paths should avoid string formatting.
- Hot paths should avoid timezone or time-format conversions.
- Hot paths should avoid node-based containers unless justified.
- Hot paths should not copy large payloads unless ownership transfer requires it.

## Separate Core Model From Boundary Format

Core logic should use typed domain objects.

Boundary layers handle:

- file names
- storage paths
- parquet, CSV, JSON, or Redis formats
- logs
- human-readable labels
- compatibility formatting

Rules:

- Formatting belongs at the edge.
- Serialization belongs at the edge.
- Core state must not depend on output path layout.
- Publish markers such as `.done` must have a documented contract.

## Reuse Existing Components First

Before adding new code, search for:

- existing domain types
- existing parsers and formatters
- existing identity or key helpers
- existing caches or global managers
- existing operators, sinks, writers, and async helpers
- existing config patterns
- existing test helpers
- existing benchmark or replay tools

Rules:

- Prefer established project components over new local helpers.
- Match the project's ownership, config, logging, and error-handling style.
- Add a new abstraction only when it expresses a missing concept or removes real duplication.
- Do not introduce a parallel implementation of logic that already exists elsewhere.

## Make Policies Explicit

Do not hide important behavior in incidental control flow.

Use named policies for:

- duplicate data
- late data
- missing data
- unknown keys
- partial publish
- overwrite behavior
- backpressure
- overflow
- retry
- compaction

Rules:

- If behavior affects correctness, give it a name.
- If a downstream consumer depends on it, document it in the type or config.
- If behavior differs between online, offline, replay, or test mode, make that explicit.

## Keep State Compact And Local

State should contain only what it owns or must mutate.

Avoid:

- copying static fields into every state object
- storing full payloads when an index is enough
- duplicating keys already known by the enclosing map
- storing both formatted and raw representations without need
- nested maps where a flat indexed layout would work

Prefer:

- compact structs
- structure-of-arrays or dense arrays when access is columnar
- sparse observed rows when data is sparse
- ordinals for repeated entity references
- separate immutable metadata from mutable runtime state

## Validate With Adversarial Cases

Tests and benchmarks must protect the model, not mirror the implementation.

Always consider:

- identity collision
- duplicate input
- missing input
- late input
- empty input
- boundary time or window
- cross-day or multi-session cases
- partial failure during publish
- repeated publish
- large universe or high cardinality

Benchmarks should compare realistic layouts, not just old implementation against new implementation.

## Hard Rules

- Do not start a large change without a current plan.
- Do not execute an old plan without re-checking the whole flow.
- Do not patch local code without checking upstream and downstream contracts.
- Do not create new helpers before searching for existing components.
- Do not use display labels as identity.
- Do not use strings as repeated hot-path keys when ordinals can be used.
- Do not copy large data across layers without a reason.
- Do not store the same static data in many runtime states.
- Do not use `std::map` on hot paths unless ordering is required and justified.
- Do not hide ownership behind `shared_ptr` unless shared lifetime is real.
- Do not let file format or output path define core semantics.
- Do not implement edge-case behavior without naming the policy.
- Do not benchmark only against an old flawed model.

## Short Memory Hooks

Use these as quick implementation checks:

```text
Plan before changing.
Trace the whole flow.
Reuse existing components.
Store canonical data once.
Borrow by view.
Transfer by move.
Share by explicit owner.
Refer by index.
Format only at the edge.
Choose containers by access pattern.
Name correctness policies.
Validate against adversarial cases.
```
