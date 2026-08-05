<!--
PROJECT README TEMPLATE — copy to the repo root as README.md during the first docs round,
AFTER renaming the kit's own README.md to KIT-README.md (see docs/README.md, "The repo
front page"). This is the front page a human or agent lands on first: what this project is,
where it stands, and where to resume.

No YAML frontmatter here — the frontmatter rule (00_WAYS_OF_WORKING.md §4) covers docs/,
and a frontmatter block renders as junk on a repo's front page.

Keep it a LIVING overview, not a snapshot: the Status section is the part that rots
fastest, so update it in the same change as each status report. Delete sections that don't
apply yet rather than leaving <placeholders> on the front page.
-->

# <project-name>

<One or two sentences: what this is, for whom, in plain language. **Bold** the two or three
phrases that carry the idea — this line is what someone reads before deciding to keep
reading.>

> Built from the DrewskiLabs baseline starter kit (see [`KIT-README.md`](KIT-README.md)).
> This README is a **living project overview** — it grows as the project does.

## Status

**Phase:** <one sentence — what stage the project is actually at, in the present tense.>

<A bullet per completed or in-flight unit of work, newest thinking last. Each states the
outcome and links its evidence — the spike report, ADR, or feature spec. Keep the honest
marker (✅ / ⚠ / ❌) that the status report used; a README that only shows ✅ is a brochure.>

- **<Spike/decision>:** ✅ validated — [SPIKE-NN](docs/spikes/SPIKE-NN-<slug>.md) (<the
  finding in one clause — including the constraint it uncovered>).
- **<Decision>:** ✅ decided — adopt **<choice>** ([ADR-NNNN](docs/adr/ADR-NNNN-<slug>.md)).
- **<Slice id>:** ✅ built — <what is now usable, and where it runs>
  ([FEAT-<id>](docs/features/<id>-<slug>.md)).
- **<Slice id>:** ⚠ <what is deferred, and why> — <owner or gating item>.
- **Resume from:** the newest status report —
  [`docs/status-reports/<YYYY-MM-DD-slug>.md`](docs/status-reports/<YYYY-MM-DD-slug>.md).
- **Next:** <the next roadmap item and what gates it> — see
  [`docs/03_ROADMAP.md`](docs/03_ROADMAP.md).

## What it is (and isn't)

- **Is:** <the one-paragraph shape of the thing — including where the real work lives.>
- **Isn't** (current non-goals): <the deliberate exclusions, briefly>. Full list in
  [`docs/02_PRD.md`](docs/02_PRD.md) §4.

> Non-goals on the front page are not padding: they are what stops a returning reader (or a
> fresh agent session) from helpfully building something the project decided against.

## Stack

Chosen per project via ADRs (see [`docs/adr/`](docs/adr/)). **Carry each choice's status
across** — a `Proposed` row on the front page is a live warning that something is decided
but not yet validated.

| Layer | Choice | Decision |
| ----- | ------ | -------- |
| <Language / runtime> | <choice> | [`ADR-0001`](docs/adr/ADR-0001-<slug>.md) — **<status>** |
| <Framework> | <choice> | [`ADR-000N`](docs/adr/ADR-000N-<slug>.md) — **<status>** |
| <Datastore> | <choice> | [`ADR-000N`](docs/adr/ADR-000N-<slug>.md) — **<status>** |
| Gate | `<the one command that runs the gate>` + CI in `.github/workflows/gate.yml` | wired (<slice id>) |
| <Fixed constraint, if any> | <e.g. the target hardware> | fixed constraint |

## How we work

This project follows the kit's process spine — **reality before paper; vertical, not
horizontal; front-load risk; usable every step; decided ≠ validated; secure from commit zero.**

- Contributor + agent guide: [`CLAUDE.md`](CLAUDE.md)
- Process spine (read first): [`docs/00_WAYS_OF_WORKING.md`](docs/00_WAYS_OF_WORKING.md)
- Documentation map: [`docs/README.md`](docs/README.md)

## Documentation

| Doc | What |
| --- | ---- |
| [`docs/01_INTAKE.md`](docs/01_INTAKE.md) | Captured discovery — problem, users, the core bet |
| [`docs/02_PRD.md`](docs/02_PRD.md) | Product requirements — goals, non-goals, journeys |
| [`docs/03_ROADMAP.md`](docs/03_ROADMAP.md) | Living plan of record (+ [history](docs/03_ROADMAP-HISTORY.md)) |
| [`docs/adr/`](docs/adr/) | Architecture decisions |
| [`docs/spikes/`](docs/spikes/) | Time-boxed investigations |
| [`docs/status-reports/`](docs/status-reports/) | Hand-off snapshots (start from the newest) |
| [`docs/KIT_FEEDBACK.md`](docs/KIT_FEEDBACK.md) | Improvements fed back to the baseline kit as we build |

## Getting started

<How to actually run it: prerequisites, the setup command, the run command, the gate
command. Copy the real commands from `ADR-0001` — a README that describes a stack without
the commands to exercise it sends every new reader digging.>

## Operating notes

<Only what a person needs to operate or reach this specific project — the target host and
how it is reached, environment/config entry points, anything that will bite someone on
their first day. Delete this section if the project has no operational surface yet.>
