"""Stub nodes for the 10 phases. Each produces artifacts and then waits for approval."""

import logging
from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt

from src.graph.state import PhaseState

logger = logging.getLogger(__name__)

# Phase personas for consistent messaging
PHASE_PERSONA_MESSAGES = {
    1: "🍎 <b>Steve Bobs</b>\n\nОтличная идея! Я создал бизнес-анализ.\nИзучи документы и дай знать, готов ли двигаться дальше.",
    2: "🥗 <b>Smarty Vegan</b>\n\nSteve передал мне эстафету! User stories и MVP scope созданы.\nВсё по методологии — чисто и понятно.",
    3: "🎨 <b>Johnny Vibe</b>\n\nДизайн готов! Каждый пиксель на своём месте.\nЭто будет выглядеть потрясающе.",
    4: "⚙️ <b>Linus Codevalds</b>\n\nАрхитектура спроектирована. Система будет масштабироваться.\nПроверь техническую документацию.",
    5: "💻 <b>Dave Railsman</b>\n\nКод написан! Чистый, тестируемый, готовый к деплою.\nПосмотри что получилось.",
    6: "☁️ <b>Kelly Cloudtower</b>\n\nИнфраструктура готова! Kubernetes, мониторинг, автодеплой.\nПродукт готов к запуску.",
    7: "☁️ <b>Kelly Cloudtower</b>\n\nТесты пройдены! Багов не найдено.\nМожем уверенно двигаться дальше.",
    8: "🔐 <b>Bruce Securer</b>\n\nSecurity audit завершён. Все уязвимости закрыты.\nПродукт защищён.",
    9: "📈 <b>Andy Chain</b>\n\nАналитика настроена! Метрики собираются.\nГотовы к запуску.",
    10: "📈 <b>Andy Chain</b>\n\n🎉 Поздравляю! Продукт готов к production!\n\nВся команда AI Dream Team поработала на отлично.\nТеперь твоя очередь — завоёвывай рынок!",
}

PHASE_NAMES = [
    "visionary_business_audit",
    "product_management_backlog_mvp",
    "ui_ux_design",
    "system_architecture_hdl",
    "project_initialization",
    "tdd",
    "implementation",
    "visual_qa_patch_loops",
    "guardrails",
    "devops_growth_sre",
]


def phase_node(phase_num: int):
    """Return a node that runs phase N, then interrupts for Telegram approval."""

    def _node(state: PhaseState, config: RunnableConfig) -> dict[str, Any]:
        thread_id = config.get("configurable", {}).get("thread_id", "default")
        logger.info("phase_%d_start", phase_num, extra={"phase": phase_num, "thread_id": thread_id})
        # Stub: in real impl, produce artifacts under artifacts/<thread_id>/docs/ and persist
        # (thread_id from config["configurable"]["thread_id"])
        # interrupt() pauses; on resume, returns Command(resume=...) value
        persona_message = PHASE_PERSONA_MESSAGES.get(
            phase_num, f"Phase {phase_num} complete. Approve in Telegram to continue."
        )
        response = interrupt(
            {
                "phase": phase_num,
                "phase_name": PHASE_NAMES[phase_num - 1],
                "message": persona_message,
            }
        )
        approved = response.get("approved", False) if isinstance(response, dict) else bool(response)
        return {
            "current_phase": phase_num,
            "approved": approved,
        }

    _node.__name__ = f"phase_{phase_num}"
    return _node


