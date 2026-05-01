# docs/PHASE_06_TDD.md

## Phase 6 — Minimal TDD (Safety Net, Not “Perfect Tests”)

### Objective
Add a **thin, high-ROI test safety net** so we can implement fast in Phase 7 without breaking:
- orchestration (LangGraph + HITL)
- persistence (PostgresSaver checkpoints/resume)
- bot control plane (Approve/Refine/GoBack)
- artifact storage (run docs)

This phase is **not** about exhaustive app testing. It’s about **protecting the factory core loop**.

---

## Scope (What we test)
**Only “factory P0 invariants”.** Keep the suite small and deterministic.

### P0 invariants (must be covered)
1) **DB boots + schema ok** (tables exist / migrations applied)
2) **Checkpoint works** (write checkpoint → resume from it)
3) **Graph HITL works** (interrupt → approve continues)
4) **Command routing works** (Approve/Refine/GoBack triggers correct transitions)
5) **Artifacts CRUD works** (create/update/read run docs)

### Explicit non-goals (do NOT do here)
- Full coverage of every phase output format
- UI/visual tests (Playwright/Maestro) — later / optional
- End-to-end tests across all 10 phases
- External integrations (Stripe/PostHog/etc.)

---

## Inputs
- `artifacts/<thread_id>/docs/HDL_Business_Flows.md`
- `artifacts/<thread_id>/docs/Data_Model.md`
- `artifacts/<thread_id>/docs/Sprint_1_TODO.md`

Where `<thread_id>` = LangGraph configurable thread_id (Telegram user/session identifier).

---

## Primary Outputs
- `/tests` contains **minimal** unit/integration tests for factory P0 invariants
- `artifacts/<thread_id>/docs/Test_Report.md` (summary + commands)

---

## Strategy: Thin-TDD Loop
### Step 1 — Write tests for invariants (RED)
Write a small set of tests that express expected behavior for:
- DB + migrations
- PostgresSaver checkpoint/resume
- Graph interrupt/continue
- bot command → orchestrator event mapping
- artifact store read/write

### Step 2 — Implement only what makes them pass (GREEN)
Implement the minimum code to satisfy tests.
No “nice-to-have” abstractions yet.

### Step 3 — Small refactor (optional)
Refactor only if it reduces risk or simplifies Phase 7.

---

## Required Test Set (Minimum)
Create these tests (names can vary; intent must match):

### A) Infra / DB
- [ ] `test_db_boot_and_schema()`  
  Ensures DB reachable and required tables exist (or migrations applied).

### B) Persistence (PostgresSaver)
- [ ] `test_checkpointer_writes_and_resumes()`  
  Run graph step → checkpoint saved → rebuild graph → resume continues.

### C) Orchestrator HITL
- [ ] `test_phase_interrupt_and_approve_continues()`  
  Phase node interrupts → approval event continues to next node.

### D) Control-plane routing
- [ ] `test_telegram_command_maps_to_orchestrator_event()`  
  Approve/Refine/GoBack payload becomes correct internal event.

### E) Artifact store
- [ ] `test_run_docs_create_read_update()`  
  Create Business_Logic + Assumptions for a run → update → read latest.

> If WebApp editor exists: add auth verification test for Telegram initData.  
> If it doesn’t exist yet: skip it (don’t block Phase 7).

---

## Commands (Single-command reproducibility)
Tests must run with **one** command.

Preferred (Docker-first, no local Python dependency):
```bash
make test