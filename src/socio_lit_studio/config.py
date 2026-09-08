from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _env(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    return value.strip() if value else default


@dataclass(frozen=True)
class Settings:
    openalex_mailto: str = _env("OPENALEX_MAILTO", "research@example.com")
    openalex_base_url: str = _env("OPENALEX_BASE_URL", "https://api.openalex.org")
    xai_api_key: str = _env("XAI_API_KEY")
    xai_base_url: str = _env("XAI_BASE_URL", "https://api.x.ai/v1")
    xai_model: str = _env("XAI_MODEL", "grok-4")
    output_dir: Path = Path(_env("OUTPUT_DIR", "./outputs"))


settings = Settings()
