---
id: FEAT-LH-S1
type: feature-spec
status: Proposed
roadmap-item: LH-S1
---

# Feature Spec — LH-S1: Hub foundation (Homepage + Portainer)

| Field        | Value                                                                 |
| ------------ | --------------------------------------------------------------------- |
| Feature ID   | FEAT-LH-S1                                                             |
| Status       | Implemented                                                          |
| Owner        | wes-cutting                                                          |
| Last updated | 2026-07-26                                                           |
| Related      | PRD §3 goal 1–2, journeys 1–3 · [ADR-0001](../adr/ADR-0001-os-and-container-runtime.md) · [ADR-0002](../adr/ADR-0002-service-data-and-state.md) · [ADR-0003](../adr/ADR-0003-hub-platform.md) · [SPIKE-05](../spikes/SPIKE-05-hub-platform-evaluation.md) |

> **Combined feature + UX spec** (right-sized per [Ways of Working §11](../00_WAYS_OF_WORKING.md) —
> the hub is essentially one screen, the Homepage dashboard). UX flows + screen states are in §12.

## 1. Summary

Turn the throwaway SPIKE-05 eval stack into a **clean, repo-tracked, reproducible hub
foundation**: a Compose definition (`deploy/`) that stands up **Homepage** (the launcher —
label-driven service catalog + health + at-a-glance resources) and **Portainer** (container
lifecycle + live per-service CPU/RAM), on the `ADR-0002` data-root, deployed to the Pi
**git-based**, with a **gate runnable from commit zero**.

## 2. Scope

- **In scope**
  - `deploy/compose.yml` for **Homepage + Portainer** (restart policies, healthchecks, data-root bind mounts).
  - Homepage config tracked in-repo (docker auto-discovery via labels; system-resources widget).
  - Least-privilege socket posture: Homepage gets a **read-only** Docker socket; Portainer RW (with a socket-proxy noted as future hardening).
  - A **gate** (`make gate`): `docker compose config` validation + `yamllint`, plus a **smoke** script (Homepage + Portainer respond). Wired into `.github/workflows/gate.yml`.
  - **Git-based deploy** mechanism + docs (`git pull && docker compose up -d` on the Pi).
- **Out of scope**
  - Jellyfin as a managed service (**LH-S2**) and the custom-service pattern (**LH-S3**).
  - A hub-level auth gate (open launcher per ADR-0003; forward-auth deferred).
  - Persistence-medium migration + backup (**SPIKE-02/03**, LH-S4) — foundation stays on SD for now.
  - Historical metrics (Beszel) — deferred.

## 3. User stories

| ID   | Story | Priority |
| ---- | ----- | -------- |
| US-1 | As the operator, I want one launcher page on the LAN that lists my services so I can reach any of them. | Must |
| US-2 | As the operator, I want each service's health visible at a glance so I know what's up/down. | Must |
| US-3 | As the operator, I want to start/stop/update/see-resources of any container from a UI so I can manage the node. | Must |
| US-4 | As the operator, I want the whole hub defined in the repo and stood up from that definition so it's reproducible. | Must |
| US-5 | As the operator, I want a new (labeled) service to appear on the launcher automatically so adding services is low-effort. | Should |

## 4. Acceptance criteria

- **Given** the tracked `deploy/compose.yml`, **when** I run the documented deploy on the Pi, **then** Homepage (`:3000`) and Portainer (`:9000`) come up healthy from that definition alone.
- **Given** a running service with `homepage.*` labels, **when** I open Homepage, **then** it appears as a tile with its group/name/href and a health/status indicator. *(Validated against the existing Jellyfin + Homebox.)*
- **Given** Portainer, **when** I open it, **then** I can see all containers (incl. stopped), start/stop/restart one, and view its live CPU/RAM.
- **Given** the repo, **when** I run `make gate`, **then** compose config validates and YAML lints with **no errors** (exit 0), and `make smoke` reports Homepage + Portainer reachable.
- **Given** Homepage, **when** it loads with the docker provider, **then** the **system-resources** widget shows CPU/RAM/disk (proving the cgroup fix end-to-end).

## 5. Edge cases & error handling

| Scenario | Expected behavior |
| -------- | ----------------- |
| Docker socket unavailable to Homepage | Homepage still renders; docker-sourced tiles show an error/○ rather than crashing the page. |
| A service container is stopped | Homepage tile shows down/unhealthy (text, not color-only); Portainer lists it under stopped. |
| `HOMEPAGE_ALLOWED_HOSTS` unset/mismatched | Homepage refuses the request (blank/Error) — `.env` documents the required value. |
| Portainer first-run token/timeout | One-time admin creation; token retrievable from logs; documented in `deploy/README.md`. |
| Data-root path missing on Pi | Deploy step creates `/srv/labs-hub/<svc>` before `up`. |

