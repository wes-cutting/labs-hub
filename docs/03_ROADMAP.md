---
id: ROADMAP
type: roadmap
status: Living
roadmap-item: —
---

# Roadmap — labs-hub

| Field         | Value                          |
| ------------- | ------------------------------ |
| Status        | Living                         |
| Owner         | wes-cutting                    |
| Last updated  | 2026-07-26                     |
| History       | [`03_ROADMAP-HISTORY.md`](03_ROADMAP-HISTORY.md) — re-sequencing log + done/shipped ledger |
| Sources       | [`01_INTAKE.md`](01_INTAKE.md) · [`02_PRD.md`](02_PRD.md) · [`ADR-0001`](adr/ADR-0001-os-and-container-runtime.md) · [`ADR-0002`](adr/ADR-0002-service-data-and-state.md) |

**Current focus:** **LH-S1 — foundation hub slice** (now unblocked). SPIKE-05 decided:
**adopt Homepage + Portainer, don't build** ([ADR-0003](adr/ADR-0003-hub-platform.md)). LH-S1
is now *assemble & configure* the Homepage+Portainer seed stack (already running on the Pi)
into a proper, reproducible foundation. Needs a feature spec + UX spec (≥`Proposed`) and the
gate wired before build.

---

## 1. How to use this roadmap

Plan of record, kept live; ordered by **uncertainty × value**, not by layer. Every build item
is a **vertical, usable, gate-green slice**. Item status (delivery) ≠ document status
(`Proposed`/`Validated`/… on specs/ADRs). Re-sequencing and the shipped ledger live in the
[history sibling](03_ROADMAP-HISTORY.md).

**Item status vocabulary:** `Planned` · `Ready` · `In progress` · `Done` · `Deferred` · `Dropped`.

## 2. Sequencing model

Feasibility risk is already retired (SPIKE-01). So: **foundation slice first** (a usable shell
to build into), then **domain slices** (Jellyfin, custom services), with **persistence/backup
+ NFR hardening** pulled in as its gating spikes land. This is single-track (solo operator), so
Epics are skipped — items are `LH-S##` directly. Spikes keep the `SPIKE-##` series.

## 3. The plan

**Top = next.** Value / Risk are High/Med/Low. Next item = highest **Risk × Value** not yet
retired, whose gate (if any) has landed.

### Foundation

| Id | Item | Kind | Value | Risk | Gated by | Status | Links (spec · UX · spike) |
| -- | ---- | ---- | ----- | ---- | -------- | ------ | ------------------------- |
| LH-S1 | Foundation hub slice — **assemble & configure Homepage + Portainer** (open launcher + label-driven catalog + health + lifecycle) into a reproducible Compose foundation on the data-root | slice | High | Med | ✅ SPIKE-05 (done) → [ADR-0003](adr/ADR-0003-hub-platform.md) | Planned | spec: _todo_ · ux: _todo_ · [SPIKE-05](spikes/SPIKE-05-hub-platform-evaluation.md) |

### Spikes (risk retirement)

| Id | Item | Kind | Value | Risk | Answers (the question) | Status | Spike report |
| -- | ---- | ---- | ----- | ---- | ---------------------- | ------ | ------------ |
| SPIKE-01 | Pi 5 hub + Jellyfin feasibility | spike | High | High | Can the Pi 5 run a hub + Jellyfin transcode with headroom? | **Done (PASS)** | [SPIKE-01](spikes/SPIKE-01-pi5-hub-plus-jellyfin-feasibility.md) |
| SPIKE-05 | **Hub platform: adopt vs. build** | spike | High | High | Does an existing tool (or a light pairing) meet the hub must-haves on the Pi 5, or build custom? | **Done (adopt Homepage+Portainer)** | [SPIKE-05](spikes/SPIKE-05-hub-platform-evaluation.md) |
| SPIKE-02 | SD-card wear vs. external USB-3 SSD | spike | High | Med | Does 24/7 write load justify moving the data root to SSD, and does SSD behave on the Pi 5? | Planned | → `ADR-0002` |
| SPIKE-03 | At-rest encryption + backup/restore (headless) | spike | High | Med | Can a headless node unlock encrypted data acceptably, and can the data root be backed up **and restored**? | Planned | → `ADR-0002` |
| SPIKE-04 | Small quantized LLM (~1–3B) on the Pi | spike | Med | High | Is a small LLM usable alongside other services within the CPU/RAM budget? | Deferred | intake §4 #4 |

### Domain slices

| Id | Item | Kind | Value | Risk | Gated by | Status | Links (spec · UX) |
| -- | ---- | ---- | ----- | ---- | -------- | ------ | ----------------- |
| LH-S2 | Assemble **Jellyfin** into the hub (media), within the single-stream transcode budget | slice | High | Med | LH-S1 | Planned | _todo_ |
| LH-S3 | **Custom-service** deployment through the hub (same mechanism as assembled) | slice | High | Med | LH-S1 | Planned | _todo_ |

> **LH-S2 note — direct-play vs. transcode (address when the Jellyfin slice starts):**
> Direct-play (no live transcode → avoids the SPIKE-01 CPU ceiling) is decided by **all** of:
> container, **video codec**, **audio codec** (DTS/TrueHD are common hidden triggers),
> **subtitles** (image subs like PGS/VOBSUB force a *full* video transcode), and **bitrate**
> (a client cap below the source transcodes even when codecs match) — **and by the client.**
> `.mkv` alone does *not* guarantee direct-play (browsers can't direct-play `.mkv` at all).
> Safe browser target: **`.mp4` + H.264 + AAC + text (SRT) subs** at/under the playback cap.
> Native Jellyfin apps (TV/phone) decode far more and may direct-play the existing library
> untouched. **Open question feeding this slice + `07_NFR.md`:** which client devices will
> actually be used (browser vs. native apps)? — that determines how big the transcode
> constraint really is. "Pre-optimized library" = storing media in the client-friendly combo
> so the Pi never transcodes live.

### Hardening

| Id | Item | Kind | Value | Risk | Trigger (when) | Status | Links |
| -- | ---- | ---- | ----- | ---- | -------------- | ------ | ----- |
| LH-S4 | Persistence medium migration (data root → SSD) + backup/restore | hardening | High | Med | after SPIKE-02/03 | Planned | `ADR-0002` · `07_NFR.md` |
| LH-S5 | NFR budgets + transcode caps + observability | hardening | Med | Med | real multi-service usage exists | Planned | `07_NFR.md` |

## 4. History

Re-sequencing log + done/shipped ledger are append-only in
[`03_ROADMAP-HISTORY.md`](03_ROADMAP-HISTORY.md).
