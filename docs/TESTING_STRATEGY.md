---
id:     DOC-TESTING-STRATEGY
type:   standard
status: Accepted
---
# Testing Strategy

| Field   | Value                                                  |
| ------- | ----------------------------------------------------- |
| Status  | Accepted                                              |
| Owner   | DrewskiLabs                                           |
| Purpose | The test layers and the gate every slice must pass.   |

Stack-agnostic: the project names the concrete runners in its `ADR-0001` and README; the
layers and the gate below are constant.

---

## 1. Test layers

| Layer | Scope | Speed | Notes |
| ----- | ----- | ----- | ----- |
| **Unit** | Pure domain + library logic (no I/O) | Instant | The bulk of tests live here because the logic lives here (pure core). |
| **Property** | Invariants over generated inputs | Fast | For rules that must always hold (exact-quantity math, idempotence, ordering, tenancy scoping). |
| **Integration** | The adapter boundary against a **real ephemeral dependency** | Moderate | Spin up a throwaway datastore/service; assert real behavior, not mocks. |
| **End-to-end** | Critical user journeys through the **running app + real API** | Slower | The only layer that exercises the **browser→API seam** (CORS, headers, content-type, preflight methods) the others mock away. Includes an **automated accessibility scan** (e.g. axe) on user-facing flows. |
| **Performance** | The heaviest reads/journeys at a realistic data volume | Slowest | Assert the `07_NFR.md` budgets (p95) against **synthetic volume**, not an empty dev DB. |

Guidelines:
- **Most coverage at the bottom** (pure unit), least at the top (e2e) — but every
  critical journey has at least one e2e.
- Prefer **real dependencies over mocks** at the integration layer; mocks hide the bugs
  that integration tests exist to catch.
- **Synthetic fixtures only** — never real confidential data in tests. Build fixtures in
  code where possible so they're reviewable in diffs.
- **Ship the real browser→API smoke in the foundation, not in hardening.** The unit /
  integration / component layers never exercise a real browser hitting the real API, so a
  whole class of bug (CORS, content-type, preflight methods) is invisible to them — exactly
  what shipped on the prior project and was only caught by running the app by hand. Wire one
  real e2e (app loads + one journey against the running API) **and** lint in the foundation
  slice, so "the gate" is real on day one rather than aspirational.
- **Lint config must exclude nested, tool-created checkouts from day zero** (e.g. `.claude/`,
  `**/worktrees/**`). An agent-spawned worktree left behind after a task looks like source to
  a repo-wide lint sweep — often without its own `node_modules`, so it fails with confusing
  "rule not found" errors that read as a real regression, not an environment artifact.
  `git worktree list` is the first diagnostic when lint errors point outside the working tree.

## 2. What must be tested

- **Every acceptance criterion** (feature spec + UX spec) maps to at least one test.
- **Invariants** (the recommended patterns you adopted — exact-quantity math, derived
  values, tenancy scoping) get **property tests**, not just examples.
- **Edge/error paths and UX states** (empty/loading/error/success), not only happy paths.
- **Reconcilable imports/migrations**: a test that the reconciliation gate **passes** on a
  good fixture and **fails** on a deliberately corrupted one.

## 3. The gate

Every slice must pass, locally and in CI, before it's done:

```
types/typecheck  →  lint  →  format check  →  unit + integration  →  e2e (incl. a11y)  →  build
```

- **A failing or skipped test blocks completion.** No exceptions, no "temporarily
  skipped."
- CI runs the same gate as local; keep them identical. The baseline ships
  [`.github/workflows/gate.yml`](../.github/workflows/gate.yml) encoding this order in two
  jobs: **`docs`**, which is real and runs on every push/PR from commit zero, and **`stack`**,
  whose steps are placeholders you wire to the project's commands (manual-only until then, so
  a skeleton never reports a false green *and* never spams red).
- Tests should need **no manual setup** — ephemeral dependencies boot as part of the test
  run.
- Keep the exact gate **commands in one canonical place** (the project README's scripts
  table) and *reference* it from CI and status reports — don't restate them in three docs,
  they drift (a step gets added in one place and missed in another).
- **A gate's coverage is exactly the set of properties it checks — audit the complement
  rather than assuming it.** Every step has an implicit scope (a tsconfig's `include`, a scan
  suite's list of pages, a link-checker's rule set) and *nothing reports what it left out*, so
  a green gate over an unread directory looks identical to a green gate over a checked one.
  This is the **Unasked-Question Gate** ([`00_WAYS_OF_WORKING.md`](00_WAYS_OF_WORKING.md) §10).
  The audit is mechanical, so make it one: enumerate the files that exist and diff them
  against the files the step actually read (e.g. `find . -name '*.ts'` vs. `tsc --listFiles`
  per project) — once per project, rather than reasoning about globs. Expect it to find holes
  nobody named *and* to disprove ones people asserted; belief about coverage is usually
  unchecked in both directions. Every `.ts` in the repo belongs to some typecheck project —
  repo-root `scripts/`, build configs and test configs included — or a comment says why not.
  Budget the fix as **one pattern applied N times**: code that was never typechecked doesn't
  accumulate varied looseness, it accumulates whichever strict flag never got to run.
- **The docs are part of the gate — and this one is already wired.** The baseline ships
  [`scripts/check-docs.py`](../scripts/check-docs.py) (`python3 scripts/check-docs.py`,
  stdlib only) plus its self-test [`scripts/test-check-docs.py`](../scripts/test-check-docs.py).
  It is the one gate step that needs no stack, so it is **not** a placeholder: if it is red,
  the docs are actually broken. Policy in [`00_WAYS_OF_WORKING.md`](00_WAYS_OF_WORKING.md) §4;
  per-project settings are the script's CONFIG block. A documentation gate that validates
  frontmatter but never resolves a link is the same false green as a typecheck that skips a
  directory — so this one resolves links from the first version, and prints both its coverage
  and its permitted exceptions on every run.

