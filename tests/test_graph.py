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
async def test_build_workflow_with_memory_saver(monkeypatch: pytest.MonkeyPatch) -> None:
    """Graph compiles with in-memory checkpointer (no Postgres in test)."""
    from unittest.mock import MagicMock

    from langgraph.checkpoint.memory import InMemorySaver

    # Mock Ollama API
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "message": {
            "content": """# Business Logic

## Core Concept
Test business idea

## Target Audience
**Primary Users:** Test users
**Primary Pain:** Test problem

## USP
Test USP

## Monetization Strategy
Test monetization

## Competitive Landscape
Test competitors

## Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Test Risk 1 | H | M | Test mitigation |

## Compliance & Privacy
Test compliance

---DOCUMENT_SEPARATOR---

# Assumptions & Unknowns

## Unknowns (To Verify)
- [ ] Test assumption 1

## Dependencies
- Test dependency

## Technical Assumptions
- Test technical assumption

## Market Assumptions
- Test market assumption"""
        }
    }
    mock_response.raise_for_status = MagicMock()
    
    mock_post = MagicMock(return_value=mock_response)
    monkeypatch.setattr("requests.post", mock_post)

    checkpointer = InMemorySaver()
    graph = build_workflow(checkpointer)
    assert graph is not None
    # Invoke once; should interrupt after phase_1
    config = {"configurable": {"thread_id": "test-thread"}}
    initial: PhaseState = {
        "messages": [],
        "current_phase": 0,
        "approved": False,
        "ceo_prompt": "Build a test SaaS product",
    }
    result = await graph.ainvoke(initial, config=config)
    assert "__interrupt__" in result
    assert result["__interrupt__"]
    payload = result["__interrupt__"][0].value
    assert payload.get("phase") == 1
    assert "message" in payload


@pytest.mark.asyncio
async def test_phase_1_creates_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Phase 1 creates artifacts folder and AI-generated analysis files."""
    from unittest.mock import MagicMock

    from langgraph.checkpoint.memory import InMemorySaver

    # Mock Ollama API
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "message": {
            "content": """# Business Logic

## Core Concept
A SaaS invoice management platform for freelancers

## Target Audience
**Primary Users:** Freelancers and independent contractors
**Primary Pain:** Manual invoice creation and payment tracking

## USP
Automated invoice generation with integrated time tracking

## Monetization Strategy
Monthly subscription ($10-30/mo) with tiered features

## Competitive Landscape
Competing with FreshBooks, Wave, but focused on simplicity

## Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Low user adoption | M | H | Free tier + referral program |
| Payment integration issues | L | M | Use established providers (Stripe) |
| Competition | H | M | Focus on UX simplicity |

## Compliance & Privacy
GDPR-compliant data storage, encrypted payment info, SOC 2 Type II certification required

---DOCUMENT_SEPARATOR---

# Assumptions & Unknowns

## Unknowns (To Verify)
- [ ] Willingness to pay $10-30/mo for invoicing
- [ ] Average invoice volume per freelancer
- [ ] Required payment gateway integrations

## Dependencies
- Stripe/PayPal API availability
- Email delivery service reliability

## Technical Assumptions
- React frontend, Node.js backend scalable to 10K users
- PostgreSQL sufficient for invoice storage

## Market Assumptions
- Target market: 5M+ freelancers in US/EU
- 20% actively seeking better invoicing tools"""
        }
    }
    mock_response.raise_for_status = MagicMock()
    
    mock_post = MagicMock(return_value=mock_response)
    monkeypatch.setattr("requests.post", mock_post)

    # Change to tmp directory for test isolation
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        checkpointer = InMemorySaver()
        graph = build_workflow(checkpointer)

        config = {"configurable": {"thread_id": "test-user-123"}}
        initial: PhaseState = {
            "messages": [],
            "current_phase": 0,
            "approved": False,
            "ceo_prompt": "Build a SaaS platform for freelancers to manage invoices and track time",
        }

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
        assert "freelancers" in business_logic.lower()  # Check AI-generated content

        assumptions = (artifacts_dir / "Assumptions.md").read_text()
        assert "# Assumptions" in assumptions
        assert "Unknowns" in assumptions
    finally:
        os.chdir(original_cwd)


@pytest.mark.asyncio
async def test_phase_to_phase_transition(monkeypatch: pytest.MonkeyPatch) -> None:
    """Approving Phase 1 triggers Phase 2 interrupt."""
    from unittest.mock import MagicMock

    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.types import Command

    # Mock Ollama API
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "message": {"content": "# Business Logic\nTest\n---DOCUMENT_SEPARATOR---\n# Assumptions\nTest"}
    }
    mock_response.raise_for_status = MagicMock()
    
    mock_post = MagicMock(return_value=mock_response)
    monkeypatch.setattr("requests.post", mock_post)

    checkpointer = InMemorySaver()
    graph = build_workflow(checkpointer)

    config = {"configurable": {"thread_id": "test-transition"}}
    initial: PhaseState = {
        "messages": [],
        "current_phase": 0,
        "approved": False,
        "ceo_prompt": "Test business idea",
    }

    # Phase 1 interrupts
    result1 = await graph.ainvoke(initial, config=config)
    assert "__interrupt__" in result1
    assert result1["__interrupt__"][0].value.get("phase") == 1

    # Resume with approval -> Phase 2 should interrupt
    result2 = await graph.ainvoke(Command(resume={"approved": True}), config=config)
    assert "__interrupt__" in result2
    assert result2["__interrupt__"][0].value.get("phase") == 2
    assert "Phase 2" in result2["__interrupt__"][0].value.get("message", "")
