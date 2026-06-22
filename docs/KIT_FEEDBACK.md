<!--
KIT FEEDBACK — a running log of improvements to the *baseline starter kit* discovered while
building THIS project. Feedback FROM the project TO the kit (distinct from ORIGIN.md, which
records the kit's founding lessons from a prior project). Carry this stub into every project;
append a row as each lesson surfaces. At a later "kit pass," each row becomes a concrete change
to the baseline so the next project doesn't hit it. See 00_WAYS_OF_WORKING.md §9.
-->

# Kit feedback — improvements discovered while building <Project>

| Field   | Value                                                                                        |
| ------- | -------------------------------------------------------------------------------------------- |
| Status  | Living                                                                                        |
| Owner   | <name>                                                                                        |
| Purpose | Capture baseline-kit improvements found while building a real project, for a later kit pass.  |
| Related | [`ORIGIN.md`](../ORIGIN.md) (kit's founding lessons)                                          |

## How to use this

Each item is something the **kit itself** should change so the *next* project doesn't hit it —
not a fix scoped to this project. Priority is the **kit-impact**, not this project's. "Source"
is where it surfaced here. When something would have been a better baseline default (a tooling
gap, an example-code default, doc/process friction), add a row **as it surfaces** rather than
only fixing it locally — capturing it later is how lessons get lost.

Good candidates:

- **Gate/tooling that's documented but not runnable** from commit zero (lint, e2e, a11y scan,
  perf harness, CI that auto-fails before it's wired).
- **Example-code defaults** the scaffold should ship, so the right pattern is copied rather than
  retrofitted later as an "engineering-health" slice.
- **Doc/process friction** — a missing template section, a handoff gap, summary/link drift.

## Open items

| # | Priority | Kit improvement | Source | Recommendation |
| - | -------- | --------------- | ------ | -------------- |
| K1 | … | … | … | … |

## Notes for the kit pass

- Group related items; the highest-value cluster is usually a single theme. Note which items are
  already **validated** in-project (the proven artifact/shape to port) vs. still advice-only.
