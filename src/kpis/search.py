from __future__ import annotations

import pandas as pd

from src.logging_utils import get_logger
from src.quality.checks import _require_cols

logger = get_logger()


def _pipe_to_list(val: object) -> list[str]:
    """Split pipe-delimited string into list of tokens (lowercased)."""
    if val is None:
        return []
    if not isinstance(val, str):
        return []
    v = val.strip()
    if v == "":
        return []
    return [x.strip().lower() for x in v.split("|") if x.strip()]


def _has_token_pipecol(series: pd.Series, token: str) -> pd.Series:
    """Case-insensitive exact match in a pipe-delimited string column."""
    t = token.lower()
    return series.apply(lambda x: t in _pipe_to_list(x))


def _contains_text(series: pd.Series, text: str) -> pd.Series:
    """Case-insensitive substring match for a string column."""
    return series.astype("string").str.lower().str.contains(text.lower(), na=False)


def search1_bruce_willis_scifi_action(df: pd.DataFrame) -> pd.DataFrame:
    """
    Best-rated Science Fiction + Action movies starring Bruce Willis,
    sorted by vote_average desc, tie-breaker vote_count desc.
    """
    _require_cols(df, ["genres", "cast", "vote_average", "vote_count", "popularity", "release_date", "title"],
                 "search1_bruce_willis_scifi_action")

    out = df.copy()
    mask = (
        _has_token_pipecol(out["genres"], "Science Fiction")
        & _has_token_pipecol(out["genres"], "Action")
        & _has_token_pipecol(out["cast"], "Bruce Willis")
    )
    out = out.loc[mask].copy()

    out = out.sort_values(["vote_average", "vote_count"], ascending=[False, False])

    cols = ["title", "release_date", "genres", "cast", "vote_average", "vote_count", "popularity"]
    logger.info("search1_bruce_willis_scifi_action: rows=%s", len(out))
    return out.loc[:, cols]


def search2_uma_thurman_tarantino(df: pd.DataFrame) -> pd.DataFrame:
    """
    Movies starring Uma Thurman, directed by Quentin Tarantino,
    sorted by runtime asc.
    """
    _require_cols(df, ["cast", "director", "runtime", "title", "release_date", "vote_average", "vote_count"],
                 "search2_uma_thurman_tarantino")

    out = df.copy()
    mask = _has_token_pipecol(out["cast"], "Uma Thurman") & _contains_text(out["director"], "Quentin Tarantino")
    out = out.loc[mask].copy()

    out = out.sort_values("runtime", ascending=True)

    cols = ["title", "release_date", "runtime", "director", "cast", "vote_average", "vote_count"]
    logger.info("search2_uma_thurman_tarantino: rows=%s", len(out))
    return out.loc[:, cols]