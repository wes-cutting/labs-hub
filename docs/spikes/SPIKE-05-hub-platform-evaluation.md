---
id: SPIKE-05
type: spike
status: Done
roadmap-item: LH-S1
---

# SPIKE-05: Adopt an existing hub platform, or build custom?

| Field      | Value                                                                 |
| ---------- | --------------------------------------------------------------------- |
| Status     | Done                                                                   |
| Type       | Integration / feasibility                                             |
| Owner      | wes-cutting                                                           |
| Time-box   | 1 day — honored (single session)                                      |
| Date       | 2026-07-26                                                             |
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

Ran on the real Pi 5, all four candidates deployed against three real services (Jellyfin,
Homebox, an nginx placeholder). Footprints measured with `docker stats` (after enabling the
**memory cgroup** — see below). UI/UX criteria evaluated by the operator in-browser.

**Prerequisite uncovered (applies platform-wide):** the Pi's **memory cgroup controller was
disabled by default** (`cgroup.controllers` lacked `memory`), so `docker stats` reported
`MEM 0B` and per-service memory metrics (M6) were impossible for *any* candidate. Fixed by
adding `cgroup_enable=memory cgroup_memory=1` to `/boot/firmware/cmdline.txt` + reboot; RAM
metrics then read correctly. This is also a prerequisite for per-service memory *limits*
(feeds `07_NFR.md`).

### Score matrix

| Candidate | M1 catalog(+stopped) | M2 health | M3 gate(multi-user) | M4 widgets/custom | M5 lifecycle | M6 metrics | M7 footprint | M8 self-host/least-priv | Notes |
| --------- | -- | -- | -- | -- | -- | -- | -- | -- | ----- |
| **Homepage** | ⚠ launcher tiles (label auto-discovery), not stopped mgmt | ✅ | ❌ no built-in auth | ✅✅ widgets; custom via labels | ❌ launch-only | ⚠ via widget | ✅ ~169 MiB, 1 ctr | ✅ (RO socket possible) | Loved: simple, YAML, auto-discovery |
| **Portainer** | ✅ all containers incl. stopped | ✅ | ✅ users/teams/RBAC | ⚠ stacks, no widgets | ✅ start/stop/update | ✅ live CPU/RAM (no history) | ✅ ~87 MiB, 1 ctr | ⚠ RW docker socket | Management half of the pairing |
| **Dockge** | ⚠ compose stacks only | ⚠ basic | ✅ login | ❌ | ✅ (compose) | ✅ per-stack | ✅ light | ⚠ RW socket | **Ruled out** — stack-centric, no launcher/widgets |
| **Cosmos** | ✅ Servapps | ✅ + **history** | ✅✅ SSO/2FA path | ✅ app-store + custom | ✅ | ✅ system + per-app **history** | ⚠ ~21 MiB* but **privileged + host-net** | ❌ privileged; reverse-proxy SPOF | Most complete on paper; heaviest; assumes domain/public-HTTPS |

\* Cosmos' container RAM understates it — it runs `--privileged` with host networking, spawns
its own MongoDB, and becomes the reverse proxy the whole access path depends on.

### Confirmed
- **A launcher + manager pairing (Homepage + Portainer) covers the operator's real needs** on
  the Pi with a tiny footprint (~256 MiB combined, 2 unprivileged-ish containers) and full
  transparency.
- Homepage auto-discovers services from **container labels** — zero per-app routing.
- Portainer gives lifecycle (start/stop/update) + **live** per-container CPU/RAM (once the
  cgroup fix landed) behind its own gated admin.
- Cosmos is genuinely the most *complete* single tool (integrated gate + app-store + historical
  monitoring) and the only one with a real centralized-SSO path.

### Invalidated / revised
- **M3 ("single-login gate for the hub") revised.** Hands-on, the operator chose an **open
  launcher on the trusted LAN + per-app auth**, not a hub gate. M3 is *revised, not failed* —
  PRD updated; a forward-auth gate (e.g. Authelia) remains an add-later option.
- Cosmos' strengths (gate + history) land exactly on things the operator **deprioritized**
  (open launcher fine; "don't over-invest in multi-user"), so they don't justify its costs.

### Surprises / unknowns uncovered
- The **memory-cgroup prerequisite** above (Pi-wide; now fixed).
- **Cosmos assumes a domain / public-HTTPS / reverse-proxy model** that fights the LAN-only,
  CGNAT, no-domain reality (forced into "self-signed + allow local IP" side-paths).
- Homebox's current image **panics without `HBOX_AUTH_API_KEY_PEPPER` (≥32 bytes)** — noted
  for whenever Homebox becomes a real service (LH-S3-adjacent).

## 5. Recommendation / decision

**Adopt the pairing: Homepage (launcher/catalog/health/widgets) + Portainer (lifecycle +
live per-container metrics). Reject Cosmos and Dockge. Do not build a custom hub.**

Rationale (maps to the operator's decision criteria): open launcher is acceptable → no need
for Cosmos' gate; "don't over-invest in multi-user" → skip Cosmos' SSO machinery; prioritize
**resilience + least-privilege** → avoid Cosmos' privileged host-net reverse-proxy SPOF;
value **simple, transparent pieces** → Homepage YAML + Portainer over an all-in-one.

**Accepted trade-offs (with cheap exits):** no built-in history (add **Beszel** later if
wanted — far lighter than Cosmos/Grafana; verify ARM64 then); Portainer holds a RW Docker
socket (mitigate later with a socket-proxy — note in `07_NFR.md`).

→ Draft **`ADR-0003`** (hub platform) at `Validated`; re-scope **LH-S1** as *assemble &
configure Homepage + Portainer* (not "author a hub").

## 6. Impact on the plan

- **Specs/ADRs:** new `ADR-0003` (Validated) · `02_PRD.md` M3/auth goal + journey revised
  (open launcher) · `07_NFR.md` to carry the socket-proxy + memory-limit notes.
- **Scope:** LH-S1 becomes assemble-not-build; a custom hub is explicitly *not* being built.
- **Sequencing:** LH-S1 unblocked; Homepage + Portainer seed stack kept running on the Pi.

## 7. Follow-ups

- [x] `ADR-0003` (hub platform) — Homepage + Portainer.
- [x] Re-scope LH-S1 (assemble & configure).
- [ ] Future: Beszel for historical metrics (if desired); socket-proxy for Portainer (`07_NFR`).
- [ ] Future: forward-auth gate (Authelia) *if* the multi-user/SSO future arrives (`ADR-0003` growth path).
- [ ] Homebox needs `HBOX_AUTH_API_KEY_PEPPER` set when it becomes a real service.
