# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

Autonomous AI Venture Studio — a local-first, stateful "software factory" that drives an idea through a strict **10-phase SDLC pipeline** (Vision → Backlog → UI/UX → Architecture → Init → TDD → Implementation → Visual QA → Guardrails → DevOps). The pipeline is a **LangGraph** state machine with a **Postgres**-backed checkpointer; the only user-facing control plane is a **Telegram bot** (Aiogram). Each phase node generates artifacts, then calls `interrupt()` to pause until the CEO presses an inline approval button in Telegram, at which point the bot resumes the graph with `Command(resume=...)`.

LLM calls go to a **local Ollama** (default `llama3.1:8b`) — there is no Anthropic/OpenAI dependency. Phase 3 additionally calls **Google Stitch** for UI prototypes when enabled.

> **Working-tree note (snapshot dependent):** at the time of writing, `git status` shows the entire `src/`, `tests/`, `infra/`, `Makefile`, and `pyproject.toml` as deleted on the worktree but still present at HEAD. The architecture below reflects HEAD, which is the canonical state. If you need to inspect runtime code, use `git show HEAD:<path>` or check out a clean copy.

## Common commands

All primary commands run **inside Docker** (no local Python required) via the Makefile in HEAD:

| Task | Command | Underlying |
|---|---|---|
| Boot full stack (app + postgres) | `make boot` | `docker compose -f infra/docker-compose.yml --env-file .env up --build` |
| Run all tests | `make test` | `docker compose ... run --rm app python -m pytest` |
| Lint + format check | `make lint` | `ruff check .` + `ruff format --check .` |
| Shell into app container | `make shell` | `docker compose ... run --rm app sh` |

Run a single test:
```
docker compose -f infra/docker-compose.yml --env-file .env run --rm app python -m pytest tests/test_graph.py::test_name -v
# or, after `make shell`:
python -m pytest tests/test_graph.py -k <substring> -v
```

Optional **local venv** path (only if Python 3.11+ on host):
```
make install       # creates .venv and installs -e ".[dev]"
make local-test    # pytest in .venv
make local-lint    # ruff in .venv
```

CI (`.github/workflows/ci.yml`) runs `ruff check`, `ruff format --check`, and `pytest` on Python 3.11.

## Required environment

`.env` (copied from `.env.example`) must define:

- `PG_CONNECTION_STRING` — required. In compose, points at the bundled `postgres` service.
- `TELEGRAM_BOT_TOKEN` — required for the bot to receive updates.
- `OLLAMA_BASE_URL` (default `http://host.docker.internal:11434`), `OLLAMA_MODEL` (default `llama3.1:8b`), `OLLAMA_TIMEOUT`.
- `GOOGLE_STITCH_ENABLED` (default `true`), `GOOGLE_STITCH_API_KEY`, `GOOGLE_STITCH_BASE_URL`, `GOOGLE_STITCH_TIMEOUT` — Phase 3 only; if `ENABLED=true` the API key is mandatory.

`docker-compose.yml` passes these vars into the `app` container. The Makefile must invoke compose with `--env-file .env`, otherwise variable interpolation silently fails (a documented past bug — see commit log).

## Architecture (the parts that span multiple files)

### Boot sequence — `src/main.py`
1. Load `.env`.
2. `setup_database(PG_CONNECTION_STRING)` opens a connection, runs `AsyncPostgresSaver.setup()` (creates checkpoint tables), then opens an `AsyncConnectionPool` (`src/persistence/postgres.py`).
3. `get_checkpointer(pool)` → fresh `AsyncPostgresSaver` bound to the pool.
4. `build_workflow(checkpointer)` compiles the 10-phase graph.
5. `run_bot(token, graph, pool)` starts Aiogram polling.

### Graph — `src/graph/workflow.py` + `nodes.py` + `state.py`
- `PhaseState` (`TypedDict`) carries: `messages`, `current_phase`, `approved`, `ceo_prompt`, plus Phase-3 design fields (`stitch_project_id`, `stitch_preview_url`, `refinement_prompt`).
- Topology is linear: `START → phase_1 → phase_2 → … → phase_10 → END`. There are no conditional edges; "approval gating" is implemented inside each node via `langgraph.types.interrupt(...)`. The graph blocks at the interrupt; the bot resumes it with `Command(resume={"approved": True/False, ...})`.
- **Per-session keying:** every graph invocation uses `config={"configurable": {"thread_id": "<session_id>"}}`, which is also used to namespace artifacts on disk.
- `phase_1`, `phase_2`, `phase_3` have full implementations (Ollama prompts + parsing; Phase 3 additionally orchestrates Stitch via `src/integrations/stitch_client.py` and prompts built by `stitch_prompt_builder.py`). `phase_4` … `phase_10` are stub `phase_node(N)` factories that just persona-message and interrupt — extending them is the natural way to grow the pipeline.

