---
id: SPIKE-01
type: spike
status: Done
roadmap-item: —
---

# SPIKE-01: Can a Pi 5 (8GB) carry an orchestrated hub plus Jellyfin with headroom to grow?

| Field      | Value                                                                 |
| ---------- | --------------------------------------------------------------------- |
| Status     | Done                                                                   |
| Type       | Technical/feasibility                                                  |
| Owner      | wes-cutting                                                            |
| Time-box   | 1 day — honored (ran in a single session)                             |
| Date       | 2026-07-26                                                             |
| Blocks     | `ADR-0001` (OS + container runtime) · `ADR-0002` (service data/state) · the foundation hub slice · `02_PRD.md` |

## 1. The question

**Can a Raspberry Pi 5 (8GB) run a container-orchestrated hub *plus* Jellyfin actually
serving and transcoding one real media stream to a LAN client — while leaving enough
RAM / CPU / thermal headroom to add more services?**

Falsifiable against the pass/fail thresholds in §2. One question only: this spike does **not**
decide the final orchestration layer, build the real hub, or tune performance — it measures
whether the *pattern* is viable on this hardware.

## 2. Method

Run on the **real hardware**: the in-hand Raspberry Pi 5 (8GB, CanaKit PRO), on its
preinstalled **64-bit Raspberry Pi OS**, on the **van LAN** (or an equivalent local network),
playing a **real media file** to **one real client** (a laptop/phone browser on the same LAN).
Throwaway `docker compose` stack; nothing here is promoted to production.

**Reality sources (confirm before measuring — a vacuous pass is worse than a fail):**
- **Compute reality:** the actual Pi 5, not an emulator/another ARM board. Confirm with
  `cat /proc/cpuinfo | grep -m1 Model` → expect `Raspberry Pi 5`.
- **Load reality:** a **real** media file that *forces a transcode* (not a direct-play/remux).
  Use a high-bitrate 1080p or 4K source and a client/profile that requires re-encode. Confirm
  in the Jellyfin dashboard's **Active Devices** that the session shows **Transcoding**
  (not "Direct Play"/"Direct Stream") — otherwise the CPU test validates vacuously.

**Steps:**
1. Baseline the idle box: `free -m`, `vcgencmd measure_temp`, `vcgencmd get_throttled`
   (expect `throttled=0x0`), `uptime` load average.
2. Install a container runtime (Docker Engine, ARM64) and Compose.
3. Bring up a **throwaway compose stack**: a trivial "hub" placeholder (any small container
   exposing a health endpoint, e.g. a static nginx) **+ `jellyfin/jellyfin`**, with a small
   real media library mounted read-only.
4. From the LAN client, start playback of the transcoding test file; **verify the session is
   actually transcoding** (see above).
5. Under sustained transcode (let it run ~10–15 min to reach thermal steady state), sample:
   - RAM used/free — `free -m`
   - CPU load / per-core — `top -bn1` / `uptime`
   - SoC temperature — `vcgencmd measure_temp`
   - Throttling/undervoltage — `vcgencmd get_throttled` (any non-zero = a problem; decode it)
   - Playback quality on the client — smooth vs. stutter/buffer
6. Record idle vs. under-load deltas.

**Pass / fail thresholds (headroom "to add more services"):**
- **RAM:** with hub + Jellyfin transcoding one stream, **≥ ~3 GB free** (≳40% of 8 GB). *Fail
  if free RAM approaches exhaustion / swapping under a single stream.*
- **Thermal:** SoC stays **below the throttle point** and `get_throttled` stays **`0x0`**
  through steady state. *Fail on any throttling or undervoltage flag.*
- **Playback:** the single stream plays **smoothly** end-to-end. *Fail on sustained
  stutter/buffering at one stream.*
- **Overall:** PASS = all three hold with visible headroom → the hub-plus-services pattern is
  viable on this box. FAIL / MARGINAL = one or more breached → reconsider (leaner OS, hardware
  transcode/tuning, or scope the service catalog down) before building on it.

**Deliberately NOT doing:** choosing the final orchestration layer, building the real hub or
auth, adding a second service, or measuring wall-power draw (note it as optional — a USB-C
power meter can be added later; `get_throttled` is the on-device undervoltage proxy).

## 3. Findings

**Environment (real box):** Raspberry Pi 5 Model B Rev 1.1, Debian 12 (Bookworm) aarch64,
kernel 6.12.93, 7.9 GiB RAM, on **Wi-Fi** (`wlan0`; `eth0` down). Docker **29.6.2** +
Compose **v5.3.1** (installed during the spike). Throwaway `docker compose` stack:
`hub` (nginx:alpine, `:8080`) + `jellyfin/jellyfin` (`:8096`), library bind-mounted read-only.

**Fixture (synthetic, per kit principle):** ffmpeg-generated **1080p HEVC, 10 min, ~12 Mbps,
872 MB** — HEVC chosen so browser clients cannot direct-play, forcing a transcode. Confirmed
transcoding via the Jellyfin player quality cap (4 Mbps) — verified server-side in the
transcode log (`libx264`, not direct-play).

