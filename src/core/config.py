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

    # Ollama (local LLM)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "120"))

    # Google Stitch (UI/UX Design)
    GOOGLE_STITCH_API_KEY: str = os.getenv("GOOGLE_STITCH_API_KEY", "")
    GOOGLE_STITCH_BASE_URL: str = os.getenv("GOOGLE_STITCH_BASE_URL", "https://stitch.google.com")
    GOOGLE_STITCH_TIMEOUT: int = int(os.getenv("GOOGLE_STITCH_TIMEOUT", "120"))
    GOOGLE_STITCH_ENABLED: bool = os.getenv("GOOGLE_STITCH_ENABLED", "true").lower() == "true"

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration is present."""
        errors = []
        if not cls.PG_CONNECTION_STRING:
            errors.append("PG_CONNECTION_STRING not set")
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN not set")
        # Ollama doesn't require API key, just URL
        # Stitch is optional - if enabled, API key is required
        if cls.GOOGLE_STITCH_ENABLED and not cls.GOOGLE_STITCH_API_KEY:
            errors.append("GOOGLE_STITCH_API_KEY not set (or set GOOGLE_STITCH_ENABLED=false)")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")


# Create global config instance
config = Config()
