"""Tests for the 10-phase graph (stub nodes and workflow build)."""

import os
from pathlib import Path

import pytest

from src.graph.nodes import PHASE_NAMES, phase_node
from src.graph.state import PhaseState
from src.graph.workflow import PHASE_NODES, build_workflow


def test_phase_names_count() -> None:
    """There are exactly 10 phase names."""
    assert len(PHASE_NAMES) == 10


def test_phase_node_stub() -> None:
    """Phase node returns current_phase and approved (stub; no interrupt without checkpointer)."""
    node = phase_node(1)
    # Without checkpointer, interrupt() would raise; we test the node exists and is callable
    assert callable(node)


def test_workflow_has_10_phase_nodes() -> None:
    """Workflow is built with 10 phase nodes."""
    assert len(PHASE_NODES) == 10
    for i, (name, fn) in enumerate(PHASE_NODES, start=1):
        assert name == f"phase_{i}"
        assert callable(fn)


@pytest.mark.asyncio
async def test_build_workflow_with_memory_saver() -> None:
    """Graph compiles with in-memory checkpointer (no Postgres in test)."""
    from langgraph.checkpoint.memory import InMemorySaver

    checkpointer = InMemorySaver()
    graph = build_workflow(checkpointer)
    assert graph is not None
    # Invoke once; should interrupt after phase_1
    config = {"configurable": {"thread_id": "test-thread"}}
    initial: PhaseState = {"messages": [], "current_phase": 0, "approved": False}
    result = await graph.ainvoke(initial, config=config)
    assert "__interrupt__" in result
    assert result["__interrupt__"]
    payload = result["__interrupt__"][0].value
    assert payload.get("phase") == 1
    assert "message" in payload


@pytest.mark.asyncio
async def test_phase_1_creates_artifacts(tmp_path: Path) -> None:
    """Phase 1 creates artifacts folder and template files."""
    from langgraph.checkpoint.memory import InMemorySaver

    # Change to tmp directory for test isolation
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        checkpointer = InMemorySaver()
        graph = build_workflow(checkpointer)

        config = {"configurable": {"thread_id": "test-user-123"}}
        initial: PhaseState = {"messages": [], "current_phase": 0, "approved": False}

        await graph.ainvoke(initial, config=config)

        # Check artifacts were created
        artifacts_dir = tmp_path / "artifacts" / "test-user-123" / "docs"
        assert artifacts_dir.exists()
        assert (artifacts_dir / "Business_Logic.md").exists()
        assert (artifacts_dir / "Assumptions.md").exists()

        # Check content has required sections
        business_logic = (artifacts_dir / "Business_Logic.md").read_text()
        assert "# Business Logic" in business_logic
        assert "## Core Concept" in business_logic
        assert "## Risk Matrix" in business_logic

        assumptions = (artifacts_dir / "Assumptions.md").read_text()
        assert "# Assumptions & Unknowns" in assumptions
        assert "## Unknowns (To Verify)" in assumptions
    finally:
        os.chdir(original_cwd)
