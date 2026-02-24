from __future__ import annotations

from src.config import Paths, Settings, MOVIE_IDS
from src.logging_utils import get_logger
from src.pipeline.extract_bronze import download_movies_parallel
from src.pipeline.build_silver import read_bronze_json, build_silver

logger = get_logger()


def main() -> None:
    paths = Paths().ensure()
    settings = Settings()

    if not settings.tmdb_api_key:
        raise ValueError("TMDB_API_KEY missing. Add it to .env or environment variables.")

    # 1) Bronze extract
    download_movies_parallel(
        movie_ids=MOVIE_IDS,
        out_dir=paths.bronze_dir,
        api_key=settings.tmdb_api_key,
        max_workers=8,
        sleep_between_calls=0.0,
        verbose=True,
    )

    # 2) Silver build
    df_bronze = read_bronze_json(paths.bronze_dir)
    df_silver = build_silver(df_bronze)

    out_path = paths.silver_dir / "tmdb_movies_silver.parquet"
    paths.silver_dir.mkdir(parents=True, exist_ok=True)
    df_silver.to_parquet(out_path, index=False)
    logger.info("Saved silver: %s (rows=%s)", out_path, len(df_silver))


if __name__ == "__main__":
    main()