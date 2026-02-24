from __future__ import annotations

import pandas as pd

from src.logging_utils import get_logger
from src.quality.checks import _require_cols

logger = get_logger()


def top_directors(df: pd.DataFrame, min_movies: int = 2) -> pd.DataFrame:
    """Most successful directors (min_movies filter), ordered by total_revenue_musd desc."""
    _require_cols(df, ["director", "revenue_musd", "roi", "vote_average"], "top_directors")

    d = df.loc[df["director"].notna()].copy()

    out = (
        d.groupby("director", as_index=False)
         .agg(
            n_movies=("id", "count"),
            total_revenue_musd=("revenue_musd", "sum"),
            mean_roi=("roi", "mean"),
            mean_rating=("vote_average", "mean"),
         )
    )

    out = out.loc[out["n_movies"] >= int(min_movies)].copy()
    out = out.sort_values("total_revenue_musd", ascending=False)
    logger.info("top_directors: rows=%s (min_movies=%s)", len(out), min_movies)
    return out