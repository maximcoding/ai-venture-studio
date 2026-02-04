"""Tests for the 10-phase graph (stub nodes and workflow build)."""

import os
from pathlib import Path
from typing import Any

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
async def test_phase_2_creates_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Phase 2 reads Phase 1 artifacts and creates 3 Phase 2 artifacts."""
    from unittest.mock import MagicMock

    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.types import Command

    # Setup Phase 1 artifacts manually (Phase 1 already tested separately)
    artifacts_dir = tmp_path / "artifacts" / "test-user-phase2" / "docs"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    (artifacts_dir / "Business_Logic.md").write_text("# Business Logic\n\nTest business content")
    (artifacts_dir / "Assumptions.md").write_text("# Assumptions\n\nTest assumptions")

    # Mock Ollama API - Phase 1 and Phase 2 responses
    phase1_response = {
        "message": {"content": "# Business Logic\nTest\n---DOCUMENT_SEPARATOR---\n# Assumptions\nTest"}
    }
    phase2_response = {
        "message": {
            "content": """# Product Backlog

## User Personas
- Freelancer

## User Stories
**US-1**: As a freelancer, I want to create invoices, so that I can bill clients
- **Priority**: P0
- **AC1**: User can create invoice with line items
- **AC2**: Invoice has unique ID

---DOCUMENT_SEPARATOR---

# MVP Scope

## IN SCOPE
- Invoice creation and editing
- PDF export
- Email delivery

## OUT OF SCOPE
- Time tracking (v2)
- Payment integration (v2)

## Success Metrics
- 100 users in 3 months
- 80% invoice completion rate

---DOCUMENT_SEPARATOR---

# Sprint 1 TODO

## Backend
- [ ] Setup PostgreSQL schema for invoices
- [ ] Create REST API for CRUD operations

## Frontend
- [ ] Build invoice form component
- [ ] Implement PDF generation

## DevOps
- [ ] Setup Docker Compose