### Telegram bot — `src/telegram_bot/bot.py`
- Commands: `/start` (team intro), `/help`, `/run <idea>` (initial CEO prompt → kicks off `graph.ainvoke({...}, config)`).
- Inline keyboards built per phase. Phase 3 has additional `REFINE SCREEN` / `CHANGE THEME` buttons; all other phases get `APPROVE` / `VIEW DOCS` / `GO BACK`.
- Callback handlers parse `f"{action}:{phase}"` payloads and resume the graph. On interrupt the bot reads `interrupt.value` to obtain the persona message + `artifact_files`, sends each artifact as a Telegram document/photo, and renders the keyboard.
- `_active_sessions` deduplicates concurrent `/run` invocations per chat.

### Artifacts & SSOT split (read this before touching disk paths)

There are **two** sources of truth and they must not bleed into each other:

- `/docs/` — **factory manuals** (static, repo-level): `PHASES_INDEX.md`, `PHASE_01_*.md` … `PHASE_10_*.md`, `Foundation_Template.md`, `description-2.1.md`. Code changes that alter pipeline behavior must keep these in sync (this is enforced by `.cursor/rules/00-global.mdc`).
- `artifacts/<thread_id>/` — **run outputs** (dynamic, per Telegram session). `docs/` for generated markdown/JSON, `assets/ui/` for Stitch screenshots, `visual-qa/` for evidence packs (Phase 8), `snapshots/` for Time-Machine rollbacks when no git remote is available. The canonical store is Postgres; the filesystem copy exists because `infra/docker-compose.yml` mounts `../artifacts:/app/artifacts`, giving host visibility.
- **Never write run artifacts into `/docs`**, and never read run state from `/docs`.

### `/refs/` is read-only
Cloned donor repos used for pattern extraction (`cursor-langgraph-starter`, `fastapi-langgraph-agent-production-ready-template`, `langgraph-telegram-bot`, `react-native-cli-starter`). Do not modify; copy patterns into `/src` instead. The fit-check decision matrix lives in `docs/Foundation_Template.md` (verdict: none ≥90%, all kept as donors).

## Project laws (from `.cursor/rules/`)

These are non-negotiable invariants enforced across the codebase:

- **Approval gate is mandatory.** No phase advances without `[✅ APPROVE]` from Telegram — implemented as `interrupt()` in every phase node. Don't add edges that bypass this.
- **`/docs` is SSOT for the factory.** If you change phase behavior or structure, update `PHASES_INDEX.md` and the relevant `PHASE_NN_*.md` in the same change.
- **Postgres is system memory.** Use `AsyncPostgresSaver` for checkpoints (already wired in `persistence/postgres.py`). Resume-after-restart is a hard requirement.
- **Layering:** `domain` imports nothing from `persistence`/`telegram`/`api`; `persistence` may import `domain`; `telegram`/`api` may import `domain` + services. Configuration comes from `core/config.py` — no `os.getenv` scattered in business code.
- **No secrets in code.** `.env.example` only; `.gitignore` already excludes `.env`, `*-service-account.json`, `secrets/`.
- **Telegram messages on phase completion** must include: produced artifacts (paths/buttons), validation result, next step, and the standard button set (APPROVE / REFINE / GO_BACK / VIEW_DOCS).
- **Visual QA evidence pack standard** (Phase 8, `.cursor/40-testing-visualqa.mdc`): every failure produces `expected.png`, `actual.png`, `diff.png`, `trace.zip`, `meta.json`, `repro.txt` under `/artifacts/visual-qa/<run-id>/`, and is linked from `docs/QA_Report.md`.

## Where to start when extending the pipeline

- **New AI logic in an existing phase:** edit the corresponding `phase_N` function in `src/graph/nodes.py`. Follow the Phase 1/2/3 pattern: read prior-phase artifacts → build Ollama prompt → POST `/api/chat` (with a phase-appropriate timeout) → parse with `---DOCUMENT_SEPARATOR---` → write artifacts under `artifacts/<thread_id>/docs/` → `interrupt(...)` with the persona message + `artifact_files`.
- **New phase button or refinement flow:** extend `_approval_keyboard` in `src/telegram_bot/bot.py` and add a callback handler that resumes the graph with the appropriate `Command(resume={...})` payload.
- **New external integration:** add a client under `src/integrations/`, expose a typed wrapper, and gate it behind a `GOOGLE_STITCH_ENABLED`-style flag in `core/config.py` so the pipeline degrades gracefully when credentials are missing (see Phase 3's text-only fallback as the reference implementation).
