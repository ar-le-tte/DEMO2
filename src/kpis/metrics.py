from __future__ import annotations

import numpy as np
import pandas as pd

from src.logging_utils import get_logger
from src.quality.checks import _require_cols

logger = get_logger()


def add_kpi_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add KPI columns used across the GOLD layer:
      - profit_musd = revenue_musd - budget_musd
      - roi = revenue_musd / budget_musd (NaN if budget is null/0)

    Expects columns:
      - budget_musd
      - revenue_musd

    Returns a COPY of df with new columns.
    """
    _require_cols(df, ["budget_musd", "revenue_musd"], "add_kpi_columns")
    logger.info("add_kpi_columns: adding profit_musd and roi")

    out = df.copy()

    out["profit_musd"] = out["revenue_musd"] - out["budget_musd"]

    denom = out["budget_musd"]
    out["roi"] = np.where(denom.isna() | (denom == 0), np.nan, out["revenue_musd"] / denom)

    return out