# docs/PHASE_02_Product_Management_Backlog_MVP.md

## Phase 2 — Product Management (Backlog & MVP)

### Objective
Convert Phase 1 outputs into an executable delivery plan:
- a strict MVP boundary
- prioritized user stories with acceptance criteria
- Sprint 1 engineering TODO that Phase 6 (TDD) and Phase 7 (Implementation) can run without guessing

This phase is **for the factory**, not for the CEO to read details.

---

## Inputs (per-run artifacts)
- `artifacts/<thread_id>/docs/Business_Logic.md`
- `artifacts/<thread_id>/docs/Assumptions.md`

Where:
- `<thread_id>` = LangGraph configurable `thread_id` (Telegram user/session identifier)
- `artifacts/<thread_id>/docs/` = per-run SSOT for product run artifacts

---

## Primary Outputs (per-run artifacts)
- `artifacts/<thread_id>/docs/MVP_Scope.md`  
  MVP boundary with **IN / OUT**, plus constraints and explicit trade-offs.

- `artifacts/<thread_id>/docs/Product_Backlog.md`  
  Epics + user stories + acceptance criteria + priority + dependencies.

- `artifacts/<thread_id>/docs/Sprint_1_TODO.md`  
  Concrete engineering tasks mapped to MVP P0s, sized for Phase 6/7 execution.

---

## CEO Visibility (summary-only)
Default behavior: **CEO sees only an HLD-style summary** in Telegram.

- CEO does **not** read backlog/TODO files by default.
- Full artifacts exist for automation + rollback + auditability.
- “Details” are shown only if CEO taps **DRILL DOWN**.

This is mandatory to keep the CEO loop lightweight while keeping the factory deterministic.

---

## Cursor-First Workflow (factory instructions)

### Step 1 — Parse Phase 1 artifacts
- Read:
  - `Business_Logic.md` for product goal, USP, monetization, risks.
  - `Assumptions.md` for unknowns and constraints that must become tasks.

### Step 2 — Create Epics
Create 3–8 epics max. Example types:
- Identity & access
- Core workflow(s)
- Data model & persistence
- Billing/monetization
- Observability & analytics
- Compliance posture (data minimization, retention, consent)

### Step 3 — Write User Stories (+ Acceptance Criteria)
For each epic, generate user stories with:
- **Story**: “As a <role>, I want <capability> so that <benefit>.”
- **Priority**: P0 / P1 / P2
- **Dependencies**: story IDs this depends on
- **Acceptance Criteria**: 3–7 bullet checks, testable, unambiguous
- **Notes**: edge cases, constraints, non-goals

Rules:
- P0 stories must form a single coherent “happy path”.
- Anything not required for P0 path is OUT for MVP (goes to P1+).

### Step 4 — Cut MVP (IN / OUT)
Generate `MVP_Scope.md`:
- **MVP IN**: only P0 stories and minimal infra required to run them
- **MVP OUT**: explicit exclusions (features, integrations, roles, platforms)
- **Constraints**: budget/time/region/forbidden features carried forward
- **Trade-offs**: what we sacrifice to ship faster

### Step 5 — Produce Sprint 1 TODO (engineering plan)
Generate `Sprint_1_TODO.md`:
- Group tasks into sections:
  - Repo/infra (compose, env, CI checks) — only if missing
  - Data model (schemas, migrations strategy, seed data)
  - API contracts (DTOs, endpoints, errors)
  - Core services (business logic)
  - Bot UX (commands, approval flows, doc viewer)
  - Tests (unit/integration baseline)
- Each task must have:
  - `Owner`: phase executor (TDD / Implementation / Infra)
  - `DoD`: definition of done (what must be true)
  - `Links`: references to story IDs

Sprint 1 rule:
- Only tasks that unblock Phase 6/7 execution.
- Keep it small enough to complete in one iteration.

---

## Artifact Formats (strict)

### `Product_Backlog.md` format
Required sections:
- `## Epics`
- `## User Stories`
- `## Dependencies`
- `## Open Questions (carry from Assumptions)`

User story template:
- `ID: US-###`
- `Epic: EP-###`
- `Priority: P0|P1|P2`
- `Story: ...`
- `Acceptance Criteria:`
  - `- AC1 ...`
  - `- AC2 ...`
- `Dependencies: [US-###, ...]`
- `Notes: ...`

### `MVP_Scope.md` format
Required sections:
- `## MVP IN (P0 only)`
- `## MVP OUT (explicit)`
- `## Constraints`
- `## Trade-offs`
- `## MVP Risks (top 3)`

### `Sprint_1_TODO.md` format
Required sections:
- `## Sprint Goal`
- `## Task List`
- `## Test Plan (minimum)`
- `## Exit Criteria`

Task template:
- `- [ ] T-### <task title>`
  - `Owner: TDD|Implementation|Infra`
  - `Maps to: US-###`
  - `DoD: ...`

---

## DoD Checklist (approval gate)
- [ ] `MVP_Scope.md` exists with clear IN/OUT and constraints
- [ ] `Product_Backlog.md` has stories with acceptance criteria and priorities
- [ ] `Sprint_1_TODO.md` maps to MVP P0 stories and is actionable
- [ ] Dependencies are explicit (no hidden sequencing)
- [ ] Telegram summary prepared (HLD-level only)

---

## Telegram Completion Message (summary-only template)

**Title:** Phase 2 complete — MVP + Sprint Plan ready

**Summary (HLD-style):**
- 🎯 MVP (P0 only): <3–5 bullets>
- 🧱 Key system implications: <2–3 bullets> (data model / APIs / bot UX / infra)
- ⚖️ Trade-offs: <1–2 bullets>
- 🚧 Blockers / Unknowns: <0–3 bullets> (carry as assumptions)

**Buttons:**
- [✅ APPROVE]
- [🔁 OTHER OPTIONS] (regen alternative MVP cuts)
- [🧾 CHANGE CONSTRAINTS] (CEO sends one message; rerun Phase 2)
- [🔍 DRILL DOWN] (show backlog + TODO excerpts)
- [🔙 GO BACK TO PHASE 1]
- [📄 VIEW DOCS] (link/paths only; optional)

---

## If REFINE / LOOP
Trigger conditions:
- CEO changes constraints (budget/timeline/region/forbidden features)
- MVP feels too big/small
- Trade-offs unacceptable

Loop behavior:
1. Update `MVP_Scope.md` first (IN/OUT + constraints)
2. Recompute backlog priorities (only impacted epics/stories)
3. Regenerate `Sprint_1_TODO.md` to match the new MVP boundary
4. Re-emit summary-only Telegram message

---

## Implementation Note (for the factory code)
When Phase 2 node runs:
1. read Phase 1 artifacts from `artifacts/<thread_id>/docs/`
2. generate and write Phase 2 artifacts to the same folder
3. emit **summary-only** message to Telegram
4. interrupt for approval