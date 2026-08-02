# labs-hub — hub + services gate & ops.
# The gate mirrors CI (.github/workflows/gate.yml): same checks, same order.
# Compose spans the hub (compose.yml) + each service file (compose.*.yml).
COMPOSE := docker compose -f deploy/compose.yml -f deploy/compose.media.yml -f deploy/compose.budgeteer-demo.yml
HOST    ?= localhost

.PHONY: help gate lint validate shellcheck smoke up down deploy

help:
	@echo "make gate    - static gate: yamllint + compose config + shellcheck (mirrors CI)"
	@echo "make up      - bring the hub stack up      (needs docker)"
	@echo "make down    - stop the hub stack"
	@echo "make smoke   - probe Homepage + Portainer  (HOST=<ip> default localhost)"
	@echo "make deploy  - on the Pi: git pull --ff-only && compose up -d && smoke"

# --- Gate (must be green before 'done') ---
gate: lint validate shellcheck

lint:
	yamllint deploy/

# Placeholder secrets for the STRUCTURAL check only. The budgeteer demo stack declares its
# secrets with `${VAR:?...}` so a real `make up` fails loudly by name when they are missing —
# but that same guard would make `config -q` unrunnable on any machine without deploy/.env
# (CI, a fresh clone). Supplying throwaway values here validates the shape without weakening
# the runtime guard: `up` does not set them.
validate:
	BUDGETEER_DEMO_POSTGRES_PASSWORD=gate-placeholder \
	BUDGETEER_DEMO_SESSION_SECRET=gate-placeholder \
	$(COMPOSE) config -q

shellcheck:
	shellcheck scripts/*.sh

# --- Ops ---
smoke:
	scripts/smoke.sh $(HOST)

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

# Run on the Pi from the repo clone (git-based deploy — see deploy/README.md).
deploy:
	git pull --ff-only
	$(COMPOSE) up -d --remove-orphans
	scripts/smoke.sh localhost
