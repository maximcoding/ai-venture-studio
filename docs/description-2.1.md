**документ v2.1**

---

# Autonomous AI Venture Studio — Cursor-First PRD (v2.1, English)

## 0) Executive Summary

Autonomous AI Venture Studio is a **local-first, stateful software manufacturing factory** that turns an idea into a deployed MVP via a strict **10-phase SDLC pipeline**. The user is the **CEO** (vision, constraints, approvals). The system is the execution org (PM/CTO/Dev/QA/DevOps/SRE).

**v2.1 focus:** Make the factory **Cursor-first** to reduce external paid providers. Cursor becomes the primary execution surface for: multi-file code generation, infra authoring, security review, documentation, and patch loops.

---

## 1) Product Goals & Principles

### 1.1 Goals

* Convert an idea into a working MVP with **traceability**, **repeatability**, and **rollback**.
* Enforce **Gatekeeper Logic**: Phase N requires explicit CEO approval before Phase N+1.
* Maintain a **Time Machine**: rollback to any approved checkpoint without losing artifacts.
* Centralize execution and review inside **Cursor**; rely on OSS tooling for deterministic QA (visual + tests).

### 1.2 Non-Goals

* Fully autonomous progression without CEO approvals.
* Pure “free exploration clicking” as the default QA mode (optional later).
* One fixed tech stack for every project (stack-agnostic by design).

### 1.3 Principles

* **SSOT in `/docs`**: Every phase produces deterministic docs.
* **Statefulness via PostgreSQL**: artifacts + checkpoints persist across restarts.
* **Reproducible runs**: Docker + CI for consistent execution.
* **Cursor-First**: use Cursor (Composer/Chat/Review/@Codebase/@Terminal/@Web/Apply) before adding external providers.

---

## 2) Infrastructure (Local-First Factory)

### 2.1 Local Host (Powerhouse)

A 24/7 machine running:

* Orchestrator services (LangGraph runner)
* Telegram bot service
* PostgreSQL in Docker
* Optional build runners / emulators / test runners (web + mobile)

### 2.2 Telegram Bot (Control Plane)

The only interface:

* input: text/voice/files (templates, screenshots, specs)
* output: summaries, approval buttons, links to artifacts, test reports, diffs, build links

### 2.3 PostgreSQL (Eternal Memory)

Stores:

* all documents: PRD/HDL/Roadmap/Tokens/Reports
* **LangGraph checkpoints** (required for “resume after restart”)
* traceability logs: decisions, approvals, costs, diffs references

**Requirement:** LangGraph persistence uses **Postgres-backed checkpointing (PostgresSaver)** or equivalent so the orchestrator can resume from the last approved node deterministically.

### 2.4 LangGraph (Orchestrator)

* Strict 10-phase state machine
* Cycles for refine loops
* Interrupts for CEO approval
* Rollback commands (“Time Machine”) mapped to checkpoints

### 2.5 Docker Compose (Tooling Layer)

* Reproducible environment for orchestrator, DB, bot, and test runners
* A single `docker-compose.yml` (or per-service compose) to boot the factory reliably

---

## 3) Environment (Cursor-First, Multi-Model Strategy)

### 3.1 Cursor-First Replacements

* **Instead of Aider CLI:** Cursor **Composer/Agent** for multi-file feature implementation.
* **Instead of DevOps agents/engineers:** Cursor **@Terminal + @Web** to generate Dockerfiles, CI/CD YAML, deployment scripts, monitoring configs; validate by running commands.
* **Instead of paid security scanners (primary):** Cursor **Chat + @Codebase** and **Review** for audits and remediation patches. (Optional OSS scanners in CI.)
* **Instead of manual stub coding:** Cursor **Apply** to materialize Phase 1–4 artifacts into stubs/skeleton.
* **Instead of technical writers:** Cursor **@Codebase** generates and updates README, API docs, architecture docs, runbooks.

### 3.2 Multi-Model Strategy (Inside Cursor)

We keep role specialization but use Cursor-supported models:

* Planning/PM/PRD: reasoning model in Cursor
* Architecture/Implementation: Claude-class model in Cursor
* Research/verification: Cursor **Plan** + **@Web** (no separate Gemini subscription)

---

## 4) Repository Layout & Artifact Standards

### 4.1 Baseline Structure

* `/docs` (SSOT)
* `/src`, `/tests`
* `/infra` (Docker/CI/monitoring/deploy)
* `/refs` (read-only cloned references)
* `/artifacts` (test logs, visual diffs, traces; CI-uploaded)

### 4.2 Deterministic Doc Set (SSOT)

* `docs/Business_Logic.md`
* `docs/Product_Backlog.md`
* `docs/MVP_Scope.md`
* `docs/HDL_Business_Flows.md`
* `docs/System_Architecture.md`
* `docs/Roadmap.md`
* `docs/Design_System.md` + `docs/Design_Tokens.json`
* `docs/Test_Report.md`
* `docs/QA_Report.md`
* `docs/Security_Policy.md` + `docs/Budget_Guardrails.md`
* `docs/Operations_Runbook.md`

### 4.3 “Evidence Pack” Standard (required for QA loops)

Any failing validation (tests/visual/security) must produce:

* Repro command
* Logs
* Minimal artifact set (diffs/traces where applicable)
* A short Markdown report in `/docs`

---