## 4. Speed & hygiene

- Keep the unit/integration gate fast enough to run constantly; isolate slow e2e behind
  its own command.
- Reset state between tests (truncate/teardown) for isolation.
- Flaky tests are bugs — fix or quarantine with a tracked issue, never ignore.
- **A recurring flake in a *timing* test is a measurement bug until proven otherwise.**
  "The perf test flaked again" reads as environmental noise, which is exactly what lets a
  broken measurement survive months of triage. Two specifics worth shipping correctly the
  first time: use a **nearest-rank percentile** (index `ceil(p × n) − 1`, so p95 of 20 runs
  is the 19th, not the 20th — an off-by-one here silently turns "p95" into "no single run may
  exceed the budget", which one GC pause fails), and **discard a warm-up phase** before
  measuring. The load-bearing rule: **the statistic you assert must be the statistic the NFR
  names** ([`../templates/NFR-TEMPLATE.md`](../templates/NFR-TEMPLATE.md)).
- **Relative-date fixtures tested against the real calendar are a smell** — a test that
  passes today and fails on some future date with no code change. Use fixed/injected dates
  (the injected-clock pattern, [`ENGINEERING_STANDARDS.md`](ENGINEERING_STANDARDS.md) §4).
- **Demo/seed-data captures earn the same reset-before-run discipline as tests** — see the
  demo-asset-capture pattern ([`ENGINEERING_STANDARDS.md`](ENGINEERING_STANDARDS.md) §4).

## 5. e2e conventions

- **Split specs per area, with a shared setup helper**; every new slice lands with its own
  spec. A single growing journey file is slow to isolate when it breaks.
- Prefer **`exact: true`** (or your runner's equivalent) for accessible-name/role queries
  when the target name appears inside another element's accessible name — a substring match
  silently grabs the wrong control.
- The a11y scan should fail on **serious/critical** violations and ship a baseline
  accessibility CSS floor (e.g. a minimum interactive target size) so WCAG 2.2 AA is enforced
  from commit zero, not discovered late.
- **A scan suite's coverage is its list of surfaces — so adding a route is what obliges you
  to add a scan.** A green a11y suite is evidence about the pages someone remembered to add
  and *nothing whatsoever* about a page it has never loaded; a mature harness (dozens of
  scans, light and dark, wired into the gate) can sail through slices that ship brand-new
  screens it never visits. This is why the Definition of Done asks you to **name the scans**
  rather than assert the outcome ([`ENGINEERING_STANDARDS.md`](ENGINEERING_STANDARDS.md) §2).
- **Verify a new scan or regression test fails against an injected defect before trusting
  it.** A test that passes the moment you write it has told you nothing — it may be asserting
  a property that was never at risk, or pointing at the wrong element. Break the thing on
  purpose, watch it go red, then fix it. Corollary, since this is where the confusion starts:
  **verify the defect you think you found actually exists** before fixing it — measure the
  live system (computed styles, hit-testing, a timed probe) instead of inferring a cause from
  the source. A regression test written for an imagined bug also passes immediately, which is
  the tell.
- **Ship a cold-start e2e that provisions the first principal through the UI.** One test that
  begins from a **genuinely empty** datastore and gets a usable, signed-in app using only the
  documented steps — explicitly **forbidden from reusing the suite's shared authenticated
  session fixture**. Shared-session fixtures are excellent for speed and are precisely what
  hides this class of bug, so the archetype has to be named or it will never be written: every
  automated consumer tends to provision its credential out of band (calling a setup endpoint
  directly, self-provisioning, or running with auth switched off), and a suite built that way
  only ever tests the app *after* the hard part.
- **An auto-dismissing overlay that pauses on hover is a deadlock source, not a timing
  nuisance.** Toasts, snackbars and tooltips that sit over the UI and pause their own dwell
  timer while hovered will **deadlock a retrying click API**: the runner moves the pointer onto
  the target on every retry, the target is under the overlay, the hover keeps the overlay
  alive, and the two hold each other open until the full timeout — a 5s dwell becomes a 30s
  failure. So a helper that triggers one must **clear it deterministically** (via its own
  dismiss affordance) **and park the pointer away from it**. Both halves are needed:
  dismissing by *clicking* leaves the pointer in that corner, which pins the *next* overlay
  open forever. Never simply wait the dwell out — besides being slow, you pay it at every
  mutation in the suite.
- **Read a failure log literally, and measure the live element before theorising.** The log
  above named the elements actually intercepting the click; the honest next step is to probe
  the running page (computed styles, hit-testing, a timed observation), not to infer a cause
  from the stylesheet. In the case this rule comes from, the obvious first theory — that an
  empty overlay container was a permanent click-swallowing dead zone — was **wrong**, and the
  regression test written for that imagined defect passed immediately, which was the tell (see
  the injected-defect rule above).
- **The harness owns the ephemeral stack it tests against — never reuse a server it didn't
  start.** Attaching to a dev server "for convenience" silently invalidates empty-state
  assertions (a real dev store isn't empty) and can leak test-written data into it. Either
  the harness starts every dependency itself, or it **fails fast** with a clear message when
  a port it needs is already held — don't let it silently attach. Verify a port is genuinely
  free with the OS (e.g. `lsof -iTCP:<port> -sTCP:LISTEN`), not by trusting that a wrapper
  process was stopped — stopping the wrapper can still orphan the child holding the port.
- A **reference e2e + a11y + perf harness** (Playwright, per-area split, axe scan, a p95
  budget test) lives in the budgeteer project — port its *shape*, not its stack.
