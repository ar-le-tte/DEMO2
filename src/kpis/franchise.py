from __future__ import annotations

import numpy as np
import pandas as pd

from src.logging_utils import get_logger
from src.quality.checks import _require_cols

logger = get_logger()


def add_franchise_flag(df: pd.DataFrame) -> pd.DataFrame:
    """Add is_franchise flag based on belongs_to_collection being non-null."""
    _require_cols(df, ["belongs_to_collection"], "add_franchise_flag")
    out = df.copy()
    out["is_franchise"] = out["belongs_to_collection"].notna()
    return out


def franchise_vs_standalone(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare franchise vs standalone:
      mean revenue, median ROI, mean budget, mean popularity, mean rating.
    """
    _require_cols(df, ["belongs_to_collection", "revenue_musd", "roi", "budget_musd", "popularity", "vote_average"],
                 "franchise_vs_standalone")

    d = add_franchise_flag(df)

    out = (
        d.groupby("is_franchise", as_index=False)
         .agg(
            n_movies=("id", "count"),
            mean_revenue_musd=("revenue_musd", "mean"),
            median_roi=("roi", "median"),
            mean_budget_musd=("budget_musd", "mean"),
            mean_popularity=("popularity", "mean"),
            mean_rating=("vote_average", "mean"),
         )
         .sort_values("is_franchise", ascending=False)
    )
    return out


def top_franchises(df: pd.DataFrame, min_movies: int = 2) -> pd.DataFrame:
    """Most successful franchises (min_movies filter), ordered by total_revenue_musd desc."""
    _require_cols(df, ["belongs_to_collection", "budget_musd", "revenue_musd", "vote_average"], "top_franchises")

    d = df.loc[df["belongs_to_collection"].notna()].copy()

    out = (
        d.groupby("belongs_to_collection", as_index=False)
         .agg(
            n_movies=("id", "count"),
            total_budget_musd=("budget_musd", "sum"),
            mean_budget_musd=("budget_musd", "mean"),
            total_revenue_musd=("revenue_musd", "sum"),
            mean_revenue_musd=("revenue_musd", "mean"),
            mean_rating=("vote_average", "mean"),
         )
    )

    out = out.loc[out["n_movies"] >= int(min_movies)].copy()
    out = out.sort_values("total_revenue_musd", ascending=False)
    logger.info("top_franchises: rows=%s (min_movies=%s)", len(out), min_movies)
    return out