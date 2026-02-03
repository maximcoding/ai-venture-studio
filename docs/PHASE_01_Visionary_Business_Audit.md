# docs/PHASE_01_Visionary_Business_Audit.md

## Phase 1 — Visionary & Business Audit

### Objective
Turn a raw idea into a viable, bounded business concept with clear constraints, risks, and compliance considerations.

### Primary Outputs (Run Artifacts, NOT Factory Docs)
> These files are generated per *project run* (per Telegram thread/session). 이해: they must NOT live in the factory `/docs` folder.

- `artifacts/<thread_id>/docs/Business_Logic.md`
- `artifacts/<thread_id>/docs/Assumptions.md`

Where:
- `<thread_id>` = the LangGraph configurable thread_id (Telegram chat/session identifier)
- `artifacts/<thread_id>/docs/` = the per-run SSOT folder for product artifacts


### Inputs
- CEO idea (1–3 paragraphs)
- Constraints: budget, timeline, region, must-have integrations, forbidden features
- Any existing notes, links, or competitor examples

### Cursor-First Workflow
- **Cursor Plan**: structure the analysis (market, differentiation, feasibility, risks)
- **Cursor @Web**: validate key claims (pricing norms, platform constraints, legal/GDPR basics)
- **Cursor Chat**: synthesize into clear artifacts

### Required Content in `Business_Logic.md`
- One-sentence Core Concept
- Target Audience + primary pain
- USP (why users choose us)
- Monetization (first version)
- Competitive snapshot (high-level)
- Risk Matrix (top 5 risks + mitigation)
- Compliance notes (privacy/data handling posture)

### DoD Checklist (Approval Gate)
- [ ] `Business_Logic.md` exists and includes all required sections
- [ ] `Assumptions.md` lists unknowns + what to verify later
- [ ] Risks are actionable (mitigation or pivot option per risk)
- [ ] Phase summary prepared for Telegram

### Telegram Completion Message (Template)
- ✅ Artifacts: Business_Logic.md, Assumptions.md
- ⚠️ Top Risks: <3 bullets>
- ➡️ Next: Phase 2 (Backlog + MVP cut)
- Buttons: [✅ APPROVE] [🔁 OTHER OPTIONS] [🗣️ WANT TO SAY SOMETHING] [📄 VIEW DOCS]

### If REFINE / LOOP
- Apply CEO feedback to Business_Logic + Assumptions
- Re-run @Web verification only for changed/critical claims
