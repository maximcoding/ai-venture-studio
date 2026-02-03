# docs/PHASE_03_UI_UX_Design_Google_Stitch.md

## Phase 3 — UI/UX Design (Google Stitch)

### Objective
Produce an approved visual direction and a tokenized design system that implementation must follow.

### Primary Outputs (per-run artifacts)
- `artifacts/<thread_id>/docs/Design_System.md`
- `artifacts/<thread_id>/docs/Design_Tokens.json`
- `artifacts/<thread_id>/docs/Prototype_Link.md`
- `artifacts/<thread_id>/docs/UI_Screens_List.md`
- `artifacts/<thread_id>/assets/ui/` (icons/images if needed)

Where `<thread_id>` = LangGraph configurable thread_id (Telegram user/session identifier).

### Inputs
- `artifacts/<thread_id>/docs/MVP_Scope.md`
- `artifacts/<thread_id>/docs/Product_Backlog.md`

### Cursor-First Workflow
- **Cursor Chat**: convert MVP scope → Stitch prompt spec (screens + states)
- **Cursor Plan**: define component taxonomy + token schema
- Generate `Design_Tokens.json` (colors/spacing/typography/radius/shadows)

### Must-Define in Design
- Key screens (minimum): Auth, Home/Dashboard, Primary flow screen(s), Settings/Profile
- UI states: loading / empty / error
- Responsive rules (breakpoints or device targets)

### DoD Checklist (Approval Gate)
- [ ] Prototype link is available (Stitch/Figma)
- [ ] `Design_System.md` defines components + interaction patterns
- [ ] `Design_Tokens.json` is complete and stable
- [ ] Screen list covers MVP P0 flows

### Telegram Completion Message (Template)
- ✅ Artifacts: Design_System.md, Design_Tokens.json, Prototype_Link.md
- 🖼️ Screens: <list>
- Buttons: [✅ APPROVE VISUALS] [🔁 REFINE DESIGN] [🔁 RE-GENERATE] [🔙 GO BACK TO PHASE 2] [📄 VIEW DOCS]
