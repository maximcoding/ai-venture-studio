# docs/PHASE_06_TDD.md

## Phase 6 — Test-Driven Development (TDD)

### Objective
Lock correctness for MVP core logic via tests before full implementation.

### Primary Outputs (per-run artifacts)
- `/tests` contains unit + integration tests for MVP P0 flows
- `artifacts/<thread_id>/docs/Test_Report.md`

Where `<thread_id>` = LangGraph configurable thread_id (Telegram user/session identifier).

### Inputs
- `artifacts/<thread_id>/docs/HDL_Business_Flows.md`
- `artifacts/<thread_id>/docs/Data_Model.md`
- `artifacts/<thread_id>/docs/Sprint_1_TODO.md`

### Cursor-First Workflow
- **Cursor Composer/Agent**: write tests first (red)
- **Cursor @Terminal**: run tests and collect logs (green loop)
- **Cursor Apply**: implement minimal code to satisfy tests
- Refactor while keeping tests green

### DoD Checklist (Approval Gate)
- [ ] P0 flows covered by tests
- [ ] Tests are reproducible with a single command
- [ ] `docs/Test_Report.md` includes: commands, summary, links to logs
- [ ] Tests are green (or approved xfail list with rationale)

### Telegram Completion Message (Template)
- ✅ Artifacts: Test_Report.md
- ✅ Validation: <test command> (passed)
- Buttons: [📄 VIEW TEST RESULTS] [✅ PROCEED TO IMPLEMENTATION] [🔁 REFINE LOGIC] [🔙 GO BACK TO PHASE 4]