## 5) SDLC Pipeline (10 Phases, Approval-Gated)

> **Global Rule:** No phase advances without Telegram `[✅ APPROVE]`.

### Phase 1 — Visionary & Business Audit

**Output:** `Business_Logic.md` (concept, audience, USP, monetization, risks, compliance notes), `Assumptions.md`
**Cursor:** Plan + @Web for verification; Chat for synthesis
**Approve when:** business logic + risks are explicit and bounded

### Phase 2 — Product Management (Backlog & MVP)

**Output:** `Product_Backlog.md`, `MVP_Scope.md`, `Sprint_1_TODO.md`
**Approve when:** MVP boundary is strict; acceptance criteria exist

### Phase 3 — UI/UX Design (Google Stitch)

**Output:** `Design_System.md`, `Design_Tokens.json`, `Prototype_Link.md`, `UI_Assets/`
**Approve when:** prototype direction accepted + tokens schema stable

### Phase 4 — System Architecture & HDL

**Output:** `HDL_Business_Flows.md`, `System_Architecture.md`, `Data_Model.md`, `Roadmap.md`
**Approve when:** flows, boundaries, data model, and roadmap are consistent

### Phase 5 — Project Initialization (Materialization)

**Mandatory step: Foundation Boilerplate Fit Check**
Cursor must evaluate these repos as base codebases:

1. `naoufalelh/cursor-langgraph-starter`
2. `wassim249/fastapi-langgraph-agent-production-ready-template`
3. `francescofano/langgraph-telegram-bot`

**Rule:** If a repo fits ≥90%, use it as the base. Otherwise clone all into `/refs` and extract patterns.

**Output:** repo created, `/docs` synced, `/infra` scaffolded, CI baseline, `.env.example`
**Cursor:** @Terminal + @Web generate infra; @Codebase aligns docs
**Approve when:** project boots locally + CI skeleton runs

### Phase 6 — TDD

**Output:** tests implemented + minimal logic to pass core flows; `Test_Report.md`
**Cursor:** Composer writes tests; @Terminal runs; Apply patches
**Approve when:** core tests green and reproducible

### Phase 7 — Implementation (Factory)

**Output:** MVP features implemented; API docs generated; `Implementation_Notes.md`
**Cursor replaces Aider fully:** Composer/Agent implements multi-file modules; Review gate
**Approve when:** tests green, architecture respected, PR-level diffs reviewed

### Phase 8 — Visual QA & Patch Loops (OSS Harness Default)

**Default harness:** Playwright (web) + Maestro (mobile) generate artifacts. Cursor fixes code.

**Evidence Pack requirements (visual):**

* `expected.png`, `actual.png`, `diff.png`
* trace/report/logs
* `docs/QA_Report.md` linking to artifacts + repro command

**Cursor loop:** attach diff/trace → Cursor analyzes → patch via Apply → rerun
**OpenClaw:** optional later for exploratory clicking; not required by default
**Approve when:** diffs within accepted threshold; critical flows stable

### Phase 9 — Guardrails (Sentinel & Vault)

**Financial Sentinel (required)**

* define daily/monthly token/compute budget
* any “expensive loop” requires approval prompt in Telegram

**Vault / Secrets (required)**

* secrets never in code; `.env.example` only
* CI secret scanning (Gitleaks) is recommended baseline gate
* Cursor @Codebase reviews for leaked keys / insecure configs

**Design Tokens ↔ Code Gate (required)**

* verify that UI code uses tokens (colors/spacing/typography) consistently
* Cursor Review enforces token usage rules

**Outputs:** `Security_Policy.md`, `Budget_Guardrails.md`, CI gates configured
**Approve when:** budget rules + secrets hygiene + audits pass

### Phase 10 — DevOps, Growth & SRE

**DevOps:** deploy scripts/configs, infra as code
**SRE:** monitoring/alerts + incident runbook + patch workflow
**Growth:** launch checklist + initial marketing assets drafts (as artifacts)
**Cursor:** @Terminal + @Web for configs; Review for infra diffs
**Approve when:** deploy is reproducible + monitoring exists + rollback plan documented

---

## 6) Governance — Human-in-the-Loop (Command Matrix)

### 6.1 Telegram Controls

* `[✅ APPROVE]` checkpoint + advance
* `[🔁 REFINE]` loop current phase
* `[🔙 TIME MACHINE]` rollback to Phase X checkpoint

### 6.2 Time Machine (Rollback Semantics) — Required

On rollback:

1. restore checkpoint state from PostgreSQL
2. preserve current repo state into a `draft/<timestamp>` branch
3. apply CEO edits to artifacts (docs)
4. recompute downstream phases (Architecture/Roadmap/TDD) deterministically
5. re-run validations (tests/visual/security) before allowing re-approval

---

## Appendix A — OSS Visual QA Stack (Recommended, optional but pre-planned)

* Web: Playwright snapshot tests → expected/actual/diff + trace/report
* Mobile: Maestro flows + screenshots + reports
* CI: store `/artifacts/visual-qa/**` and link them in `docs/QA_Report.md`

---

## Appendix B — Starter Repo Fit Check (Required)

* Evaluate ≥90% fit, otherwise clone into `/refs` and extract:

  * Telegram bot patterns
  * LangGraph orchestration patterns (interrupts/checkpoints)
  * Postgres persistence patterns
  * Docker/compose + CI conventions

