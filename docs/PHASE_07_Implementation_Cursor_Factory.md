# docs/PHASE_07_Implementation_Cursor_Factory.md

## Phase 7 — Implementation (The Cursor Factory)

### Objective
Ship the MVP by implementing `Sprint_1_TODO.md` fast while keeping:
- the factory control loop correct (HITL approve/refine/go_back)
- persistence correct (Postgres checkpoints + run artifacts)
- Phase 6 safety net green (minimal tests stay green)

This is **factory implementation**, not “product UI polish”.

---

## Inputs
- `artifacts/<thread_id>/docs/Sprint_1_TODO.md`
- `artifacts/<thread_id>/docs/System_Architecture.md`
- `/tests` (minimal safety net from Phase 6 — must stay green)

Where `<thread_id>` = LangGraph configurable thread_id (Telegram user/session identifier).

---

## Cursor replaces Aider (required workflow)
Use Cursor as the only “coding engine”:

- **Multi-file features:** Cursor Composer (Cmd+I)
- **Repo reasoning:** Cursor Chat + `@Codebase`
- **Patch gate:** Cursor Review
- **Apply changes:** Cursor Apply
- **Run & validate:** Cursor `@Terminal` (compose / lint / tests)

No external “agent CLI” assumptions.

---

## Implementation order (hard order, no debate)
Build in this sequence to avoid rework:

1) **Core runtime boots**
   - docker compose boots app + postgres
   - bot starts and can receive messages

2) **Run identity & state**
   - derive `thread_id = user_<telegram_user_id>`
   - create/load a `run` record (or equivalent) for thread_id

3) **Doc review/edit loop (phone-first)**
   - implement Telegram-first doc viewer (paged) + edit/save
   - (Web App editor can be added later; don’t block MVP)

4) **Phase 1 end-to-end**
   - Phase 1 writes run docs (Business_Logic + Assumptions) into the chosen storage
   - bot can show summary + OPEN DOCS + edit + save + refine loop
   - approve advances to Phase 2

5) **Phase 2 end-to-end**
   - generate backlog + MVP scope + Sprint_1_TODO (run artifacts)
   - approve advances

6) **Phase 3 (Stitch MCP integration)**
   - generate Stitch prompt
   - call Stitch via MCP (client from container)
   - return Stitch link + allow refine screen instructions

7) **Time-machine**
   - implement GO BACK semantics across phases (pointer rollback)
   - ensure checkpoint/resume consistent

> Rule: each new capability must not break Phase 6 tests. Add tests only if they protect a P0 invariant.

---

## Primary Outputs (per-run artifacts)
- `/src` implements MVP factory functionality for the current Sprint
- `artifacts/<thread_id>/docs/Implementation_Notes.md`

If relevant to the run, also ensure:
- run artifacts exist for produced docs (Phase 1/2/3 outputs)
- bot messages include the correct control buttons

---

## Required file: Implementation_Notes.md (run artifact)
Path:
- `artifacts/<thread_id>/docs/Implementation_Notes.md`

Must include:
- `## What was implemented` (bullets)
- `## Decisions` (what + why, short)
- `## Trade-offs` (what we skipped intentionally)
- `## Extension points` (where Phase 8/9/10 will plug in)
- `## How to validate` (exact commands)
- `## Known gaps` (explicit, no hiding)

---

## Validation commands (must be copy-paste)
Primary (Docker-first):
- Boot: `make boot`
- Lint: `make lint`
- Tests: `make test`

Optional:
- Shell: `make shell`

---

## DoD Checklist (Approval Gate)
- [ ] Sprint_1 P0 tasks implemented (per `Sprint_1_TODO.md`)
- [ ] Phase 6 tests remain green (`make test`)
- [ ] Bot control plane works:
  - [ ] APPROVE advances
  - [ ] REFINE loops current phase
  - [ ] GO BACK rewinds correctly
  - [ ] VIEW/OPEN DOCS shows current run docs
- [ ] Persistence works:
  - [ ] checkpoints saved + resume works
  - [ ] run docs persist (not ephemeral)
- [ ] `Implementation_Notes.md` exists and matches reality

---

## Telegram Completion Message (Template)
- ✅ Implemented: Sprint_1 P0 factory features
- ✅ Tests: `make test` green
- ✅ Notes: `Implementation_Notes.md`
- Buttons: [📄 VIEW CODE DIFFS] [✅ PROCEED TO PHASE 8] [🔁 REFINE FUNCTIONALITY] [🔙 GO BACK TO PHASE 6]