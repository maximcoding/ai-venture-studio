# Foundation Template Fit Check (Phase 5)

## Goal
Pick at most ONE repository as the base (≥90% fit).  
All others are cloned into `/refs` as read-only donors.

## Candidates
1) https://github.com/naoufalelh/cursor-langgraph-starter
2) https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template
3) https://github.com/francescofano/langgraph-telegram-bot

---

## Our Non-Negotiables (must-have)
- LangGraph with 10 phases + HITL interrupts
- PostgreSQL persistence + checkpoint/resume (PostgresSaver or equivalent)
- Telegram bot control plane (Aiogram preferred)
- Docker compose local-first setup
- Clean /docs as SSOT (PHASE_*.md + PHASES_INDEX.md)
- Testing scaffold (pytest) and CI baseline

---

## Scoring (0–10 each)
Score each repo:

### A) Architecture Fit
- LangGraph orchestration present?
- Stateful persistence/checkpoint pattern present?
- Clear separation: bot/orchestrator/storage?

### B) Telegram HITL Fit
- Aiogram v3 handlers?
- Inline keyboard patterns for approve/refine/go_back?
- Clean handler/service separation?

### C) Infra Fit
- Docker compose includes Postgres?
- Env management (.env.example)?
- CI pipeline exists?

### D) Code Quality Fit
- Typed code, modular structure?
- Tests present?
- Minimal tech debt?

### E) Effort to Adapt (inverse)
- How many days to reach our Phase 5 DoD?

---

## Decision Table

| Repo | A Arch (10) | B Telegram (10) | C Infra (10) | D Quality (10) | E Effort (10) | Total /50 | Verdict |
|------|-------------|------------------|--------------|----------------|---------------|-----------|---------|
| #1   | 3           | 0                | 5            | 7              | 2             | 17        | Refs    |
| #2   | 7           | 0                | 9            | 8              | 6             | 30        | Refs    |
| #3   | 6           | 5                | 8            | 6              | 5             | 30        | Refs    |

### Base Repo Choice
- Selected Base: none
- Rationale (3 bullets):
  1) Stack requires Python + Aiogram + 10-phase LangGraph + Postgres; no candidate has ≥90% fit (50/50).
  2) #1 is TypeScript, no Postgres/Telegram; #2 has no Telegram; #3 uses python-telegram-bot and no 10-phase/HITL buttons.
  3) We built our own skeleton and use refs as read-only donors; patterns copied into `/src` where useful.

---

## If NOT Base: Cloned All Into /refs
Refs are already cloned at:
- refs/cursor-langgraph-starter
- refs/fastapi-langgraph-agent-production-ready-template
- refs/langgraph-telegram-bot

Rules:
- `/refs` is read-only (no modifications)
- We only copy/adapt patterns into our `/src`

---

## What We Reuse From Each Repo (if any)
- Repo #1:
  - Reuse: Interrupt pattern (concept only).
  - Why: We already have Python equivalent in our graph nodes; ref confirms HITL semantics.
- Repo #2:
  - Reuse: Postgres pool + AsyncPostgresSaver pattern, env/config style, Makefile/CI layout.
  - Why: Best infra and LangGraph+Postgres alignment; we mirrored pool + checkpointer in src/persistence/postgres.py.
- Repo #3:
  - Reuse: Postgres utils + checkpointer/store setup, bot lifecycle and message-handling concepts.
  - Why: Only ref with Telegram + LangGraph + Postgres; we use Aiogram and our own handlers but aligned on lifecycle.

---

## Phase 5 DoD Checklist
- [x] Folder structure exists: /docs /src /tests /infra /artifacts /refs
- [x] docker-compose boots postgres + app
- [x] .env.example exists and is safe
- [x] CI runs lint + tests (even placeholders)
- [x] Docs are synced and consistent with SSOT
