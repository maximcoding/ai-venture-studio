"""Shared state for the 10-phase pipeline."""

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class PhaseState(TypedDict, total=False):
    """State passed between phase nodes. thread_id in config for Postgres checkpoints."""

    messages: Annotated[list[BaseMessage], add_messages]
    current_phase: int  # 1..10
    approved: bool  # True after human approval in Telegram
    ceo_prompt: str  # CEO's initial idea/prompt for Phase 1 analysis
    stitch_project_id: str  # Google Stitch project ID for design continuity
    stitch_preview_url: str  # Interactive Stitch prototype URL
    refinement_prompt: str  # User's refinement instruction (for design iterations)