def phase_1(state: PhaseState, config: RunnableConfig) -> dict[str, Any]:
    """Phase 1 — Visionary & Business Audit. AI-powered analysis using Ollama."""
    from pathlib import Path

    import requests

    from src.core.config import config as app_config

    # Extract thread_id and CEO prompt
    thread_id = config.get("configurable", {}).get("thread_id", "default")
    ceo_prompt = state.get("ceo_prompt", "")
    
    if not ceo_prompt:
        logger.error("phase_1_no_prompt", extra={"thread_id": thread_id})
        raise ValueError("CEO prompt is required for Phase 1 analysis")

    artifacts_dir = Path(f"artifacts/{thread_id}/docs")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Create analysis prompt
    analysis_prompt = f"""You are a startup advisor conducting Phase 1 business analysis.

CEO's Idea:
{ceo_prompt}

Task: Analyze this business idea and generate TWO structured documents:

1. **Business_Logic.md** with:
   - Core Concept (one sentence)
   - Target Audience (who + primary pain)
   - USP (why choose this over alternatives)
   - Monetization Strategy (first version revenue model)
   - Competitive Landscape (high-level snapshot)
   - Risk Matrix (5 top risks with Likelihood/Impact/Mitigation)
   - Compliance & Privacy (data handling, GDPR, security requirements)

2. **Assumptions.md** with:
   - Unknowns to Verify (3-5 bullet points)
   - Dependencies (external factors)
   - Technical Assumptions (platform/stack to validate)
   - Market Assumptions (audience/demand to verify)

Requirements:
- Be specific and actionable
- Risk Matrix must have real risks with H/M/L ratings
- Focus on MVP viability, not perfection
- Compliance notes must address data handling

Output format: Return TWO markdown documents separated by "---DOCUMENT_SEPARATOR---"
First document: Business_Logic.md content
Second document: Assumptions.md content"""

    logger.info("phase_1_calling_ollama", extra={"thread_id": thread_id, "model": app_config.OLLAMA_MODEL})

    # Call Ollama API
    try:
        response = requests.post(
            f"{app_config.OLLAMA_BASE_URL}/api/chat",
            json={
                "model": app_config.OLLAMA_MODEL,
                "messages": [{"role": "user", "content": analysis_prompt}],
                "stream": False,
            },
            timeout=app_config.OLLAMA_TIMEOUT,
        )
        response.raise_for_status()
        
        # Extract content from Ollama response
        analysis_text = response.json()["message"]["content"]
        
        # Split into two documents
        if "---DOCUMENT_SEPARATOR---" in analysis_text:
            business_logic, assumptions = analysis_text.split("---DOCUMENT_SEPARATOR---", 1)
        else:
            # Fallback: try to split by "# Assumptions"
            parts = analysis_text.split("# Assumptions", 1)
            business_logic = parts[0].strip()
            assumptions = "# Assumptions" + parts[1].strip() if len(parts) > 1 else ""
        
        # Clean up and ensure proper markdown headers
        business_logic = business_logic.strip()
        if not business_logic.startswith("# Business Logic"):
            business_logic = "# Business Logic\n\n" + business_logic
        
        assumptions = assumptions.strip()
        if not assumptions.startswith("# Assumptions"):
            assumptions = "# Assumptions & Unknowns\n\n" + assumptions
        
        # Write artifacts
        (artifacts_dir / "Business_Logic.md").write_text(business_logic, encoding="utf-8")
        (artifacts_dir / "Assumptions.md").write_text(assumptions, encoding="utf-8")
        
        logger.info(
            "phase_1_ai_analysis_complete",
            extra={
                "thread_id": thread_id,
                "artifacts_dir": str(artifacts_dir),
                "prompt_length": len(ceo_prompt),
                "response_length": len(analysis_text),
            },
        )
    except Exception as e:
        logger.exception("phase_1_ai_failed", extra={"thread_id": thread_id, "error": str(e)})
        raise

    # Then continue with interrupt logic
    artifact_files = [
        str(artifacts_dir / "Business_Logic.md"),
        str(artifacts_dir / "Assumptions.md"),
    ]
    response = interrupt(
        {
            "phase": 1,
            "phase_name": "visionary_business_audit",
            "message": PHASE_PERSONA_MESSAGES[1],
            "artifact_files": artifact_files,
        }
    )
    approved = response.get("approved", False) if isinstance(response, dict) else bool(response)
    return {"current_phase": 1, "approved": approved}


