# docs/PHASE_04_System_Architecture_HDL.md

## Phase 4 — System Architecture & HDL

### Objective
Define the technical blueprint (flows, boundaries, data model, integrations) aligned to MVP and design tokens.

### Primary Outputs (per-run artifacts)
- `artifacts/<thread_id>/docs/HDL_Business_Flows.md`
- `artifacts/<thread_id>/docs/System_Architecture.md`
- `artifacts/<thread_id>/docs/Data_Model.md`
- `artifacts/<thread_id>/docs/Roadmap.md`

Where `<thread_id>` = LangGraph configurable thread_id (Telegram user/session identifier).

### Inputs
- `artifacts/<thread_id>/docs/MVP_Scope.md`
- `artifacts/<thread_id>/docs/Design_Tokens.json`
- `artifacts/<thread_id>/docs/Design_System.md`

### Cursor-First Workflow
- **Cursor Plan**: choose architecture style (monolith/modular/services)
- **Cursor Chat**: write HDL flows and system blueprint
- **Cursor @Web**: verify key framework/tool constraints if needed

### DoD Checklist (Approval Gate)
- [ ] HDL describes end-to-end flows for all MVP P0 user journeys
- [ ] Architecture document includes: boundaries, auth, storage, integrations
- [ ] Data model includes entities + relationships + migration strategy
- [ ] Roadmap sequences implementation (what first, what later) with risks

### Telegram Completion Message (Template)
- ✅ Artifacts: HDL_Business_Flows.md, System_Architecture.md, Data_Model.md, Roadmap.md
- 🧱 Key Decisions: <3 bullets>
- Buttons: [✅ APPROVE ARCHITECTURE] [🔁 OTHER TECH STACK] [🔙 GO BACK TO PHASE 3] [📄 VIEW DOCS]
