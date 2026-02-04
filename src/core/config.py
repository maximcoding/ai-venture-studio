"""Centralized configuration for AI Venture Studio."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    """Application configuration from environment variables."""

    # PostgreSQL
    PG_CONNECTION_STRING: str = os.getenv("PG_CONNECTION_STRING", "")

    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # Anthropic Claude
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    ANTHROPIC_MAX_TOKENS: int = int(os.getenv("ANTHROPIC_MAX_TOKENS", "4096"))

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration is present."""
        errors = []
        if not cls.PG_CONNECTION_STRING:
            errors.append("PG_CONNECTION_STRING not set")
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN not set")
        if not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY not set (required for Phase 1+)")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")


# Create global config instance
config = Config()
