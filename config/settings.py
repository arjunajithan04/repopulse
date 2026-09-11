from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@dataclass(frozen=True)
class Settings:
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    github_api_base_url: str = os.getenv("GITHUB_API_BASE_URL", "https://api.github.com")
    app_title: str = os.getenv("APP_TITLE", "RepoPulse")
    github_max_pages: int = int(os.getenv("GITHUB_MAX_PAGES", "10"))
    github_commit_pages: int = int(os.getenv("GITHUB_COMMIT_PAGES", "3"))


settings = Settings()
