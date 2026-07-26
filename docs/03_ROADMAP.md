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

**Current focus:** **LH-S1 — the foundation hub slice** (auth barrier + hub shell listing
services & health + bring-one-service-up). Not yet `Ready`: it needs a feature spec + UX spec
(at least `Proposed`) and the stack scaffold with the gate wired (`ADR-0001`) before build.

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
| LH-S1 | Foundation hub slice — auth barrier + hub shell (list services + health) + bring one service up | slice | High | Med | — (feasibility retired by SPIKE-01) | Planned | spec: _todo_ · ux: _todo_ · [SPIKE-01](spikes/SPIKE-01-pi5-hub-plus-jellyfin-feasibility.md) |

### Spikes (risk retirement)

| Id | Item | Kind | Value | Risk | Answers (the question) | Status | Spike report |
| -- | ---- | ---- | ----- | ---- | ---------------------- | ------ | ------------ |
| SPIKE-01 | Pi 5 hub + Jellyfin feasibility | spike | High | High | Can the Pi 5 run a hub + Jellyfin transcode with headroom? | **Done (PASS)** | [SPIKE-01](spikes/SPIKE-01-pi5-hub-plus-jellyfin-feasibility.md) |
| SPIKE-02 | SD-card wear vs. external USB-3 SSD | spike | High | Med | Does 24/7 write load justify moving the data root to SSD, and does SSD behave on the Pi 5? | Planned | → `ADR-0002` |
| SPIKE-03 | At-rest encryption + backup/restore (headless) | spike | High | Med | Can a headless node unlock encrypted data acceptably, and can the data root be backed up **and restored**? | Planned | → `ADR-0002` |
| SPIKE-04 | Small quantized LLM (~1–3B) on the Pi | spike | Med | High | Is a small LLM usable alongside other services within the CPU/RAM budget? | Deferred | intake §4 #4 |

### Domain slices

| Id | Item | Kind | Value | Risk | Gated by | Status | Links (spec · UX) |
| -- | ---- | ---- | ----- | ---- | -------- | ------ | ----------------- |
| LH-S2 | Assemble **Jellyfin** into the hub (media), within the single-stream transcode budget | slice | High | Med | LH-S1 | Planned | _todo_ |
| LH-S3 | **Custom-service** deployment through the hub (same mechanism as assembled) | slice | High | Med | LH-S1 | Planned | _todo_ |

### Hardening

| Id | Item | Kind | Value | Risk | Trigger (when) | Status | Links |
| -- | ---- | ---- | ----- | ---- | -------------- | ------ | ----- |
| LH-S4 | Persistence medium migration (data root → SSD) + backup/restore | hardening | High | Med | after SPIKE-02/03 | Planned | `ADR-0002` · `07_NFR.md` |
| LH-S5 | NFR budgets + transcode caps + observability | hardening | Med | Med | real multi-service usage exists | Planned | `07_NFR.md` |

## 4. History

Re-sequencing log + done/shipped ledger are append-only in
[`03_ROADMAP-HISTORY.md`](03_ROADMAP-HISTORY.md).
