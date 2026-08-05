---
id:     DOC-WAYS-OF-WORKING
type:   standard
status: Accepted
---
# 00 — Ways of Working

| Field   | Value                                                          |
| ------- | ------------------------------------------------------------- |
| Status  | Accepted                                                      |
| Owner   | DrewskiLabs                                                   |
| Purpose | The process spine for every project built from this baseline. |

This document is **stack-agnostic** and **project-agnostic**. It encodes *how* we
build, not *what* any given application is. If a project's plan conflicts with this
document, **stop and reconcile it here first** — don't diverge silently.

---

## 1. Why this exists (the lessons, in one place)

These principles were distilled from a prior project that reached a complete, fully
tested, gate-green state and was still scrapped — because the **process** produced a
polished system around unvalidated assumptions. The five failures we never want to
repeat:

1. **Built horizontally** (a whole back end, then a whole UI) → there was no usable
   product for a long stretch, and no early feedback. The first warning sign was reaching
   for a feature and finding it had no UI at all.
2. **Specced before observing reality** → specs/ADRs were "Accepted" on assumptions the
   real data/integration later contradicted (e.g. a legacy source whose actual shape
   differed from what the spec described).
3. **Saved the riskiest work for last** → the genuine unknown (does the external data
   load and reconcile? does the integration behave?) ran dead last, after everything was
   built on top of it.
4. **Never tested the value hypothesis** → when the central bet was finally exercised, it
   delivered nothing usable; the premise it rested on had never been checked.
5. **Documentation created false certainty** → "Accepted/Shipped" status made paper
   decisions feel verified when they weren't.

Principles 1–5 in §2 are the direct fix for each of these five. Two further principles
(usable at every step; secure from commit zero) add the guardrails the same episode taught
— including the data-in-the-repo lesson recorded in [`ORIGIN.md`](../ORIGIN.md).

---

## 2. Core principles