## Testing
- [ ] Unit tests for invoice model"""
        }
    }

    call_count = 0
    def mock_post_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        mock_response = MagicMock()
        if call_count == 1:
            mock_response.json.return_value = phase1_response
        else:
            mock_response.json.return_value = phase2_response
        mock_response.raise_for_status = MagicMock()
        return mock_response
    
    monkeypatch.setattr("requests.post", mock_post_side_effect)

    # Change to tmp directory for test isolation
    import os
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        checkpointer = InMemorySaver()
        graph = build_workflow(checkpointer)

        config = {"configurable": {"thread_id": "test-user-phase2"}}
        initial: PhaseState = {
            "messages": [],
            "current_phase": 0,
            "approved": False,
            "ceo_prompt": "Build invoice management SaaS",
        }

        # Phase 1 interrupts
        result1 = await graph.ainvoke(initial, config=config)
        assert "__interrupt__" in result1

        # Resume Phase 1 with approval -> Phase 2 runs and interrupts
        result2 = await graph.ainvoke(Command(resume={"approved": True}), config=config)
        assert "__interrupt__" in result2
        assert result2["__interrupt__"][0].value.get("phase") == 2

        # Check Phase 2 artifacts were created
        assert (artifacts_dir / "Product_Backlog.md").exists()
        assert (artifacts_dir / "MVP_Scope.md").exists()
        assert (artifacts_dir / "Sprint_1_TODO.md").exists()

        # Check content
        backlog = (artifacts_dir / "Product_Backlog.md").read_text()
        assert "Product Backlog" in backlog
        assert "User Stories" in backlog

        mvp_scope = (artifacts_dir / "MVP_Scope.md").read_text()
        assert "MVP Scope" in mvp_scope
        assert "IN SCOPE" in mvp_scope
        assert "OUT OF SCOPE" in mvp_scope

        sprint = (artifacts_dir / "Sprint_1_TODO.md").read_text()
        assert "Sprint 1" in sprint or "TODO" in sprint
        assert "Backend" in sprint or "Frontend" in sprint
    finally:
        os.chdir(original_cwd)


@pytest.mark.asyncio
async def test_phase_3_creates_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Phase 3 reads Phase 2 artifacts and creates design artifacts (Stitch disabled fallback)."""
    from unittest.mock import MagicMock

    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.types import Command

    # Disable Stitch for this test (fallback mode)
    from src.core.config import config as app_config
    monkeypatch.setattr(app_config, "GOOGLE_STITCH_ENABLED", False)

    # Setup Phase 1 and Phase 2 artifacts manually
    artifacts_dir = tmp_path / "artifacts" / "test-user-phase3" / "docs"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    (artifacts_dir / "Business_Logic.md").write_text("# Business Logic\n\nTest business")
    (artifacts_dir / "Assumptions.md").write_text("# Assumptions\n\nTest assumptions")
    (artifacts_dir / "Product_Backlog.md").write_text("# Product Backlog\n\nUser stories")
    (artifacts_dir / "MVP_Scope.md").write_text("# MVP Scope\n\nIN SCOPE: Features")
    (artifacts_dir / "Sprint_1_TODO.md").write_text("# Sprint 1\n\nTasks")

    # Mock Ollama API - Phase 1, 2, 3 responses
    phase1_response = {
        "message": {"content": "# Business Logic\nTest\n---DOCUMENT_SEPARATOR---\n# Assumptions\nTest"}
    }
    phase2_response = {
        "message": {"content": "# Product Backlog\nTest\n---DOCUMENT_SEPARATOR---\n# MVP Scope\nTest\n---DOCUMENT_SEPARATOR---\n# Sprint 1\nTest"}
    }
    phase3_response = {
        "message": {
            "content": """```json
{
  "high_level_concept": "An app for test users",
  "vibe_adjectives": "modern and clean",
  "target_audience": "test users",
  "color_mood": "professional",
  "font_style": "sans-serif",
  "border_style": "rounded",
  "image_style": "minimalist",
  "screens": [
    {
      "name": "Login",
      "purpose": "Authentication",
      "components": ["email input", "password input", "login button"],
      "cta": "Sign In",
      "states": ["idle", "loading"]
    }
  ]
}
```

---DOCUMENT_SEPARATOR---

# Design System

## Brand Identity
Modern SaaS Design

## Colors
- Primary: Blue #0066CC
- Secondary: Green #00CC66

## Typography
- Headings: Inter Bold
- Body: Inter Regular

## Components
- Buttons: Rounded, shadow
- Cards: White background, border

---DOCUMENT_SEPARATOR---

```json
{
  "colors": {
    "primary": "#0066CC",
    "secondary": "#00CC66",
    "neutral": {
      "50": "#F9FAFB",
      "900": "#111827"
    }
  },
  "typography": {
    "fontFamily": {
      "sans": "Inter, sans-serif"
    },
    "fontSize": {
      "base": "16px",
      "lg": "18px"
    }
  },
  "spacing": {
    "base": "4px",
    "scale": [4, 8, 16, 24, 32, 48, 64]
  },
  "borderRadius": {
    "sm": "4px",
    "md": "8px",
    "lg": "12px"
  }
}
```

---DOCUMENT_SEPARATOR---

# UI Screens List

## 1. Login Screen
- **Purpose**: User authentication
- **Components**: Email input, password input, login button
- **States**: idle, loading, error

## 2. Dashboard
- **Purpose**: Main hub
- **Components**: Navigation, stats cards, action buttons

## 3. Settings
- **Purpose**: User preferences
- **Components**: Profile form, preferences toggle

---DOCUMENT_SEPARATOR---

# Stitch Refinement Guide

Common refinement prompts:
- On homepage, add search bar
- Change button to larger size
- Update theme to warm colors"""
        }
    }

    call_count = 0
    def mock_post_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        mock_response = MagicMock()
        if call_count == 1:
            mock_response.json.return_value = phase1_response
        elif call_count == 2:
            mock_response.json.return_value = phase2_response
        else:
            mock_response.json.return_value = phase3_response
        mock_response.raise_for_status = MagicMock()
        return mock_response
    
    monkeypatch.setattr("requests.post", mock_post_side_effect)

    # Change to tmp directory for test isolation
    import os
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        checkpointer = InMemorySaver()
        graph = build_workflow(checkpointer)

        config = {"configurable": {"thread_id": "test-user-phase3"}}
        initial: PhaseState = {
            "messages": [],
            "current_phase": 0,
            "approved": False,
            "ceo_prompt": "Build design system for SaaS",
        }

        # Phase 1 interrupts
        result1 = await graph.ainvoke(initial, config=config)
        assert "__interrupt__" in result1

        # Resume Phase 1 -> Phase 2 interrupts
        result2 = await graph.ainvoke(Command(resume={"approved": True}), config=config)
        assert "__interrupt__" in result2
        assert result2["__interrupt__"][0].value.get("phase") == 2

        # Resume Phase 2 -> Phase 3 runs and interrupts
        result3 = await graph.ainvoke(Command(resume={"approved": True}), config=config)
        assert "__interrupt__" in result3
        assert result3["__interrupt__"][0].value.get("phase") == 3

        # Check Phase 3 artifacts were created
        assert (artifacts_dir / "Design_Strategy.json").exists()
        assert (artifacts_dir / "Design_System.md").exists()
        assert (artifacts_dir / "Design_Tokens.json").exists()
        assert (artifacts_dir / "UI_Screens_List.md").exists()
        assert (artifacts_dir / "Prototype_Link.md").exists()

        # Check Design_Strategy.json is valid JSON with required fields
        import json
        strategy = json.loads((artifacts_dir / "Design_Strategy.json").read_text())
        assert "high_level_concept" in strategy
        assert "vibe_adjectives" in strategy
        assert "screens" in strategy

        # Check content
        design_system = (artifacts_dir / "Design_System.md").read_text()
        assert "Design System" in design_system or "Brand" in design_system

        # Check Design_Tokens.json is valid JSON
        tokens = json.loads((artifacts_dir / "Design_Tokens.json").read_text())
        assert "colors" in tokens
        assert "typography" in tokens or "spacing" in tokens

        screens = (artifacts_dir / "UI_Screens_List.md").read_text()
        assert "Screen" in screens or "Login" in screens or "Dashboard" in screens

        # Check Prototype_Link.md (should be fallback mode since Stitch disabled)
        prototype = (artifacts_dir / "Prototype_Link.md").read_text()
        assert "Prototype" in prototype or "Manual" in prototype
    finally:
        os.chdir(original_cwd)