## 6. Data changes

No domain data. Introduces the **deployment data-root** per [ADR-0002](../adr/ADR-0002-service-data-and-state.md):
`/srv/labs-hub/portainer/data` (bind mount). Homepage config is **tracked in the repo**
(`deploy/homepage/config/`), bind-mounted read-only-ish into the container. (Still on the SD
card until SPIKE-02.)

## 7. Interface changes

No application API. The **UI surface** is:
- **Homepage** dashboard (the launcher/catalog/health/resources) — the primary user surface (see §12).
- **Portainer** UI (management) — gated by its own admin login.

## 8. Dependencies

- [ADR-0001](../adr/ADR-0001-os-and-container-runtime.md) (Docker/Compose), [ADR-0003](../adr/ADR-0003-hub-platform.md) (Homepage+Portainer), [SPIKE-05](../spikes/SPIKE-05-hub-platform-evaluation.md).
- The memory-cgroup fix (already applied) for the resources widget / Portainer RAM.
- Git-based deploy needs the branch **pushed** + the Pi able to **pull** (deploy key / public repo) — see §11.

## 9. Security, privacy & accessibility

- **Least privilege:** Homepage → **read-only** Docker socket; Portainer → RW (needed for lifecycle) — the main residual privilege; socket-proxy is future hardening (`07_NFR`).
- **Auth:** launcher open on the trusted LAN (ADR-0003); Portainer admin-gated; no secrets in the repo (any secrets via `.env`, git-ignored).
- **Accessibility:** Homepage/Portainer are third-party UIs (we configure, not author). Baseline WCAG 2.2 AA is a project standard; we ensure health/status is conveyed by **text/icon, not color alone** in Homepage config where configurable, and note third-party a11y limits rather than claiming full control.

## 10. Test plan

Right-sized, infra-appropriate (no app unit tests yet):
- **Static gate:** `docker compose config -q` (compose valid) + `yamllint` (configs valid) — in `make gate` and CI.
- **Smoke (integration):** `scripts/smoke.sh` — Homepage `/api/healthcheck` and Portainer `:9000` return healthy; run post-deploy.
- **Manual acceptance:** discovery of Jellyfin/Homebox tiles; Portainer start/stop + live stats; resources widget populated.

## 11. Open questions

| Question | Owner | Status |
| -------- | ----- | ------ |
| Pi ↔ GitHub access for git deploy: public repo vs. read-only deploy key? | wes-cutting | **Resolved** → public repo (repo verified secret-clean first) |
| Hardcode the Pi IP, or DHCP-reserve/hostname the Pi? | wes-cutting | **Resolved** → single `LABS_HUB_HOST` var (default `raspberrypi.local`, mDNS) flows into allowed-hosts + tile links; no IP hardcoded |

## 12. UX (folded in)

**User & job:** the operator, on the van LAN, wants one place to see and reach all services and know they're healthy. (PRD journeys 1–2.)

**Entry point & navigation:** browser → `http://<pi>:3000` (Homepage). From a tile → the service. Management → Portainer `:9000` (separate, gated).

**Primary flow:**
1. Operator opens `http://<pi>:3000`.
2. Homepage renders grouped service tiles (auto-discovered from labels) with health + a resources widget.
3. Operator clicks a tile → opens that service (which handles its own auth).
4. For lifecycle/troubleshooting → Portainer.

**Screen: Homepage dashboard — states:**
- **Empty** (no labeled services): renders the shell + resources widget + a note; not a crash.
- **Loading:** brief; tiles/widgets show a pending state.
- **Populated:** grouped tiles (e.g. *Media → Jellyfin*, *Utilities → Homebox*) each with name/href/status; resources widget shows CPU/RAM/disk.
- **Error** (docker provider down): affected tiles show an error indicator (text/icon), page still renders.

**Wireframe:**
```
+-----------------------------------------------------------+
|  labs-hub                         [CPU 12% | RAM 1.2G | Disk] |
|                                                           |
|  Media                          Utilities                 |
|   ┌───────────────┐              ┌───────────────┐        |
|   │ Jellyfin   ●up │              │ Homebox    ●up │       |
|   │ Media server   │              │ Home inventory │       |
|   └───────────────┘              └───────────────┘        |
+-----------------------------------------------------------+
```

**Content/copy:** title "labs-hub"; group names from labels (Media/Utilities); status as text+icon ("up"/"down"), never color-only.

**Accessibility:** semantic headings for groups; status text+icon; keyboard-navigable links (Homepage defaults); note third-party limits.

**UX acceptance:** the Populated + Empty + Error states render as above; tiles show text/icon status; resources widget populated.

## 13. Out of scope / later

Jellyfin managed service (LH-S2), custom-service pattern (LH-S3), hub auth gate, historical metrics, persistence migration + backup (LH-S4).
