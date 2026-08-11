"""
Application configuration.

Loads environment variables (via python-dotenv) into a single typed
Settings object so the rest of the codebase never touches os.getenv()
directly. Fails fast at import time if required variables are missing.
"""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    groq_api_key: str
    groq_model: str
    groq_temperature: float
    groq_max_tokens: int
    max_history_messages: int
    system_prompt: str
    allowed_origins: list[str]


def _get_env(name: str, default: Optional[str] = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Set it in backend/.env before starting the server."
        )
    return value or ""


def load_settings() -> Settings:
    return Settings(
        groq_api_key=_get_env("GROQ_API_KEY", required=True),
        groq_model=_get_env("GROQ_MODEL", default="llama-3.3-70b-versatile"),
        groq_temperature=float(_get_env("GROQ_TEMPERATURE", default="0.7")),
        groq_max_tokens=int(_get_env("GROQ_MAX_TOKENS", default="1024")),
        max_history_messages=int(_get_env("MAX_HISTORY_MESSAGES", default="20")),
        system_prompt=_get_env(
            "SYSTEM_PROMPT",
            default="You are a helpful, concise AI assistant.",
        ),
        allowed_origins=[
            origin.strip()
            for origin in _get_env("ALLOWED_ORIGINS", default="*").split(",")
            if origin.strip()
        ],
    )


settings = load_settings()
