# Deploy — labs-hub hub foundation (LH-S1)

Git-based deployment of the hub (**Homepage** + **Portainer**) to the Raspberry Pi.
See the spec: [`docs/features/LH-S1-hub-foundation.md`](../docs/features/LH-S1-hub-foundation.md).

## Model

The Pi holds a **clone of this repo** and runs Compose from `deploy/`. To ship a change:
edit here → commit/push → on the Pi `git pull` → `docker compose up -d`. (`make deploy`
wraps the last two steps.)

## First-time setup on the Pi

```bash
# 1. Clone the repo (public — no auth needed):
git clone https://github.com/wes-cutting/labs-hub.git ~/labs-hub
cd ~/labs-hub

# 2. Local config (not committed):
cp deploy/.env.example deploy/.env
$EDITOR deploy/.env          # set LABS_HUB_HOST to how you reach the hub (default raspberrypi.local)

# 3. Data-root (ADR-0002):
sudo mkdir -p /srv/labs-hub/portainer/data \
              /srv/labs-hub/jellyfin/config /srv/labs-hub/jellyfin/cache \
              /srv/labs-hub/media          # drop media here (LABS_HUB_MEDIA_ROOT)
sudo mkdir -p /srv/labs-hub/budgeteer-demo/db
sudo chown 999:999 /srv/labs-hub/budgeteer-demo/db   # postgres initdb runs as uid 999

# 4. Bring it up:
make up
scripts/smoke.sh localhost
```

Then open **Homepage** at `http://<pi>:3000`, **Portainer** at `http://<pi>:9000`
(first visit creates the Portainer admin — see the token note below), **Jellyfin** at
`http://<pi>:8096` (first visit creates the Jellyfin admin + library from `/media`), and the
**Budgeteer demo** at `http://<pi>:3010` (see below).

### Jellyfin transcode budget (required — SPIKE-01)

The Pi 5 has **no hardware H.264 encoder**, so one live 1080p transcode ≈ all four cores. To
stop a second stream from tanking the node, after Jellyfin first-run:

- **Cap concurrent streams/transcodes** — Dashboard → Users → (each user) → set a
  **simultaneous stream limit** (default to **1** on this hardware).
- **Favor direct-play** — keep media in client-friendly formats; avoid forcing transcodes.
- Future hardening: enable HW-accelerated HEVC **decode** (V4L2) to widen the budget.

### Budgeteer demo instance (LH-S3-demo)

A showcase box on `http://<pi>:3010` holding **strictly synthetic data** — sign in as
**`demo` / `demo-budgeteer`**. It is *not* the household's real ledger; deploying that is
LH-S3 proper. Full rationale: budgeteer's
[`DEPLOY_CONTRACT.md` §10](https://github.com/wes-cutting/budgeteer/blob/main/docs/DEPLOY_CONTRACT.md).

The image is **pulled** from GHCR (public, ARM64) and never built on the Pi. Secrets come from
`deploy/.env` (see `.env.example`) — the stack fails loudly by name without them.

**Seeding needs a budgeteer repo checkout**, and that is by design: `seedDemo` is deliberately
absent from the production image, so demo data is *absent* from a real deployment rather than
guarded behind a flag. The demo database is published on the Pi's **loopback only**, so seed it
over an SSH tunnel from a machine that has the checkout:

```bash
# On your workstation, from the budgeteer checkout (npm install done):
ssh -fNL 5434:127.0.0.1:5434 wesker@raspberrypi.local     # tunnel to the Pi's demo Postgres
PW=$(ssh wesker@raspberrypi.local "grep '^BUDGETEER_DEMO_POSTGRES_PASSWORD=' ~/labs-hub/deploy/.env | cut -d= -f2-")
DATABASE_URL="postgres://budgeteer:$PW@127.0.0.1:5434/budgeteer" \
  npm run seed:demo --workspace @budgeteer/api
```

Create the demo account first (one-shot; answers `409` once it exists):

```bash
curl -X POST http://raspberrypi.local:3010/api/auth/setup \
  -H 'content-type: application/json' \
  -d '{"username":"demo","password":"demo-budgeteer"}'
```

To re-pristine between showings, reset the ledger in-container (this preserves the demo
account — budgeteer BUD-S90) and reseed:

```bash
ssh wesker@raspberrypi.local 'docker exec budgeteer-demo node apps/api/dist/db/reset.js'
# then re-run the seed command above
```

The published credential is deliberate, not an oversight: it guards a throwaway database of
invented figures on its own signing secret. The generated values in `deploy/.env` *are*
secrets and stay out of git.

## Everyday deploy

```bash
cd ~/labs-hub && make deploy      # git pull --ff-only + compose up -d + smoke
```

## Gate (mirrors CI)

```bash
make gate      # yamllint + docker compose config + shellcheck
```

## Notes / gotchas

- **Homepage** discovers services from container `homepage.*` labels (read-only socket).
  A new labelled container appears automatically — no edits here.
- **Portainer** first-run asks for a setup token (printed in its logs) and has a ~5-min
  admin-creation window. If it expires: `docker restart portainer` and read the fresh token
  from `docker logs portainer`. Once the admin exists (persisted in the data-root), it's a
  non-issue.
- **Portainer holds a read-write Docker socket** (root-equivalent) — the main privilege cost.
  Future hardening: front it with a socket-proxy (tracked for `07_NFR.md`).
- **Images are `:latest`** (as validated in SPIKE-05). For stricter reproducibility, pin to a
  specific version/digest here once you settle on one.
- **Memory metrics** need the memory cgroup, already enabled on the Pi
  (`cgroup_enable=memory cgroup_memory=1` in `/boot/firmware/cmdline.txt`).
