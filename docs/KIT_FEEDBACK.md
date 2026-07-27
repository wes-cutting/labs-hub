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

| # | Priority | Kit improvement | Source | Recommendation |
| - | -------- | --------------- | ------ | -------------- |
| K1 | High | The kit's "first spike" defaults are **data-centric** and blind to **infrastructure / assembly** projects. `DISCOVERY-GUIDE.md` §4 and `01_INTAKE.md` §4 both assert "the first spike of a data-driven project is a data-profiling spike on the real source" — but a project whose reality is *hardware and load* (a self-hosted hub on a Pi) has no dataset to profile; its first reality check is **profiling the real hardware under real load**. | labs-hub discovery — the whole project is infra/assembly, not data. | Generalize the concept to **"reality-profiling"** with named variants (data-profiling · **hardware/load-profiling** · integration-behavior). Add an infra example to `DISCOVERY-GUIDE.md` §4 and a one-line note in the `01_INTAKE.md` §4 preamble so infra projects aren't nudged toward a dataset that doesn't exist. |
| K2 | Medium | The **value-hypothesis machinery assumes a falsifiable product bet**. For homelab / learning / self-tooling projects the value is largely the *journey* (control, understanding, customization) and is **near-unfalsifiable** — so the value-hypothesis spike doesn't apply, and the real risk lives in **feasibility + scope discipline**. The kit doesn't name this case, so an agent can waste effort trying to "spike the value." | labs-hub intake §3 — adopted hypothesis is intentionally near-unfalsifiable. | In `DISCOVERY-GUIDE.md` §3.3 add a short branch: *if the value is intrinsic/near-unfalsifiable, skip the value-hypothesis spike and move risk to feasibility + scope discipline (name non-goals aggressively).* Mirror one line in `00_WAYS_OF_WORKING.md` §2 principle 4. |
| K4 | Medium | **The first docs round should hand the repo's front page over to the project.** The kit ships `README.md` describing *the kit*, but once a project starts, the top-level README should describe *the project* and evolve with it — otherwise the repo's front page stays about the starter kit indefinitely, and the kit's own overview and the project's overview collide in one file. | labs-hub — noticed the root README still described the kit after discovery + planning were done. | In the first-round docs step, **rename the kit README (e.g. `KIT-README.md`) and create a new project `README.md`** from a small project-README template (name, one-liner, status, stack per `ADR-0001`, links into `docs/`, pointer to the newest status report + the kit README). Add a `README-TEMPLATE.md` to `templates/` and list it in `docs/README.md`'s carry/fill-in table. |
| K3 | Medium | **Infra / self-hosted projects need a "target-host access" setup step the kit doesn't mention.** SPIKE-01 required an agent to reach a separate device (the Pi); getting there cost real time: SSH is off by default on Raspberry Pi OS, mDNS `.local` didn't resolve (used ARP + IP), passwordless SSH keys had to be set up for non-interactive runs, and **macOS's per-app "Local Network" privacy permission silently blocked Chrome/Brave from a LAN IP while `curl` worked**. None of this is in the kit, yet every on-device/self-hosted project hits it before the first spike can run. | labs-hub SPIKE-01 execution — connectivity troubleshooting before any measurement. | Add a short **"Target-host access" checklist** (SSH enabled + key-based/non-interactive, reachability by IP when mDNS fails, sandbox/in-app browsers can't reach the LAN, host OS local-network permissions, **resource-accounting prerequisites** — e.g. Raspberry Pi OS ships with the memory cgroup *disabled*, so `docker stats` shows 0 B RAM and memory limits silently don't work until `cgroup_enable=memory cgroup_memory=1` is added + reboot) to the spike/execution guidance for projects whose "reality" is a separate machine. Consider a one-liner in `DISCOVERY-GUIDE.md` §3.6 constraints (how will the agent reach the target hardware?). |
| K5 | Medium | **Close each completed unit of work with a ready-to-paste commit message + filled PR body.** The kit ships a PR template and mandates Conventional Commits, but nothing tells the agent to *produce* them per result. Doing so — a short single-line Conventional Commit message **plus** the `.github/PULL_REQUEST_TEMPLATE.md` filled in (right-sized, and honest: un-checkable boxes marked n/a-with-reason, never falsely ticked) — made merging fast and kept the DoD checklist honest each result. | labs-hub — operator asked for this exact output on every result. | In `CLAUDE.md` "Commits & workflow" (and/or `00_WAYS_OF_WORKING.md` §9), state that the agent ends each completed spike / slice / fix with (1) a single-line Conventional Commit message and (2) a PR description filled into the PR template — right-sized to the change, marking un-checkable boxes n/a-with-reason under "Carries / follow-ups". |

## Notes for the kit pass

- Group related items; the highest-value cluster is usually a single theme. Note which items are
  already **validated** in-project (the proven artifact/shape to port) vs. still advice-only.
