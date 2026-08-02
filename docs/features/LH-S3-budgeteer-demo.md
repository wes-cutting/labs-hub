---
id: FEAT-LH-S3-DEMO
type: feature-spec
status: Proposed
roadmap-item: LH-S3-demo
---

# Feature Spec — LH-S3-demo: budgeteer demo instance on the hub

| Field        | Value                                                                 |
| ------------ | --------------------------------------------------------------------- |
| Feature ID   | FEAT-LH-S3-DEMO                                                        |
| Status       | Implemented                                                            |
| Owner        | wes-cutting                                                            |
| Last updated | 2026-08-02                                                             |
| Related      | [FEAT-LH-S1](LH-S1-hub-foundation.md) · [ADR-0002](../adr/ADR-0002-service-data-and-state.md)/[0003](../adr/ADR-0003-hub-platform.md) · budgeteer [`DEPLOY_CONTRACT.md`](https://github.com/wes-cutting/budgeteer/blob/main/docs/DEPLOY_CONTRACT.md) §10 (the demo instance) · budgeteer `ADR-0008` (runtime) / `ADR-0009` (auth) |

> Combined feature + UX spec (right-sized per [§11](../00_WAYS_OF_WORKING.md)). budgeteer's UI is
> authored in its own repo and a11y-gated there; this slice's UX is how the box appears in and is
> reached from the hub (§12).

## 1. Summary

Run **budgeteer's demo instance** as a first-class tracked hub service: defined in
`deploy/compose.budgeteer-demo.yml`, image **pulled** from GHCR (public, `linux/arm64`, pinned by
digest), Postgres state on the `ADR-0002` data-root, auto-discovered on the Homepage launcher, and
health-checked in the smoke test.

This is the **first custom application** on the hub, and it deliberately carries **strictly
synthetic data** — the showcase box from budgeteer's `DEPLOY_CONTRACT` §10, not the household's
real ledger. It is therefore the low-risk half of LH-S3: it proves the whole custom-service
pattern (CI→GHCR→pull, a database container, data-root, labels, `/api/health` in smoke) against a
box where a mistake costs nothing.

## 2. Scope

- **In scope**
  - `deploy/compose.budgeteer-demo.yml` — app + Postgres 16, on their own network, DB state on the data-root, Homepage labels.
  - Makefile + CI gate compose all three service files; smoke checks `/api/health`.
  - `deploy/.env` gains the hub's **first secrets** (demo database password, demo session secret), gitignored, with no fallback in the stack.
  - Seeding runbook: an SSH tunnel to the Pi's loopback-bound demo Postgres, seeded from a budgeteer checkout.
- **Out of scope**
  - **The real budgeteer deployment** — that is LH-S3 proper, and it still needs its own decisions (TLS/cookie posture, backup, at-rest encryption). See §11.
  - TLS termination at the hub — nothing here terminates TLS yet (§9).
  - `ADR-0004` formalizing the custom-service pattern — deliberately deferred until the *real* deployment exercises it (§11).
  - Homebox formalization (still ad-hoc from `spike01`).

## 3. User stories

| ID   | Story | Priority |
| ---- | ----- | -------- |
| US-1 | As the operator, I open the demo from the hub launcher and sign in with a published credential. | Must |
| US-2 | As the operator, the demo runs as a **tracked, reproducible** service (defined in the repo, pinned image, on the data-root). | Must |
| US-3 | As the operator, the demo shows healthy in the hub and is caught by the smoke test. | Must |
| US-4 | As the operator, I can **hand the box to someone** without the household's real ledger being reachable from it. | Must |
| US-5 | As the operator, I can **re-pristine** the box between showings. | Should |

## 4. Acceptance criteria

- **Given** the three compose files, **when** the tracked deploy runs, **then** the demo app and its Postgres come up healthy, with database state under `/srv/labs-hub/budgeteer-demo/db`.
- **Given** the running demo, **when** I open Homepage, **then** a **Budgeteer (demo)** tile appears (Apps group) with health.
- **Given** `make smoke`, **then** the demo's `/api/health` returns `200` — which per `DEPLOY_CONTRACT` §6 is *readiness*, so it also proves the database answers.
- **Given** the seeded box, **when** I sign in as `demo` / `demo-budgeteer`, **then** I land on a dashboard of invented money.
- **Given** no secrets in `deploy/.env`, **when** I run `make up`, **then** the stack **fails loudly by name** rather than starting with a default.
- **Given** the gate, **when** I run `make gate`, **then** yamllint + `docker compose config` (all three files) + shellcheck pass.

## 5. Edge cases & error handling

| Scenario | Expected behavior |
| -------- | ----------------- |
| Secrets missing from `deploy/.env` | `compose config`/`up` exits non-zero naming the variable. No fallback exists. |
| Data-root DB directory root-owned | Postgres `initdb` fails (it runs as uid 999). The README's setup step `chown 999:999`s it. |
| App starts before Postgres accepts queries | `depends_on: condition: service_healthy` + `pg_isready` gates it (`DEPLOY_CONTRACT` §4). |
| Viewer changes the demo password / leaves junk data | `reset.js` in-container + reseed restores it; the reset preserves users/sessions (budgeteer BUD-S90). |
| A viewer's session outlives a showing | The password reset path revokes that user's sessions. |
| Someone tries to reach the demo database from the LAN | Not possible: the DB port is bound to `127.0.0.1` and the pair sits on its own bridge network. |

## 6. Data changes

Data-root addition per [ADR-0002](../adr/ADR-0002-service-data-and-state.md):
`/srv/labs-hub/budgeteer-demo/db` (Postgres 16 data directory, owned by uid 999). Still on SD
until SPIKE-02. **It holds synthetic data only**, so it is the one service subtree that needs
neither backup nor at-rest encryption — a useful property while SPIKE-03 is still open.

## 7. Interface changes

budgeteer serves its SPA **and** its API from one process on one port (`3001` in-container,
published as `3010`). Hub-facing surfaces: `GET /api/health` (readiness, public, detail-free) and
the **Homepage tile** (Apps group).

## 8. Dependencies

[FEAT-LH-S1](LH-S1-hub-foundation.md) (hub + deploy pattern), ADR-0002/0003, and — across the
project boundary — budgeteer's `DEPLOY_CONTRACT` §1–§7 (image, ports, env, health, first run) plus
§10 (the demo instance). §1–§7 is a promise to this repo; §10 explicitly is not, so the demo's
shape may change under us without coordination.

## 9. Security, privacy & accessibility

- **Synthetic data only.** The rule LH-S3 established — *a custom service handling sensitive data
  must have default-deny auth before LAN exposure* — is satisfied twice over here: budgeteer now
  has default-deny auth (its `ADR-0009`), **and** this box holds nothing real.
- **Structural isolation** from any future real deployment: its own database, its own bridge
  network, its own signing secret under a distinct variable name, and a `DATABASE_URL` hard-wired
  in the file rather than read from the environment.
- **Secrets** are generated per host into `deploy/.env` (gitignored); the stack has no fallback.
- **`SESSION_COOKIE_SECURE=false`** — a deliberate, documented deviation. The hub serves plain
  HTTP, and a browser discards a `Secure` cookie sent over HTTP. What this trades away is a session
  token, on the LAN, for a box of invented figures. It must flip to `true` when the hub terminates
  TLS, and **the real deployment must not inherit this setting**.
- **The published credential** (`demo` / `demo-budgeteer`) is deliberate, not a leak: it guards a
  throwaway database on its own signing secret.
- **Accessibility:** budgeteer's surfaces are axe-gated in its own repo (BUD-S91/S92); the hub tile
  inherits Homepage's a11y.

## 10. Test plan

- **Gate:** `make gate` — yamllint + `docker compose config` across all three files + shellcheck.
- **Smoke:** `scripts/smoke.sh` adds the demo's `/api/health` → 200.
- **Manual acceptance:** tile appears + healthy; sign in with the published credential; dashboard renders seeded synthetic data; `up` without secrets fails by name.

## 11. Open questions

| Question | Owner | Status |
| -------- | ----- | ------ |
| **The real budgeteer deployment** — TLS at the hub vs. `SESSION_COOKIE_SECURE=false` (`DEPLOY_CONTRACT` §5) | wes-cutting | open — must be decided before the real ledger is served; the demo's answer does not transfer |
| `ADR-0004` formalizing the custom-service pattern | wes-cutting | deferred — the pattern is now *exercised* but not yet *validated* against a service that matters; write it with the real deployment |
| At-rest encryption for a real ledger on a stealable node | SPIKE-03 | open — not blocking here (synthetic data), blocking for LH-S3 proper |
| No automated test pins the demo profile | budgeteer (BUD-S93 §6) | open — carried from the sibling repo |

## 12. UX (folded in)

**Entry/navigation:** Homepage tile (Apps → "Budgeteer (demo)") → budgeteer's own sign-in.
**States:** unclaimed (a purged box routes to `/setup` for the viewer to claim) · signed out (login)
· seeded dashboard (the normal demo state) · degraded (`/api/health` 503 when Postgres is
unreachable — the tile shows unhealthy). **Content:** tile name "Budgeteer (demo)", group "Apps",
description "Envelope budgeting — synthetic demo data", status text+icon.
**Accessibility:** authored and axe-gated in the budgeteer repo; hub tile inherits Homepage's.

## 13. Out of scope / later

The real budgeteer deployment (LH-S3 proper), `ADR-0004`, TLS termination, Homebox formalization,
pinning the remaining hub images by digest.
