---
id: FEAT-LH-S2
type: feature-spec
status: Proposed
roadmap-item: LH-S2
---

# Feature Spec — LH-S2: Jellyfin as a managed service

| Field        | Value                                                                 |
| ------------ | --------------------------------------------------------------------- |
| Feature ID   | FEAT-LH-S2                                                             |
| Status       | Implemented                                                          |
| Owner        | wes-cutting                                                          |
| Last updated | 2026-07-26                                                           |
| Related      | PRD §3 goal 2, journey 4 · [FEAT-LH-S1](LH-S1-hub-foundation.md) · [ADR-0001](../adr/ADR-0001-os-and-container-runtime.md)/[0002](../adr/ADR-0002-service-data-and-state.md)/[0003](../adr/ADR-0003-hub-platform.md) · [SPIKE-01](../spikes/SPIKE-01-pi5-hub-plus-jellyfin-feasibility.md) |

> Combined feature + UX spec (right-sized per [§11](../00_WAYS_OF_WORKING.md)). Jellyfin's own UI
> is third-party; the slice's UX is how it appears in / is reached from the hub (§12).

## 1. Summary

Bring **Jellyfin** into the tracked hub as a first-class managed service: defined in
`deploy/compose.media.yml`, persistent state on the `ADR-0002` data-root, media from a defined
media root, auto-discovered on the Homepage launcher, health-checked in the smoke test — and
**operated within the SPIKE-01 transcode budget** (one live 1080p transcode ≈ all 4 cores; no
HW H.264 encode). Replaces the throwaway `spike01` Jellyfin.

## 2. Scope

- **In scope**
  - `deploy/compose.media.yml` — Jellyfin service (config/cache on data-root, media root, Homepage labels, `:ro` media).
  - Makefile composes hub + media together; smoke checks Jellyfin `/health`.
  - **Transcode budget baked in:** documented + configured concurrent-transcode cap; favor direct-play.
  - Seed `/srv/labs-hub/media` with the synthetic clip; decommission the `spike01` Jellyfin.
- **Out of scope**
  - Homebox (still ad-hoc from `spike01` — separate follow-up).
  - Hardware-accelerated decode tuning (V4L2) — future hardening.
  - A real media library / library curation — operator populates later.
  - Jellyfin-authenticated Homepage widget (needs an API key/secret) — later.

## 3. User stories

| ID   | Story | Priority |
| ---- | ----- | -------- |
| US-1 | As the operator, I open Jellyfin from the hub launcher and play media. | Must |
| US-2 | As the operator, Jellyfin runs as a **tracked, reproducible** service (defined in the repo, on the data-root). | Must |
| US-3 | As the operator, Jellyfin shows healthy in the hub and is caught by the smoke test. | Must |
| US-4 | As the operator, the node **won't fall over from transcodes** — concurrent transcoding is capped and direct-play is favored. | Must |

## 4. Acceptance criteria

- **Given** `deploy/compose.yml` + `deploy/compose.media.yml`, **when** the tracked deploy runs, **then** Jellyfin comes up healthy on the data-root (config/cache under `/srv/labs-hub/jellyfin`, media from the media root).
- **Given** the running Jellyfin, **when** I open Homepage, **then** a **Jellyfin** tile appears (Media group) with health.
- **Given** `make smoke`, **then** Jellyfin `/health` returns `200` (added alongside Homepage/Portainer).
- **Given** the seeded synthetic clip, **when** I play it, **then** it plays (direct-play or a single transcode within budget).
- **Given** the transcode budget, **then** a **concurrent-transcode cap is configured** (Jellyfin streaming limit) and documented, so a 2nd concurrent transcode is prevented rather than degrading both.
- **Given** the gate, **when** I run `make gate`, **then** yamllint + `docker compose config` (both files) + shellcheck pass.

## 5. Edge cases & error handling

| Scenario | Expected behavior |
| -------- | ----------------- |
| Empty media library (first run) | Jellyfin shows its empty-library state; hub tile still healthy. |
| Second concurrent transcode requested | Blocked by the streaming/transcode cap (user sees "stream limit"), protecting the node — not two degraded streams. |
| Media root missing on Pi | Deploy step creates `/srv/labs-hub/media`; Jellyfin starts with an empty library. |
| HEVC to an incompatible client | Transcodes (software libx264) — within the single-stream budget; direct-play preferred where the client supports it. |

## 6. Data changes

Data-root additions per [ADR-0002](../adr/ADR-0002-service-data-and-state.md):
`/srv/labs-hub/jellyfin/config`, `/srv/labs-hub/jellyfin/cache`, and a media root
`/srv/labs-hub/media` (mounted **read-only** into Jellyfin). Still on SD until SPIKE-02.

## 7. Interface changes

No app API. **UI surfaces:** the Jellyfin app itself (third-party, its own auth) and its
**Homepage tile** (Media group). Reached from the hub launcher (journey 4).

## 8. Dependencies

[FEAT-LH-S1](LH-S1-hub-foundation.md) (the hub + deploy pattern), ADR-0001/0002/0003,
SPIKE-01 (the transcode ceiling this slice must respect).

## 9. Security, privacy & accessibility

- Jellyfin has its **own auth** (created at first-run); media mounted **read-only** (least privilege).
- No secrets in the repo; the Homepage-widget API-key integration is deferred to avoid one.
- Accessibility: Jellyfin is a third-party UI (we don't author it); noted, not claimed.

## 10. Test plan

- **Gate:** `make gate` — yamllint + `docker compose config` across both files + shellcheck.
- **Smoke:** `scripts/smoke.sh` adds Jellyfin `/health` → 200.
- **Manual acceptance:** tile appears + healthy; play the synthetic clip; confirm the concurrent-transcode cap blocks a 2nd transcode.

## 11. Open questions

| Question | Owner | Status |
| -------- | ----- | ------ |
| Concrete concurrent-transcode cap: 1 or 2 streams? | wes-cutting | open — default to **1** on this hardware; revisit with real usage |
| Enable HW-accelerated HEVC **decode** (V4L2) to widen the budget? | wes-cutting | open — future hardening spike |

## 12. UX (folded in)

**Entry/navigation:** Homepage tile (Media → Jellyfin) → opens Jellyfin (its own login). **States:** empty
library (first run) · populated (media present) · playing (direct-play or single transcode) · stream-limited
(2nd concurrent transcode blocked, clear message). **Content:** tile name "Jellyfin", group "Media",
description "Media server", status text+icon. **Accessibility:** third-party UI; hub tile inherits Homepage's.

## 13. Out of scope / later

Homebox formalization, HW-decode tuning, real library curation, Jellyfin API-key widget.