**Transcode path actually used:** hardware-assisted **HEVC decode → software `libx264`
(preset veryfast) H.264 encode.** (The Pi 5 has **no hardware H.264 encoder** — unlike the
Pi 4 — so the encode is CPU-bound software libx264.)

**Idle baseline:** 48.3 °C · 7.3 GiB free · `get_throttled=0x0`.

**Under one live transcode (32 samples over ~9 min, 15 s interval):**

| Metric | Value | Threshold | Verdict |
| ------ | ----- | --------- | ------- |
| Min free RAM | **6,854 MB** | ≥ ~3,000 MB | ✅ (huge margin) |
| Max SoC temp | **75 °C** | below throttle | ✅ |
| `get_throttled` | **0x0** entire run | stays 0x0 | ✅ |
| Jellyfin CPU (1 stream) | peak **~379% of 400%** | — | ⚠ near-saturates 4 cores |
| Transcode realtime factor | **~2.8× realtime** (`speed=…x` climbed 1.62→2.82) | ≥ 1× | ✅ stays ahead |
| Playback smoothness | **inferred smooth** (2.8× headroom, buffer never starves) — **not visually verified** (operator didn't watch) | smooth | ✅ (objective) / ⚠ (subjective unobserved) |

Note the CPU pattern was a ~2-min burst at ~375% then idle: at 2.8× realtime Jellyfin
transcoded well ahead of playback and its throttle paused the encoder once buffered — **not**
a stall (`get_throttled` stayed `0x0` throughout).

### Confirmed
- The **hub + Jellyfin container pattern runs on the Pi 5** on stock Raspberry Pi OS 64-bit
  with Docker/Compose — no special setup, ARM64 images available.
- **RAM is not the constraint** — ~6.8 GB free under a live transcode. Many lightweight
  services can be stacked.
- **Thermal is fine** for a single stream — 75 °C peak, zero throttling/undervoltage.
- **A single 1080p transcode is comfortably realtime** (~2.8×) thanks to HW HEVC decode.

### Invalidated
- The naïve "8 GB RAM is the thing to watch" framing — **CPU, not RAM, is the binding
  constraint** on this hardware, specifically during transcode.
- Any assumption of hardware H.264 *encode* on the Pi 5 — there is none; transcode encode is
  software libx264.

### Surprises / unknowns uncovered
- **One 1080p transcode ≈ all four cores.** A **second concurrent transcode** would contend
  and likely drop both below realtime → concurrent-transcode capacity is ~1 on this box.
  (New question: how many concurrent *direct-play* streams before Wi-Fi/IO limits bite?)
- The Pi is on **Wi-Fi**; wired Ethernet would give cleaner throughput for multi-client use.
- macOS "Local Network" per-app privacy permission blocked Chrome/Brave from reaching the LAN
  IP while `curl` worked — an access-setup gotcha for infra projects (see KIT_FEEDBACK K3).

## 4. Recommendation / decision

**PASS — build the hub-plus-services pattern on this hardware.** Concretely:

- **`ADR-0001` (OS + container runtime):** adopt **Raspberry Pi OS 64-bit + Docker + Compose**
  — validated by this spike. Draft the ADR at `Validated`.
- **Design around the CPU limit, not RAM:** treat **live transcoding as a scarce, ~single-
  stream resource.** Prefer **direct-play** (keep/curate media in client-compatible formats),
  consider **pre-optimized/pre-transcoded** libraries, and **cap concurrent transcodes** in
  Jellyfin. This belongs in the PRD non-functional section and `07_NFR.md`.
- **Foundation hub slice may proceed** — the placeholder `hub` (health + bring services up)
  is unblocked. Size the *service catalog* expectations to the measured headroom (RAM-abundant,
  transcode-scarce).
- **No follow-up spike required before building.** Two *future* spikes remain deferred
  (LLM feasibility; at-rest encryption) — unchanged from intake.

## 5. Impact on the plan

- **Specs/ADRs affected:** `ADR-0001` → draft `Validated` (OS + Docker/Compose). `ADR-0002`
  (service data/state, backup, theft-encryption) → still `Proposed`; the spike used bind
  mounts only, so the persistence/backup decision is **not** yet validated. `02_PRD.md` →
  unblocked to write, must carry the transcode-as-scarce-resource NFR.
- **Scope changes:** add an explicit **"favor direct-play; cap/limit concurrent transcodes"**
  constraint. LLM + encryption remain deferred (intake §4 #4/#5).
- **Sequencing changes:** foundation hub slice unblocked. `07_NFR.md` matters earlier than the
  kit's default "hardening" stage because the transcode ceiling is a first-order design input.

## 6. Follow-ups

- [ ] Draft `ADR-0001` (OS + container runtime) and `ADR-0002` (service data/state) from the result.
- [ ] Write `02_PRD.md` once the feasibility bet is de-risked.
- [ ] Future spike: small quantized LLM (~1–3B) feasibility alongside other services (intake §4, #4).
- [ ] Future spike: at-rest encryption for the physically-stealable node (intake §4, #5).
