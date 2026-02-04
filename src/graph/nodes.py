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
    """Phase 1 — Visionary & Business Audit. Creates artifacts."""
    from pathlib import Path

    # Extract thread_id
    thread_id = config.get("configurable", {}).get("thread_id", "default")
    artifacts_dir = Path(f"artifacts/{thread_id}/docs")

    # Create directory structure
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Write Business_Logic.md with required sections
    business_logic = """# Business Logic

## Core Concept
[One-sentence description of the product idea]

## Target Audience
**Primary Users:** [Who are they?]
**Primary Pain:** [What problem does this solve?]

## USP (Unique Selling Proposition)
[Why would users choose this over alternatives?]

## Monetization Strategy
[First version revenue model]

## Competitive Landscape
[High-level snapshot of competitors and differentiation]

## Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [Risk 1] | [H/M/L] | [H/M/L] | [Strategy] |
| [Risk 2] | [H/M/L] | [H/M/L] | [Strategy] |
| [Risk 3] | [H/M/L] | [H/M/L] | [Strategy] |
| [Risk 4] | [H/M/L] | [H/M/L] | [Strategy] |
| [Risk 5] | [H/M/L] | [H/M/L] | [Strategy] |

## Compliance & Privacy
[Data handling posture, GDPR considerations, security requirements]
"""
    (artifacts_dir / "Business_Logic.md").write_text(business_logic, encoding="utf-8")

    # Write Assumptions.md
    assumptions = """# Assumptions & Unknowns

## Unknowns (To Verify)
- [ ] [Assumption 1 - what needs validation?]
- [ ] [Assumption 2 - what needs validation?]
- [ ] [Assumption 3 - what needs validation?]

## Dependencies
- [External factor or decision we're waiting on]

## Technical Assumptions
- [Platform/stack assumptions to validate]

## Market Assumptions
- [Target audience or demand assumptions to verify]
"""
    (artifacts_dir / "Assumptions.md").write_text(assumptions, encoding="utf-8")

    logger.info(
        "phase_1_artifacts_created",
        extra={"thread_id": thread_id, "artifacts_dir": str(artifacts_dir)},
    )

    # Then continue with interrupt logic
    artifact_files = [
        str(artifacts_dir / "Business_Logic.md"),
        str(artifacts_dir / "Assumptions.md"),
    ]
    response = interrupt(
        {
            "phase": 1,
            "phase_name": "visionary_business_audit",
            "message": f"Phase 1 complete. Review artifacts:\n\n"
            "📄 `Business_Logic.md`\n📄 `Assumptions.md`\n\n"
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
