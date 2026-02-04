"""Tests for Google Stitch integration."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.integrations.stitch_client import StitchClient, StitchError
from src.integrations.stitch_prompt_builder import StitchPromptBuilder


class TestStitchPromptBuilder:
    """Tests for StitchPromptBuilder following article best practices."""

    def test_build_initial_prompt_structure(self) -> None:
        """Prompt follows article structure: concept, vibe, screens, theme, imagery."""
        strategy = {
            "high_level_concept": "An app for marathon runners to find training partners",
            "vibe_adjectives": "vibrant and encouraging",
            "screens": [
                {
                    "name": "Login",
                    "purpose": "User authentication",
                    "components": ["email input", "password input", "login button"],
                    "cta": "Sign In button (large, primary color)",
                    "states": ["idle", "loading", "error"],
                }
            ],
            "color_mood": "energetic and motivating",
            "font_style": "playful sans-serif",
            "border_style": "fully rounded corners",
            "image_style": "action photos of runners in motion",
        }

        builder = StitchPromptBuilder(strategy)
        prompt = builder.build_initial_prompt()

        # Check all sections present
        assert "marathon runners" in prompt
        assert "vibrant and encouraging" in prompt
        assert "Login Screen" in prompt
        assert "email input" in prompt
        assert "energetic and motivating" in prompt
        assert "playful sans-serif" in prompt
        assert "fully rounded corners" in prompt
        assert "action photos" in prompt

    def test_specific_color_vs_mood_based(self) -> None:
        """Supports both specific colors and mood-based palettes."""
        # Specific colors
        strategy_specific = {
            "high_level_concept": "Test app",
            "vibe_adjectives": "modern",
            "screens": [],
            "primary_color": "#FF5722",
            "secondary_color": "#4CAF50",
        }
        builder = StitchPromptBuilder(strategy_specific)
        prompt = builder.build_initial_prompt()
        assert "#FF5722" in prompt
        assert "#4CAF50" in prompt

        # Mood-based
        strategy_mood = {
            "high_level_concept": "Test app",
            "vibe_adjectives": "modern",
            "screens": [],
            "color_mood": "warm and inviting",
        }
        builder = StitchPromptBuilder(strategy_mood)
        prompt = builder.build_initial_prompt()
        assert "warm and inviting" in prompt

    def test_refinement_prompt_validation(self) -> None:
        """Refinement prompts must be specific with UI keywords and actions."""
        strategy = {
            "high_level_concept": "Test app",
            "vibe_adjectives": "modern",
            "screens": [],
        }
        builder = StitchPromptBuilder(strategy)

        # Valid refinements
        assert builder.build_refinement_prompt("On homepage, add search bar to header") is not None
        assert builder.build_refinement_prompt("Change primary button to larger size") is not None
        assert builder.build_refinement_prompt("Update login screen background color") is not None

        # Invalid refinements (too vague)
        with pytest.raises(ValueError, match="more specific"):
            builder.build_refinement_prompt("Make it better")

        with pytest.raises(ValueError, match="more specific"):
            builder.build_refinement_prompt("Fix the design")

    def test_theme_change_prompt(self) -> None:
        """Theme changes follow article guidelines for color/font/border updates."""
        strategy = {
            "high_level_concept": "Test app",
            "vibe_adjectives": "modern",
            "screens": [],
        }
        builder = StitchPromptBuilder(strategy)

        theme_changes = {
            "primary_color": "forest green",
            "font_style": "elegant serif",
            "border_style": "sharp edges with 2px borders",
        }

        prompt = builder.build_theme_change_prompt(theme_changes)
        assert "forest green" in prompt
        assert "elegant serif" in prompt
        assert "sharp edges" in prompt

    def test_parse_design_strategy_from_json(self) -> None:
        """Parse Design_Strategy.json from Ollama output (with or without markdown)."""
        # With markdown code block
        ollama_output = """```json
{
  "high_level_concept": "Test app",
  "vibe_adjectives": "modern",
  "screens": []
}
```"""
        strategy = StitchPromptBuilder.parse_design_strategy(ollama_output)
        assert strategy["high_level_concept"] == "Test app"

        # Raw JSON
        raw_json = '{"high_level_concept": "Test app", "vibe_adjectives": "modern", "screens": []}'
        strategy = StitchPromptBuilder.parse_design_strategy(raw_json)
        assert strategy["high_level_concept"] == "Test app"


class TestStitchClient:
    """Tests for StitchClient API integration."""

    def test_requires_api_key(self) -> None:
        """StitchClient requires API key."""
        with pytest.raises(ValueError, match="API key is required"):
            StitchClient(api_key="", base_url="https://stitch.google.com")

    @patch("requests.Session.post")
    def test_create_design_success(self, mock_post: MagicMock) -> None:
        """create_design calls Stitch API and returns project data."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "project_id": "test_project_123",
            "preview_url": "https://stitch.google.com/preview/123",
            "screenshots": ["https://stitch.google.com/ss/1.png"],
            "figma_export_url": "https://figma.com/file/123",
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = StitchClient(api_key="test_key", base_url="https://stitch.google.com")
        result = client.create_design("Test prompt", "Test Project")

        assert result["project_id"] == "test_project_123"
        assert result["preview_url"] == "https://stitch.google.com/preview/123"
        assert len(result["screenshots"]) == 1

        # Check API was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "/api/v1/generate" in call_args[0][0]
        assert call_args[1]["json"]["prompt"] == "Test prompt"
        assert call_args[1]["json"]["mode"] == "initial_design"

    @patch("requests.Session.post")
    def test_refine_design_success(self, mock_post: MagicMock) -> None:
        """refine_design calls Stitch API with incremental update mode."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "project_id": "test_project_123",
            "preview_url": "https://stitch.google.com/preview/123",
            "screenshots": ["https://stitch.google.com/ss/updated.png"],
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = StitchClient(api_key="test_key", base_url="https://stitch.google.com")
        result = client.refine_design("test_project_123", "On homepage, add search bar")

        assert result["project_id"] == "test_project_123"

        # Check incremental mode used
        call_args = mock_post.call_args
        assert "/projects/test_project_123/refine" in call_args[0][0]
        assert call_args[1]["json"]["mode"] == "incremental_update"
        assert call_args[1]["json"]["prompt"] == "On homepage, add search bar"

    @patch("requests.Session.post")
    def test_create_design_timeout(self, mock_post: MagicMock) -> None:
        """Timeout raises StitchError."""
        mock_post.side_effect = requests.exceptions.Timeout("Timeout")

        client = StitchClient(api_key="test_key", base_url="https://stitch.google.com", timeout=30)

        with pytest.raises(StitchError, match="timeout"):
            client.create_design("Test prompt")

    @patch("requests.Session.post")
    def test_create_design_http_error(self, mock_post: MagicMock) -> None:
        """HTTP errors raise StitchError with status code."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_post.return_value = mock_response

        client = StitchClient(api_key="test_key", base_url="https://stitch.google.com")

        with pytest.raises(StitchError, match="400"):
            client.create_design("Test prompt")

    @patch("requests.Session.get")
    def test_download_screenshot(self, mock_get: MagicMock, tmp_path: Path) -> None:
        """download_screenshot fetches and saves image."""
        mock_response = MagicMock()
        mock_response.content = b"fake_png_data_12345"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        client = StitchClient(api_key="test_key", base_url="https://stitch.google.com")
        save_path = tmp_path / "test_screen.png"

        result_path = client.download_screenshot("https://stitch.google.com/ss/1.png", save_path)

        assert result_path == save_path
        assert save_path.exists()
        assert save_path.read_bytes() == b"fake_png_data_12345"

    def test_download_all_screenshots(self, tmp_path: Path) -> None:
        """download_all_screenshots handles multiple screenshots."""
        with patch.object(StitchClient, "download_screenshot") as mock_download:
            mock_download.side_effect = lambda url, path: path

            client = StitchClient(api_key="test_key", base_url="https://stitch.google.com")
            urls = [
                "https://stitch.google.com/ss/1.png",
                "https://stitch.google.com/ss/2.png",
            ]

            result = client.download_all_screenshots(urls, tmp_path / "screens")

            assert len(result) == 2
            assert mock_download.call_count == 2
