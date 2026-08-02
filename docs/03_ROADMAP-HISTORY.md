---
id: ROADMAP-HISTORY
type: roadmap-history
status: Append-only
roadmap-item: —
---

# Roadmap History — labs-hub

| Field  | Value        |
| ------ | ------------ |
| Status | Append-only  |
| Owner  | wes-cutting  |
| Plan   | [`03_ROADMAP.md`](03_ROADMAP.md) — the living plan this history belongs to |

Never edit past entries; append a new one. This doc only grows.

## 1. Re-sequencing log

| Date | Change | Trigger (spike / surprise) | Effect on the plan |
| ---- | ------ | -------------------------- | ------------------ |
| 2026-07-26 | Initial plan created from intake + PRD | discovery + [SPIKE-01](spikes/SPIKE-01-pi5-hub-plus-jellyfin-feasibility.md) | Feasibility retired first; foundation slice LH-S1 next. |
| 2026-07-26 | Added SPIKE-02 (SD vs SSD) and SPIKE-03 (encryption + backup/restore); pulled persistence/NFR forward from generic "hardening" | SPIKE-01 finding: **CPU (transcode), not RAM, is the ceiling**; SD-card wear + theft exposure surfaced | Persistence medium + backup treated as first-order (`ADR-0002` stays `Proposed` until these land); transcode-cap NFR added to PRD §5. |
| 2026-07-26 | Added **SPIKE-05** (hub platform: adopt vs. build) and made it the gate on LH-S1 | Operator hub criteria ("Okta-like": service catalog incl. stopped, health, single-login gate, lifecycle mgmt, per-service metrics, custom widgets/services) — "custom vs. assemble" must be decided before LH-S1 | LH-S1 re-gated by SPIKE-05; auth scoped to *just gate the hub* (heavy IdPs deprioritized); current focus moved from LH-S1 to SPIKE-05. |
| 2026-07-26 | **LH-S3 scoped to deploy budgeteer, then BLOCKED** on budgeteer gaining auth; SPIKE-03 priority raised | Analysis of the sibling budgeteer project: no auth + real financial data; operator chose "add auth into budgeteer first" | LH-S3 → `Blocked` (dep: budgeteer roadmap #19, a cross-project prerequisite); deploy shape decided (CI→GHCR ARM64, Postgres container, gated by budgeteer's own auth); recommended interim labs-hub work = SPIKE-02/03; new rule: sensitive custom services need default-deny auth before LAN exposure. |
| 2026-07-26 | **SPIKE-05 done → adopt Homepage + Portainer** (not Cosmos/Dockge; not custom); LH-S1 re-scoped to *assemble & configure* | [SPIKE-05](spikes/SPIKE-05-hub-platform-evaluation.md) hands-on eval + operator criteria (open launcher OK, don't over-invest in multi-user, resilience/least-privilege, simple transparent pieces) | [ADR-0003](adr/ADR-0003-hub-platform.md) recorded; **M3 revised** (open launcher + per-app auth, PRD updated); Cosmos rejected (privileged/host-net SPOF, domain-model friction); current focus → LH-S1 (unblocked). |
| 2026-08-02 | **LH-S3 unblocked, then split**: `LH-S3-demo` (synthetic showcase box) shipped now; `LH-S3` (the real ledger) stays `Planned` | budgeteer shipped its auth epic (BUD-S87..S89, its `ADR-0009` Accepted) — the blocking condition — **and** added a purpose-built demo instance (BUD-S93, `DEPLOY_CONTRACT` §10): same image, own database/network/secret, synthetic data only | The blocker ("no auth + real financial data") is retired on both counts. Splitting lets the custom-service pattern (CI→GHCR→pull, Postgres container, data-root, labels, `/api/health` in smoke) be proven against a box where a mistake costs nothing, while the decisions the *real* ledger needs — TLS vs. `SESSION_COOKIE_SECURE`, backup, at-rest encryption (SPIKE-03) — stay explicitly open. `ADR-0004` deliberately deferred: the pattern is now exercised, not yet validated on a service that matters. |

## 2. Done / shipped

| Id | Item | Shipped | Notes |
| -- | ---- | ------- | ----- |
| LH-S3-demo | budgeteer demo instance (first custom app on the hub) | 2026-08-02 | `deploy/compose.budgeteer-demo.yml`; budgeteer `v0.2.0` pulled from GHCR (public, arm64, digest-pinned) + Postgres 16 on the data-root, own bridge network, `deploy/.env` holds the hub's first secrets; `make gate`/`make smoke` (`/api/health`) green; discovered on the hub. **Synthetic data only** — the real ledger is LH-S3 proper. [FEAT-LH-S3-DEMO](features/LH-S3-budgeteer-demo.md). |
| LH-S2 | Jellyfin as a managed service | 2026-07-26 | `deploy/compose.media.yml`; config/cache on data-root, media RO; `make gate`/`make smoke` (Jellyfin `/health`) green; discovered on the hub; ad-hoc spike01 Jellyfin decommissioned. Carry: Jellyfin first-run + transcode cap (operator). [FEAT-LH-S2](features/LH-S2-jellyfin.md). |
| LH-S1 | Hub foundation (Homepage + Portainer) | 2026-07-26 | `deploy/` Compose foundation; `make gate` green + CI wired; running on the Pi from the tracked def; auto-discovers Jellyfin/Homebox (RO socket). Carry: git-deploy activation (public repo push). [FEAT-LH-S1](features/LH-S1-hub-foundation.md). |
| SPIKE-05 | Hub platform: adopt vs. build | 2026-07-26 | **Adopt Homepage + Portainer** (reject Cosmos/Dockge; don't build). Report: [SPIKE-05](spikes/SPIKE-05-hub-platform-evaluation.md) → [ADR-0003](adr/ADR-0003-hub-platform.md). |
| SPIKE-01 | Pi 5 hub + Jellyfin feasibility | 2026-07-26 | PASS — ~2.8× realtime single transcode, 75 °C, no throttle, ~6.8 GB free; CPU is the ceiling. Report: [SPIKE-01](spikes/SPIKE-01-pi5-hub-plus-jellyfin-feasibility.md). |
