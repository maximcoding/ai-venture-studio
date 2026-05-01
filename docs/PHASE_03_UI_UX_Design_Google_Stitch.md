# Phase 3 — UI/UX Design (Google Stitch via MCP)

[Goal] Implement Phase 3 “Google Stitch via MCP” end-to-end automation in our factory repo.
[Context] Bot runs in Docker. We must generate Stitch project + screens automatically and deliver link + screenshots to Telegram. No manual copy/paste. Per-run outputs live only under artifacts/<thread_id>/.
[Repo] Use stitch-mcp (Node MCP server) as the Stitch integration. Spawn it from Python via stdio MCP client.
[Required Changes]
1) Update docs/PHASE_03_UI_UX_Design_Google_Stitch.md to exactly match the attached spec (manifest.json + optional screenshots, buttons: APPROVE DESIGN / REFINE SCREEN / GO BACK / VIEW STATUS).
2) Implement src/phase_03.py:
   - Build a single Stitch prompt from MVP_Scope + Product_Backlog
   - Spawn MCP server: STITCH_MCP_CMD + STITCH_MCP_ARGS (default: npx -y stitch-mcp)
   - Call tools: create_project → generate_screen_from_text for each P0 screen → list_screens → fetch_screen_image
   - Persist artifacts to artifacts/<thread_id>/stitch/manifest.json and screenshots to artifacts/<thread_id>/stitch/screens/
   - Return payload containing stitch_url + screenshot paths for Telegram delivery
3) Implement Telegram UX:
   - After Phase 3 completes, send stitch_url + screenshots + short summary
   - Add button REFINE SCREEN: user selects screen + instruction, regenerate only that screen, re-fetch screenshot, update manifest.json, resend screenshot
4) Docker:
   - Ensure the bot container can run node+npx and spawn stitch-mcp
   - Add env vars: GOOGLE_CLOUD_PROJECT, GOOGLE_APPLICATION_CREDENTIALS, STITCH_MCP_CMD, STITCH_MCP_ARGS
   - Mount credentials as secret (no commit)
[Constraints]
- Keep file outputs minimal: only manifest.json + optional screenshots
- Never write product outputs into factory /docs
- No Gemini / external providers required for Phase 3
[Done When]
- Running Phase 3 creates a real Stitch project and posts link + screenshots to Telegram
- REFINE SCREEN regenerates and posts updated screenshot
- manifest.json is always updated and auditable (prompt_used + stitch_url + screen_index)


## Objective
Fully automate UI generation in Google Stitch:
- Bot generates a Stitch prompt from MVP scope.
- Bot calls Stitch through MCP (no manual copy/paste).
- Bot returns: Stitch project link + screenshots in Telegram.
- CEO can request refinements per screen inside Phase 3.

## Non-Negotiables
- Works from Docker (bot runs in container).
- Uses Stitch MCP (MCP server + MCP client).
- No external paid LLM providers required for this phase.
- Telegram is the only control plane.

## Inputs (per-run)
- `artifacts/<thread_id>/docs/MVP_Scope.md`
- `artifacts/<thread_id>/docs/Product_Backlog.md`

Where:
- `<thread_id>` = LangGraph `configurable.thread_id` (Telegram session/user id)

## Primary Outputs (per-run)
Keep outputs minimal and auditable:

- `artifacts/<thread_id>/stitch/manifest.json`
  - stitch_project_id
  - stitch_url
  - screen_index (ordered P0 first)
  - prompt_used (exact text sent to Stitch)
  - design_context (if extracted)
  - exported_assets (paths to screenshots if fetched)

- `artifacts/<thread_id>/stitch/screens/*.png` (optional, if MCP can fetch images)

## How it works (automated)

### Step 1 — Build the Stitch prompt
Generate a single prompt that contains:
- App concept (1 paragraph)
- Visual style rules (colors/typography/spacing mood)
- Navigation model (tabs/stack/etc.)
- Screen list (P0 first)
- Per-screen requirements (components + states: loading/empty/error/success)

### Step 2 — Call Stitch MCP from Docker
The bot runs an MCP client that spawns the Stitch MCP server (Node) via stdio.

MCP tools used (from stitch-mcp):
- `create_project(name, description)`
- `generate_screen_from_text(projectId, text, screenName)`
- `list_screens(projectId)`
- `fetch_screen_image(projectId, screenId)`
- `extract_design_context(projectId, screenId)` (optional for style consistency)
- `fetch_screen_code(projectId, screenId)` (optional for debugging)

### Step 3 — Deliver to Telegram (review UX)
Bot sends:
- Stitch URL (clickable)
- Screenshot gallery (one message per screen or grouped)
- Short “HLD-level” summary (not the whole prompt)

Buttons:
- [✅ APPROVE DESIGN]
- [🛠️ REFINE SCREEN]
- [🔙 GO BACK TO PHASE 2]
- [📄 VIEW STATUS]

### Step 4 — Refinement loop (within Phase 3)
When CEO taps [🛠️ REFINE SCREEN]:
1) Bot asks: screen name + change request (one message).
2) Bot regenerates ONLY that screen using:
   - prior design_context (if available)
   - prior prompt constraints
3) Bot re-fetches screenshot(s)
4) Bot posts updated screenshot + keeps same Stitch project link

Repeat until approved.

## DoD (Approval Gate)
- [ ] Stitch project created and URL returned
- [ ] All P0 screens generated
- [ ] Telegram received screenshots for P0 screens (or at least confirmation + URL if screenshots unavailable)
- [ ] `manifest.json` exists with prompt_used + stitch_url + screen_index
- [ ] Refinement path works: “REFINE SCREEN → regenerate → new screenshot”

## Config
Environment (Docker):
- `GOOGLE_CLOUD_PROJECT` = GCP project id
- `GOOGLE_APPLICATION_CREDENTIALS` = path to service account json inside container
- `STITCH_MCP_CMD` = command to run MCP server (default: `npx`)
- `STITCH_MCP_ARGS` = args (default: `-y stitch-mcp`)

Notes:
- No manual Stitch steps.
- No UI files in factory `/docs`.
- Everything here is per-run under `artifacts/<thread_id>/`.