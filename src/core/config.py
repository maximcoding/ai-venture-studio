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

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration is present."""
        errors = []
        if not cls.PG_CONNECTION_STRING:
            errors.append("PG_CONNECTION_STRING not set")
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN not set")
        # Ollama doesn't require API key, just URL
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")


# Create global config instance
config = Config()
