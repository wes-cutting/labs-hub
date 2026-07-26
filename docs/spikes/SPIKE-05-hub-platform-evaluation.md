---
id: SPIKE-05
type: spike
status: Open
roadmap-item: LH-S1
---

# SPIKE-05: Adopt an existing hub platform, or build custom?

| Field      | Value                                                                 |
| ---------- | --------------------------------------------------------------------- |
| Status     | Open                                                                   |
| Type       | Integration / feasibility                                             |
| Owner      | wes-cutting                                                           |
| Time-box   | 1 day — honor it; deeper eval of the winner becomes its own work      |
| Date       | —                                                                     |
| Blocks     | **LH-S1** (foundation hub slice — decides what it *is*) · possibly `ADR-0003` (hub platform choice) |

## 1. The question

**Does an existing self-hosted tool (or a minimal pairing of two) meet the labs-hub hub
must-haves — on the Pi 5, within an acceptable footprint — or must we build a custom hub?**

Falsifiable: score each candidate against the must-have matrix (§2) on the real box.
**PASS** = at least one candidate (or a two-tool pairing) meets all must-haves with an
acceptable measured footprint → adopt it. **FAIL** = none do → build custom (and this spike's
matrix becomes the custom hub's requirements).

## 2. Must-have matrix (from PRD §3 + operator criteria, 2026-07-26)

| # | Must-have | Notes |
| - | --------- | ----- |
| M1 | **Service catalog** — lists services, **running *and* installed-but-stopped** | Container/Compose is the unit (`ADR-0001`); stopped = `docker ps -a`. Host (non-container) apps are out of scope by design. |
| M2 | **Live health & status** | Per-service up/down at minimum. |
| M3 | **Single-login gate for the hub** | *Just gate the hub* (not full SSO); services keep own logins. **Must have a credible path to multi-user/SSO later.** |
| M4 | **Extensibility** — custom widgets **and** custom services | Can the operator add an in-house service + a custom tile/widget without forking? |
| M5 | **Container lifecycle** — start / stop / update from the hub | Not just links. |
| M6 | **Per-service resource metrics** (CPU / RAM) | Ties to the SPIKE-01 CPU ceiling — operator must *see* transcode load. |
| M7 | **Pi-5 fit** — ARM64 image + acceptable **measured** footprint | RAM is abundant (SPIKE-01) but count containers/idle RAM; must not crowd the transcode budget. |
| M8 | **Self-hosted, offline/LAN-friendly, solo-maintainable** | No cloud dependency; sane config/upgrade story for one operator. |

**Scored but not must-have (tie-breakers / future value):**
- **App-store / install-catalog** ("browse & install new apps") — an all-in-one feature; note if present.
- **Auto-discovery** of services from Docker labels (vs. hand-maintained lists).
- **Passkeys / 2FA** (deferred by operator, but note if free).
- **Reverse proxy + LAN TLS** at a single entry point (note if bundled).

## 3. Method

Throwaway, on the **real Pi 5** (reuse/extend the SPIKE-01 Docker environment; the existing
`spike01` stack gives real containers to discover/manage). Install the shortlist one at a time,
point each at real running containers, and score the matrix. **Measure** idle + added footprint
(`docker stats`, `free -m`) — do not assume it.

**Candidate shortlist** (verify ARM64 image + current status *during* the spike — reality
before paper):

| Candidate | Shape | Why on the list |
| --------- | ----- | --------------- |
| **Cosmos-Server** | All-in-one: auth gate + reverse proxy + container mgmt + monitoring + app store | Matches the most must-haves in one tool; heaviest — footprint must be measured. |
| **Portainer** | Container management UI (start/stop/update, stopped containers, stats, users) | Strong on M1/M5/M6/M3; weaker on M4 widgets / launcher feel. |
| **Homepage** | Launcher + widgets + Docker auto-discovery + service integrations | Strong on M1/M2/M4; **no built-in auth** (needs a light gate) and no lifecycle mgmt (M5). |
| **Dockge** | Compose-focused management UI | Light; good M5 for Compose; thin on health widgets/metrics. |
| _(pairing)_ **Homepage + a light gate** (e.g. Authelia forward-auth) + Portainer/Dockge | Compose two tools to cover launcher+health+auth + management | Fallback if no single tool passes; note the added complexity cost. |

**Deliberately NOT doing:** full SSO-in-front-of-services (operator chose *just gate the hub*),
multi-user rollout, production hardening, or picking the app catalog's contents. Time-box to the
scoring, not a bake-off to perfection.

## 4. Findings

> _To be filled when the spike runs. Fill the matrix per candidate (✅/⚠/❌ + evidence),
> paste measured idle/added RAM and container counts, and note each tool's extensibility
> mechanism + multi-user path._

### Score matrix (fill in)

| Candidate | M1 | M2 | M3 | M4 | M5 | M6 | M7 | M8 | Footprint (idle RAM / #containers) |
| --------- | -- | -- | -- | -- | -- | -- | -- | -- | ---------------------------------- |
| Cosmos | | | | | | | | | |
| Portainer | | | | | | | | | |
| Homepage (+gate) | | | | | | | | | |
| Dockge | | | | | | | | | |

### Confirmed / Invalidated / Surprises
- …

## 5. Recommendation / decision

> _To be filled._ Adopt <X> / adopt pairing <X+Y> / build custom. If adopt → draft `ADR-0003`
> (hub platform) and scope LH-S1 as "stand up + configure <X> as the hub." If build → LH-S1 is
> "author the hub"; this matrix is its requirements.

## 6. Follow-ups

- [ ] `ADR-0003` (hub platform) if a tool is adopted.
- [ ] Re-scope LH-S1 from the outcome (assemble-and-configure vs. author).
- [ ] Note multi-user/SSO growth path for a future ADR (deferred, per operator).