1. **Reality before paper.** Look at the real data, the real API, the real constraint
   *before* writing the spec or ADR that depends on it. (Fix for #2.)
2. **Vertical, not horizontal.** Every increment is a thin slice through all layers
   (data → API → UI) that a human can *use*. No "back-end phase / UI phase." (Fix for #1.)
3. **Front-load risk.** Do the most uncertain, most assumption-laden work first, as a
   throwaway spike. (Fix for #3.)
4. **Validate the value, not just the build.** Prove the core hypothesis ("if we do X,
   the user gets Y") with a spike before building the machinery around it. (Fix for #4.)
   *Where the value is intrinsic and near-unfalsifiable* — a homelab, a learning build,
   self-tooling — there is no bet a spike can kill; don't stage a theatrical one. Move the
   risk to **feasibility and scope discipline** instead
   ([`../templates/DISCOVERY-GUIDE.md`](../templates/DISCOVERY-GUIDE.md) §3.3).
5. **Decided ≠ validated.** Document status must distinguish a decision on paper from one
   checked against reality. (Fix for #5.)
6. **Usable at every step.** "Is it usable / demoable yet?" is a first-class check on
   every increment, not an end-phase activity.
7. **Secure from commit zero.** Secrets and confidential data handling are set up in the
   scaffold, before any real data can touch the repo.

---

## 3. The lifecycle: Spike → Spec → Slice → Review

Every capability moves through these stages. Small/low-risk capabilities can compress
stages, but never skip the spike when an assumption is unproven (see §11 for how to
right-size).

```
            ┌──────────┐   ┌────────┐   ┌──────────────┐   ┌────────┐
  unknown → │  SPIKE   │ → │  SPEC  │ → │ VERTICAL     │ → │ REVIEW │ → done
            │ (prove)  │   │(decide)│   │ SLICE (build)│   │(verify)│
            └──────────┘   └────────┘   └──────────────┘   └────────┘
```

1. **Spike** — time-boxed, throwaway investigation that answers a specific question
   against reality (data, library, feasibility, UX). Output: a
   [Spike Report](../templates/SPIKE-REPORT-TEMPLATE.md), not production code.
2. **Spec** — only *after* the spike de-risks it. Produce/update the PRD, domain/data/API
   specs, the **UX spec**, and any ADRs. Status starts at `Proposed`.
3. **Vertical slice** — build data → API → UI for the capability behind the gate
   (typecheck/lint/format/tests/build, as the project's stack defines them). The slice is
   **usable** when done.
4. **Review** — confirm acceptance criteria *and* that reality matched the spec. Promote
   doc status to `Validated`/`Accepted`. Capture anything surprising as a follow-up spike.

---

## 4. Document status semantics

Every spec and ADR carries a `Status`. **Never mark something `Accepted` on an
assumption that hasn't been checked against reality.**

| Status        | Meaning                                                              |
| ------------- | ------------------------------------------------------------------- |
| `Draft`       | Being written; not ready to act on.                                 |
| `Proposed`    | A decision/plan on paper. **Not yet validated against reality.**    |
| `Validated`   | A spike or prototype has confirmed the key assumptions hold.        |
| `Accepted`    | Validated **and** adopted. Safe to build large amounts on top of.   |
| `Implemented` | Built and passing the gate.                                         |
| `Superseded`  | Replaced by a later decision (ADRs are append-only — supersede, don't edit). |

Rule of thumb: the amount of code you may build on a document scales with its status.
`Proposed` supports a spike or one slice; `Accepted` supports a phase.

### Frontmatter (machine-readable identity)

Every doc under `docs/` carries a lightweight YAML frontmatter block, not only the prose
meta-table above — and **so does every template that produces one**, pre-filled with that
type's naming rule, so a doc copied from a template arrives already valid:

```yaml
---
id: <PREFIX-slug>           # stable + typed — see the prefix table below
type: <doc-type>            # feature-spec · ux-spec · spike · status-report · adr · standard · index · …
status: <ladder value>      # the status ladder above
roadmap-item: <id>          # cross-links to the roadmap's stable id (ROADMAP-TEMPLATE.md §3)
supersedes: <id>            # ADRs/specs only — append-only, never edit a superseded doc
---
```

**Every `id` is typed by its prefix, unique across the repo, and stable for the life of the
doc** — the same stable-handle rule the roadmap uses for work items (`ROADMAP-TEMPLATE.md` §2),
applied to documents. One prefix per `type`:

| Prefix | For | Example |
| ------ | --- | ------- |
| `ADR-` | architecture decisions | `ADR-0007` |
| `SPIKE-` | spike reports | `SPIKE-11` |
| `FEAT-` | feature specs | `FEAT-envelope-transfers` |
| `UX-` | UX specs | `UX-envelope-transfers` |
| `SR-` | status reports | `SR-2026-08-03-s97` |
| `REV-` | reviews, audits, initiatives | `REV-2026-07-12-roadmap-restructure` |
| `DOC-` | everything else under `docs/` | `DOC-ROADMAP`, `DOC-SECURITY` |

The point is that **the id, not the filename, is the identity**: `DOC-ROADMAP` stays
`DOC-ROADMAP` when `03_ROADMAP.md` is renamed, re-sequenced or restructured. The gate
validates that ids are unique, well-formed, and match their `type`.

> **What this rule deliberately does *not* mean:** rewriting the prose to reference ids
> instead of file paths. That would need a render step, which turns `docs/` into generated
> output and contradicts *keep the frontmatter minimal and the prose primary* (below). Links
> stay ordinary markdown links; **stability comes from the id plus a link check that fails
> loudly the moment a rename breaks a reference** — which is what a rename actually needs.

**When a gate starts enforcing a doc convention, the templates are part of that change — not
a follow-up.** A convention that lives only in a process doc is one that gets skipped: the
template is the only documentation most people actually read. Ship it the other way round and
the person who followed the template *correctly* is the one who gets the red gate, holding a
doc that was pre-broken before they typed a word.

This is what turns "which roadmap item is this report?" from hand-work into something
*generated*: a docs map, an artifact crosswalk, and a gate check can all be built **from**
the frontmatter instead of hand-authored and left to rot (closes the doc-index half of
**Summary Drift**, §10). Keep the frontmatter minimal and the prose meta-table primary —
this nudges the kit from *prose-first* toward *tooling-checked*, not the other way round;
don't let the schema grow past what a gate check actually needs.

**The kit ships this, runnable from commit zero:** [`scripts/check-docs.py`](../scripts/check-docs.py)
(`python3 scripts/check-docs.py`), Python 3 stdlib only so it needs no stack, no package
manifest and no install. It runs as its own always-on CI job in
[`.github/workflows/gate.yml`](../.github/workflows/gate.yml) — separate from the
stack-specific steps, which stay manual until wired — and has its own self-test
([`scripts/test-check-docs.py`](../scripts/test-check-docs.py)), because a gate nobody has
watched *fail* is an assertion about itself rather than a check. It validates frontmatter
(ids unique, well-formed, matching their `type`), resolves links under the policy above, and
catches the structural drift that rots docs quietly: ragged or header-less tables, gaps in
section numbering, and a README file-tree block that no longer matches the repo.

One thing it does that a naïve checker cannot: **a template's links are resolved from its
copy destination, not its own location** (`TEMPLATE_DEST` in the script). A spike-report
template lands in `docs/spikes/`, so its link to the spine is `../`, not `../docs/` — the
constant-prefix bug called out below, made checkable.

A richer variant — adding a generated artifact crosswalk and dangling `roadmap-item`
detection — lives in the budgeteer project as `scripts/check-docs.ts` (`npm run docs:check`);
port its *shape*, not its stack.

**The docs check must resolve links, from the first version.** Frontmatter validation without
a link check is an *Unasked-Question Gate* (§10) — it will print `OK` over a hundred broken
links indefinitely. The policy has no safe default, so decide it explicitly:

- **doc → doc: strict everywhere, no exception.** Every `.md` target must exist. A broken
  doc link is always rot — including inside ADRs and other append-only records, because
  append-only protects the *decision*, not a wrong path.
- **doc → code: strict in docs describing the current system; permitted in dated records**
  (status reports, spikes, reviews) — a snapshot's code references *should* rot, since the
  code moved and rewriting the record to chase it falsifies it. But **print every permitted
  one on each run**, so the exception stays a visible, bounded list rather than a hole.

Two lexical rules any real repo needs: **skip fenced code blocks** (kickoff prompts and
examples are sample text, not references), and treat a trailing `:227` as a **line reference**
— strip it before resolving, so the file itself still gets checked.

Two things this buys, both observed: a rename becomes a **worklist the gate produces for you**
instead of a grep-and-hope exercise. And one thing it can never buy — **a link check verifies
that a path resolves, never that it resolves to what the author meant**, so reusing a retired
document's filename is its blind spot: every stale reference keeps resolving, silently, to
different content.

**Renaming a doc — and the one part no gate can check.** A rename that gives the replacement
a *new* name is fully handled by the tooling: the check turns what would have been a
grep-and-hope exercise into a worklist, naming every broken link before you fix one. But
**reusing a retired document's name is invisible to every link checker, because nothing
breaks.** Old references keep resolving — to a file whose sections are now arranged
differently, or whose content moved to a sibling. Green links, wrong destination. So:

- **Prefer not to reuse a retired name.** If the replacement can keep its own name, every
  stale reference stays *visibly* stale instead of quietly wrong.
- **When reuse is the point** — the unsuffixed name is sometimes the actual deliverable — the
  rename is not done until the prose says so in **both** directions: the new occupant states
  that pre-cutover references to this name meant the deleted file, and whichever doc inherited
  the old content states where it came from and when the original was deleted. Treat that as a
  required step of the rename, exactly like updating the tooling. It is the only part of a
  name-reuse rename that nothing can check for you.

A generator that *emits* links must take its output location as an input: the relative prefix
is a function of the file being written, never a constant. The largest single source of broken
links in the reference implementation was the generator the gate itself blessed, emitting one
hard-coded `../` prefix into two output files at different depths.

**Which states apply to which artifact** (not every status fits every doc):

| Artifact | States it uses |
| -------- | -------------- |
| Specs & models — PRD, domain, data, API, UX, NFR | `Draft → Proposed → Validated → Accepted`, then kept current in place |
| Feature specs | the above **plus** `Implemented` (built and passing the gate — the buildable unit) |
| ADRs | `Proposed → Validated → Accepted`, then `Superseded` (append-only; never edited) |
| Spikes · Roadmap · Status reports · Intake | their own short lifecycles (`Open`/`Done` · `Living` · `Snapshot` · `Draft`/`Proposed`) |

---

## 5. Vertical slices

A slice is the unit of progress. It is **not** "a layer."

**Definition of Ready (before starting a slice)**
- The capability has a spec and a **UX spec** (flows + screen states), at least
  `Proposed`.
- Any unproven assumption it depends on has been spiked.
- Acceptance criteria are written and map to tests.

**Definition of Done (before calling a slice complete)**
- Data → API → UI all present; the capability is **usable in the running app**.
- Gate green: typecheck/types, lint, format, unit + integration tests, end-to-end for the
  journey, build — per the project's stack. No skipped/failing tests.
- Acceptance criteria met and tested; UX states (empty/loading/error/success) handled.
- Accessibility check on any new UI.
- Docs updated **in the same change**; doc status promoted as warranted.
- Inputs validated at the boundary; secrets never logged/committed.

(Projects extend this with their stack-specific checklist in `ENGINEERING_STANDARDS.md`.)

---

## 6. Spikes — when and how

**A spike is mandatory when** a decision rests on something you haven't directly
observed: an external/legacy data source, a third-party API/library's real behavior, a
performance assumption, or whether a feature delivers the intended value.

Rules:
- **Time-boxed** (state the box up front, e.g. half a day) and **throwaway** — spike code
  is not promoted to production; its *findings* are.
- Produces a [Spike Report](../templates/SPIKE-REPORT-TEMPLATE.md) that explicitly says
  what it **confirmed**, what it **invalidated**, and the **recommended decision**.
- **The first spike is a reality-profiling spike** — a first honest look at whatever this
  project's reality actually *is*. Pick the variant that matches:
  - **data-profiling** — a data-driven project: profile the real source.
  - **hardware/load-profiling** — an infrastructure/assembly project: profile the real box
    under the real workload. There is no dataset here; the hardware is the reality.
  - **integration-behavior** — a project resting on a third party: profile the real API's
    actual behavior, not its documentation.
  - **value-hypothesis** — a product bet: the cheapest real test of the bet itself.

**When the reality is a separate machine** (a Pi, a NAS, a VM, a lab box), reaching it is
real work that happens *before* any measurement — and it is routinely unbudgeted. Clear
these as part of the time-box, not as a surprise inside it:

- **SSH on and non-interactive.** It ships disabled on some images, and an agent run stalls
  forever on a password prompt — set up key-based auth first.
- **A name that actually resolves.** mDNS `.local` fails on plenty of networks; keep the IP
  (via an ARP scan) as the fallback, and put the reachable name in *one* configurable place
  so it isn't hard-coded across the repo.
- **The host OS can block the agent silently.** macOS's per-app **Local Network** permission
  will stop a browser from reaching a LAN address while `curl` on the same machine succeeds.
  A tool that "can't connect" may be facing a permission, not a network.
- **Resource accounting has to be switched on.** Measuring is the whole point, and it can be
  off by default: Raspberry Pi OS ships with the **memory cgroup disabled**, so `docker
  stats` reports 0 B and memory limits silently do nothing until `cgroup_enable=memory
  cgroup_memory=1` is set and the box rebooted. A spike that measures through a disabled
  counter reports confident zeros.

> Most painful integrations are a short, honest look at the real input away from being
> avoided. The spike is the cheapest insurance we have.

---

## 7. Sequencing a project

Order work by **uncertainty and value-at-risk**, not by comfort or layer:

1. **Foundation slice** — a reusable, vertically-complete base (e.g. user/auth across
   data → API → UI) so there's a usable shell to build into.
2. **Riskiest assumption spikes** — data, integrations, value hypothesis. Resolve the
   unknowns that could invalidate the whole plan *before* building on them.
3. **Domain slices** — vertical, prioritized by value, each usable on its own.
4. **Hardening** — performance budgets, observability, dependency/security gates, once
   there's real data and real usage to measure against. Record these as
   non-functional requirements and an operational-readiness checklist at `docs/07_NFR.md`,
   created from [`../templates/NFR-TEMPLATE.md`](../templates/NFR-TEMPLATE.md).

For multi-track projects, run independent tracks in parallel (e.g. a *foundation* track
and a *data-extraction-to-clean-seed* track) and merge them in a later track (*domain
features on the foundation, seeded by the clean data*).

Capture the **actual** ordered plan — the backlog of spikes and slices with their gating
and status — as a living roadmap at `docs/03_ROADMAP.md`, created from
[`../templates/ROADMAP-TEMPLATE.md`](../templates/ROADMAP-TEMPLATE.md). This section is
the model; the roadmap is the project's plan of record, re-sequenced as spikes change what
we know.

---

## 8. Security & data from day zero

- The scaffold ships a `.gitignore` that excludes secrets and **local/confidential data
  files** *before* any such file exists. Real data never enters the repo.
- Tests use **synthetic fixtures**, never real confidential data.
- Validate all external input at the boundary; never log or commit secrets/tokens.
- Authn/authz is default-deny; recovery flows are enumeration-safe by default; follow the
  baseline `SECURITY.md`.

---

## 9. Working with the AI agent

This baseline assumes a human + AI-agent pair. To avoid the failure mode where the agent
executes a flawed plan flawlessly:

- **Start with discovery.** On a new project the agent's first move is the intake
  conversation — guided by [`../templates/DISCOVERY-GUIDE.md`](../templates/DISCOVERY-GUIDE.md),
  captured in [`01_INTAKE.md`](01_INTAKE.md) — which surfaces the problem, the core bet,
  and the riskiest assumptions, and **names the first spike** before any spec is written.
- **The agent challenges the plan before executing.** Before a phase, it names the
  riskiest assumptions, the sequencing risks, and anything being decided ahead of
  validation — and proposes a spike if warranted.
- **The human reviews planning docs early**, at the start of each phase, not just the
  output. (Reviewing the plan is what catches "no UI is being built" immediately.)
- **"Is it usable yet?"** is asked at every increment by both parties.
- **One slice per session — stop at the slice boundary and report.** A session builds
  **exactly one** roadmap item, writes its status report, and **stops for review** — even when
  the next item is obvious, unblocked, and there is context to spare. Finishing early is a
  reason to report, not to continue. The point is that the human sees each slice while it is
  still cheap to redirect: a session that lands five slices has made four decisions nobody
  reviewed, and unwinding the first now means unwinding all five. **A kickoff prompt listing
  several items describes the *order*, not permission** — if a slice turns out to be trivial,
  report it and let the human say "keep going" rather than assuming it. The cost here is not
  the code, which may be perfectly good and gate-green; it is that a breaking decision buried
  in slice one only surfaces after four more were built on top of it.
- **Surprises become spikes**, not silent workarounds. **And before you pin a surprise with a
  test or a runbook entry, decide whether it is behaviour or a bug.** The reflex — assert it
  so the runbook "cannot drift", document it under *"things that will bite you"* — is exactly
  right for a constraint and exactly wrong for a defect, and both artifacts then actively
  defend it: a harness check written to broken behaviour **goes red when someone fixes the
  bug**, and the next person reading that failure has every reason to conclude the *fix* is
  the regression. A documented trap also reads as a decision somebody made. **Pin what you
  want to be true; file what you don't.** If it can't be decided within the slice, the honest
  artifact is a ⚠ carry naming the open question — **not** a green assertion. A passing test
  is a statement of intent, not merely of fact.
- **Close out each block with a Definition-of-Done snapshot.** At the end of every executed
  block — a spike, a vertical slice, or a phase — write a dated
  [status report](../templates/STATUS-REPORT-TEMPLATE.md) whose **outline is the Definition
  of Done** (§5): report each check (vertical & usable · gate-green · acceptance criteria &
  UX states · accessibility · input-validation & secrets · docs-in-the-same-change) as
  ✅/⚠/❌ **with evidence**, then the test-count delta and a one-line Conventional-Commit
  summary. Anything not done stays visible (⚠ + reason + owner) so a snapshot never
  overstates "done." This is what makes hand-offs between sessions/context windows clean and
  honest — and it doubles as the per-block review record.
- **Hand over the two artifacts that actually merge the work.** A status report says what
  happened; it doesn't land the change. With it, produce **(1) a single-line Conventional
  Commit message** and **(2) a PR description filled into
  [`../.github/PULL_REQUEST_TEMPLATE.md`](../.github/PULL_REQUEST_TEMPLATE.md)** — written
  out, ready to paste, right-sized to the change (a one-line docs fix gets a commit line and
  nothing more). **Fill it honestly:** a check that genuinely doesn't apply is marked **n/a
  with its reason**, never quietly ticked to make the list look complete, and anything
  deferred is named under *Carries / follow-ups*. The value is in the timing — filling the
  DoD checklist **while the work is fresh** surfaces the box you can't honestly tick at the
  moment you can still do something about it, rather than at review, when the incentive is
  to tick it and move on.
- **End each milestone handoff-ready, with the next session's kickoff prompt.** When a
  roadmap item reaches `Done`, the project must be resumable cold: gate green, docs updated,
  the status report's **Resume here** current. Close that report with a **copy-pasteable
  "Next-session kickoff prompt"** — the exact text to paste into a fresh context window to
  start the next item (it specializes the generic *Resume* prompt in
  [`KICKOFF-PROMPT.md`](../KICKOFF-PROMPT.md): names the next item, its risks, and any new
  setup). The newest status report is then both the handoff record and the launch pad — a new
  session reads it and nothing else to get going.
- **Feed kit-level lessons back.** When something would have been a better *baseline* default
  (a tooling gap, an example-code default, doc/process friction), log it in
  [`KIT_FEEDBACK.md`](KIT_FEEDBACK.md) as it surfaces — not only fixed locally — so a later
  kit pass can fold it into the starter for the next project.
- Keep the practices that worked: pure-core/impure-shell (so logic is testable without
  I/O), pass/fail gates, gate-green-per-slice, and resumable status reports for clean
  hand-offs between sessions/context windows.

---

## 10. Anti-patterns (named, so we catch them)

- **The Horizontal Build** — finishing a whole layer before the next. (Build slices.)
- **Spec-Ahead-of-Reality** — an `Accepted` decision about data/integrations nobody has
  looked at. (Spike first; status `Proposed` until validated.)
- **Risk-Last** — leaving the scariest unknown for the end. (Front-load it.)
- **False-Certainty Docs** — rigor and formatting mistaken for correctness. (Status
  honesty.)
- **Data-in-the-Repo** — confidential/real data committed because guardrails came late.
  (Scaffold the `.gitignore` first.)
- **Build-Without-Use** — large surface with no one having used it. (Usable every step.)
- **Summary Drift** — overview lines, counts, and internal links rot while the detailed
  sections stay correct. (Treat overview prose + links as part of "docs updated in the same
  change"; a link-check helps.)
- **Documented-but-Unwired Gate** — a DoD/CI that lists lint, e2e, or a11y the scaffold never
  shipped runnable, so "the gate" overstates enforced rigor. (Ship it runnable from commit
  zero — the False-Certainty anti-pattern applied to tooling.)
- **Unasked-Question Gate** — a step that *is* wired, *does* run, and is green over a scope
  nobody ever checked: a typecheck whose `include` never named a directory, an accessibility
  suite over pages it has never loaded, a docs check that validates frontmatter but resolves
  no link, a "p95" assertion that is arithmetically the maximum, a test suite that only ever
  exercises the app *after* someone provisioned the first login out of band. The green is
  real, and it means far less than it looks like it means. **A gate's coverage is exactly the
  set of properties it checks** — and nothing reports the complement, so coverage has to be
  audited mechanically rather than reasoned about
  ([`TESTING_STRATEGY.md`](TESTING_STRATEGY.md) §3). The sharper sibling of
  *Documented-but-Unwired*: there the gate was missing; here it was asked the wrong question.

---

## 11. Scaling the process up and down

The process scales to the **risk and reach** of the work. Match the ceremony to the
uncertainty and the blast radius — applying it uniformly is a mistake in both directions:
under-applied on risky work is how the prior project failed; over-applied on a throwaway
script is how a process gets abandoned. Right-size **deliberately**, and say which path
you're on.

### Never skip (whatever the size)

These are load-bearing — they're what the lessons cost us, and they hold for a one-line fix
as much as for a phase:

- **Spike before building on an assumption you haven't checked against reality** (§6).
- **Every increment is a vertical, usable slice** — never a horizontal layer (§5).
- **Gate-green before done:** no failing or skipped tests (§5,
  [`TESTING_STRATEGY.md`](TESTING_STRATEGY.md)).
- **Secrets/confidential data never committed or logged; external input validated at the
  boundary** (§8, [`SECURITY.md`](SECURITY.md)).
- **Status honesty** — never `Accepted` on an unchecked assumption (§4).

### Scale to fit

The kit is sized for a **focused product or app** — the bold row below. Lighter work
compresses; heavier work adds to it. Find the row you're nearest and adjust from there:

| Project shape (example) | Process & docs it warrants | vs. this kit |
| ----------------------- | -------------------------- | ------------ |
| Trivial fix or refactor — a rename, a dependency bump, a copy change | a Conventional Commit; gate-green; no spec (touch a doc only if a shape changed) | lighter |
| One throwaway question — "can library X read this file?" | a single spike report; no PRD, no slice; time-box it and record confirmed/invalidated | lighter |
| A one-screen tool, or a CLI/service with no user-facing surface | one feature note + tests; the feature spec *is* the UX spec (or none for a CLI) — still cover empty/loading/error/success on any UI | lighter |
| **A focused product or app** — a handful of journeys, one datastore, one team (e.g. an internal invoicing tool, a booking app, an import-reconcile-and-dashboard utility) | **the full kit as written: intake → first spikes → PRD → roadmap → a feature spec + UX spec per capability → `ADR-0001/0002` + a few cross-cutting ADRs → vertical slices → status reports** | **as written** |
| Multi-tenant SaaS, or an external/legacy integration at the core (money, auth, RBAC) | the kit **plus** a tenancy/isolation ADR with property tests, a security/threat-model pass, and performance budgets asserted on realistic volumes | heavier |
| Many teams or parallel tracks, several services, regulated/PII data, or high availability | the above **plus** a dedicated NFR/SLO doc, observability + on-call runbooks, a cross-track integration/contract plan, and a formal security/compliance review | heavier |

Whichever row you're on, the **Never skip** rules above still apply.

### The fast path (small, low-risk)

A one-paragraph feature note (what · acceptance criteria · UX states) → build the vertical
slice → gate → done. Skip the separate UX spec, the PRD, and ADRs **until** a trigger below
appears.

### Scale back up when any of these appear

Re-add the full spike → spec → UX spec → ADR ceremony the moment the work touches:

- **Money, auth, or multi-tenant / owner-scoped data** — correctness and isolation are
  never "small."
- **An external/legacy data source or third-party integration** — spike it (§6).
- **A performance or scale assumption** — measure against realistic volumes.
- **Anything expensive to reverse** (data representation, API style, tenancy) — write an ADR.
- **A user-facing surface with real states** — write the UX spec; its absence is the exact
  failure this kit was built to prevent.

> One line: **match the ceremony to the uncertainty and the blast radius — when unsure,
> spike.**
