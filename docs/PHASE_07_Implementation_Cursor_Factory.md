# docs/PHASE_07_Implementation_Cursor_Factory.md

## Phase 7 — Implementation (The Cursor Factory)

### Objective
Implement MVP features while preserving green tests and architecture constraints.

### Cursor Replaces Aider (Required)
- Multi-file features: **Cursor Composer (Cmd+I)**
- Codebase-wide reasoning: **Cursor Chat + @Codebase**
- Review gate: **Cursor Review**
- Safe application of patches: **Cursor Apply**
- Validation: **Cursor @Terminal** (tests/build/lint)

### Inputs
- `artifacts/<thread_id>/docs/Sprint_1_TODO.md`
- `artifacts/<thread_id>/docs/System_Architecture.md`
- `/tests` (green baseline)

Where `<thread_id>` = LangGraph configurable thread_id (Telegram user/session identifier).

### Primary Outputs (per-run artifacts)
- `/src` implements MVP
- API docs (if applicable) generated
- `artifacts/<thread_id>/docs/Implementation_Notes.md` (decisions, trade-offs, extension points)

### DoD Checklist (Approval Gate)
- [ ] All P0 tasks completed
- [ ] Tests remain green
- [ ] Architecture boundaries respected
- [ ] `Implementation_Notes.md` written and accurate

### Telegram Completion Message (Template)
- ✅ Artifacts: Implementation_Notes.md + diff summary
- ✅ Validation: tests green
- Buttons: [📄 VIEW CODE DIFFS] [✅ PROCEED TO VISUAL QA] [🔁 REFINE FUNCTIONALITY] [🔙 GO BACK TO PHASE 6]
