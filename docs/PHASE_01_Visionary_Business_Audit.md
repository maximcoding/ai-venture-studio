# docs/PHASE_01_Visionary_Business_Audit.md

## Phase 1 — Visionary & Business Audit

### Objective
Turn a raw idea into a viable, bounded business concept with:
- clear USP
- monetization for v1
- top risks + mitigations
- basic compliance posture (privacy/data handling)

This phase must support a **Telegram-first review + edit loop** (phone-first, no file downloads required).

---

## Inputs (from CEO via Telegram)
- Idea (1–3 paragraphs)
- Constraints:
  - budget
  - timeline
  - region/jurisdiction
  - must-have integrations
  - forbidden features
- Optional: links, competitor examples, notes

---

## Primary Outputs (Run Artifacts)
These are **per-run** documents stored in PostgreSQL and editable in Telegram UX.
Filesystem export under `artifacts/<thread_id>/...` is **optional debug cache**.

**Canonical (DB) docs:**
- `BUSINESS_LOGIC` (markdown)
- `ASSUMPTIONS` (markdown)

**Optional filesystem export (debug only):**
- `artifacts/<thread_id>/docs/Business_Logic.md`
- `artifacts/<thread_id>/docs/Assumptions.md`

Where:
- `<thread_id>` = `user_<telegram_user_id>` (derived from Telegram user id)
- `thread_id` is also passed as LangGraph `configurable.thread_id`

---

## Required Content — BUSINESS_LOGIC (Markdown)
Must include these sections (headings exact):

- `## Core Concept (One Sentence)`
- `## Target Audience`
- `## Primary Pain`
- `## USP (Why Users Choose Us)`
- `## Monetization (V1)`
- `## Competitive Snapshot`
- `## Risk Matrix (Top 5)`
  - For each risk: `Risk / Impact / Likelihood / Mitigation or Pivot`
- `## Compliance Notes`
  - data collected (high level)
  - storage + retention intent
  - user rights posture (delete/export)
  - security stance (secrets, access control)
- `## Delivery Surface`
  - > This is a hard constraint. Phase 4 MUST use it to pick the architecture shape.
  - > Phase 2 MUST use it to shape the backlog (UI vs API vs jobs).
  - `### Mode`
    - Choose ONE: `auto`, `mobile`, `web`, `api`, `automation`
    - **mode:** auto
  - `### Auto resolution rules (if mode=auto)`
    - If Phase 3 (Stitch) is enabled for this run → `web`
    - Else → `api`
  - `### Notes / Constraints`
    - Platforms: TBD (iOS/Android, browser, server-only, etc.)
    - Forbidden surfaces: TBD
    - Must-have integrations impacting surface: TBD

---

## Required Content — ASSUMPTIONS (Markdown)
Must include these sections:

- `## Unknowns`
- `## What We Must Verify Later`
- `## Decisions Made With Limited Info`

---

## Execution Contract (What Phase 1 MUST do in code)

### 1) Identify run + thread_id
- Extract Telegram user id from incoming update.
- Set:
  - `thread_id = f"user_{telegram_user_id}"`
- Use this as:
  - DB `runs.thread_id`
  - LangGraph `configurable.thread_id`

### 2) Ensure run exists
On first message from a user (or when starting a run):
- Create `runs` row if not exists:
  - `thread_id`
  - `current_phase = 1`
  - `status = RUNNING`
  - `needs_refine = false` (optional)

### 3) Generate docs
Phase 1 agent logic produces:
- BUSINESS_LOGIC markdown
- ASSUMPTIONS markdown

Store as documents in DB (revisions model):
- Upsert `documents` rows (doc_type BUSINESS_LOGIC / ASSUMPTIONS)
- Insert `document_revisions` rows with `author=AGENT`, `content_markdown`

Optional:
- store short `summary_json` for chat summary

### 4) Deliver Phase 1 summary in Telegram
Send a concise message (<= ~20 lines) containing:
- Core concept (1 sentence)
- Target audience (1 line)
- Monetization (1 line)
- Top 3 risks (bullets)
- Next step: “Phase 2”

Then send buttons (inline keyboard):
- `📄 OPEN DOCS`
- `🔁 REFINE`
- `✅ APPROVE`
- `🔁 OTHER OPTIONS`

### 5) Review & edit loop (phone-first)
The CEO must be able to review/edit inside Telegram UX.

#### UX option A (preferred): Telegram Web App mini-editor
- `📄 OPEN DOCS` opens Telegram Web App (phone-first).
- Web App provides:
  - docs list for the active run
  - markdown editor per doc
  - save → creates new revision in DB
  - optional preview + minimal diff indicator

