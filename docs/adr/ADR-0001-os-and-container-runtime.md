---
id: ADR-0001
type: adr
status: Validated
supersedes: —
---

# ADR-0001: OS and container runtime — Raspberry Pi OS 64-bit + Docker + Compose

| Field         | Value                                                              |
| ------------- | ----------------------------------------------------------------- |
| Status        | Validated                                                         |
| Date          | 2026-07-26                                                        |
| Deciders      | wes-cutting                                                       |
| Validated by  | [SPIKE-01](../spikes/SPIKE-01-pi5-hub-plus-jellyfin-feasibility.md) |

## Context

`labs-hub` is a self-hosted hub/control plane on fixed hardware — a **Raspberry Pi 5 (8GB,
ARM64)**. The kit requires the OS and the mechanism that runs services to be chosen in an ADR
after a feasibility spike, not assumed. The incumbent OS is the CanaKit-preinstalled
**64-bit Raspberry Pi OS (Debian 12 Bookworm)**; the orchestration layer was open (bare
containers vs. Docker Compose vs. k3s).

[SPIKE-01](../spikes/SPIKE-01-pi5-hub-plus-jellyfin-feasibility.md) ran the real hardware:
Docker + Compose brought up a hub placeholder + Jellyfin from stock ARM64 images with no
special setup, and served a live 1080p transcode at ~2.8× realtime, 75 °C, `get_throttled=0x0`,
~6.8 GB RAM free. The pattern works; the binding constraint is **CPU during transcode**, not
RAM (the Pi 5 has no hardware H.264 encoder — encode is software libx264).

## Decision

We will run `labs-hub` on **64-bit Raspberry Pi OS (Debian 12 Bookworm)** and orchestrate
services with **Docker Engine + the Docker Compose plugin** (validated at Docker 29.6.2 /
Compose v5.3.1). Concretely:

- Each service (assembled or custom) is a **container**, declared in **Compose** — this is the
  single deploy/manage mechanism the hub drives; custom services deploy the same way as
  assembled ones.
- We stay on the stock OS rather than a leaner distro — SPIKE-01 showed no resource pressure
  from the base OS, so the cost of a custom base isn't justified now.
- We defer **k3s / Kubernetes** — a single node with a solo operator does not need cluster
  orchestration; Compose is the right-sized tool (revisit only if multi-node ever becomes a
  goal, which is currently a non-goal).

## Consequences

### Positive
- Broad ARM64 image availability (Jellyfin and most self-hosted services publish arm64).
- Compose files are declarative, diffable, and reproducible — a natural fit for the hub.
- Stock OS = well-trodden support path; no bespoke base image to maintain.

### Negative / cost
- **No hardware H.264 encode** on the Pi 5 → live transcoding is software libx264 and
  effectively single-stream (see `ADR`-adjacent NFR in `02_PRD.md`/`07_NFR.md`). Not an OS
  choice we can fix — a hardware reality this stack must design around.
- Docker adds a daemon + overlay networking overhead (negligible at this scale per SPIKE-01).

### Neutral
- Docker group membership grants root-equivalent access; on a single-operator box this is
  acceptable, but it is a security note for `SECURITY.md` (the hub must still enforce its own
  auth barrier).

## Alternatives considered

### Bare containers (podman/docker run) without Compose
Rejected: loses the declarative, multi-service manifest the hub needs; Compose is the
lowest-ceremony way to express "these services, these volumes, these ports."

### k3s / lightweight Kubernetes
Rejected (deferred): cluster orchestration is unjustified complexity for one node and one
operator; multi-node is a current non-goal.

### A leaner base OS (DietPi / Ubuntu Server ARM64)
Rejected for now: SPIKE-01 showed the stock OS imposes no meaningful resource cost, so a
migration buys little and adds risk.

## Supersedes / superseded by

- Supersedes: —
- Superseded by: —
