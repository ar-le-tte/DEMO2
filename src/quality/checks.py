from __future__ import annotations

from typing import Iterable
import pandas as pd

from src.logging_utils import get_logger

logger = get_logger()


def _require_cols(df: pd.DataFrame, cols: Iterable[str], fn_name: str) -> None:
    """
    Validate that a DataFrame contains a required set of columns.
    """
    missing = [c for c in cols if c not in df.columns]
    if missing:
        msg = f"{fn_name}: missing required columns: {missing}"
        logger.error(msg)
        raise ValueError(msg)