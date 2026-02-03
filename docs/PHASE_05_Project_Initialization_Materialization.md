# docs/PHASE_05_Project_Initialization_Materialization.md

## Phase 5 — Project Initialization (Materialization)

### Objective
Materialize the project repository and runtime environment: structure, docs, infra scaffold, CI baseline, and initial code skeleton.

### Mandatory Step: Starter Repo Fit Check
Evaluate these candidates as base codebases (≥90% fit → adopt):
1) https://github.com/naoufalelh/cursor-langgraph-starter  
2) https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template  
3) https://github.com/francescofano/langgraph-telegram-bot  

If <90% fit:
- All cloned in `/refs/` (read-only)
- Extract patterns into our structure

### Primary Outputs
- Repo created with baseline structure: `/docs`, `/src`, `/tests`, `/infra`, `/artifacts`, `/refs`
- `/docs` synced with Phase 1–4 artifacts
- Docker runtime (compose) boots core services
- CI skeleton runs lint + tests
- `.env.example` exists

### Inputs
- Phase 1–4 docs
- Roadmap + chosen stack

### Cursor-First Workflow
- **Cursor @Terminal**: generate/validate Dockerfiles, compose, CI YAML; run bootstrap commands
- **Cursor @Web**: consult official docs for CI syntax or tool flags
- **Cursor @Codebase**: ensure docs are present and consistent
- **Cursor Apply**: generate initial skeleton/stubs from Phase 1–4 docs

### Requirements
- **Docker** (default): No local Python required. All commands run in a Python 3.12+ container.
- Optional local path: Python 3.11+ and `make install` then `make local-lint` / `make local-test`.

### Validation (minimum) — exact commands (Docker, no local Python)
- **Boot stack:** `make boot` → `docker compose -f infra/docker-compose.yml up --build`
- **Lint:** `make lint` → `docker compose -f infra/docker-compose.yml run --rm app python -m ruff check .` and `python -m ruff format --check .`
- **Test:** `make test` → `docker compose -f infra/docker-compose.yml run --rm app python -m pytest`
- **Shell in app container:** `make shell` → `docker compose -f infra/docker-compose.yml run --rm app sh`

### DoD Checklist (Approval Gate)
- [x] Starter repo decision recorded in `docs/Foundation_Template.md`
- [x] Project boots locally (compose up / local run)
- [x] CI pipeline exists and runs baseline checks
- [x] `/docs` is complete and current
- [x] `.env.example` is safe (no secrets)

### Telegram Completion Message (Template)
- ✅ Artifacts: Foundation_Template.md + repo tree snapshot
- ✅ Validation: boot command + CI run summary
- Buttons: [✅ INITIALIZE & START] [📄 EXPLORE STRUCTURE] [🔁 REFINE STRUCTURE] [🔙 GO BACK TO PHASE 4]
