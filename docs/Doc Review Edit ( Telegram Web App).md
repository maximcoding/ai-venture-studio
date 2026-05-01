# Doc Review & Edit (Telegram Web App) — Factory Feature Spec (v2)

## 0) Goal
Phone-first review/edit loop for the CEO **inside Telegram**:

- Open generated phase docs in a Telegram Web App (no downloads).
- Edit as a mini-editor.
- Save → create revision → trigger **refine re-run** of the current phase.
- Approve → advance to next phase.

This is **factory control-plane UI** (platform feature), not the end-product UI.

---

## 1) Where this is built (Factory SDLC)
This feature must exist before product-run Phase 1 becomes usable.

Build in:
- **Factory Phase 6 (TDD):** tests for auth, docs CRUD, revisions, refine/approve events.
- **Factory Phase 7 (Implementation):** Web App + API + bot wiring + orchestrator hooks.
- **Factory Phase 8 (Visual QA):** optional Playwright screenshots + basic UX regression.

Used by:
- **Product-run Phase 1+** (every phase that generates docs).

---

## 2) CEO UX (Telegram, phone-first)

### 2.1 Telegram buttons shown after a phase
- **📄 OPEN DOCS** (opens Web App)
- **✅ APPROVE**
- **🔁 REFINE**
- **🔙 GO BACK** (time-machine)

### 2.2 Web App screens (inside Telegram)
#### Screen A — Docs list (per run)
- List of doc types for this run (P0 first):
  - BUSINESS_LOGIC
  - ASSUMPTIONS
  - PRODUCT_BACKLOG
  - MVP_SCOPE
  - SPRINT_1_TODO
  - STITCH_PROMPT
  - etc.
- Each item shows:
  - title
  - last updated
  - status: Draft / Updated / Approved

Actions:
- tap doc → editor
- back to chat

#### Screen B — Doc editor (markdown)
Layout:
- Top bar: doc name + status + last updated
- Main: markdown editor (textarea / CodeMirror)
- Optional side/bottom: short summary panel (auto-generated)

Actions:
- **💾 SAVE**
- **🧾 PREVIEW**
- **↩️ DISCARD**
- (Optional) **✅ APPROVE DOC** (shortcut; still must satisfy phase DoD rules)

On SAVE:
- create new revision
- mark run as `needs_refine=true`
- optionally auto-trigger refine re-run (configurable)

#### Screen C — Diff confirm (optional)
After SAVE:
- “changed lines count” or small diff
- CONFIRM / CANCEL

---

## 3) Refine mechanics (source of truth behavior)

### 3.1 Basic rule
Edits are **phase inputs**. When CEO saves a doc:
- SSOT updated (latest revision becomes canonical for that doc)
- run is marked `needs_refine=true`
- orchestrator re-runs **current phase** using:
  - latest doc revisions
  - optional refinement message (if provided)

### 3.2 REFINE button (in chat)
When CEO taps **🔁 REFINE**:
- bot asks for **one message** (bullets or voice)
- saved as `REFINE_REQUEST`
- triggers phase re-run (even if docs were not edited)

### 3.3 Auto vs manual refine
Config:
- `AUTO_REFINE_ON_SAVE=true|false`
- If `true`: saving a doc immediately enqueues refine
- If `false`: saving only sets `needs_refine=true`; user presses REFINE to run

---

## 4) Storage model (no “download .md” UX)

### 4.1 Canonical SSOT
**PostgreSQL** is canonical for all run docs + revisions.

Filesystem exports are optional:
- used for debug/backups only
- never required for CEO workflow

Optional export path (debug only):
- `artifacts/<thread_id>/docs/<doc_type>.md`

---

## 5) Data model (minimal)

### 5.1 Runs
- `runs`
  - `run_id` (uuid)
  - `thread_id` (string; default `user_<telegram_user_id>`)
  - `current_phase` (int)
  - `status` (RUNNING|WAITING_APPROVAL|REFINING|DONE)
  - `needs_refine` (bool)

> Note: if later you want multiple runs per user, keep `thread_id=user_<id>` and distinguish by `run_id`.

### 5.2 Docs + revisions
- `documents`
  - `document_id` (uuid)
  - `run_id`
  - `doc_type` (enum)
  - `title`
  - `status` (DRAFT|APPROVED)
- `document_revisions`
  - `revision_id` (uuid)
  - `document_id`
  - `created_at`
  - `author` (CEO|AGENT)
  - `content_markdown` (text)
  - `summary_json` (optional)

### 5.3 Phase events (audit + triggers)
- `phase_events`
  - `event_id` (uuid)
  - `run_id`
  - `phase`
  - `event_type` (GENERATED|EDITED|APPROVED|REFINE_REQUEST|GO_BACK)
  - `payload_json`

---

## 6) Security (Telegram Web App auth)
Web App must accept requests only from Telegram.

Use Telegram Web App `initData` verification:
- Web App receives `initData`
- Backend verifies signature using bot token
- Backend derives:
  - `telegram_user_id`
  - default `thread_id = user_<telegram_user_id>`
- Access control:
  - user can only access runs bound to their `thread_id` (unless admin mode exists)

