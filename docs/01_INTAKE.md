---
id: INTAKE
type: intake
status: Proposed
roadmap-item: —
---

# Intake — labs-hub

| Field        | Value                                  |
| ------------ | -------------------------------------- |
| Status       | Validated (feasibility bet confirmed by SPIKE-01) |
| Owner        | wes-cutting (DrewskiLabs)              |
| Facilitated  | human + agent                          |
| Last updated | 2026-07-26                             |

**Resume here:** `labs-hub` is a **self-hosted hub / control plane** that assembles proven
services (e.g. Jellyfin) and custom-built ones onto a single portable node — a Raspberry Pi
5 (8GB) — for a solo operator running a personal home/van ecosystem. The core bet is the
*hub*, not re-implementing mature services. Value comes as much from building and owning
every layer as from the end features. **Feasibility is now proven:**
[SPIKE-01](spikes/SPIKE-01-pi5-hub-plus-jellyfin-feasibility.md) (2026-07-26) confirmed the
Pi 5 runs a Docker/Compose hub + Jellyfin with a single 1080p transcode at ~2.8× realtime,
75 °C, no throttling, ~6.8 GB RAM free — **but CPU, not RAM, is the ceiling** (one transcode
≈ all 4 cores; Pi 5 has no HW H.264 encode → favor direct-play, cap concurrent transcodes).
**Next:** draft `ADR-0001` (Raspberry Pi OS 64-bit + Docker/Compose, `Validated`) and
`ADR-0002` (service data/state — still open), then write `02_PRD.md` (carrying the
transcode-as-scarce-resource NFR) and `03_ROADMAP.md`, then build the foundation hub slice.

---

## 1. Problem & why now

The operator wants a **personal, self-owned home network platform** — the entry point into
an at-home (and in-van) ecosystem — that he fully controls and understands at every layer.
Today there is no existing solution in place; this is the first real attempt. Off-the-shelf
homelab platforms exist (CasaOS, Umbrel, Synology) but were unknown at intake and, more to
the point, are deliberately *not* the path: the explicit intent is to **roll his own** so it
is truly customizable, and so the **act of building it is itself the value**. Context is
**Vanlife** — the platform lives on portable hardware in a van.

A second, deliberate purpose: this project **exercises and grows the baseline kit** itself.
Kit friction is captured in `docs/KIT_FEEDBACK.md` as a first-class co-deliverable.

## 2. Users & context

- **Primary (and only) user:** the operator — solo, tech-savvy, hands-on, able to drop to a
  shell and fill gaps with agile problem-solving. No third-party/stranger deployment burden.
- **Access:** even though solo, the hub requires an **authentication barrier** (single-user,
  default-deny) — not left open on the LAN.
- **Operating envelope (corrected during discovery):** the van has a **reliable power
  source** and **Starlink**, and is **parked while the platform is in use**. So the system
  does *not* need to survive zero-power/zero-internet operation. The honest requirement is
  **"tolerates Starlink"**: intermittent/high-latency connectivity and **CGNAT** (no public
  inbound IP by default). Physical context still implies heat, vibration/movement, and
  **theft exposure of the data** on the device.

## 3. The value hypothesis (the core bet)

> If I build a **portable, offline-capable hub** that lets me deploy and manage both
> assembled and custom services on the Pi, then I'll have a self-owned home/van ecosystem I
> can extend indefinitely — worth it because I control and understand every layer.

- **How we'd know it paid off:** the operator can bring a new service (assembled or custom)
  online through the hub, reach it authenticated on the van LAN, and see it healthy — and
  keep doing so as the catalog grows, without the node falling over.
- **Validation status:** ☑ intentionally near-unfalsifiable (value accrues from the journey
  regardless), so **no value-hypothesis spike applies**. Risk moves to **feasibility** and
  **scope discipline** instead — see §4.

## 4. Riskiest assumptions & the spikes they imply

Ordered most-plan-invalidating first. For an infrastructure project the first reality check
is **profiling the real hardware under real load**, not a dataset.

| # | Assumption (what we believe) | Have we looked? | Cheapest way to check (→ spike) | Spike type |
| - | ---------------------------- | --------------- | ------------------------------- | ---------- |
| 1 | A Pi 5 (8GB) can run an orchestrated hub **plus** a real service (Jellyfin, transcoding) with headroom to add more. | No | Stand it up on the actual Pi, serve one real stream to a LAN client, measure RAM/CPU/thermal/power headroom vs a threshold. | **feasibility** → SPIKE-01 |
| 2 | Scope stays disciplined — homelab sprawl is the real failure mode here, not a data surprise. | Partially (non-goals set, §5) | Enforced by process: vertical slices + roadmap, not a spike. | — |
| 3 | Container orchestration on ARM64 (runtime + how the hub brings services up/reports health) behaves as expected. | No | Folded into SPIKE-01; if it dominates, split into its own feasibility spike. | feasibility |
| 4 | Small quantized LLMs (~1–3B) are usable on the Pi alongside other services. | No | A later, isolated feasibility spike — deliberately deferred. | feasibility (future) |
| 5 | At-rest data on a physically stealable node needs encryption. | No | Later security spike once real data lands; noted, not first. | security (future) |

