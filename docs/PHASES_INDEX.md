# Autonomous AI Venture Studio — Phases Index

Single navigation for the 10-phase pipeline. **No phase advances without CEO approval in Telegram.**

---

## Product Goals

* Convert an idea into a working MVP with **traceability**, **repeatability**, and **rollback**.
* **Gatekeeper:** Phase N requires explicit CEO approval in Telegram before Phase N+1.
* **Time Machine:** Roll back to any approved checkpoint; current state is preserved (git draft branch or filesystem snapshot).
* **Cursor-first execution;** OSS tooling for tests and visual QA.
* **Factory SSOT** lives in `/docs` (manuals + phase specs). **Run SSOT** lives in DB (documents + revisions), with optional export cache under `artifacts/<thread_id>/`.

---

## Factory Manuals vs Run Artifacts

### Factory manuals (static, repo-level)

Live in:

* `/docs/` (this folder)

Examples:

* `PHASE_01_*.md` … `PHASE_10_*.md`
* `Foundation_Template.md`
* `PHASES_INDEX.md`

### Run artifacts (dynamic, per Telegram run/session)

Canonical store:

* **PostgreSQL** documents + revisions keyed by `thread_id`

Optional export/debug cache:

* `artifacts/<thread_id>/docs/` (markdown exports)
* `artifacts/<thread_id>/visual-qa/` (evidence packs)
* `artifacts/<thread_id>/snapshots/` (rollback snapshots if git isn’t available)

Rule:

* **Never** write run artifacts into `/docs`.

---

## Global Rules

* **Approval gate:** Each phase produces required outputs + reproducible validation. CEO approves in Telegram before the next phase.
* **Control plane:** Telegram chat + Telegram Web App (doc viewer/editor). No “download .md to phone” workflow.
* **Folders:**

  * `/docs` — factory manuals (SSOT)
  * `/src` — factory runtime + product code skeleton
  * `/tests` — test harness
  * `/infra` — docker/CI/deploy
  * `/artifacts/<thread_id>/` — run exports/evidence/snapshots (optional but useful)
  * `/refs` — read-only cloned donor repos
* **Delivery Surface is a hard constraint:** `mobile | web | api | automation`

  * Defined in Phase 1 (Business_Logic).
  * Shapes Phase 2 backlog.
  * Determines Phase 3 (UI design) behavior.
  * Determines Phase 4 architecture shape.

---

## Phase Map

```mermaid
flowchart LR
  P1[1 Vision] --> P2[2 Backlog] --> P3[3 UI/UX] --> P4[4 Architecture] --> P5[5 Init] --> P6[6 TDD] --> P7[7 Implementation] --> P8[8 Visual QA] --> P9[9 Guardrails] --> P10[10 DevOps]
```

---

## Phase Summaries

### Phase 1 — Visionary & Business Audit

* **What:** Turn a raw idea into a viable, bounded concept (USP, monetization, risks, compliance posture).
* **Includes:** **Delivery Surface** (`mobile | web | api | automation`) — hard constraint for later phases.
* **How:** Cursor Plan + @Web validate key claims; synthesize into run documents; review/edit via Telegram Web App.
* **Doc:** [PHASE_01_Visionary_Business_Audit.md](PHASE_01_Visionary_Business_Audit.md)

### Phase 2 — Product Management (Backlog & MVP)

* **What:** Convert approved business logic into epics, user stories, acceptance criteria, and a strict MVP boundary.
* **How:** Cursor Plan (epics → stories → AC) + Chat for backlog/MVP cut; CEO reviews summaries (not wall-of-text).
* **Doc:** [PHASE_02_Product_Management_Backlog_MVP.md](PHASE_02_Product_Management_Backlog_MVP.md)

### Phase 3 — UI/UX Design (Google Stitch)

