from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")

    timeout_s: int = int(os.getenv("TIMEOUT_S", "40"))
    mock_mode: bool = os.getenv("MOCK_MODE", "false").lower() in {"1","true","yes"}

SETTINGS = Settings()