#!/usr/bin/env bash
# Smoke test for the labs-hub foundation (LH-S1): are Homepage + Portainer reachable?
# Usage: scripts/smoke.sh [host]   (default: localhost — run it on the Pi)
set -euo pipefail

HOST="${1:-localhost}"
fail=0

check() { # name url expected_code
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$2" || echo 000)
  if [ "$code" = "$3" ]; then
    printf 'OK    %-10s %s -> %s\n' "$1" "$2" "$code"
  else
    printf 'FAIL  %-10s %s -> %s (want %s)\n' "$1" "$2" "$code" "$3"
    fail=1
  fi
}

check "Homepage" "http://$HOST:3000/api/healthcheck" "200"
check "Portainer" "http://$HOST:9000/" "200"

exit "$fail"