* **What:** Produce an approved visual direction and a prototype link.
* **Conditional:** Runs only if Delivery Surface is `web` or `mobile` (or `auto` resolves there). Skipped for `api`/`automation`.
* **How:** Generate a Stitch prompt → call Stitch via MCP → post link + screenshots back to Telegram; allow refine loop by screen.
* **Doc:** [PHASE_03_UI_UX_Design_Google_Stitch.md](PHASE_03_UI_UX_Design_Google_Stitch.md)

### Phase 4 — System Architecture & HDL

* **What:** Define the technical blueprint aligned to MVP and (if applicable) design outputs.
* **How:** Architecture shape is driven by Delivery Surface:

  * `web/mobile`: UI + API + storage + auth boundaries
  * `api`: API-first + jobs + storage + auth boundaries
  * `automation`: job runner + schedulers + storage + integrations
* **Doc:** [PHASE_04_System_Architecture_HDL.md](PHASE_04_System_Architecture_HDL.md)

### Phase 5 — Project Initialization (Materialization)

* **What:** Materialize the repo and runtime: structure, infra scaffold, CI baseline, and initial skeleton.
* **How:** Evaluate candidate bases; adopt ≤1 base if ≥90% fit; otherwise keep all as donors in `/refs`. Ensure docker-compose and artifacts persistence.
* **Doc:** [PHASE_05_Project_Initialization_Materialization.md](PHASE_05_Project_Initialization_Materialization.md)

### Phase 6 — TDD

* **What:** Lock correctness for MVP P0 flows with *minimal* tests (only what blocks iteration).
* **How:** Cursor writes tests where they reduce churn; allow xfails where justified; produce a reproducible `make test` report.
* **Doc:** [PHASE_06_TDD.md](PHASE_06_TDD.md)

### Phase 7 — Implementation (The Cursor Factory)

* **What:** Implement MVP features while respecting architecture constraints.
* **How:** Cursor Composer/Apply/Review/@Codebase/@Terminal. Keep changes small, validate continuously.
* **Doc:** [PHASE_07_Implementation_Cursor_Factory.md](PHASE_07_Implementation_Cursor_Factory.md)

### Phase 8 — Visual QA & Patch Loops

* **What:** Achieve design fidelity (expected vs actual) within approved thresholds.
* **Where it runs:**

  * `web`: Playwright against a running URL
  * `mobile`: Maestro against emulator/simulator builds
* **How:** Evidence pack → Cursor analysis → patch → rerun loop until pass/approved exception.
* **Doc:** [PHASE_08_Visual_QA_Patch_Loops.md](PHASE_08_Visual_QA_Patch_Loops.md)

### Phase 9 — Guardrails (Sentinel & Vault)

* **What:** Budget controls + secrets hygiene + basic security posture before launch.
* **How:** Spending thresholds require Telegram approval for expensive loops; secret scanning gates; Cursor security pass on codebase.
* **Doc:** [PHASE_09_Guardrails_Sentinel_Vault.md](PHASE_09_Guardrails_Sentinel_Vault.md)

### Phase 10 — DevOps, Growth & SRE

* **What:** Deploy reliably, observe the system, define runbooks/rollback, and prep launch loops.
* **How:** Cursor writes deploy configs and runbooks; minimal monitoring + alerting; launch checklist + KPIs.
* **Doc:** [PHASE_10_DevOps_Growth_SRE.md](PHASE_10_DevOps_Growth_SRE.md)

---

## Time Machine (Rollback)

On rollback to Phase X:

1. Restore **checkpoint state** from PostgreSQL (LangGraph checkpointer).
2. Preserve current repo state:

   * If git remote + credentials exist (e.g., GitHub): create `draft/<timestamp>` branch.
   * Else: snapshot to `artifacts/<thread_id>/snapshots/<timestamp>/` (tarball or file list).
3. Apply CEO edits to run documents (DB revisions; export cache optional).
4. Recompute downstream phases (X+1..10) and rerun validations before re-approval.

---
