# Phase 5: docker-first. No local Python required.
# Primary: make boot, make lint, make test, make shell (all run via Docker).

COMPOSE_FILE = infra/docker-compose.yml
COMPOSE = docker compose -f $(COMPOSE_FILE) --env-file .env

.PHONY: boot test lint shell install local-test local-lint

# --- Docker (primary) ---
boot:
	$(COMPOSE) up --build

test:
	$(COMPOSE) run --rm app python -m pytest

lint:
	$(COMPOSE) run --rm app python -m ruff check .
	$(COMPOSE) run --rm app python -m ruff format --check .

shell:
	$(COMPOSE) run --rm app sh

# --- Local .venv (optional; requires Python 3.11+ on host) ---
VENV = .venv
PYTHON = $(shell command -v python3.12 2>/dev/null || command -v python3.11 2>/dev/null || command -v python3 2>/dev/null || echo python3)
VENV_PYTHON = $(VENV)/bin/python

install: $(VENV)/.installed

$(VENV)/.installed: pyproject.toml
	@$(PYTHON) -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null || \
		(echo "ERROR: Python 3.11+ required. Use docker instead: make test make lint"; exit 1)
	$(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -e ".[dev]"
	touch $(VENV)/.installed

local-test: install
	$(VENV_PYTHON) -m pytest

local-lint: install
	$(VENV_PYTHON) -m ruff check .
	$(VENV_PYTHON) -m ruff format --check .
