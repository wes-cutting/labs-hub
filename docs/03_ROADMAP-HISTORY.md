---
id: ROADMAP-HISTORY
type: roadmap-history
status: Append-only
roadmap-item: —
---

# Roadmap History — labs-hub

| Field  | Value        |
| ------ | ------------ |
| Status | Append-only  |
| Owner  | wes-cutting  |
| Plan   | [`03_ROADMAP.md`](03_ROADMAP.md) — the living plan this history belongs to |

Never edit past entries; append a new one. This doc only grows.

## 1. Re-sequencing log

| Date | Change | Trigger (spike / surprise) | Effect on the plan |
| ---- | ------ | -------------------------- | ------------------ |
| 2026-07-26 | Initial plan created from intake + PRD | discovery + [SPIKE-01](spikes/SPIKE-01-pi5-hub-plus-jellyfin-feasibility.md) | Feasibility retired first; foundation slice LH-S1 next. |
| 2026-07-26 | Added SPIKE-02 (SD vs SSD) and SPIKE-03 (encryption + backup/restore); pulled persistence/NFR forward from generic "hardening" | SPIKE-01 finding: **CPU (transcode), not RAM, is the ceiling**; SD-card wear + theft exposure surfaced | Persistence medium + backup treated as first-order (`ADR-0002` stays `Proposed` until these land); transcode-cap NFR added to PRD §5. |

## 2. Done / shipped

| Id | Item | Shipped | Notes |
| -- | ---- | ------- | ----- |
| SPIKE-01 | Pi 5 hub + Jellyfin feasibility | 2026-07-26 | PASS — ~2.8× realtime single transcode, 75 °C, no throttle, ~6.8 GB free; CPU is the ceiling. Report: [SPIKE-01](spikes/SPIKE-01-pi5-hub-plus-jellyfin-feasibility.md). |
