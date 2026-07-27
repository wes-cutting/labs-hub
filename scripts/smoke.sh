#!/usr/bin/env bash
# Smoke test for the labs-hub foundation (LH-S1): are Homepage + Portainer reachable?
# Waits for readiness (containers take a little while to boot), so it's safe to run
# immediately after `compose up` (e.g. from `make deploy`).
# Usage: scripts/smoke.sh [host]      (default host: localhost — run it on the Pi)
# Env:   SMOKE_RETRIES (default 20)  SMOKE_INTERVAL seconds (default 3)
set -euo pipefail

HOST="${1:-localhost}"
RETRIES="${SMOKE_RETRIES:-20}"
INTERVAL="${SMOKE_INTERVAL:-3}"
fail=0

check() { # name url expected_code
  local code i
  for ((i = 1; i <= RETRIES; i++)); do
    code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$2" || echo 000)
    if [ "$code" = "$3" ]; then
      printf 'OK    %-10s %s -> %s\n' "$1" "$2" "$code"
      return 0
    fi
    sleep "$INTERVAL"
  done
  printf 'FAIL  %-10s %s -> %s (want %s; gave up after %ss)\n' \
    "$1" "$2" "$code" "$3" "$((RETRIES * INTERVAL))"
  fail=1
}

check "Homepage" "http://$HOST:3000/api/healthcheck" "200"
# Portainer's / redirects (307) depending on state; /api/status is the stable health endpoint.
check "Portainer" "http://$HOST:9000/api/status" "200"
check "Jellyfin" "http://$HOST:8096/health" "200"

exit "$fail"
