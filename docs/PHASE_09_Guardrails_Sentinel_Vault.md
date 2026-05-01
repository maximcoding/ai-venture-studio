# docs/PHASE_09_Guardrails_Sentinel_Vault.md

## Phase 9 — Guardrails (Sentinel & Vault)

### Objective
Ship with control. Prevent:
- runaway spend (LLM loops, visual QA loops, refactors)
- secret leaks (tokens/keys in repo, logs, artifacts)
- obvious security footguns (auth, input validation, CORS, deps)

This is **pre-launch hardening**. No new features.

---

## Inputs
- `artifacts/<thread_id>/docs/System_Architecture.md`
- `artifacts/<thread_id>/docs/Implementation_Notes.md`
- `artifacts/<thread_id>/docs/QA_Report.md` (if surface has UI)
- Repo config: `.env.example`, CI workflows, Docker compose

Where `<thread_id>` = `user_<telegram_user_id>`.

---

## Primary Outputs (per-run artifacts)
- `artifacts/<thread_id>/docs/Budget_Guardrails.md`
- `artifacts/<thread_id>/docs/Security_Policy.md`
- Repo-level hardening:
  - `.env.example` (safe)
  - CI gates enabled (lint/test/secret scan + optional SAST)
  - pre-commit hooks optional (but CI must enforce)

---

## Sentinel — Budget Guardrails (Required)

### What gets budgeted
We budget **factory operations**, not the product runtime:
- LLM calls (phase generation, refine loops)
- Visual QA loops (reruns, traces, screenshot diffs)
- Large refactors / migration passes

### Budget Model (deterministic)
Define thresholds in `Budget_Guardrails.md` as numbers:
- Daily cap (USD)
- Monthly cap (USD)
- Per-action cap (USD) — single loop iteration cost ceiling

Also define behavior when estimates are missing:
- If cost cannot be estimated → treat as “needs approval”.

### Approval Gate (Telegram)
Any action classified as “expensive” must pause and request explicit approval:
- “Run Phase 8 loop again (web/mobile)”
- “Re-run Phase 3 Stitch generation”
- “Mass refactor across /src”
- “Dependency upgrade sweep”

Telegram approval message must include:
- action name
- reason (what failed / what will improve)
- estimated cost range (min/max)
- expected outputs (what artifacts change)
Buttons:
- ✅ APPROVE ONCE
- ✅ APPROVE UNTIL END OF PHASE (bounded)
- ❌ CANCEL
- ⚙️ CHANGE LIMITS

### Config (implementation-level)
Store guardrails config as one source of truth (choose one):
- `infra/config/budget_guardrails.yaml`
OR
- `.env` values (less ideal but acceptable)

Minimum fields:
- `BUDGET_DAILY_USD`
- `BUDGET_MONTHLY_USD`
- `BUDGET_PER_ACTION_USD`
- `BUDGET_APPROVAL_MODE=always|expensive_only`

---

## Vault — Secrets Hygiene (Required)

### Non-negotiables
- No secrets in git
- No secrets in `/docs`
- No secrets in `artifacts/` committed (artifacts must be gitignored)
- `.env.example` only (placeholders, never real values)
- Production secrets come from runtime injection:
  - Docker env file at deploy time
  - platform secret store (recommended)

### Git hygiene
Repo must include:
- `.gitignore` covering:
  - `.env`
  - `.venv`
  - `artifacts/`
  - `secrets/`
  - any build outputs

### CI Secret Scanning Gate
Enable at least ONE:
- Gitleaks (recommended)
- TruffleHog
- GitHub Advanced Security (if available)

Gate rules:
- Fail CI on detected secrets
- Allowlist file must be explicit and minimal (false positives only)

### Runtime secret handling
- No printing secrets in logs
- No returning secrets in API responses
- Avoid storing secrets in DB unless encrypted + justified (ideally never)

---

## Security Review — Cursor-First (Required)

### Scope
We check **factory + product skeleton**:
- bot endpoints / web app endpoints (if present)
- auth boundaries
- input validation
- permissions
- dependency hygiene

### Audit Passes (must run)
1) **Codebase scan (Cursor Chat + @Codebase)**
   Look for:
   - hard-coded tokens, URLs with keys, “Bearer …”
   - missing validation / unsafe parsing
   - unsafe shell calls / command injection
   - open CORS / permissive headers (if web)
   - auth bypass patterns (trusting client fields)
   - SSRF vectors (fetching URLs from user input)
   - path traversal in file operations
   - unsafe deserialization

2) **Dependency review**
   - lock versions where possible
   - remove unused deps
   - check for known critical CVEs (CI step optional)
   - ensure minimal runtime deps for production

3) **Configuration review**
   - docker-compose: no privileged containers, no host network, no mounting Docker socket (unless explicitly needed)
   - postgres: credentials via env, not defaults in code
   - ports: expose only what’s needed
   - TLS termination plan documented (if web)

### Remediation workflow
- Cursor proposes diffs
- Cursor Review acts as the gate
- All fixes land with:
  - short commit message
  - note in `Security_Policy.md` (“what changed / why”)

---

## Budget_Guardrails.md — Required Structure
Must include:
- `## Thresholds`
  - daily / monthly / per-action
- `## What Requires Approval`
  - list of actions
- `## Estimation Rules`
  - how we estimate cost (or default to approval)
- `## Telegram Approval UX`
  - message template + buttons
- `## Overrides`
  - how CEO can temporarily raise limits

---

## Security_Policy.md — Required Structure
Must include:
- `## Data Surfaces`
  - Delivery surface (web/mobile/api/automation)
  - what endpoints exist (high-level)
- `## Authentication & Authorization`
  - how users are identified
  - what permissions exist
- `## Input Validation`
  - where enforced (API layer, bot handlers)
- `## Secrets Handling`
  - where secrets live
  - how injected
- `## Logging`
  - what we log
  - what we never log
- `## Dependencies`
  - how we scan / pin
- `## Known Risks & Mitigations`
  - short list, actionable

---

## DoD Checklist (Approval Gate)
- [ ] `Budget_Guardrails.md` exists and thresholds are numeric and enforced
- [ ] Telegram approval gate exists for expensive loops
- [ ] `.env.example` is safe and complete (placeholders only)
- [ ] CI secret scanning gate is enabled and passing
- [ ] `Security_Policy.md` exists and matches actual repo behavior
- [ ] Security scan findings are fixed or explicitly documented as accepted risk

---

## Telegram Completion Message (Template)
- ✅ Artifacts: Budget_Guardrails.md, Security_Policy.md
- ✅ Gates: lint/test + secret scan pass
- ⚠️ Open Risks (if any): <1–3 bullets>
Buttons:
- [📄 VIEW BUDGET]
- [🔁 SCAN SECURITY]
- [✅ APPROVE GUARDRAILS]
- [🔙 GO BACK TO PHASE 7/8]