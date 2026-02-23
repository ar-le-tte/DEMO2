from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List


# ---- Movie IDs for this lab ----
MOVIE_IDS: List[int] = [
    0, 299534, 19995, 140607, 299536, 597, 135397, 420818, 24428,
    168259, 99861, 284054, 12445, 181808, 330457, 351286, 109445,
    321612, 260513
]

PROJECT_ROOT = Path(__file__).resolve().parents[1] 
@dataclass(frozen=True)
class Paths:
    """Project data folders."""
    data_dir: Path = PROJECT_ROOT / "data"
    bronze_dir: Path = PROJECT_ROOT / "data" / "bronze"
    silver_dir: Path = PROJECT_ROOT / "data" / "silver"
    gold_dir: Path = PROJECT_ROOT / "data" / "gold"
    reports_dir: Path = PROJECT_ROOT / "data" / "reports"

    def ensure(self) -> "Paths":
        for p in [self.data_dir, self.bronze_dir, self.silver_dir, self.gold_dir, self.reports_dir]:
            p.mkdir(parents=True, exist_ok=True)
        return self


@dataclass(frozen=True)
class Settings:
    """
    Pipeline settings
    """
    tmdb_api_key: str = os.getenv("TMDB_API_KEY", "")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_to_file: bool = os.getenv("LOG_TO_FILE", "1").lower() not in ("0", "false", "no")
    request_timeout: int = int(os.getenv("TMDB_TIMEOUT", "30"))
    request_sleep: float = float(os.getenv("TMDB_SLEEP", "0.25"))