@pytest.mark.asyncio
async def test_phase_3_with_stitch_enabled(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Phase 3 with Stitch integration creates visual prototypes and screenshots."""
    from unittest.mock import MagicMock

    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.types import Command

    # Enable Stitch for this test by patching config
    from src.core.config import config as app_config
    monkeypatch.setattr(app_config, "GOOGLE_STITCH_ENABLED", True)
    monkeypatch.setattr(app_config, "GOOGLE_STITCH_API_KEY", "test_api_key")

    # Setup Phase 1 and Phase 2 artifacts manually
    artifacts_dir = tmp_path / "artifacts" / "test-stitch-user" / "docs"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    (artifacts_dir / "Business_Logic.md").write_text("# Business Logic\n\nTest")
    (artifacts_dir / "Assumptions.md").write_text("# Assumptions\n\nTest")
    (artifacts_dir / "Product_Backlog.md").write_text("# Product Backlog\n\nUser stories")
    (artifacts_dir / "MVP_Scope.md").write_text("# MVP Scope\n\nIN SCOPE: Features")
    (artifacts_dir / "Sprint_1_TODO.md").write_text("# Sprint 1\n\nTasks")

    # Mock Ollama API
    phase1_response = {"message": {"content": "# Business Logic\nTest\n---DOCUMENT_SEPARATOR---\n# Assumptions\nTest"}}
    phase2_response = {
        "message": {"content": "# Product Backlog\nTest\n---DOCUMENT_SEPARATOR---\n# MVP Scope\nTest\n---DOCUMENT_SEPARATOR---\n# Sprint 1\nTest"}
    }
    phase3_response = {
        "message": {
            "content": """```json
{
  "high_level_concept": "An app for testing Stitch",
  "vibe_adjectives": "modern and vibrant",
  "screens": [{"name": "Login", "purpose": "Auth", "components": ["email input"], "cta": "Sign In", "states": ["idle"]}]
}
```
---DOCUMENT_SEPARATOR---
# Design System
Test design system
---DOCUMENT_SEPARATOR---
```json
{"colors": {"primary": "#0066CC"}, "typography": {"base": "16px"}}
```
---DOCUMENT_SEPARATOR---
# UI Screens
Test screens
---DOCUMENT_SEPARATOR---
# Refinement Guide
Test refinements"""
        }
    }

    ollama_call_count = 0
    def mock_ollama_post(*args, **kwargs):
        nonlocal ollama_call_count
        ollama_call_count += 1
        mock_response = MagicMock()
        if ollama_call_count == 1:
            mock_response.json.return_value = phase1_response
        elif ollama_call_count == 2:
            mock_response.json.return_value = phase2_response
        else:
            mock_response.json.return_value = phase3_response
        mock_response.raise_for_status = MagicMock()
        return mock_response

    # Mock Stitch API create_design
    from src.integrations.stitch_client import StitchClient

    original_create = StitchClient.create_design
    def mock_create_design(self, prompt: str, project_name: str | None = None) -> dict[str, Any]:
        return {
            "project_id": "stitch_test_123",
            "preview_url": "https://stitch.google.com/preview/test_123",
            "screenshots": ["https://stitch.google.com/screenshots/screen1.png"],
            "figma_export_url": None,
        }

    # Mock Stitch API download_all_screenshots
    original_download = StitchClient.download_all_screenshots
    def mock_download_screenshots(self, screenshot_urls: list[str], save_dir: Path) -> list[Path]:
        save_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = save_dir / "screen_01.png"
        screenshot_path.write_bytes(b"fake_png_data")
        return [screenshot_path]

    monkeypatch.setattr("requests.post", mock_ollama_post)
    monkeypatch.setattr(StitchClient, "create_design", mock_create_design)
    monkeypatch.setattr(StitchClient, "download_all_screenshots", mock_download_screenshots)

    # Change to tmp directory
    import os
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        checkpointer = InMemorySaver()
        graph = build_workflow(checkpointer)

        config = {"configurable": {"thread_id": "test-stitch-user"}}
        initial: PhaseState = {
            "messages": [],
            "current_phase": 0,
            "approved": False,
            "ceo_prompt": "Build Stitch test app",
        }

        # Phase 1 -> Phase 2 -> Phase 3
        result1 = await graph.ainvoke(initial, config=config)
        result2 = await graph.ainvoke(Command(resume={"approved": True}), config=config)
        result3 = await graph.ainvoke(Command(resume={"approved": True}), config=config)

        assert result3["__interrupt__"][0].value.get("phase") == 3

        # Check Phase 3 artifacts
        assert (artifacts_dir / "Design_Strategy.json").exists()
        assert (artifacts_dir / "Design_System.md").exists()
        assert (artifacts_dir / "Stitch_Prompt.txt").exists()
        assert (artifacts_dir / "Prototype_Link.md").exists()

        # Check Stitch integration worked
        prototype = (artifacts_dir / "Prototype_Link.md").read_text()
        assert "stitch.google.com/preview/test_123" in prototype
        assert "stitch_test_123" in prototype

        # Check screenshot was downloaded
        assets_dir = tmp_path / "artifacts" / "test-stitch-user" / "assets" / "ui"
        assert (assets_dir / "screen_01.png").exists()

        # Stitch integration successful (verified by artifacts above)
    finally:
        os.chdir(original_cwd)


@pytest.mark.asyncio
async def test_phase_to_phase_transition(monkeypatch: pytest.MonkeyPatch) -> None:
    """Approving Phase 1 triggers Phase 2 interrupt."""
    from unittest.mock import MagicMock

    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.types import Command

    # Mock Ollama API - return different responses for Phase 1 and Phase 2
    phase1_content = "# Business Logic\nTest\n---DOCUMENT_SEPARATOR---\n# Assumptions\nTest"
    phase2_content = """# Product Backlog
Test backlog
---DOCUMENT_SEPARATOR---
# MVP Scope
Test MVP scope
---DOCUMENT_SEPARATOR---
# Sprint 1 TODO
Test sprint tasks"""

    call_count = 0
    def mock_post_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        mock_response = MagicMock()
        if call_count == 1:
            # Phase 1 call
            mock_response.json.return_value = {"message": {"content": phase1_content}}
        else:
            # Phase 2 call
            mock_response.json.return_value = {"message": {"content": phase2_content}}
        mock_response.raise_for_status = MagicMock()
        return mock_response
    
    monkeypatch.setattr("requests.post", mock_post_side_effect)

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
    # Check for persona message
    message = result2["__interrupt__"][0].value.get("message", "")
    assert "Smarty Vegan" in message or "Phase 2" in message
