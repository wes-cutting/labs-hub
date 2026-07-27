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
$EDITOR deploy/.env          # set HOMEPAGE_ALLOWED_HOSTS to how you reach the Pi

# 3. Data-root (ADR-0002):
sudo mkdir -p /srv/labs-hub/portainer/data

# 4. Bring it up:
docker compose -f deploy/compose.yml up -d
scripts/smoke.sh localhost
```

Then open **Homepage** at `http://<pi>:3000` and **Portainer** at `http://<pi>:9000`
(first visit creates the Portainer admin — see the token note below).

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
