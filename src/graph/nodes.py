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

    # Call Ollama
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
        result = response.json()
        full_text = result["message"]["content"]
    except Exception as e:
        logger.exception("phase_2_ollama_failed", extra={"thread_id": thread_id, "error": str(e)})
        raise

    # Parse the 3 documents
    try:
        parts = full_text.split("---DOCUMENT_SEPARATOR---")
        if len(parts) < 3:
            raise ValueError(f"Expected 3 documents, got {len(parts)}")
        
        backlog = parts[0].strip()
        mvp_scope = parts[1].strip()
        sprint_todo = parts[2].strip()

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
    """Phase 3 — UI/UX Design (Google Stitch). AI-powered design system generation using Ollama."""
    import json
    import requests
    from pathlib import Path
    from src.core.config import config as app_config

    thread_id = config.get("configurable", {}).get("thread_id", "default")
    logger.info("phase_3_start_ai", extra={"phase": 3, "thread_id": thread_id})

    # Prepare artifacts directory
    artifacts_dir = Path("artifacts") / thread_id / "docs"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Read Phase 2 artifacts
    mvp_scope_path = artifacts_dir / "MVP_Scope.md"
    backlog_path = artifacts_dir / "Product_Backlog.md"

    try:
        mvp_scope = mvp_scope_path.read_text(encoding="utf-8")
        backlog = backlog_path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        logger.error("phase_3_missing_input", extra={"thread_id": thread_id, "error": str(e)})
        raise ValueError(f"Phase 2 artifacts not found: {e}")

    # Construct prompt for Ollama
    design_prompt = f"""You are Johnny Vibe, a world-class UI/UX Designer.

You have been given the following product specifications:

---MVP SCOPE---
{mvp_scope}

---PRODUCT BACKLOG---
{backlog}

Your task is to create 4 design documents:

1. **Design_System.md** - Complete design system with:
   - Brand identity (name suggestions, tagline, tone)
   - Color palette (primary, secondary, neutrals, semantic colors)
   - Typography scale (headings, body, captions)
   - Component library (buttons, inputs, cards, navigation, modals)
   - Spacing system (grid, margins, padding)
   - Interaction patterns (hover states, animations, transitions)
   - Accessibility guidelines (WCAG 2.1 AA)

2. **Design_Tokens.json** - Design tokens in JSON format:
   - colors: primary, secondary, neutrals, semantic (success/warning/error)
   - typography: font families, sizes, weights, line heights
   - spacing: base unit and scale (4px, 8px, 16px, 24px, 32px, 48px, 64px)
   - borderRadius: none, sm, md, lg, xl, full
   - shadows: sm, md, lg, xl
   - breakpoints: mobile, tablet, desktop

3. **UI_Screens_List.md** - Complete list of screens with:
   - Screen name and purpose
   - User stories it satisfies
   - Key components on the screen
   - States (loading, empty, error, success)
   - Navigation flow
   Minimum screens: Auth (login/signup), Home/Dashboard, Primary feature screens, Settings/Profile

4. **Prototype_Link.md** - Prototype information with:
   - Design tool recommendation (Figma/Stitch)
   - Screens to prototype
   - Interactive flows to demonstrate
   - Link placeholder: "[TO BE CREATED IN FIGMA]"
   - Instructions for designer to follow

Make the design modern, beautiful, and user-friendly. Consider current UI/UX trends (glassmorphism, micro-interactions, minimalism).

IMPORTANT: Separate each document with the exact marker:
---DOCUMENT_SEPARATOR---

Order: Design_System.md, then Design_Tokens.json, then UI_Screens_List.md, then Prototype_Link.md"""

    # Call Ollama
    try:
        response = requests.post(
            f"{app_config.OLLAMA_BASE_URL}/api/chat",
            json={
                "model": app_config.OLLAMA_MODEL,
                "messages": [{"role": "user", "content": design_prompt}],
                "stream": False,
            },
            timeout=app_config.OLLAMA_TIMEOUT,
        )
        response.raise_for_status()
        result = response.json()
        full_text = result["message"]["content"]
    except Exception as e:
        logger.exception("phase_3_ollama_failed", extra={"thread_id": thread_id, "error": str(e)})
        raise

    # Parse the 4 documents
    try:
        parts = full_text.split("---DOCUMENT_SEPARATOR---")
        if len(parts) < 4:
            raise ValueError(f"Expected 4 documents, got {len(parts)}")
        
        design_system = parts[0].strip()
        design_tokens_text = parts[1].strip()
        ui_screens = parts[2].strip()
        prototype_link = parts[3].strip()

        # Write artifacts
        (artifacts_dir / "Design_System.md").write_text(design_system, encoding="utf-8")
        (artifacts_dir / "UI_Screens_List.md").write_text(ui_screens, encoding="utf-8")
        (artifacts_dir / "Prototype_Link.md").write_text(prototype_link, encoding="utf-8")
        
        # Extract and write Design_Tokens.json
        # Try to find JSON in the text (it might be wrapped in markdown code blocks)
        import re
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', design_tokens_text, re.DOTALL)
        if json_match:
            tokens_json = json_match.group(1)
        elif design_tokens_text.strip().startswith('{'):
            # Already JSON, just extract it
            tokens_json = design_tokens_text.strip()
        else:
            # Try to find any JSON object
            json_match = re.search(r'(\{.*\})', design_tokens_text, re.DOTALL)
            if json_match:
                tokens_json = json_match.group(1)
            else:
                raise ValueError("Could not extract JSON from Design_Tokens")
        
        # Validate JSON
        tokens_data = json.loads(tokens_json)
        (artifacts_dir / "Design_Tokens.json").write_text(
            json.dumps(tokens_data, indent=2), encoding="utf-8"
        )

        logger.info(
            "phase_3_artifacts_written",
            extra={
                "thread_id": thread_id,
                "design_system_len": len(design_system),
                "tokens_keys": list(tokens_data.keys()) if isinstance(tokens_data, dict) else "not_dict",
                "screens_len": len(ui_screens),
            },
        )
    except Exception as e:
        logger.exception("phase_3_parse_failed", extra={"thread_id": thread_id, "error": str(e)})
        raise

    # Then continue with interrupt logic
    artifact_files = [
        str(artifacts_dir / "Design_System.md"),
        str(artifacts_dir / "Design_Tokens.json"),
        str(artifacts_dir / "UI_Screens_List.md"),
        str(artifacts_dir / "Prototype_Link.md"),
    ]
    response = interrupt(
        {
            "phase": 3,
            "phase_name": "ui_ux_design_google_stitch",
            "message": PHASE_PERSONA_MESSAGES[3],
            "artifact_files": artifact_files,
        }
    )
    approved = response.get("approved", False) if isinstance(response, dict) else bool(response)
    return {"current_phase": 3, "approved": approved}


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
