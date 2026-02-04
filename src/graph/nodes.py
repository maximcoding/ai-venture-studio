"""Stub nodes for the 10 phases. Each produces artifacts and then waits for approval."""

import logging
from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt

from src.graph.state import PhaseState

logger = logging.getLogger(__name__)

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
        response = interrupt(
            {
                "phase": phase_num,
                "phase_name": PHASE_NAMES[phase_num - 1],
                "message": f"Phase {phase_num} complete. Approve in Telegram to continue.",
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
            "message": "Phase 1 complete. Review artifacts below.\n\n"
            "After review, approve to continue to Phase 2.",
            "artifact_files": artifact_files,
        }
    )
    approved = response.get("approved", False) if isinstance(response, dict) else bool(response)
    return {"current_phase": 1, "approved": approved}


def phase_2(state: PhaseState, config: RunnableConfig) -> dict[str, Any]:
    """Phase 2 — Product Management (Backlog & MVP)."""
    return phase_node(2)(state, config)


def phase_3(state: PhaseState, config: RunnableConfig) -> dict[str, Any]:
    """Phase 3 — UI/UX Design."""
    return phase_node(3)(state, config)


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