Auth:
- verify Telegram `initData` server-side
- derive `telegram_user_id` from initData
- enforce access to docs only for that user/thread_id

On SAVE:
- create revision
- set `needs_refine=true` (or enqueue refine event)
- bot sends: “Saved. Tap REFINE to re-run Phase 1 using the new doc.”

#### UX option B (fallback): Chat paging viewer + edit page
If Web App not available, implement paging in chat:

- `OPEN DOCS` shows doc list and opens selected doc with paging.
- Page size <= 3500 chars (Telegram safe chunk).
- Navigation buttons:
  - `⬅️ Prev` `➡️ Next`
  - `✏️ Edit`
  - `🔙 Back`

Edit:
- on `✏️ Edit`, bot asks user to reply with full new page text
- bot applies patch to doc content (rebuilds doc)
- saves as new revision in DB
- returns to viewer

**Note:** Option B exists only as fallback. CEO default UX should be Web App.

### 6) REFINE behavior (explicit intent)
When CEO taps `🔁 REFINE`:
- Bot asks for one message: “Write changes as bullets (or send voice).”
- Save that message as `phase_events` record `REFINE_REQUEST`
- Mark run as `needs_refine=true`
- Orchestrator re-runs Phase 1 using:
  - latest doc revisions
  - the refine request message as additional constraints

### 7) OTHER OPTIONS behavior (alternatives)
When CEO taps `🔁 OTHER OPTIONS`:
- Phase 1 generates **3 alternative variants** (business model / audience / monetization)
- Store them as either:
  - a separate doc type `PHASE1_ALTERNATIVES` (markdown), OR
  - 3 variants in `summary_json` + also persisted markdown

Bot returns:
- short list of 3 variants
- buttons:
  - `✅ PICK A (1/2/3)`
  - `📄 OPEN DOCS`
  - `🔁 REFINE`

Picking a variant:
- updates BUSINESS_LOGIC revision accordingly
- keeps trace in `phase_events`

### 8) APPROVE behavior (gate)
When CEO taps `✅ APPROVE`:
- Phase 1 DoD must be satisfied (see checklist).
- If OK:
  - set `runs.current_phase = 2`
  - set status for Phase 1 as `APPROVED`
  - proceed to Phase 2

If not OK:
- bot replies with missing checklist items + offers `OPEN DOCS` and `REFINE`.

---

## DoD Checklist (Approval Gate)
Checklist is stored per run and rendered in Telegram (toggle UI).

### Checklist items
- [ ] BUSINESS_LOGIC exists (latest revision non-empty)
- [ ] ASSUMPTIONS exists (latest revision non-empty)
- [ ] Risk Matrix contains 5 risks with mitigation/pivot each
- [ ] Phase 1 summary delivered to CEO in Telegram

### Telegram checklist UX (chat)
- Render checklist text with `☐ / ✅`
- Provide buttons `[1] [2] [3] [4]` to toggle items
- Re-render message via `editMessageText()` on toggle
- Store checklist state in DB (preferred) or JSON file (debug)

---

## Data Model (minimum; DB is SSOT)

### runs
- run_id (uuid)
- thread_id (text, unique)
- current_phase (int)
- status (text: RUNNING / NEEDS_REFINE / APPROVED)
- created_at, updated_at

### documents
- document_id (uuid)
- run_id (uuid)
- doc_type (enum: BUSINESS_LOGIC, ASSUMPTIONS, PHASE1_ALTERNATIVES)
- title (text)

### document_revisions
- revision_id (uuid)
- document_id (uuid)
- created_at
- author (enum: AGENT, CEO)
- content_markdown (text)
- summary_json (jsonb, optional)

### phase_events
- event_id (uuid)
- run_id (uuid)
- phase (int = 1)
- event_type (GENERATED / EDITED / REFINE_REQUEST / APPROVED / OTHER_OPTIONS / PICKED_VARIANT)
- payload_json (jsonb)

---

## Telegram Completion Message (Template)
After Phase 1 generates initial docs:

✅ Artifacts (in DB): BUSINESS_LOGIC, ASSUMPTIONS  
⚠️ Top Risks:
- <risk 1>
- <risk 2>
- <risk 3>

➡️ Next: Phase 2 (Backlog + MVP cut)

Buttons:
- [📄 OPEN DOCS]
- [🔁 REFINE]
- [✅ APPROVE]
- [🔁 OTHER OPTIONS]

---

## Failure / Loop Rules
- If CEO edits docs or submits refine request:
  - set run to NEEDS_REFINE
  - re-run Phase 1 with latest revisions
- If @Web verification is configured:
  - re-run only for claims changed or high-risk claims
- Phase 1 should never block on filesystem exports.
