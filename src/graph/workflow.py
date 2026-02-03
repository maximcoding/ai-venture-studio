"""Build the 10-phase LangGraph workflow with interrupt after each phase."""

from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.graph.state import PhaseState
from src.graph.nodes import (
    phase_1,
    phase_2,
    phase_3,
    phase_4,
    phase_5,
    phase_6,
    phase_7,
    phase_8,
    phase_9,
    phase_10,
)

PHASE_NODES = [
    ("phase_1", phase_1),
    ("phase_2", phase_2),
    ("phase_3", phase_3),
    ("phase_4", phase_4),
    ("phase_5", phase_5),
    ("phase_6", phase_6),
    ("phase_7", phase_7),
    ("phase_8", phase_8),
    ("phase_9", phase_9),
    ("phase_10", phase_10),
]


def build_workflow(checkpointer: Any) -> CompiledStateGraph:
    """Build and compile the 10-phase graph with Postgres checkpointer.

    Each phase runs then interrupts for human approval (Telegram).
    Use config={"configurable": {"thread_id": "<session_id>"}} for persistence.
    """
    builder = StateGraph(PhaseState)

    for name, node in PHASE_NODES:
        builder.add_node(name, node)

    builder.add_edge(START, "phase_1")
    for i in range(len(PHASE_NODES) - 1):
        builder.add_edge(PHASE_NODES[i][0], PHASE_NODES[i + 1][0])
    builder.add_edge(PHASE_NODES[-1][0], END)

    return builder.compile(checkpointer=checkpointer)
