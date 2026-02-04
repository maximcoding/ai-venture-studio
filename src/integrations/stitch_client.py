"""
Google Stitch API Client.

Handles communication with Google Stitch for UI/UX design generation.
"""

import logging
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)


class StitchError(Exception):
    """Base exception for Stitch API errors."""

    pass


class StitchClient:
    """Client for Google Stitch API."""

    def __init__(self, api_key: str, base_url: str, timeout: int = 120):
        """
        Initialize Stitch client.

        Args:
            api_key: Google Stitch API key
            base_url: Stitch API base URL
            timeout: Request timeout in seconds (default: 120)
        """
        if not api_key:
            raise ValueError("Stitch API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )

    def create_design(self, prompt: str, project_name: str | None = None) -> dict[str, Any]:
        """
        Create new Stitch design from prompt.

        Args:
            prompt: Structured Stitch prompt (from StitchPromptBuilder)
            project_name: Optional project name

        Returns:
            Dict with:
                - project_id: str
                - preview_url: str (interactive prototype)
                - screenshots: list[str] (URLs)
                - figma_export_url: str | None

        Raises:
            StitchError: If API request fails
        """
        logger.info("stitch_create_design_start", extra={"project_name": project_name})

        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/generate",
                json={
                    "prompt": prompt,
                    "project_name": project_name or "AI Venture Studio Design",
                    "mode": "initial_design",
                    "export_formats": ["screenshots", "figma_url", "responsive_html"],
                    "responsive": True,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                "stitch_create_design_success",
                extra={
                    "project_id": result.get("project_id"),
                    "screens": len(result.get("screenshots", [])),
                },
            )

            return {
                "project_id": result["project_id"],
                "preview_url": result["preview_url"],
                "screenshots": result.get("screenshots", []),
                "figma_export_url": result.get("figma_export_url"),
            }

        except requests.exceptions.Timeout:
            logger.error("stitch_timeout", extra={"timeout": self.timeout})
            raise StitchError(f"Stitch API timeout after {self.timeout}s")
        except requests.exceptions.HTTPError as e:
            logger.error("stitch_http_error", extra={"status": e.response.status_code, "error": str(e)})
            raise StitchError(f"Stitch API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.exception("stitch_unexpected_error", extra={"error": str(e)})
            raise StitchError(f"Unexpected Stitch error: {e}")

    def refine_design(self, project_id: str, refinement_prompt: str) -> dict[str, Any]:
        """
        Refine existing Stitch design with incremental changes.

        Args:
            project_id: Existing Stitch project ID
            refinement_prompt: Specific refinement instruction

        Returns:
            Dict with updated design data (same structure as create_design)

        Raises:
            StitchError: If API request fails
        """
        logger.info(
            "stitch_refine_design_start",
            extra={"project_id": project_id, "instruction_length": len(refinement_prompt)},
        )

        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/projects/{project_id}/refine",
                json={
                    "prompt": refinement_prompt,
                    "mode": "incremental_update",  # Article: one change at a time
                    "export_formats": ["screenshots"],
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            result = response.json()

            logger.info("stitch_refine_design_success", extra={"project_id": project_id})

            return {
                "project_id": result["project_id"],
                "preview_url": result["preview_url"],
                "screenshots": result.get("screenshots", []),
                "figma_export_url": result.get("figma_export_url"),
            }

        except requests.exceptions.HTTPError as e:
            logger.error(
                "stitch_refine_http_error",
                extra={"project_id": project_id, "status": e.response.status_code},
            )
            raise StitchError(f"Stitch refinement error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.exception("stitch_refine_unexpected_error", extra={"project_id": project_id, "error": str(e)})
            raise StitchError(f"Unexpected Stitch refinement error: {e}")

    def change_theme(self, project_id: str, theme_prompt: str) -> dict[str, Any]:
        """
        Change theme for entire project.

        Args:
            project_id: Existing Stitch project ID
            theme_prompt: Theme change instructions (from StitchPromptBuilder)

        Returns:
            Dict with updated design data

        Raises:
            StitchError: If API request fails
        """
        logger.info("stitch_change_theme_start", extra={"project_id": project_id})

        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/projects/{project_id}/theme",
                json={
                    "prompt": theme_prompt,
                    "apply_to_all_screens": True,
                    "export_formats": ["screenshots"],
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            result = response.json()

            logger.info("stitch_change_theme_success", extra={"project_id": project_id})

            return {
                "project_id": result["project_id"],
                "preview_url": result["preview_url"],
                "screenshots": result.get("screenshots", []),
                "figma_export_url": result.get("figma_export_url"),
            }

        except Exception as e:
            logger.exception("stitch_theme_error", extra={"project_id": project_id, "error": str(e)})
            raise StitchError(f"Stitch theme change error: {e}")

    def download_screenshot(self, url: str, save_path: Path) -> Path:
        """
        Download screenshot from Stitch.

        Args:
            url: Screenshot URL from Stitch API
            save_path: Path to save screenshot

        Returns:
            Path to saved file

        Raises:
            StitchError: If download fails
        """
        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            save_path.write_bytes(response.content)
            logger.info("stitch_screenshot_downloaded", extra={"path": str(save_path), "size": len(response.content)})

            return save_path

        except Exception as e:
            logger.exception("stitch_screenshot_download_error", extra={"url": url, "error": str(e)})
            raise StitchError(f"Failed to download screenshot: {e}")

    def download_all_screenshots(self, screenshot_urls: list[str], save_dir: Path) -> list[Path]:
        """
        Download all screenshots from Stitch.

        Args:
            screenshot_urls: List of screenshot URLs
            save_dir: Directory to save screenshots

        Returns:
            List of paths to saved screenshots

        Raises:
            StitchError: If any download fails
        """
        save_dir.mkdir(parents=True, exist_ok=True)
        downloaded = []

        for i, url in enumerate(screenshot_urls, 1):
            filename = f"screen_{i:02d}.png"
            save_path = save_dir / filename

            try:
                self.download_screenshot(url, save_path)
                downloaded.append(save_path)
            except StitchError:
                logger.warning("stitch_screenshot_skip", extra={"url": url, "index": i})
                # Continue with other screenshots even if one fails
                continue

        if not downloaded:
            raise StitchError("No screenshots downloaded successfully")

        logger.info("stitch_all_screenshots_downloaded", extra={"count": len(downloaded)})
        return downloaded

    def export_to_figma(self, project_id: str) -> str:
        """
        Export Stitch project to Figma.

        Args:
            project_id: Stitch project ID

        Returns:
            Figma file URL

        Raises:
            StitchError: If export fails
        """
        logger.info("stitch_export_figma_start", extra={"project_id": project_id})

        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/projects/{project_id}/export/figma",
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()

            figma_url = result["figma_url"]
            logger.info("stitch_export_figma_success", extra={"project_id": project_id, "figma_url": figma_url})

            return figma_url

        except Exception as e:
            logger.exception("stitch_export_figma_error", extra={"project_id": project_id, "error": str(e)})
            raise StitchError(f"Figma export error: {e}")

    def get_project_status(self, project_id: str) -> dict[str, Any]:
        """
        Get Stitch project status.

        Args:
            project_id: Stitch project ID

        Returns:
            Dict with project status and metadata

        Raises:
            StitchError: If request fails
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/projects/{project_id}",
                timeout=10,
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.exception("stitch_get_status_error", extra={"project_id": project_id, "error": str(e)})
            raise StitchError(f"Failed to get project status: {e}")
