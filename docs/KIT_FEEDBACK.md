---
id:     DOC-KIT-FEEDBACK
type:   feedback-log
status: Living
---
<!--
KIT FEEDBACK — a running log of improvements to the *baseline starter kit* discovered while
building THIS project. Feedback FROM the project TO the kit (distinct from ORIGIN.md, which
records the kit's founding lessons from a prior project). Carry this stub into every project;
append a row as each lesson surfaces. At a later "kit pass," each row becomes a concrete change
to the baseline so the next project doesn't hit it. See 00_WAYS_OF_WORKING.md §9.
-->

# Kit feedback — improvements discovered while building labs-hub

| Field   | Value                                                                                        |
| ------- | -------------------------------------------------------------------------------------------- |
| Status  | Living                                                                                        |
| Owner   | wes-cutting                                                                                   |
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

*None open — K1–K5 all landed in **kit pass 4** (see "Ported to the kit" below). Append new
rows here as they surface, keeping this header row intact so the table still renders:*

| # | Priority | Kit improvement | Source | Recommendation |
| - | -------- | --------------- | ------ | -------------- |

## Ported to the kit

**Kit pass 4** — folded into `baseline-starter` in two reviewed clusters (per the pass rule:
one themed cluster at a time, review between them). Rows stay here rather than being deleted,
so a later pass can tell "ported" from "never captured."

| # | Kit improvement (short) | Ported in | What actually landed |
| - | ----------------------- | --------- | -------------------- |
| K1 | The kit's "first spike" defaults were **data-centric** and blind to **infrastructure / assembly** projects — a hub on a Pi has no dataset to profile; its reality check is the hardware under load. | `279ddaf` (cluster A) | Generalized to **reality-profiling** with four named variants (data-profiling · hardware/load-profiling · integration-behavior · value-hypothesis) in `00_WAYS_OF_WORKING.md` §6, `DISCOVERY-GUIDE.md` §4 (+ an infra spike example), `01_INTAKE.md` §4, and the `SPIKE-REPORT` Type row. Went two files beyond the recommendation — `PRD-TEMPLATE` and `ROADMAP-TEMPLATE` carried the same data-centric nudge and would have contradicted it. |
| K2 | The **value-hypothesis machinery assumed a falsifiable product bet**; homelab / learning / self-tooling value is near-unfalsifiable, so an agent can waste effort "spiking the value." | `279ddaf` (cluster A) | Branch added to `DISCOVERY-GUIDE.md` §3.3 (name it intrinsic, move risk to feasibility + non-goals), mirrored in `00_WAYS_OF_WORKING.md` §2 principle 4. Also relaxed §5's exit criteria, which had *required* a falsifiable sentence, and added a fourth validation-status checkbox to `01_INTAKE.md` §3. |
| K3 | **Infra projects need a "target-host access" step** — SSH off by default, `.local` not resolving, macOS Local Network permission, the disabled memory cgroup — all hit before the first measurement. | `279ddaf` (cluster A) | Checklist in `00_WAYS_OF_WORKING.md` §6 carrying all four gotchas, reached from `DISCOVERY-GUIDE.md` §3.6 constraints and the `SPIKE-REPORT` Method section (connectivity is inside the time-box; a measurement through a disabled counter reports confident zeros). |
| K4 | **The first docs round should hand the repo's front page to the project** — otherwise the repo advertises the starter kit indefinitely. | `447dae9` (cluster B) | New `templates/README-TEMPLATE.md`, **ported from this project's own README** rather than invented (it was already validated here). Rename step (`git mv README.md KIT-README.md`) documented in a new "The repo front page" section of `docs/README.md`, listed in the situational-templates table and the kit README's copy-vs-fill-in section. The kit repo itself keeps `README.md` — describing the kit is correct there. |
| K5 | **Close each unit of work with a ready-to-paste commit message + filled PR body**; the kit mandated Conventional Commits but never said to *produce* them per result. | `447dae9` (cluster B) | Bullet in `CLAUDE.md` "Commits & workflow" + a fuller one in `00_WAYS_OF_WORKING.md` §9, and a new §6 "Merge artifacts" in `STATUS-REPORT-TEMPLATE`. Went beyond the recommendation: the **PR template's header was wrong**, conflating *applies-but-not-done* (a blocker) with *doesn't-apply* (n/a) — it now separates them and says never to tick a box to make the list look complete. |

> **Numbering note.** These ids are **labs-hub's own**; the kit's ledger already spent K1–K48
> on budgeteer. The kit has no id ledger of its own (`KIT_FEEDBACK.md` there is a carry-stub),
> so kit-side references are **project-qualified** — "labs-hub K1", not a bare "K1". Worth
> knowing that `gate.yml` in the kit still cites bare "K1" and "K2/K10" meaning *budgeteer's*
> ids; that ambiguity is pre-existing and was left alone.

## Notes for the kit pass

- Group related items; the highest-value cluster is usually a single theme. Note which items are
  already **validated** in-project (the proven artifact/shape to port) vs. still advice-only.
