"""
config.py — the ONE place the whole project reads its settings from.

Why centralize this?
  - The API key and file paths are needed in several files.
  - If they're scattered, changing one means hunting through the codebase.
  - Here, everything reads `settings.something`. Change it once, fixed everywhere.
"""
"""
config.py — the ONE place the whole project reads its settings from.
"""

import os
from pathlib import Path
from dataclasses import dataclass

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    db_path: str = str(BASE_DIR / "coding_mentor.db")
    schema_path: str = str(BASE_DIR / "schema.json")
    vectorstore_dir: str = str(BASE_DIR / "data" / "vectorstore")


settings = Settings()