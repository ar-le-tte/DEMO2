from __future__ import annotations

from typing import Callable, Optional, Sequence

import pandas as pd

from src.logging_utils import get_logger
from src.quality.checks import _require_cols

logger = get_logger()


def rank_movies(
    df: pd.DataFrame,
    metric_col: str,
    n: int = 10,
    ascending: bool = False,
    filters: Optional[Sequence[Callable[[pd.DataFrame], pd.Series]]] = None,
    select_cols: Optional[list[str]] = None,
) -> pd.DataFrame:
    """
    Generic ranking helper.

    Returns
    -------
    pd.DataFrame
        Ranked subset.
    """
    _require_cols(df, [metric_col], "rank_movies")
    logger.info("rank_movies: metric=%s n=%s ascending=%s filters=%s", metric_col, n, ascending, bool(filters))

    out = df.copy()

    if filters:
        for fn in filters:
            mask = fn(out)
            out = out.loc[mask].copy()

    out = out.loc[out[metric_col].notna()].copy()

    out = out.sort_values(by=metric_col, ascending=ascending).head(int(n))

    if select_cols is None:
        select_cols = ["id", "title", "release_date", metric_col]

    _require_cols(out, select_cols, "rank_movies(select_cols)")
    return out.loc[:, select_cols]