from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.logging_utils import get_logger
from src.config import Paths
from src.kpis.metrics import add_kpi_columns
from src.kpis.ranking import rank_movies
from src.kpis.search import search1_bruce_willis_scifi_action, search2_uma_thurman_tarantino
from src.kpis.franchise import franchise_vs_standalone, top_franchises
from src.kpis.directors import top_directors

logger = get_logger()


def main() -> None:
    paths = Paths().ensure()

    silver_path = paths.silver_dir / "tmdb_movies_silver.parquet"
    if not silver_path.exists():
        raise FileNotFoundError(f"Silver not found: {silver_path}. Run silver build first.")

    df = pd.read_parquet(silver_path)
    logger.info("Loaded silver: rows=%s cols=%s", len(df), len(df.columns))

    df = add_kpi_columns(df)

    paths.gold_dir.mkdir(parents=True, exist_ok=True)

    # ---- Rankings ----
    rankings = {
        "top_revenue":        ("revenue_musd", 10, False, None),
        "top_budget":         ("budget_musd", 10, False, None),
        "top_profit":         ("profit_musd", 10, False, None),
        "low_profit":         ("profit_musd", 10, True,  None),
        "top_roi_budget_ge_10": ("roi", 10, False, [lambda d: d["budget_musd"] >= 10]),
        "low_roi_budget_ge_10": ("roi", 10, True,  [lambda d: d["budget_musd"] >= 10]),
        "most_voted":         ("vote_count", 10, False, None),
        "highest_rated_votes_ge_10": ("vote_average", 10, False, [lambda d: d["vote_count"] >= 10]),
        "lowest_rated_votes_ge_10":  ("vote_average", 10, True,  [lambda d: d["vote_count"] >= 10]),
        "most_popular":       ("popularity", 10, False, None),
    }

    for name, (metric, n, asc, flt) in rankings.items():
        out = rank_movies(df, metric_col=metric, n=n, ascending=asc, filters=flt,
                          select_cols=["id", "title", "release_date", metric])
        out.to_csv(paths.gold_dir / f"{name}.csv", index=False)
        logger.info("Saved gold ranking: %s", name)

    # ---- Searches ----
    s1 = search1_bruce_willis_scifi_action(df)
    s1.to_csv(paths.gold_dir / "search1_bruce_willis_scifi_action.csv", index=False)

    s2 = search2_uma_thurman_tarantino(df)
    s2.to_csv(paths.gold_dir / "search2_uma_thurman_tarantino.csv", index=False)

    # ---- Franchise vs Standalone ----
    fvs = franchise_vs_standalone(df)
    fvs.to_csv(paths.gold_dir / "franchise_vs_standalone.csv", index=False)

    tf = top_franchises(df, min_movies=2)
    tf.to_csv(paths.gold_dir / "top_franchises.csv", index=False)

    # ---- Directors ----
    td = top_directors(df, min_movies=2)
    td.to_csv(paths.gold_dir / "top_directors.csv", index=False)

    logger.info("build_gold: completed. outputs in %s", paths.gold_dir)


if __name__ == "__main__":
    main()