# docs/PHASE_09_Guardrails_Sentinel_Vault.md

## Phase 9 — Guardrails (Sentinel & Vault)

### Objective
Enforce budget controls, secrets hygiene, and security posture before launch.

### Sentinel (Budget Guardrails) — Required
- Define daily/monthly spend thresholds
- Any “expensive loop” (big refactor / heavy QA iteration) requires Telegram approval

### Vault (Secrets Hygiene) — Required
- Secrets never in code
- `.env.example` only
- CI secret scanning recommended (e.g., Gitleaks gate)
- Cursor @Codebase audit to find risky patterns and misconfigurations

### Security Review (Cursor-First)
- Cursor Chat + @Codebase to locate:
  - insecure auth flows
  - unsafe dependency usage
  - exposed endpoints / missing validation
  - misconfigured CORS / headers (where applicable)
- Cursor Review to approve remediation diffs

### Primary Outputs (per-run artifacts)
- `artifacts/<thread_id>/docs/Security_Policy.md`
- `artifacts/<thread_id>/docs/Budget_Guardrails.md`
- `.env.example` hardened
- CI gates enabled (lint/tests/security where applicable)

Where `<thread_id>` = LangGraph configurable thread_id (Telegram user/session identifier).

### DoD Checklist (Approval Gate)
- [ ] Budget thresholds defined + Telegram approval behavior documented
- [ ] Secrets hygiene enforced + scanning gate present
- [ ] Security audit completed and fixes applied
- [ ] Security policy doc exists and matches reality

### Telegram Completion Message (Template)
- ✅ Artifacts: Security_Policy.md, Budget_Guardrails.md
- ✅ Validation: security gates pass
- Buttons: [📄 VIEW BUDGET] [✅ APPROVE GUARDRAILS] [🔁 SCAN SECURITY] [🔙 GO BACK TO PHASE 5]
