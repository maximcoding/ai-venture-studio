# Phase 4 — System Architecture & HDL

## Objective
Produce the technical blueprint aligned to:
- approved MVP scope
- approved design (if any)
- the selected Delivery Surface (mobile/web/api/automation)

This phase MUST output stable run artifacts that Phase 6 (TDD) and Phase 7 (Implementation) can consume.

---

## Inputs (per-run artifacts)
Required:
- `artifacts/<thread_id>/docs/MVP_Scope.md`
- `artifacts/<thread_id>/docs/Business_Logic.md`

Optional (only if present / Phase 3 used):
- `artifacts/<thread_id>/docs/Design_Tokens.json`
- `artifacts/<thread_id>/docs/Design_System.md`

Where `<thread_id>` = LangGraph configurable thread id (Telegram run identifier).

---

## Step 0 — Determine Product Shape (non-negotiable)
Source of truth:
- Read `artifacts/<thread_id>/docs/Business_Logic.md` → section `## Delivery Surface`

### Resolution rules
1) If `mode` is one of: `mobile | web | api | automation` → use it.
2) If `mode=auto`:
   - if Design artifacts exist (Design_Tokens.json OR Design_System.md) → `web`
   - else → `api`

The resulting value is **Product Shape**.

Write the resolved value into:
- `System_Architecture.md` → `## Product Shape`
- `Roadmap.md` → `## Build Target`

No further debate in later phases.

---

## How (Cursor workflow)
- **Cursor Plan**: pick architecture style and boundaries based on Product Shape + MVP.
- **Cursor Chat**: generate the four run artifacts (below).
- **Cursor @Web** (optional): only to validate hard constraints (framework limits, hosting limits, auth constraints).

---

## Primary Outputs (per-run artifacts)
- `artifacts/<thread_id>/docs/HDL_Business_Flows.md`
- `artifacts/<thread_id>/docs/System_Architecture.md`
- `artifacts/<thread_id>/docs/Data_Model.md`
- `artifacts/<thread_id>/docs/Roadmap.md`

---

## Output requirements (what each file MUST contain)

### 1) HDL_Business_Flows.md
Purpose: executable clarity for TDD and orchestration.

Must include:
- `## Product Shape` (resolved)
- `## MVP P0 Flows (End-to-End)`
  - numbered flows (P0 only)
  - each flow: Trigger → Steps → Data touched → Outputs
- `## Error / Edge Cases (P0)`
- `## Non-Goals (Explicit OUT for MVP)`

Shape-specific guidance:
- **mobile/web:** flows include UI action → API call → DB write/read → UI response
- **api:** flows include endpoint → validation → service → DB → response
- **automation:** flows include schedule/trigger → job steps → retries → outputs → logs

---

### 2) System_Architecture.md
Purpose: boundaries + components + integration contract.

Must include:
- `## Product Shape` (resolved)
- `## Architecture Style`
  - monolith/modular/services (pick one and commit)
- `## Components`
  - list components with responsibilities
- `## AuthN/AuthZ`
  - who authenticates, tokens, session model
- `## Storage`
  - DB choice and why (minimal)
- `## Integrations`
  - external APIs/services and failure modes
- `## Observability`
  - logs/metrics/traces baseline
- `## Security Baseline`
  - secrets handling, least privilege, no keys in repo

Shape-specific component patterns:
- **mobile/web:** client + API + DB (+ optional worker)
- **api:** API + DB (+ optional worker)
- **automation:** worker/job runner + DB (+ optional API only if needed)

---

### 3) Data_Model.md
Purpose: schema-level clarity for Phase 6 tests and Phase 7 implementation.

Must include:
- `## Entities (MVP)`
  - each entity: fields + constraints
- `## Relationships`
- `## Indexing (only what’s needed)`
- `## Migrations Strategy`
  - how schema changes are applied
- `## Retention / Lifecycle`
  - what gets deleted, archived, kept

Shape-specific note:
- **automation** can use minimal state tables + run logs; avoid over-modeling.

---

### 4) Roadmap.md
Purpose: sequence that makes implementation deterministic.

Must include:
- `## Build Target` (Product Shape resolved)
- `## Sprint 1 (P0 only)`
  - tasks ordered by dependency
- `## Sprint 2+ (P1/P2)`
- `## Key Risks + Mitigations`
- `## “Stop Conditions”`
  - what blocks release / what can be deferred

Shape-specific Sprint 1 focus:
- **mobile/web:** API skeleton + core flow + minimal UI shell (if UI exists)
- **api:** core endpoints + auth + persistence + tests
- **automation:** first runnable job + idempotency + retries + persistence + tests

---

## DoD Checklist (Approval Gate)
- [ ] `HDL_Business_Flows.md` covers all MVP P0 journeys end-to-end
- [ ] `System_Architecture.md` contains Product Shape + boundaries + auth + storage + integrations
- [ ] `Data_Model.md` includes entities + relations + migration strategy
- [ ] `Roadmap.md` provides ordered Sprint 1 tasks and risks

---

## Telegram completion message (template)
- ✅ Artifacts: HDL_Business_Flows.md, System_Architecture.md, Data_Model.md, Roadmap.md
- 🧱 Product Shape: <mobile/web/api/automation>
- 🧭 Sprint 1: <3–5 bullets>
- Buttons: [✅ APPROVE ARCHITECTURE] [🔁 OTHER TECH STACK] [🔙 GO BACK] [📄 OPEN DOCS]