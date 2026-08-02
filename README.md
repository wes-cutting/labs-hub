# labs-hub

A **portable, self-hosted hub / control plane** for a personal home-and-van ecosystem — one
node that **assembles proven services** (Jellyfin, and more) and **hosts custom-built ones**
behind a single authentication barrier, running on a Raspberry Pi 5 you fully own and
understand.

> Built from the DrewskiLabs baseline starter kit (see [`KIT-README.md`](KIT-README.md)). This
> README is a **living project overview** — it grows as the project does.

## Status

**Phase:** foundation built. Discovery, feasibility, and the hub-platform choice are done, and
the **hub foundation (LH-S1) is running on the Pi** from a tracked, gate-green Compose definition.

- **Feasibility:** ✅ validated — [SPIKE-01](docs/spikes/SPIKE-01-pi5-hub-plus-jellyfin-feasibility.md)
  (Pi 5 runs a Docker/Compose hub + Jellyfin transcoding at ~2.8× realtime; **CPU, not RAM, is
  the ceiling** — no hardware H.264 encode, so live transcoding is effectively single-stream).
- **Hub platform:** ✅ decided — adopt **Homepage + Portainer** ([ADR-0003](docs/adr/ADR-0003-hub-platform.md), [SPIKE-05](docs/spikes/SPIKE-05-hub-platform-evaluation.md)).
- **Foundation (LH-S1):** ✅ built — `deploy/` Compose foundation, `make gate` green + CI wired, running on the Pi, auto-discovering services ([FEAT-LH-S1](docs/features/LH-S1-hub-foundation.md)).
- **Jellyfin (LH-S2):** ✅ built — managed service in `deploy/compose.media.yml`, data on the data-root, discovered on the hub, within the transcode budget ([FEAT-LH-S2](docs/features/LH-S2-jellyfin.md)).
- **Resume from:** the newest status report —
  [`docs/status-reports/2026-07-26-lh-s2.md`](docs/status-reports/2026-07-26-lh-s2.md).
- **Next:** **LH-S3** — the custom-service deployment pattern — see [`docs/03_ROADMAP.md`](docs/03_ROADMAP.md).

## What it is (and isn't)

- **Is:** a hub that brings services up/down and shows their health, behind single-user auth,
  on the van LAN — the custom work lives in the *hub*, not in re-implementing mature services.
- **Isn't** (current non-goals): multi-user/public, a rebuild of mature services,
  internet-exposed, an LLM host (yet), or high-availability/multi-node. Full list in
  [`docs/02_PRD.md`](docs/02_PRD.md) §4.

## Stack

Chosen per project via ADRs (see [`docs/adr/`](docs/adr/)):

| Layer | Choice | Decision |
| ----- | ------ | -------- |
| Hardware | Raspberry Pi 5 (8GB, ARM64), CanaKit PRO 128GB | fixed constraint |
| OS | 64-bit Raspberry Pi OS (Debian 12 Bookworm) | [`ADR-0001`](docs/adr/ADR-0001-os-and-container-runtime.md) — **Validated** |
| Orchestration | Docker Engine + Compose plugin | [`ADR-0001`](docs/adr/ADR-0001-os-and-container-runtime.md) — **Validated** |
| Service data / state | Single data-root, bind mounts, likely external SSD | [`ADR-0002`](docs/adr/ADR-0002-service-data-and-state.md) — **Proposed** (medium/backup/encryption not yet spiked) |
| Gate | `make gate` (yamllint + `docker compose config` + shellcheck) + smoke; CI in `.github/workflows/gate.yml` | wired (LH-S1) |
| Hub | Homepage (launcher/catalog/health) + Portainer (lifecycle/metrics), in `deploy/` | [ADR-0003](docs/adr/ADR-0003-hub-platform.md) — **Validated** |

## How we work

This project follows the kit's process spine — **reality before paper; vertical, not
horizontal; front-load risk; usable every step; decided ≠ validated; secure from commit zero.**

- Contributor + agent guide: [`CLAUDE.md`](CLAUDE.md)
- Process spine (read first): [`docs/00_WAYS_OF_WORKING.md`](docs/00_WAYS_OF_WORKING.md)
- Documentation map: [`docs/README.md`](docs/README.md)

## Documentation

| Doc | What |
| --- | ---- |
| [`docs/01_INTAKE.md`](docs/01_INTAKE.md) | Captured discovery — problem, users, the core bet (Validated) |
| [`docs/02_PRD.md`](docs/02_PRD.md) | Product requirements — goals, non-goals, journeys, the transcode NFR |
| [`docs/03_ROADMAP.md`](docs/03_ROADMAP.md) | Living plan of record (+ [history](docs/03_ROADMAP-HISTORY.md)) |
| [`docs/adr/`](docs/adr/) | Architecture decisions (stack + data/state) |
| [`docs/spikes/`](docs/spikes/) | Time-boxed investigations (feasibility proven here) |
| [`docs/status-reports/`](docs/status-reports/) | Point-in-time hand-off snapshots (start from the newest) |
| [`docs/KIT_FEEDBACK.md`](docs/KIT_FEEDBACK.md) | Improvements fed back to the baseline kit as we build |

## Operating notes

- **Target host:** Raspberry Pi 5 on the LAN, reached over key-based SSH at **`raspberrypi.local`**
  (mDNS/Avahi — follows the Pi across networks and DHCP IP changes; no need to chase IPs). The
  reachable name is configurable in one place via **`LABS_HUB_HOST`** in `deploy/.env`. For
  roaming/off-LAN access (Vanlife), Tailscale gives a stable name over a private overlay.
- **Growing the kit is a co-deliverable:** friction found while building is logged in
  [`docs/KIT_FEEDBACK.md`](docs/KIT_FEEDBACK.md) for a later kit pass.