No cookies required. Stateless JWT optional.

---

## 7) API (minimum contract)

### Web App bootstrap
- `GET /api/runs/active`
  - auth: Telegram initData
  - returns: active run + docs list

### Docs list
- `GET /api/runs/{run_id}/docs`
  - returns: doc list + latest revision meta

### Read doc (latest)
- `GET /api/docs/{document_id}`
  - returns: latest markdown + meta

### Save doc (new revision)
- `POST /api/docs/{document_id}/revisions`
  - body: `{ content_markdown: string }`
  - side-effects:
    - create revision
    - phase_event EDITED
    - set `needs_refine=true`
    - if `AUTO_REFINE_ON_SAVE=true` → enqueue refine

### Refine request
- `POST /api/runs/{run_id}/refine`
  - body: `{ message: string }`
  - side-effects:
    - phase_event REFINE_REQUEST
    - enqueue refine

### Approve phase
- `POST /api/runs/{run_id}/approve`
  - body: `{ phase: number }`
  - side-effects:
    - phase_event APPROVED
    - orchestrator advances

### Go back (time machine)
- `POST /api/runs/{run_id}/go-back`
  - body: `{ phase: number }`
  - side-effects:
    - phase_event GO_BACK
    - orchestrator rewinds checkpoint/state

---

## 8) Bot integration (Aiogram)

### OPEN DOCS button (primary)
Use Telegram Web App URL:
- `${WEBAPP_BASE_URL}/tg?run_id=<run_id>`
Telegram passes initData automatically.

Implementation:
- `InlineKeyboardButton(web_app=WebAppInfo(url=...))`

### VIEW DOCS in chat (fallback)
- show **short summary only**
- include “Open in Web App” button
- do not send full docs as files by default

---

## 9) Orchestrator integration (LangGraph)
On these triggers:
- EDITED (doc save)
- REFINE_REQUEST
the orchestrator must:
- keep current phase
- re-run phase node with latest doc revisions as inputs
- then interrupt to CEO again (approve/refine/go-back/open-docs)

---

## 10) DoD (Definition of Done)

### Web App
- [ ] Opens inside Telegram on phone
- [ ] Lists docs for active run
- [ ] Opens editor and edits markdown
- [ ] SAVE creates revision in DB
- [ ] Telegram initData verification enforced

### Bot
- [ ] OPEN DOCS opens Web App
- [ ] REFINE accepts one message and triggers refine
- [ ] APPROVE advances only if phase DoD is satisfied

### Orchestrator
- [ ] On EDITED/REFINE_REQUEST current phase re-runs
- [ ] Revision history retained
- [ ] Latest revision used as input for next phases

---

## 11) Testing (minimum)
- [ ] Unit: Telegram initData verification
- [ ] Unit: docs CRUD + revisions
- [ ] Integration: edit/refine triggers re-run
- [ ] E2E (optional): Playwright open → edit → save

---

## 12) Config
- `WEBAPP_BASE_URL`
- `TELEGRAM_BOT_TOKEN`
- `DATABASE_URL`
- `AUTO_REFINE_ON_SAVE=true|false`
- `CORS_ALLOWED_ORIGINS`

---

# Product-run Phase 1 — Visionary & Business Audit (v2)

## Objective
Turn CEO idea into bounded business concept:
- USP
- monetization for v1
- top risks + mitigations
- basic compliance posture

Phase 1 must produce **run docs in DB** and expose **review/edit loop** via Web App.

---

## Inputs (from CEO)
- Idea (1–3 paragraphs)
- Constraints: budget, timeline, region, must-have integrations, forbidden features
- Optional: links, competitors, notes

---

## Primary Outputs (Run Docs in DB)
Doc types (DB SSOT):
- `BUSINESS_LOGIC`
- `ASSUMPTIONS`

Optional debug export only:
- `artifacts/<thread_id>/docs/BUSINESS_LOGIC.md`
- `artifacts/<thread_id>/docs/ASSUMPTIONS.md`

---

## Required content — BUSINESS_LOGIC
Must include:
- Core Concept (one sentence)
- Target Audience + Primary Pain
- USP
- Monetization (v1)
- Competitive snapshot (high-level)
- Risk Matrix (Top 5): risk → impact → likelihood → mitigation/pivot
- Compliance notes (data posture)

## Required content — ASSUMPTIONS
Must include:
- Unknowns
- What to verify later
- Decisions made with limited info

---

## Runtime responsibilities (what Phase 1 does in code)
- Generate docs (LLM-backed or template placeholders if LLM not wired yet)
- Persist docs to DB (create/update documents + new revisions)
- Create phase_event GENERATED
- Send Telegram summary (<= 20 lines) + buttons:
  - 📄 OPEN DOCS
  - ✅ APPROVE
  - 🔁 REFINE
  - 🔙 GO BACK

---

## Phase 1 DoD gate (checkboxes in Telegram)
- [ ] BUSINESS_LOGIC exists
- [ ] ASSUMPTIONS exists
- [ ] Risk Matrix has 5 actionable mitigations/pivots
- [ ] Summary sent

Implementation note:
- checklist state stored in DB (recommended) or as run metadata.

---