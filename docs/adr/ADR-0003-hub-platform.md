---
id: ADR-0003
type: adr
status: Validated
supersedes: —
---

# ADR-0003: Hub platform — adopt Homepage + Portainer (don't build a custom hub)

| Field         | Value                                                    |
| ------------- | -------------------------------------------------------- |
| Status        | Validated                                                |
| Date          | 2026-07-26                                               |
| Deciders      | wes-cutting                                              |
| Validated by  | [SPIKE-05](../spikes/SPIKE-05-hub-platform-evaluation.md) |

## Context

The hub/control plane is the core of `labs-hub` (PRD §3). The open question was whether to
**author a custom hub** or **assemble an existing tool**, given non-goal #2 (don't reinvent
mature services). [SPIKE-05](../spikes/SPIKE-05-hub-platform-evaluation.md) evaluated four
candidates on the real Pi against an 8-item must-have matrix, with the operator judging the
UI/UX. Decision criteria the operator confirmed during the eval: an **open launcher on the
trusted LAN is acceptable** (per-app auth), **don't over-invest in multi-user** yet,
**prioritize resilience + least-privilege**, and value **simple, transparent pieces**.

## Decision

We will **adopt a pairing** as the hub, and **not build a custom hub**:

- **Homepage** — the launcher/catalog + health + widgets. Services appear via **Docker
  labels** (auto-discovery); custom services get a tile by adding labels.
- **Portainer** — container lifecycle (start/stop/update) + **live** per-container CPU/RAM,
  behind its own gated admin.

Both run as standard containers (`ADR-0001`). The launcher is **open on the LAN**; services
keep their own logins. A forward-auth gate is explicitly a **later** option, not now.

## Consequences

### Positive
- Tiny, transparent footprint (~256 MiB combined, two containers) — fits the Pi with room to
  spare and matches "understand every layer."
- **Loosely coupled / resilient:** if either tool dies, services stay reachable directly by
  port — no single point of failure.
- Least-privilege relative to the alternative (no privileged/host-net reverse proxy).
- Auto-discovery via labels means custom services (LH-S3) surface with near-zero config.

### Negative / cost
- **No built-in historical monitoring** (only live stats). Exit: add **Beszel** later
  (lightweight; verify ARM64) if trend history is wanted.
- **No hub-level auth gate** — the launcher is open on the LAN (accepted; revises PRD M3).
  Exit: add a forward-auth (e.g. Authelia) if a gate/multi-user future arrives.
- **Portainer holds a read-write Docker socket** (root-equivalent) — the main privilege cost.
  Mitigate later with a socket-proxy (note in `07_NFR.md`).

### Neutral
- Two tools instead of one; acceptable given each is single-purpose and independently swappable.

## Alternatives considered

### Cosmos-Server (all-in-one)
Rejected. The most *complete* single tool (integrated gate, app-store, historical monitoring,
real centralized-SSO path) — but its strengths (gate + SSO + history) land on exactly what the
operator deprioritized, while its costs hit what they care about: it runs **privileged with
host networking**, becomes the **reverse proxy the whole access path depends on** (SPOF),
spawns its own MongoDB, and assumes a **domain / public-HTTPS** model that fights the LAN-only,
CGNAT reality. Revisit only if a centralized-SSO multi-user future becomes a firm goal.

### Dockge
Rejected. Clean Compose-stack manager, but stack-centric with no launcher/catalog or widgets —
doesn't fit the "hub" shape.

### Build a custom hub
Rejected (for now). SPIKE-05 showed adoption meets the needs; building would violate
non-goal #2 and spend effort where mature tools already suffice. The must-have matrix remains
on file as the requirements *if* a custom hub is ever revisited.

## Growth path (deferred, not decided)

If multi-user/SSO becomes real: add a forward-auth gate (Authelia) in front of the launcher,
or re-evaluate an identity portal (Authentik) — a future ADR, gated by a real need.

## Supersedes / superseded by

- Supersedes: —
- Superseded by: —
