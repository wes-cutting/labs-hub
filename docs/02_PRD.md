---
id: PRD
type: prd
status: Proposed
roadmap-item: —
---

# Product Requirements — labs-hub

| Field        | Value                          |
| ------------ | ------------------------------ |
| Status       | Proposed                       |
| Owner        | wes-cutting                    |
| Last updated | 2026-07-26                     |

> Feasibility is `Validated` ([SPIKE-01](spikes/SPIKE-01-pi5-hub-plus-jellyfin-feasibility.md));
> the **product** bet is intentionally near-unfalsifiable (value is in owning/building it), so
> this PRD stays `Proposed` and is proven out slice-by-slice, not by a value spike. Sources:
> [`01_INTAKE.md`](01_INTAKE.md).

## 1. Problem & why now

A solo, technically capable operator wants a **personal, self-owned home/van network platform**
he controls and understands at every layer — the entry point into an at-home-and-in-van
ecosystem. Off-the-shelf homelab platforms (CasaOS, Umbrel, Synology) exist but are
deliberately not the path: the point is to **roll his own** for full customization, and the act
of building it is itself the value. Now, because the hardware (Pi 5) is in hand and feasibility
is proven.

## 2. Users

- **Primary and only user:** the operator — solo, tech-savvy, hands-on, comfortable at a shell.
- **Context:** Vanlife. The node runs on a Pi 5 in a van with **reliable power + Starlink**,
  **parked while in use**. Access is on the **van LAN**; the operator is also the LAN client.
- No third-party/stranger users (see non-goals).

## 3. Goals

1. A **hub / control plane** that can bring services up/down and show their **health**, behind
   a **single-user authentication barrier**.
2. **Assemble proven services** into the hub — first Jellyfin (media).
3. Deploy **custom-built services** through the same mechanism as assembled ones.
4. Operate reliably within the **Pi-5 + van envelope** (thermal/CPU headroom respected,
   tolerant of Starlink connectivity).

## 4. Non-goals (explicit)

1. **Not multi-user / not a product for others** — solo, single-tenant.
2. **Not re-implementing mature services** — assemble Jellyfin et al.; don't rebuild them.
3. **Not public-internet-exposed** — LAN-only while parked; no tunnels/reverse-proxy-to-the-
   world (Starlink CGNAT makes this real work anyway).
4. **Not LLM hosting yet** — deferred to a named future spike.
5. **Not high-availability / multi-node / clustering** — one node is fine (`ADR-0001`).
6. **Not unlimited concurrent transcoding** — the hardware supports ~one live transcode
   (see §5 NFR); more concurrent heavy transcodes is out of scope for the hardware.

## 5. Success metrics / value hypothesis

**Value hypothesis (adopted, intake §3):** *If I build a portable, offline-capable hub that
lets me deploy and manage both assembled and custom services on the Pi, then I'll have a
self-owned home/van ecosystem I can extend indefinitely — worth it because I control and
understand every layer.*

**Observable signal it's paying off:** the operator can bring a new service online **through
the hub**, reach it **authenticated on the van LAN**, and see it **healthy** — and keep doing
so as the catalog grows, without the node falling over.

**Key non-functional requirement (first-order, from SPIKE-01):**
> **Live transcoding is a scarce, ~single-stream resource.** One 1080p transcode ≈ all four
> cores (no HW H.264 encode on the Pi 5). The platform must **favor direct-play** (curate media
> in client-compatible formats / pre-optimized libraries) and **cap concurrent transcodes**.
> RAM is abundant; CPU-during-transcode is the ceiling. Detail belongs in `07_NFR.md`.

## 6. User journeys

Named end-to-end flows (these drive e2e tests):

1. **Sign in to the hub** — operator opens the hub on the van LAN, authenticates, lands on the
   service dashboard (default-deny: unauthenticated sees nothing).
2. **See service health** — the dashboard lists running services and each one's health status.
3. **Bring a service up / down** — operator deploys/starts (and stops) a service through the
   hub; state reflects in the dashboard.
4. **Use an assembled service** — operator opens Jellyfin from the hub and plays media
   (direct-play preferred; transcode within the single-stream budget).
5. **Add a custom service** *(later)* — operator deploys an in-house service via the same
   mechanism, and it appears in the hub like any other.

## 7. Scope (high level)

Ordered by value/uncertainty for sequencing:

1. **Foundation hub slice** — auth barrier + hub shell (list services + health) + the
   bring-a-service-up mechanism, vertically usable. (Journeys 1–3, plus surfacing one service.)
2. **Assemble Jellyfin** into the hub (journey 4), respecting the transcode budget.
3. **Custom-service deployment** through the hub (journey 5).
4. **Hardening / ops** — persistence medium + backup (`ADR-0002` spikes), NFR budgets,
   at-rest encryption, observability.

## 8. Risks & assumptions

| Assumption / risk | Status | Test |
| ----------------- | ------ | ---- |
| Pi 5 can host hub + a real service with headroom | **Validated** | [SPIKE-01](spikes/SPIKE-01-pi5-hub-plus-jellyfin-feasibility.md) |
| CPU (transcode), not RAM, is the ceiling | **Validated** | SPIKE-01 — one stream ≈ 4 cores |
| Persistence medium (SD vs SSD) survives 24/7 writes | **Open** | `ADR-0002` spike (SD wear vs USB-3 SSD) |
| Backup/restore + at-rest encryption are workable headless | **Open** | `ADR-0002` spike (security/ops) |
| Small quantized LLM usable alongside services | **Open (deferred)** | future spike (intake §4 #4) |
| Scope stays disciplined (homelab sprawl) | **Ongoing** | vertical slices + non-goals, not a spike |

## 9. Open questions

| Question | Owner | Status |
| -------- | ----- | ------ |
| What does the hub *build on* — an existing dashboard (e.g. Homepage/Dockge-style) or a custom app? | wes-cutting | open — decide at the foundation slice (may warrant `ADR-0003`) |
| What is the health-check contract each service exposes to the hub? | wes-cutting | open — defined in the foundation slice |
| Auth mechanism for the single-user barrier (local creds vs. a proven auth proxy)? | wes-cutting | open — foundation slice (may warrant an ADR) |
| Persistence medium + backup (see `ADR-0002`) | wes-cutting | open → `ADR-0002` spikes |