def phase_2(state: PhaseState, config: RunnableConfig) -> dict[str, Any]:
    """Phase 2 — Product Management (Backlog & MVP). AI-powered analysis using Ollama."""
    import requests
    from pathlib import Path
    from src.core.config import config as app_config

    thread_id = config.get("configurable", {}).get("thread_id", "default")
    logger.info("phase_2_start_ai", extra={"phase": 2, "thread_id": thread_id})

    # Prepare artifacts directory
    artifacts_dir = Path("artifacts") / thread_id / "docs"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Read Phase 1 artifacts
    business_logic_path = artifacts_dir / "Business_Logic.md"
    assumptions_path = artifacts_dir / "Assumptions.md"

    try:
        business_logic = business_logic_path.read_text(encoding="utf-8")
        assumptions = assumptions_path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        logger.error("phase_2_missing_input", extra={"thread_id": thread_id, "error": str(e)})
        raise ValueError(f"Phase 1 artifacts not found: {e}")

    # Construct prompt for Ollama
    analysis_prompt = f"""You are Smarty Vegan, a world-class Product Manager.

You have been given the following business analysis:

---BUSINESS LOGIC---
{business_logic}

---ASSUMPTIONS---
{assumptions}

Your task is to create 3 documents:

1. **Product_Backlog.md** - A complete product backlog with:
   - User personas
   - User stories in format: "As a [persona], I want [goal], so that [benefit]"
   - Acceptance criteria for each story
   - Priority (P0/P1/P2)
   - Dependencies between stories

2. **MVP_Scope.md** - A clear MVP boundary with:
   - IN SCOPE: Features that MUST be in MVP (justify each)
   - OUT OF SCOPE: Features postponed to v2+ (justify each)
   - Success metrics for MVP
   - Technical constraints
   - Timeline assumptions

3. **Sprint_1_TODO.md** - Concrete engineering tasks for first sprint:
   - Break MVP stories into specific technical tasks
   - Each task should be actionable (< 1 day of work)
   - Include dependencies and order
   - Separate by: Backend, Frontend, DevOps, Testing

Generate all 3 documents in markdown format.

IMPORTANT: Separate each document with the exact marker:
---DOCUMENT_SEPARATOR---

Order: Product_Backlog.md, then MVP_Scope.md, then Sprint_1_TODO.md"""

    # Call Ollama (Phase 2 generates 3 documents - needs more time)
    try:
        response = requests.post(
            f"{app_config.OLLAMA_BASE_URL}/api/chat",
            json={
                "model": app_config.OLLAMA_MODEL,
                "messages": [{"role": "user", "content": analysis_prompt}],
                "stream": False,
            },
            timeout=180,  # 3 minutes for Phase 2 (generates 3 documents)
        )
        response.raise_for_status()
        result = response.json()
        full_text = result["message"]["content"]
    except Exception as e:
        logger.exception("phase_2_ollama_failed", extra={"thread_id": thread_id, "error": str(e)})
        raise

    # Parse the 3 documents
    try:
        # Try primary separator first
        if "---DOCUMENT_SEPARATOR---" in full_text:
            parts = full_text.split("---DOCUMENT_SEPARATOR---")
            if len(parts) >= 3:
                backlog = parts[0].strip()
                mvp_scope = parts[1].strip()
                sprint_todo = parts[2].strip()
            else:
                logger.warning(
                    "phase_2_insufficient_separators",
                    extra={"thread_id": thread_id, "parts_count": len(parts)},
                )
                # Fallback: use whatever we have
                backlog = parts[0].strip() if len(parts) > 0 else full_text
                mvp_scope = parts[1].strip() if len(parts) > 1 else "# MVP Scope\n\nGeneration incomplete."
                sprint_todo = parts[2].strip() if len(parts) > 2 else "# Sprint 1 TODO\n\nGeneration incomplete."
        else:
            # Fallback: try to split by markdown headers
            logger.warning(
                "phase_2_no_separator_found",
                extra={"thread_id": thread_id, "text_length": len(full_text)},
            )
            
            # Try to extract by detecting section headers
            import re
            # Look for "# Product Backlog", "# MVP Scope", "# Sprint"
            backlog_match = re.search(r"#+ Product[_ ]?Backlog[\s\S]*?(?=(?:#+ MVP|$))", full_text, re.IGNORECASE)
            mvp_match = re.search(r"#+ MVP[_ ]?Scope[\s\S]*?(?=(?:#+ Sprint|$))", full_text, re.IGNORECASE)
            sprint_match = re.search(r"#+ Sprint[_ ]?1[_ ]?TODO[\s\S]*", full_text, re.IGNORECASE)
            
            backlog = backlog_match.group(0).strip() if backlog_match else f"# Product Backlog\n\n{full_text}"
            mvp_scope = mvp_match.group(0).strip() if mvp_match else "# MVP Scope\n\nGeneration incomplete."
            sprint_todo = sprint_match.group(0).strip() if sprint_match else "# Sprint 1 TODO\n\nGeneration incomplete."

        # Write artifacts
        (artifacts_dir / "Product_Backlog.md").write_text(backlog, encoding="utf-8")
        (artifacts_dir / "MVP_Scope.md").write_text(mvp_scope, encoding="utf-8")
        (artifacts_dir / "Sprint_1_TODO.md").write_text(sprint_todo, encoding="utf-8")

        logger.info(
            "phase_2_artifacts_written",
            extra={
                "thread_id": thread_id,
                "backlog_len": len(backlog),
                "mvp_len": len(mvp_scope),
                "sprint_len": len(sprint_todo),
            },
        )
    except Exception as e:
        logger.exception("phase_2_parse_failed", extra={"thread_id": thread_id, "error": str(e)})
        raise

    # Then continue with interrupt logic
    artifact_files = [
        str(artifacts_dir / "Product_Backlog.md"),
        str(artifacts_dir / "MVP_Scope.md"),
        str(artifacts_dir / "Sprint_1_TODO.md"),
    ]
    response = interrupt(
        {
            "phase": 2,
            "phase_name": "product_management_backlog_mvp",
            "message": PHASE_PERSONA_MESSAGES[2],
            "artifact_files": artifact_files,
        }
    )
    approved = response.get("approved", False) if isinstance(response, dict) else bool(response)
    return {"current_phase": 2, "approved": approved}


