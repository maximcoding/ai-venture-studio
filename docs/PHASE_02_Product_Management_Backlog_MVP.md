# docs/PHASE_02_Product_Management_Backlog_MVP.md

## Phase 2 — Product Management (Backlog & MVP)

### Objective
Translate the approved business logic into user stories, acceptance criteria, and a strict MVP boundary.

### Primary Outputs (per-run artifacts)
- `artifacts/<thread_id>/docs/Product_Backlog.md`
- `artifacts/<thread_id>/docs/MVP_Scope.md`
- `artifacts/<thread_id>/docs/Sprint_1_TODO.md`

Where `<thread_id>` = LangGraph configurable thread_id (Telegram user/session identifier).

### Inputs
- `artifacts/<thread_id>/docs/Business_Logic.md`
- `artifacts/<thread_id>/docs/Assumptions.md`

### Cursor-First Workflow
- **Cursor Plan**: define epics → user stories → acceptance criteria
- **Cursor Chat**: produce backlog + MVP cut
- **Cursor @Codebase** (optional later): keep docs aligned with implementation

### DoD Checklist (Approval Gate)
- [ ] `Product_Backlog.md` includes user stories + acceptance criteria
- [ ] `MVP_Scope.md` clearly states: IN / OUT
- [ ] `Sprint_1_TODO.md` maps MVP to concrete engineering tasks
- [ ] Dependencies and priorities (P0/P1/P2) are explicit

### Telegram Completion Message (Template)
- ✅ Artifacts: Product_Backlog.md, MVP_Scope.md, Sprint_1_TODO.md
- 🎯 MVP Summary: <5 bullets>
- ⚖️ Key Trade-offs: <2–3 bullets>
- Buttons: [✅ APPROVE BACKLOG] [🔁 RE-PRIORITIZE] [🔙 GO BACK TO PHASE 1] [📄 VIEW DOCS]
