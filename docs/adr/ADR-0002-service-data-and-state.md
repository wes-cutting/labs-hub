---
id: ADR-0002
type: adr
status: Proposed
supersedes: —
---

# ADR-0002: Service data & state — persistence, medium, and backup

| Field         | Value                                                    |
| ------------- | -------------------------------------------------------- |
| Status        | Proposed                                                 |
| Date          | 2026-07-26                                               |
| Deciders      | wes-cutting                                              |
| Validated by  | — (persistence medium + backup/restore not yet spiked)  |

> **Status is `Proposed`, not `Validated`, on purpose.** SPIKE-01 only used throwaway bind
> mounts to prove feasibility; it did **not** test the persistence medium, backup/restore, or
> at-rest encryption. Per *decided ≠ validated*, this ADR records the intended shape and names
> exactly what must be spiked before it can move to `Validated`/`Accepted`. Do not build large
> amounts of durable-data handling on it until then.

## Context

Every service the hub runs (assembled or custom) has state: Jellyfin's config/metadata, a
custom service's database, uploaded media/photos. Decisions needed: **where** persistent data
lives, **on what medium**, and **how it's backed up** — on a portable node that is physically
**stealable** (van context, intake §6) and whose default boot medium is a **128 GB SD card**,
which has finite write endurance under a 24/7 server workload.

Two hardware realities make this non-trivial and currently **unvalidated**:
1. **SD-card wear** — continuous container/database writes to an SD card risk premature
   failure; an external SSD (USB 3.0 on the Pi 5) is the likely durable medium, but neither
   the wear risk nor SSD behavior has been measured here.
2. **Theft exposure** — data at rest on a device that can be stolen argues for encryption
   (intake §4 #5), which has cost/complexity (boot unlock on a headless node) not yet assessed.

## Decision (proposed)

We *propose* to:

- Keep **all persistent service data under a single, well-known data root** (e.g.
  `/srv/labs-hub/<service>/…`), one subtree per service, mounted into each container — so the
  entire platform's state is one directory to back up, move, or encrypt.
- Prefer **bind mounts under that data root** (over anonymous Docker named volumes) so state is
  transparent, greppable, and portable across a rebuild — matching the hub's "understand every
  layer" value.
- Treat the **boot/OS medium and the data medium as separable**: plan to move the data root to
  an **external USB-3 SSD** to protect the SD card, pending the spike below.
- Define a **backup approach** (periodic snapshot/copy of the data root to a second medium)
  as part of `07_NFR.md` operational readiness — reconcilable and restore-tested, not
  assumed.

## Consequences

### Positive
- One data root → one thing to back up, encrypt, or migrate; clean disaster-recovery story.
- Bind mounts keep state legible (no opaque volume drivers), aiding debugging and portability.

### Negative / cost
- A single data root is a single blast radius — backup/restore discipline is load-bearing.
- External SSD adds a moving part and a power draw to the van setup.
- At-rest encryption on a headless node complicates unattended boot (key custody).

### Neutral
- Choice is reversible per service (bind mount ↔ volume) until real data volume accumulates.

## Alternatives considered

### Docker named volumes (default)
Rejected (proposed): opaque location, harder to back up/inspect/migrate by hand — at odds with
the operator's "understand every layer" goal. Reconsider only if a specific service needs a
volume driver.

### Everything on the SD card, no external medium
Rejected (proposed): SD write-endurance risk under 24/7 writes; a stolen/lost card also loses
everything with no separation.

## What must be validated before this is `Accepted`

- [ ] **SPIKE (feasibility): SD-card wear vs. external USB-3 SSD** — does sustained service
      write load justify moving the data root to SSD, and does the SSD behave (throughput,
      power, hotplug) on the Pi 5? → moves the medium decision to `Validated`.
- [ ] **SPIKE (security/ops): at-rest encryption + backup/restore** — can a headless node
      unlock encrypted data acceptably, and can the data root be backed up and **restored**
      end-to-end? (intake §4 #5) → moves backup + encryption to `Validated`.

## Supersedes / superseded by

- Supersedes: —
- Superseded by: —
