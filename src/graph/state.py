"""Shared state for the 10-phase pipeline."""

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class PhaseState(TypedDict, total=False):
    """State passed between phase nodes. thread_id in config for Postgres checkpoints."""

    messages: Annotated[list[BaseMessage], add_messages]
    current_phase: int  # 1..10
    approved: bool  # True after human approval in Telegram
