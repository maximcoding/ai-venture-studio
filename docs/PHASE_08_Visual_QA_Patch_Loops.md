# docs/PHASE_08_Visual_QA_Patch_Loops.md

## Phase 8 — Visual QA & Patch Loops (OSS Harness Default)

### Objective
Achieve design fidelity: expected vs actual UI must match within approved thresholds.

### Default Approach (No OpenClaw Required)
Use deterministic OSS harnesses:
- Web: Playwright visual snapshots
- Mobile: Maestro flows (screenshots + reports)

### Evidence Pack Standard (Required for Every Visual Failure)
Store in `artifacts/<thread_id>/visual-qa/<run-id>/`:
- `expected.png`
- `actual.png`
- `diff.png`
- trace/report/logs
- `meta.json` (route/screen, viewport/device, theme, commit hash)
And update:
- `artifacts/<thread_id>/docs/QA_Report.md` (screen → status → links to artifacts + repro command)

Where `<thread_id>` = LangGraph configurable thread_id (Telegram user/session identifier).

### Cursor Patch Loop
1) Run harness → produce evidence pack  
2) Attach evidence pack to Cursor Chat/Agent  
3) Cursor identifies mismatch → proposes patch  
4) Apply patch → rerun harness  
5) Repeat until pass / approved threshold

### Design Tokens ↔ Code Compliance (Must Check)
- Verify UI uses `Design_Tokens.json` consistently (colors/spacing/typography).
- Cursor @Codebase / Review enforces token usage rules.

### Optional: OpenClaw
OpenClaw remains optional for exploratory clicking if deterministic harness is insufficient.

### DoD Checklist (Approval Gate)
- [ ] `artifacts/<thread_id>/docs/QA_Report.md` exists with links to evidence packs
- [ ] All MVP P0 screens pass visual checks (or approved exceptions)
- [ ] Token compliance verified
- [ ] Repro commands documented

### Telegram Completion Message (Template)
- ✅ Artifacts: QA_Report.md + artifacts links
- ✅ Validation: visual suite pass
- Buttons: [✅ APPROVE UI] [🔁 REFINE UI] [🔙 GO BACK TO PHASE 3/7] [📄 VIEW QA REPORT]