**First spike to run:** **SPIKE-01 (feasibility)** — *Can a Pi 5 (8GB) run a
container-orchestrated hub plus Jellyfin serving/transcoding one real media stream to a LAN
client, while leaving enough RAM/CPU/thermal headroom to add more services?* Falsifiable
against a headroom threshold; ~one day on the real box. Blocks `ADR-0001` (OS + container
runtime), `ADR-0002` (service data/state), and the foundation slice. See
[`SPIKE-REPORT-TEMPLATE`](../templates/SPIKE-REPORT-TEMPLATE.md).

## 5. Scope sketch & explicit non-goals

- **In scope (roughly value/uncertainty-ordered):**
  1. The **hub / control plane** itself — bring services up/down, show health, behind auth.
  2. **Assembling proven services** into the hub (first: Jellyfin / media).
  3. **Custom services** authored by us, deployed the same way as assembled ones.
  4. Portability/operability on the Pi within the van envelope.
- **Non-goals (agreed at intake — kept honest against sprawl):**
  1. **Not multi-user / not a product for others** — solo, single-tenant.
  2. **Not re-implementing mature services** — assemble them; don't rebuild Jellyfin et al.
  3. **Not public-internet-exposed** — LAN-only while parked; no tunnels/reverse-proxy-to-
     the-world yet (Starlink CGNAT makes this real work regardless).
  4. **Not LLM hosting yet** — deferred to a named future spike (assumption #4).
  5. **Not high-availability / clustering** — one node is fine.

## 6. Constraints

| Area | Notes |
| ---- | ----- |
| Data sensitivity (confidential/regulated?) | Personal media/photos/services on a **physically stealable** node → at-rest encryption is a real future consideration (assumption #5). No regulated/third-party data. |
| Compliance / legal | None identified (personal, single-user). |
| Stack leanings & constraints | **Hardware fixed:** Raspberry Pi 5, ARM64, 8GB shared RAM (CanaKit PRO, 128GB). **OS incumbent:** 64-bit Raspberry Pi OS (preinstalled) — recorded as an `ADR-0001` *input*, not a decision; SPIKE-01 may confirm or replace it. Orchestration layer (bare Docker / Compose / k3s) is open, an `ADR-0001/0002` decision after SPIKE-01. |
| Non-functional needs (latency / volume / availability) | Single LAN client to start; must tolerate **Starlink** (intermittent, high-latency, **CGNAT**); thermal/power headroom on the Pi is the binding constraint. Seeds `07_NFR.md`. |
| Timeline / team / budget | Solo, self-paced homelab; no external deadline. |

## 7. First usable slice

The thinnest end-to-end thing the operator can actually **use**: a **running hub, behind
authentication, that brings one real assembled service (Jellyfin) up and shows it healthy
and reachable on the van LAN.** Foundation it builds into: the auth barrier, the hub shell
(list services + health), and the deploy/manage mechanism that custom services will later
reuse. (Feeds the foundation slice and `03_ROADMAP.md`.)

## 8. Open questions

| Question | Owner | Status |
| -------- | ----- | ------ |
| OS: keep Raspberry Pi OS 64-bit or move to a leaner base? | operator | open — resolved by SPIKE-01 → `ADR-0001` |
| Orchestration layer: bare Docker vs Compose vs k3s on ARM64? | operator | open — informed by SPIKE-01 → `ADR-0001/0002` |
| Where does service data/state live, and how is it backed up (theft/loss)? | operator | open → `ADR-0002`, later security spike |
| What "healthy" means to the hub (health-check contract per service)? | operator | open — defined during the foundation slice |
| LLM hosting feasibility on the Pi | operator | deferred → future spike (assumption #4) |

## 9. Outputs & next steps

- [x] **Run the first spike:** SPIKE-01 (feasibility) → **Done** (PASS) —
      [Spike Report](spikes/SPIKE-01-pi5-hub-plus-jellyfin-feasibility.md).
- [ ] **Open `ADR-0001` (stack: OS + container runtime)** — Raspberry Pi OS 64-bit +
      Docker/Compose, draft `Validated` per SPIKE-01. Then `ADR-0002` (service data/state).
- [ ] **Write the PRD** ([`02_PRD.md`](../templates/PRD-TEMPLATE.md)) — feasibility bet now
      de-risked; carry the transcode-as-scarce-resource NFR.
- [ ] **Draft the roadmap** ([`03_ROADMAP.md`](../templates/ROADMAP-TEMPLATE.md)), sequenced
      by the uncertainty above (foundation hub slice next).

> This intake was **pre-PRD** and is now `Validated` — SPIKE-01 confirmed its feasibility
> bet. Produced via [`templates/DISCOVERY-GUIDE.md`](../templates/DISCOVERY-GUIDE.md).
