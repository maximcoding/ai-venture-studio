"""
Google Stitch Prompt Builder.

Follows best practices from:
https://www.adosolve.co.in/post/stitch-prompt-guide-effective-prompting-for-better-ui-ux-designs

Key principles:
1. High-level concept OR detailed functionality
2. Vibe adjectives for brand personality
3. Screen-by-screen approach with UI/UX keywords
4. Specific theme control (colors, fonts, borders)
5. Precise image descriptions
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class StitchPromptBuilder:
    """Builds structured prompts for Google Stitch following best practices."""

    def __init__(self, design_strategy: dict[str, Any]):
        """
        Initialize with design strategy from Ollama.

        Args:
            design_strategy: Design strategy dict containing:
                - high_level_concept: str
                - vibe_adjectives: str
                - target_audience: str
                - color_mood: str OR primary_color/secondary_color
                - font_style: str
                - border_style: str
                - image_style: str
                - screens: list[dict]
        """
        self.strategy = design_strategy
        self._validate_strategy()

    def _validate_strategy(self) -> None:
        """Validate design strategy has required fields."""
        required = ["high_level_concept", "vibe_adjectives", "screens"]
        missing = [f for f in required if f not in self.strategy]
        if missing:
            raise ValueError(f"Design strategy missing required fields: {missing}")

    def build_initial_prompt(self) -> str:
        """
        Build initial Stitch prompt for project creation.

        Returns complete prompt following article structure:
        1. High-level concept
        2. Vibe adjectives
        3. Screens list (screen-by-screen)
        4. Theme specifics
        5. Image descriptions
        """
        sections = [
            self._build_high_level_section(),
            self._build_vibe_section(),
            self._build_screens_section(),
            self._build_theme_section(),
            self._build_imagery_section(),
        ]

        prompt = "\n\n".join(s for s in sections if s)
        logger.info("stitch_prompt_built", extra={"length": len(prompt), "screens": len(self.strategy["screens"])})
        return prompt

    def _build_high_level_section(self) -> str:
        """
        Section 1: High-level concept.

        Article: "Choose to start with a broad concept or specific details."
        """
        concept = self.strategy["high_level_concept"]
        return concept

    def _build_vibe_section(self) -> str:
        """
        Section 2: Vibe adjectives.

        Article: "Use adjectives to define the app's feel
        (influences colors, fonts, imagery)."
        """
        vibe = self.strategy["vibe_adjectives"]
        return f"A {vibe} app"

    def _build_screens_section(self) -> str:
        """
        Section 3: Screens (screen-by-screen with UI/UX keywords).

        Article: "Focus on specific screens/features" and
        "Use UI/UX keywords (e.g., navigation bar, call-to-action button)"
        """
        if not self.strategy.get("screens"):
            return ""

        screen_prompts = []
        for screen in self.strategy["screens"]:
            # Build detailed screen description with UI/UX keywords
            components = ", ".join(screen.get("components", []))
            screen_prompt = f"""{screen['name']} Screen:
