# docs/PHASE_03_UI_UX_Design_Google_Stitch.md

## Phase 3 — UI/UX Design (Google Stitch Integration)

### Objective
Produce an approved visual direction, tokenized design system, and interactive prototype using AI-powered design tools.

### Primary Outputs (per-run artifacts)
- `artifacts/<thread_id>/docs/Design_Strategy.json` — Structured strategy for Stitch
- `artifacts/<thread_id>/docs/Design_System.md` — Complete design system documentation
- `artifacts/<thread_id>/docs/Design_Tokens.json` — Design tokens (colors, typography, spacing, etc.)
- `artifacts/<thread_id>/docs/UI_Screens_List.md` — Detailed screen specifications
- `artifacts/<thread_id>/docs/Stitch_Prompt.txt` — Generated Stitch prompt for reproducibility
- `artifacts/<thread_id>/docs/Stitch_Refinement_Guide.md` — Common refinement examples
- `artifacts/<thread_id>/docs/Prototype_Link.md` — Interactive prototype URL (Stitch/Figma)
- `artifacts/<thread_id>/assets/ui/*.png` — Generated screen screenshots

Where `<thread_id>` = LangGraph configurable thread_id (Telegram user/session identifier).

### Inputs
- `artifacts/<thread_id>/docs/MVP_Scope.md` (from Phase 2)
- `artifacts/<thread_id>/docs/Product_Backlog.md` (from Phase 2)

### Workflow

#### STEP 1: Design Strategy Generation (Ollama)
Ollama analyzes MVP scope and backlog to create structured `Design_Strategy.json`:
- High-level concept (following [Stitch best practices](https://www.adosolve.co.in/post/stitch-prompt-guide))
- Vibe adjectives (influences colors, fonts, imagery)
- Target audience personas
- Color approach (specific colors OR mood-based palette)
- Typography style (playful/elegant/corporate)
- Border style (rounded/sharp/minimal)
- Image style and descriptions
- Screen-by-screen breakdown with UI/UX keywords

#### STEP 2: Stitch Prompt Construction
`StitchPromptBuilder` creates optimized prompt following article structure:
1. **High-Level Concept**: "An app for [audience] to [functionality]"
2. **Vibe Adjectives**: "A [adjective1] and [adjective2] app"
3. **Screens List**: Screen-by-screen with UI/UX keywords (navigation bar, CTA button, etc.)
4. **Theme Specifics**: Colors, fonts, borders
5. **Image Descriptions**: Style and mood alignment

#### STEP 3: Google Stitch API Call
If `GOOGLE_STITCH_ENABLED=true`:
- Calls Stitch API with structured prompt
- Receives: project_id, preview_url, screenshot URLs
- Downloads all screenshots to `assets/ui/`
- Generates `Prototype_Link.md` with real Stitch URL

If Stitch disabled or fails:
- Falls back to text-only mode
- Saves Stitch prompt for manual use
- Prototype_Link.md includes manual instructions

#### STEP 4: Telegram Delivery
CEO receives in Telegram:
- 📄 Design documentation files (Design_System.md, Design_Tokens.json, etc.)
- 🖼️ Screenshots (as photos with captions)
- 🔗 Interactive prototype link (in message or Prototype_Link.md)
- 🔘 Special Phase 3 buttons:
  - **✅ APPROVE DESIGN** — proceed to Phase 4
  - **🔁 REFINE SCREEN** — make incremental changes to specific screens
  - **🎨 CHANGE THEME** — update colors/fonts/borders across all screens
  - **🔙 GO BACK** — return to Phase 2

### Refinement Loop (Iterative Design)

Following [Stitch best practices](https://www.adosolve.co.in/post/stitch-prompt-guide):

**Best Practices:**
- Make 1-2 changes at a time (easier to measure impact)
- Be specific with screen/component names
- Use UI/UX keywords (button, header, navigation, card, CTA)
- Reference elements precisely ("primary button on sign-up form")

**Example Refinements:**
- "On homepage, add search bar to header"
- "Change primary CTA button to be larger and use brand blue"
- "Update login screen background to light gradient"

**Example Theme Changes:**
- Colors: "Change primary color to forest green" OR "Update theme to warm color palette"
- Fonts: "Use playful sans-serif font" OR "Change headings to elegant serif"
- Borders: "Make all buttons fully rounded corners"

### Configuration

Set in `.env`:
```bash
# Google Stitch Integration
GOOGLE_STITCH_API_KEY=your_api_key_here
GOOGLE_STITCH_BASE_URL=https://stitch.google.com
GOOGLE_STITCH_TIMEOUT=120
GOOGLE_STITCH_ENABLED=true  # Set to 'false' for text-only fallback
```

### Must-Define in Design
- Key screens (minimum): Auth, Home/Dashboard, Primary flow screen(s), Settings/Profile
- UI states: loading / empty / error / success
- Responsive rules (mobile, tablet, desktop breakpoints)
- Component specifications with UI/UX keywords
- Accessibility guidelines (WCAG 2.1 AA)

### DoD Checklist (Approval Gate)
- [ ] Interactive prototype link is available (Stitch preview URL)
- [ ] Screenshots of all key screens delivered to Telegram
- [ ] `Design_System.md` defines components + interaction patterns
- [ ] `Design_Tokens.json` is complete and stable
- [ ] `Design_Strategy.json` structured for Stitch integration
- [ ] Screen list covers all MVP P0 flows
- [ ] Stitch prompt saved for reproducibility/refinements

### Telegram Completion Message
Johnny Vibe sends:
- ✅ Artifacts: Design_System.md, Design_Tokens.json, Prototype_Link.md, screenshots
- 🖼️ Screens: Login.png, Dashboard.png, Settings.png (inline photos)
- 🔗 Interactive Prototype: [Stitch URL] (clickable)
- Buttons: [✅ APPROVE DESIGN] [🔁 REFINE SCREEN] [🎨 CHANGE THEME] [🔙 GO BACK TO PHASE 2] [📄 VIEW DOCS]

### Error Handling & Fallback
If Stitch API fails or is disabled:
- Phase continues with text-only artifacts
- `Prototype_Link.md` includes manual design instructions
- `Stitch_Prompt.txt` saved for manual Stitch use
- CEO can still review and approve design specifications
- No screenshots generated (manual design in Figma required)

### References
- [Stitch Prompt Guide - Best Practices](https://www.adosolve.co.in/post/stitch-prompt-guide-effective-prompting-for-better-ui-ux-designs)
- Google Stitch API Documentation
- Design Tokens Specification (W3C)