def phase_3(state: PhaseState, config: RunnableConfig) -> dict[str, Any]:
    """
    Phase 3 — UI/UX Design (Google Stitch Integration).
    
    Generates design system using Ollama + creates visual prototypes via Google Stitch.
    Follows best practices from: https://www.adosolve.co.in/post/stitch-prompt-guide
    """
    import json
    import requests
    from pathlib import Path
    from src.core.config import config as app_config
    from src.integrations.stitch_client import StitchClient, StitchError
    from src.integrations.stitch_prompt_builder import StitchPromptBuilder

    thread_id = config.get("configurable", {}).get("thread_id", "default")
    logger.info("phase_3_start_ai", extra={"phase": 3, "thread_id": thread_id, "stitch_enabled": app_config.GOOGLE_STITCH_ENABLED})

    # Prepare artifacts directory
    artifacts_dir = Path("artifacts") / thread_id / "docs"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = Path("artifacts") / thread_id / "assets" / "ui"
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Read Phase 2 artifacts
    mvp_scope_path = artifacts_dir / "MVP_Scope.md"
    backlog_path = artifacts_dir / "Product_Backlog.md"

    try:
        mvp_scope = mvp_scope_path.read_text(encoding="utf-8")
        backlog = backlog_path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        logger.error("phase_3_missing_input", extra={"thread_id": thread_id, "error": str(e)})
        raise ValueError(f"Phase 2 artifacts not found: {e}")

    # STEP 1: Ollama generates Design Strategy (optimized for Stitch)
    design_prompt = f"""You are Johnny Vibe, a world-class UI/UX Designer.

You have been given:
---MVP SCOPE---
{mvp_scope}

---PRODUCT BACKLOG---
{backlog}

Your task: Create design strategy optimized for Google Stitch prototype generation.

Generate 5 documents:

1. **Design_Strategy.json** - Structured data for Stitch prompt builder:
{{
  "high_level_concept": "An app for [audience] to [core functionality]",
  "vibe_adjectives": "modern and user-friendly",
  "target_audience": "specific user personas",
  "color_mood": "energetic and inviting" OR "primary_color": "#4A90E2",
  "font_style": "clean sans-serif" OR "playful rounded",
  "border_style": "fully rounded corners" OR "sharp edges",
  "image_style": "bright product photos, lifestyle imagery",
  "screens": [
    {{
      "name": "Login",
      "purpose": "User authentication",
      "components": ["email input", "password input", "primary CTA button", "social login options"],
      "cta": "Sign In button (large, primary color, fully rounded)",
      "states": ["idle", "loading", "error", "success"]
    }}
  ]
}}

2. **Design_System.md** - Full design system documentation

3. **Design_Tokens.json** - Design tokens (colors, typography, spacing, borders, shadows)

4. **UI_Screens_List.md** - Detailed screen specifications

5. **Stitch_Refinement_Guide.md** - Common refinement prompts for this design
   Include examples like:
   - "On homepage, add search bar to header"
   - "Change primary CTA button to be larger"
   - "Update theme to warm color palette"

IMPORTANT: Separate with ---DOCUMENT_SEPARATOR---
Order: Design_Strategy.json, Design_System.md, Design_Tokens.json, UI_Screens_List.md, Stitch_Refinement_Guide.md"""

    # Call Ollama (Phase 3 needs more time - 5 documents generation)
    try:
        response = requests.post(
            f"{app_config.OLLAMA_BASE_URL}/api/chat",
            json={
                "model": app_config.OLLAMA_MODEL,
                "messages": [{"role": "user", "content": design_prompt}],
                "stream": False,
            },
            timeout=240,  # 4 minutes for Phase 3 (generates 5 documents)
        )
        response.raise_for_status()
        result = response.json()
        full_text = result["message"]["content"]
    except Exception as e:
        logger.exception("phase_3_ollama_failed", extra={"thread_id": thread_id, "error": str(e)})
        raise

    # STEP 2: Parse Ollama output
    try:
        parts = full_text.split("---DOCUMENT_SEPARATOR---")
        if len(parts) < 5:
            logger.warning("phase_3_incomplete_documents", extra={"got": len(parts), "expected": 5, "thread_id": thread_id})
            # Pad with defaults if needed
            while len(parts) < 5:
                parts.append("")
        
        design_strategy_text = parts[0].strip()
        design_system = parts[1].strip()
        design_tokens_text = parts[2].strip()
        ui_screens = parts[3].strip()
        refinement_guide = parts[4].strip() if len(parts) > 4 else ""

        logger.info(
            "phase_3_parsing_design_strategy",
            extra={
                "thread_id": thread_id,
                "design_strategy_length": len(design_strategy_text),
                "design_strategy_preview": design_strategy_text[:200],
            },
        )

        # Parse Design_Strategy.json
        design_strategy = StitchPromptBuilder.parse_design_strategy(design_strategy_text)
        
        # Write artifacts
        (artifacts_dir / "Design_Strategy.json").write_text(
            json.dumps(design_strategy, indent=2), encoding="utf-8"
        )
        (artifacts_dir / "Design_System.md").write_text(design_system, encoding="utf-8")
        (artifacts_dir / "UI_Screens_List.md").write_text(ui_screens, encoding="utf-8")
        if refinement_guide:
            (artifacts_dir / "Stitch_Refinement_Guide.md").write_text(refinement_guide, encoding="utf-8")
        
        # Extract and write Design_Tokens.json
        import re
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', design_tokens_text, re.DOTALL)
        if json_match:
            tokens_json = json_match.group(1)
        elif design_tokens_text.strip().startswith('{'):
            tokens_json = design_tokens_text.strip()
        else:
            json_match = re.search(r'(\{.*\})', design_tokens_text, re.DOTALL)
            if json_match:
                tokens_json = json_match.group(1)
            else:
                raise ValueError("Could not extract JSON from Design_Tokens")
        
        tokens_data = json.loads(tokens_json)
        (artifacts_dir / "Design_Tokens.json").write_text(
            json.dumps(tokens_data, indent=2), encoding="utf-8"
        )

        logger.info(
            "phase_3_ollama_complete",
            extra={
                "thread_id": thread_id,
                "screens_count": len(design_strategy.get("screens", [])),
            },
        )
    except Exception as e:
        logger.exception("phase_3_parse_failed", extra={"thread_id": thread_id, "error": str(e)})
        raise

    # STEP 3: Google Stitch Integration (if enabled)
    stitch_project_id = None
    stitch_preview_url = None
    screenshot_paths = []

    if app_config.GOOGLE_STITCH_ENABLED and app_config.GOOGLE_STITCH_API_KEY:
        try:
            # Build Stitch prompt following best practices
            prompt_builder = StitchPromptBuilder(design_strategy)
            stitch_prompt = prompt_builder.build_initial_prompt()
            
            # Save Stitch prompt for debugging/refinement
            (artifacts_dir / "Stitch_Prompt.txt").write_text(stitch_prompt, encoding="utf-8")
            
            # Call Stitch API
            stitch_client = StitchClient(
                api_key=app_config.GOOGLE_STITCH_API_KEY,
                base_url=app_config.GOOGLE_STITCH_BASE_URL,
                timeout=app_config.GOOGLE_STITCH_TIMEOUT,
            )
            
            project_name = f"{thread_id[:8]}_design"
            stitch_result = stitch_client.create_design(stitch_prompt, project_name)
            
            stitch_project_id = stitch_result["project_id"]
            stitch_preview_url = stitch_result["preview_url"]
            
            # Download screenshots
            if stitch_result.get("screenshots"):
                screenshot_paths = stitch_client.download_all_screenshots(
                    stitch_result["screenshots"],
                    assets_dir
                )
            
            logger.info(
                "phase_3_stitch_success",
                extra={
                    "thread_id": thread_id,
                    "project_id": stitch_project_id,
                    "screenshots": len(screenshot_paths),
                },
            )
            
            # Create Prototype_Link.md with REAL Stitch URL
            prototype_content = f"""# Interactive Prototype

## Stitch Project
**Live Prototype:** {stitch_preview_url}  
**Project ID:** {stitch_project_id}

## Screens Generated
{len(screenshot_paths)} screens created

## Refinement Instructions
See `Stitch_Refinement_Guide.md` for common refinement prompts.

To refine specific screens, use the REFINE button in Telegram and provide:
- Specific screen name
- Exact change needed
- UI/UX keywords (button, header, navigation, etc.)

Example: "On homepage, add search bar to header"

## Export to Figma
Available upon request. Use the EXPORT TO FIGMA button.
"""
            
        except StitchError as e:
            logger.warning("phase_3_stitch_failed_fallback", extra={"thread_id": thread_id, "error": str(e)})
            # Fallback to text-only if Stitch fails
            prototype_content = f"""# Prototype Link

## Google Stitch Integration Failed
{str(e)}

## Fallback Mode
Using text-only design specifications.
Design can be manually created in Figma using:
- Design_System.md
- Design_Tokens.json
- UI_Screens_List.md

## Stitch Prompt
See `Stitch_Prompt.txt` for the generated Stitch prompt that can be used manually.
"""
    else:
        # Stitch disabled - text-only mode
        logger.info("phase_3_stitch_disabled", extra={"thread_id": thread_id})
        prototype_content = """# Prototype Link

## Manual Design Required
Google Stitch integration is disabled.

Create design manually in Figma/Stitch using:
- Design_System.md (design specifications)
- Design_Tokens.json (colors, fonts, spacing)
- UI_Screens_List.md (screen layouts)
- Stitch_Prompt.txt (ready-to-use Stitch prompt)

## To Enable Stitch
Set in `.env`:
```
GOOGLE_STITCH_ENABLED=true
GOOGLE_STITCH_API_KEY=your_api_key
```
"""
    
    (artifacts_dir / "Prototype_Link.md").write_text(prototype_content, encoding="utf-8")

    # STEP 4: Prepare artifact files for Telegram
    artifact_files = [
        str(artifacts_dir / "Design_System.md"),
        str(artifacts_dir / "Design_Tokens.json"),
        str(artifacts_dir / "UI_Screens_List.md"),
        str(artifacts_dir / "Prototype_Link.md"),
    ]
    
    # Add screenshots if available
    for screenshot_path in screenshot_paths:
        artifact_files.append(str(screenshot_path))
    
    # STEP 5: Interrupt for CEO approval
    response = interrupt(
        {
            "phase": 3,
            "phase_name": "ui_ux_design_google_stitch",
            "message": PHASE_PERSONA_MESSAGES[3],
            "artifact_files": artifact_files,
        }
    )
    approved = response.get("approved", False) if isinstance(response, dict) else bool(response)
    
    return {
        "current_phase": 3,
        "approved": approved,
        "stitch_project_id": stitch_project_id,
        "stitch_preview_url": stitch_preview_url,
    }


