# docs/PHASES_INDEX.md

## Autonomous AI Venture Studio — Phases Index (v2.2)

This index is the single navigation page for the 10-phase SDLC pipeline.
Rule: **No phase advances without explicit CEO approval in Telegram.**

---

## Factory vs Product Artifacts (Critical Distinction)

| Type | Location | Purpose |
|------|----------|---------|
| **Factory Manuals** | `/docs/PHASE_*.md` | Instructions for running phases (this repo's docs) |
| **Product Outputs** | `artifacts/<thread_id>/docs/*.md` | Per-run artifacts generated for each project |

- `<thread_id>` = LangGraph configurable thread_id (derived from Telegram user/session)
- Factory docs (`/docs/`) are **read-only templates** — never write product outputs here
- Product artifacts are **per-run** — each Telegram session produces its own set

---

## Global Rules

### Approval Gate (Always Required)
- Each phase produces its required artifacts in `artifacts/<thread_id>/docs/`
- Validation (tests/visual/security) must be reproducible with a command
- Telegram completion message must include: **artifacts, validation status, risks, next**
- Telegram "VIEW DOCS" button points to `artifacts/<thread_id>/docs/`
- Time Machine rollback restores checkpoint and preserves current code in a draft branch

### Shared Folders
- `/docs` — Factory manuals only (PHASE_*.md instructions, Foundation_Template.md)
- `/src` — product code
- `/tests` — tests
- `/infra` — Docker/CI/deploy/monitoring
- `/artifacts/<thread_id>/docs/` — per-run product artifacts (Business_Logic.md, etc.)
- `/artifacts/visual-qa/<run-id>/` — visual QA evidence packs
- `/refs` — cloned reference repos (read-only)

---

## Phase Map (10 Phases)

### Phase 1 — Visionary & Business Audit
**Goal:** Turn an idea into a bounded business concept (USP, monetization, risks, compliance notes).  
**Doc:** `docs/PHASE_01_Visionary_Business_Audit.md`  
**Required Artifacts (per-run):**
- `artifacts/<thread_id>/docs/Business_Logic.md`
- `artifacts/<thread_id>/docs/Assumptions.md`
**Validation:** none (logic/consistency review)  
**Telegram Buttons:**  
[✅ APPROVE] [🔁 OTHER OPTIONS] [🗣️ WANT TO SAY SOMETHING] [📄 VIEW DOCS]

---

### Phase 2 — Product Management (Backlog & MVP)
**Goal:** Convert business logic → user stories + strict MVP boundary + Sprint-1 TODO.  
**Doc:** `docs/PHASE_02_Product_Management_Backlog_MVP.md`  
**Required Artifacts (per-run):**
- `artifacts/<thread_id>/docs/Product_Backlog.md`
- `artifacts/<thread_id>/docs/MVP_Scope.md`
- `artifacts/<thread_id>/docs/Sprint_1_TODO.md`
**Validation:** none (scope sanity + acceptance criteria)  
**Telegram Buttons:**  
[✅ APPROVE BACKLOG] [🔁 RE-PRIORITIZE] [🔙 GO BACK TO PHASE 1] [📄 VIEW DOCS]

---

### Phase 3 — UI/UX Design (Google Stitch)
**Goal:** Produce prototype link + stable Design System + Design Tokens.  
**Doc:** `docs/PHASE_03_UI_UX_Design_Google_Stitch.md`  
**Required Artifacts (per-run):**
- `artifacts/<thread_id>/docs/Prototype_Link.md`
- `artifacts/<thread_id>/docs/Design_System.md`
- `artifacts/<thread_id>/docs/Design_Tokens.json`
- `artifacts/<thread_id>/docs/UI_Screens_List.md`
**Validation:** visual review (CEO approval of direction)  
**Telegram Buttons:**  
[✅ APPROVE VISUALS] [🔁 REFINE DESIGN] [🔁 RE-GENERATE] [🔙 GO BACK TO PHASE 2] [📄 VIEW DOCS]

---

### Phase 4 — System Architecture & HDL
**Goal:** Define flows, boundaries, data model, roadmap aligned to MVP + design tokens.  
**Doc:** `docs/PHASE_04_System_Architecture_HDL.md`  
**Required Artifacts (per-run):**
- `artifacts/<thread_id>/docs/HDL_Business_Flows.md`
- `artifacts/<thread_id>/docs/System_Architecture.md`
- `artifacts/<thread_id>/docs/Data_Model.md`
- `artifacts/<thread_id>/docs/Roadmap.md`
**Validation:** architecture consistency review  
**Telegram Buttons:**  
[✅ APPROVE ARCHITECTURE] [🔁 OTHER TECH STACK] [🔙 GO BACK TO PHASE 3] [📄 VIEW DOCS]

---

### Phase 5 — Project Initialization (Materialization)
**Goal:** Create repo + scaffold runtime/CI + sync docs + stubs; perform starter template fit check.  
**Doc:** `docs/PHASE_05_Project_Initialization_Materialization.md`  
**Required Artifacts:**
- `docs/Foundation_Template.md` (factory decision record: ≥90% base repo OR `/refs` clones)
- baseline repo structure: `/docs /src /tests /infra /artifacts /refs`
- `docker-compose.yml` (or equivalent)
- CI skeleton (lint + tests)
- `.env.example`
> Note: Foundation_Template.md stays in `/docs` because it's a factory setup decision, not a per-run product output.

**Validation (minimum):**
- local boot: `make boot` (or `docker compose -f infra/docker-compose.yml up --build`)
- CI baseline run passes (`make lint`, `make test`)
**Telegram Buttons:**  
[✅ INITIALIZE & START] [📄 EXPLORE STRUCTURE] [🔁 REFINE STRUCTURE] [🔙 GO BACK TO PHASE 4]

---

### Phase 6 — TDD
**Goal:** Write tests first for MVP P0 flows; keep a reproducible green baseline.  
**Doc:** `docs/PHASE_06_TDD.md`  
**Required Artifacts (per-run):**
- `/tests` (unit + integration for P0)
- `artifacts/<thread_id>/docs/Test_Report.md`
**Validation (required):**
- test command documented in `Test_Report.md`
- tests green (or approved xfail list)
**Telegram Buttons:**  
[📄 VIEW TEST RESULTS] [✅ PROCEED TO IMPLEMENTATION] [🔁 REFINE LOGIC] [🔙 GO BACK TO PHASE 4]

---

### Phase 7 — Implementation (The Cursor Factory)
**Goal:** Implement MVP features using Cursor (Composer/Apply/Review/@Codebase/@Terminal).  
**Doc:** `docs/PHASE_07_Implementation_Cursor_Factory.md`  
**Required Artifacts (per-run):**
- `/src` implements MVP P0
- `artifacts/<thread_id>/docs/Implementation_Notes.md`
- API docs (if applicable)
**Validation (required):**
- tests remain green (same command as Phase 6)
- lint/build commands documented
**Telegram Buttons:**  
[📄 VIEW CODE DIFFS] [✅ PROCEED TO VISUAL QA] [🔁 REFINE FUNCTIONALITY] [🔙 GO BACK TO PHASE 6]

---

### Phase 8 — Visual QA & Patch Loops (OSS Harness Default)
**Goal:** Achieve design fidelity using Playwright/Maestro evidence packs + Cursor patches.  
**Doc:** `docs/PHASE_08_Visual_QA_Patch_Loops.md`  
**Required Artifacts (per-run):**
- `artifacts/<thread_id>/visual-qa/<run-id>/expected.png`
- `artifacts/<thread_id>/visual-qa/<run-id>/actual.png`
- `artifacts/<thread_id>/visual-qa/<run-id>/diff.png`
- traces/reports/logs + `meta.json`
- `artifacts/<thread_id>/docs/QA_Report.md` (table with links + repro command)
**Validation (required):**
- Playwright/Maestro visual suite run reproducibly
- token compliance verified (Design Tokens ↔ Code)
**Telegram Buttons:**  
[✅ APPROVE UI] [🔁 REFINE UI] [🔙 GO BACK TO PHASE 3/7] [📄 VIEW QA REPORT]

---

### Phase 9 — Guardrails (Sentinel & Vault)
**Goal:** Budget limits + secrets hygiene + security audit before launch.  
**Doc:** `docs/PHASE_09_Guardrails_Sentinel_Vault.md`  
**Required Artifacts (per-run):**
- `artifacts/<thread_id>/docs/Budget_Guardrails.md`
- `artifacts/<thread_id>/docs/Security_Policy.md`
- `.env.example` hardened
- CI gate(s) for secret scanning recommended (e.g., gitleaks)
**Validation (required):**
- security checks pass (cursor review + any CI scanners)
- budget approval behavior documented for expensive loops
**Telegram Buttons:**  
[📄 VIEW BUDGET] [✅ APPROVE GUARDRAILS] [🔁 SCAN SECURITY] [🔙 GO BACK TO PHASE 5]

---

### Phase 10 — DevOps, Growth & SRE
**Goal:** Deploy reproducibly, monitor health, define runbooks, and prepare launch loops.  
**Doc:** `docs/PHASE_10_DevOps_Growth_SRE.md`  
**Required Artifacts (per-run):**
- `/infra` deploy configs/scripts
- `artifacts/<thread_id>/docs/Operations_Runbook.md`
- `artifacts/<thread_id>/docs/Monitoring_Plan.md`
- `artifacts/<thread_id>/docs/Launch_Checklist.md`
**Validation (required):**
- deploy test (staging/local) documented + executed at least once
- rollback path documented
**Telegram Buttons:**  
[✅ GO TO DEPLOY] [📄 VIEW RUNBOOK] [📊 VIEW HEALTH] [🔙 TIME MACHINE]

---

## Time Machine (Rollback) — Minimum Contract
On rollback to Phase X:
1) Restore checkpoint state from PostgreSQL
2) Save current repo state into `draft/<timestamp>` branch
3) Apply CEO edits to `artifacts/<thread_id>/docs/` (per-run SSOT)
4) Recompute downstream phases (X+1..10)
5) Re-run validations before allowing re-approval

---

## Docker & Volume Best Practices

**CRITICAL for artifact persistence:**
- Any directory where phases write outputs MUST be volume-mounted in docker-compose.yml
- Without volume mounts, files exist only inside the container and vanish on rebuild/restart

**Required volume mounts:**
```yaml
services:
  app:
    volumes:
      - ../artifacts:/app/artifacts    # Phase outputs (MUST persist on host)
      - ../docs:/app/docs              # Optional: if phases auto-update docs
```

**Verification after Phase 1:**
```bash
# Should show files on HOST filesystem, not just in container
ls artifacts/user_<telegram_id>/docs/
```

**Common Docker issues:**
1. **Missing .env file** → Bot won't start (no TELEGRAM_BOT_TOKEN)
2. **No volume mount** → Artifacts disappear on container restart  
3. **Stale image cache** → Code changes not reflected (run `make boot` or rebuild with `--no-cache`)
4. **Port conflicts** → Postgres 5432 already in use (change port in docker-compose.yml)