- Purpose: {screen.get('purpose', 'Main interaction')}
- Components: {components}
- Primary CTA: {screen.get('cta', 'Primary action button')}
- States: {', '.join(screen.get('states', ['idle', 'loading']))}"""
            screen_prompts.append(screen_prompt)

        return "Design the following screens:\n\n" + "\n\n".join(screen_prompts)

    def _build_theme_section(self) -> str:
        """
        Section 4: Theme control (colors, fonts, borders).

        Article: "Request specific colors or describe a mood for the color palette"
        and "Modify typography and element styling"
        """
        theme_parts = []

        # Colors - specific OR mood-based (article section 5)
        if "primary_color" in self.strategy:
            colors = f"Primary color: {self.strategy['primary_color']}"
            if "secondary_color" in self.strategy:
                colors += f", Secondary color: {self.strategy['secondary_color']}"
            theme_parts.append(colors)
        elif "color_mood" in self.strategy:
            theme_parts.append(f"Color palette: {self.strategy['color_mood']}")

        # Fonts (article section 5)
        if "font_style" in self.strategy:
            theme_parts.append(f"Typography: {self.strategy['font_style']}")

        # Borders (article section 5)
        if "border_style" in self.strategy:
            theme_parts.append(f"UI elements: {self.strategy['border_style']}")

        if not theme_parts:
            return ""

        return "Theme:\n- " + "\n- ".join(theme_parts)

    def _build_imagery_section(self) -> str:
        """
        Section 5: Image descriptions.

        Article: "Guide the style or content of images"
        """
        if not self.strategy.get("image_style"):
            return ""

        return f"Image style: {self.strategy['image_style']}\n\nMake the design responsive for mobile, tablet, and desktop."

    def build_refinement_prompt(self, instruction: str, screen_name: str | None = None) -> str:
        """
        Build refinement prompt for incremental changes.

        Article best practices:
        - Be specific and concise
        - Focus on one screen/component
        - Make one or two adjustments per prompt
        - Use UI/UX keywords

        Args:
            instruction: Specific change instruction from CEO
            screen_name: Optional screen to target

        Returns:
            Formatted refinement prompt
        """
        if not self._is_specific_enough(instruction):
            raise ValueError(
                "Refinement prompt needs to be more specific. "
                "Example: 'On homepage, add search bar to header' or "
                "'Change primary CTA button to be larger and use brand blue color'"
            )

        # If screen specified, ensure it's mentioned in instruction
        if screen_name and screen_name.lower() not in instruction.lower():
            return f"On {screen_name} screen: {instruction}"

        return instruction

    def _is_specific_enough(self, prompt: str) -> bool:
        """
        Validate refinement prompt follows article guidelines.

        Checks:
        - Mentions specific screen or component
        - Uses UI/UX keywords
        - Describes clear action
        """
        ui_keywords = [
            "button",
            "header",
            "navigation",
            "cta",
            "input",
            "card",
            "screen",
            "homepage",
            "login",
            "dashboard",
            "form",
            "menu",
            "icon",
            "image",
            "text",
            "background",
        ]

        specific_actions = [
            "add",
            "change",
            "update",
            "move",
            "resize",
            "recolor",
            "remove",
            "replace",
            "adjust",
        ]

        prompt_lower = prompt.lower()
        has_keyword = any(kw in prompt_lower for kw in ui_keywords)
        has_action = any(act in prompt_lower for act in specific_actions)

        return has_keyword and has_action

    def build_theme_change_prompt(self, theme_changes: dict[str, str]) -> str:
        """
        Build prompt for theme-wide changes.

        Article section 5: "Controlling App Theme"

        Args:
            theme_changes: Dict with keys like:
                - primary_color: str
                - font_style: str
                - border_style: str

        Returns:
            Theme update prompt
        """
        changes = []

        if "primary_color" in theme_changes:
            changes.append(f"Change primary color to {theme_changes['primary_color']}")

        if "font_style" in theme_changes:
            changes.append(f"Update typography to {theme_changes['font_style']}")

        if "border_style" in theme_changes:
            changes.append(f"Apply {theme_changes['border_style']} to all UI elements")

        if "color_mood" in theme_changes:
            changes.append(f"Update theme to a {theme_changes['color_mood']} color palette")

        return ". ".join(changes) + "."

    @staticmethod
    def parse_design_strategy(ollama_output: str) -> dict[str, Any]:
        """
        Parse Design_Strategy.json from Ollama output.

        Args:
            ollama_output: Raw output from Ollama containing JSON

        Returns:
            Parsed design strategy dict
        """
        import re

        # Try to find JSON in output (might be wrapped in markdown)
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", ollama_output, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        elif ollama_output.strip().startswith("{"):
            json_str = ollama_output.strip()
        else:
            # Try to find any JSON object
            json_match = re.search(r"(\{.*\})", ollama_output, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                raise ValueError("Could not extract JSON from Ollama output")

        return json.loads(json_str)
