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

**Current focus:** **LH-S3 is unblocked and now split.** budgeteer shipped its auth epic (its
`ADR-0009`), retiring the blocker, and added a **demo instance** (synthetic data, own database and
secrets). So **LH-S3-demo is Done** — the first custom app is on the hub, proving the whole pattern
(CI→GHCR→pull, Postgres container, data-root, labels, `/api/health` in smoke) against a box where a
mistake costs nothing. **LH-S3 proper — the real ledger — is `Planned`, not done**, and needs
decisions the demo did not answer: TLS at the hub vs. `SESSION_COOKIE_SECURE`, backup, and at-rest
encryption. The recommended next work is therefore **SPIKE-02/03** (SSD + at-rest
encryption/backup), which now gates a real financial ledger rather than merely preceding it.
(LH-S1 hub, LH-S2 Jellyfin and LH-S3-demo are deployed: tracked `deploy/`, gate-green with CI, data
on the data-root, auto-discovered — [FEAT-LH-S1](features/LH-S1-hub-foundation.md) ·
[FEAT-LH-S2](features/LH-S2-jellyfin.md) · [FEAT-LH-S3-DEMO](features/LH-S3-budgeteer-demo.md).)

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
| LH-S1 | Foundation hub slice — Homepage + Portainer as a reproducible Compose foundation (`deploy/`), gate + CI wired, git-deployed, auto-discovery | slice | High | Med | ✅ SPIKE-05 → [ADR-0003](adr/ADR-0003-hub-platform.md) | **Done** (deployed) | [FEAT-LH-S1](features/LH-S1-hub-foundation.md) (feature+UX) · [SPIKE-05](spikes/SPIKE-05-hub-platform-evaluation.md) |

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
| LH-S2 | **Jellyfin** as a managed service (`compose.media.yml`, data-root, labels), within the single-stream transcode budget | slice | High | Med | LH-S1 | **Done** | [FEAT-LH-S2](features/LH-S2-jellyfin.md) |
| LH-S3-demo | **budgeteer demo instance** (first custom app on the hub) — `v0.2.0` pulled from GHCR (arm64, digest-pinned) + Postgres 16 on the data-root, own network/secrets, labels, `/api/health` in smoke. **Synthetic data only.** | slice | Med | Low | LH-S1 · budgeteer BUD-S93 | **Done** (deployed) | [FEAT-LH-S3-DEMO](features/LH-S3-budgeteer-demo.md) |
| LH-S3 | **Deploy budgeteer for real** (the household ledger) — same image and pattern as the demo, but carrying real financial data. Auth blocker **retired** (budgeteer `ADR-0009`); now gated on the **data-at-rest and TLS decisions** instead. | slice | High | Med | SPIKE-03 (at-rest encryption/backup) · TLS-vs-cookie decision (`DEPLOY_CONTRACT` §5) · LH-S3-demo | **Planned** | see LH-S3 note below |

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

> **LH-S3 note — budgeteer, the auth-before-exposure rule, and why the slice split:**
> The original block was that `budgeteer` had **no authentication** while holding **real financial
> data**. That is **retired**: budgeteer shipped users/sessions with a default-deny gate, roles,
> login throttling and session-expiry guards (BUD-S87..S89; its `ADR-0009` is `Accepted`).
> **The deploy shape held up exactly as decided** — image built in **CI → GHCR (ARM64)**, Pi
> **pulls** it, a **Postgres container** for state, one process serving API + SPA, data on the
> data-root, Homepage labels, health in smoke — and `LH-S3-demo` has now exercised all of it.
> **Why the split:** budgeteer's own `DEPLOY_CONTRACT` §10 demo instance made it possible to prove
> the pattern with **synthetic data**, so the risky decisions are not bundled with the plumbing.
> **What the demo did NOT answer, and LH-S3 proper still must:**
> (a) **TLS vs. `SESSION_COOKIE_SECURE`** (`DEPLOY_CONTRACT` §5) — the demo sets it `false` because
> the hub serves plain HTTP and browsers discard `Secure` cookies over HTTP; a real ledger must not
> inherit that, so the hub needs TLS termination or an explicit, accepted exposure.
> (b) **At-rest encryption + backup** — **SPIKE-03**, jointly owned with budgeteer
> (`DEPLOY_CONTRACT` §8). budgeteer confines all state to one Postgres volume, which is what makes
> encrypting it tractable; nothing encrypts it today.
> (c) **`ADR-0004`** formalizing the custom-service pattern — deliberately still unwritten:
> *decided ≠ validated*, and one synthetic box is not yet validation on a service that matters.
> **General rule this established, and which still stands:** *a custom service that handles
> sensitive data must have default-deny auth before it is exposed on the LAN* (candidate for
> `SECURITY.md`).

### Hardening

| Id | Item | Kind | Value | Risk | Trigger (when) | Status | Links |
| -- | ---- | ---- | ----- | ---- | -------------- | ------ | ----- |
| LH-S4 | Persistence medium migration (data root → SSD) + backup/restore | hardening | High | Med | after SPIKE-02/03 | Planned | `ADR-0002` · `07_NFR.md` |
| LH-S5 | NFR budgets + transcode caps + observability | hardening | Med | Med | real multi-service usage exists | Planned | `07_NFR.md` |

## 4. History

Re-sequencing log + done/shipped ledger are append-only in
[`03_ROADMAP-HISTORY.md`](03_ROADMAP-HISTORY.md).