def phase_4(state: PhaseState, config: RunnableConfig) -> dict[str, Any]:
    """Phase 4 — System Architecture & HDL."""
    return phase_node(4)(state, config)


def phase_5(state: PhaseState, config: RunnableConfig) -> dict[str, Any]:
    """Phase 5 — Project Initialization."""
    return phase_node(5)(state, config)


def phase_6(state: PhaseState, config: RunnableConfig) -> dict[str, Any]:
    """Phase 6 — TDD."""
    return phase_node(6)(state, config)


def phase_7(state: PhaseState, config: RunnableConfig) -> dict[str, Any]:
    """Phase 7 — Implementation."""
    return phase_node(7)(state, config)


def phase_8(state: PhaseState, config: RunnableConfig) -> dict[str, Any]:
    """Phase 8 — Visual QA & Patch Loops."""
    return phase_node(8)(state, config)


def phase_9(state: PhaseState, config: RunnableConfig) -> dict[str, Any]:
    """Phase 9 — Guardrails."""
    return phase_node(9)(state, config)


def phase_10(state: PhaseState, config: RunnableConfig) -> dict[str, Any]:
    """Phase 10 — DevOps, Growth & SRE."""
    return phase_node(10)(state, config)


def approval_node(state: PhaseState) -> dict[str, Any]:
    """Marks state as approved so the graph can proceed to next phase."""
    return {"approved": True}
