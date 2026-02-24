from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from src.logging_utils import get_logger
from src.config import Paths

logger = get_logger()


# ----------------------
# Helpers  
# ----------------------
def empty_to_nan(x: Any) -> Any:
    if x is None:
        return np.nan
    if isinstance(x, str) and x.strip() == "":
        return np.nan
    return x


def pipe_from_array(arr: Any, field: str = "name") -> Any:
    """
    Convert a list of dicts into a |-delimited string from a given field.
    """
    if not isinstance(arr, list) or len(arr) == 0:
        return np.nan
    vals = []
    for item in arr:
        if isinstance(item, dict):
            v = item.get(field)
            v = empty_to_nan(v)
            if pd.notna(v):
                vals.append(str(v))
    return "|".join(vals) if vals else np.nan


def zero_to_nan(series: pd.Series) -> pd.Series:
    return series.mask(series == 0, np.nan)


def nullify_text_placeholders(series: pd.Series, placeholders: Optional[List[str]] = None) -> pd.Series:
    if placeholders is None:
        placeholders = ["no data", "n/a", "na", "none", "null", "tbd", "unknown", ""]
    s = series.astype("string")
    s_clean = s.str.strip().str.lower()
    return series.mask(s_clean.isin([p.lower() for p in placeholders]), np.nan)


def add_musd_columns(df: pd.DataFrame) -> pd.DataFrame:
    df["budget_musd"] = df["budget"] / 1_000_000
    df["revenue_musd"] = df["revenue"] / 1_000_000
    return df


def nullify_vote_average_when_no_votes(df: pd.DataFrame) -> pd.DataFrame:
    df.loc[df["vote_count"].fillna(0).astype("int64") == 0, "vote_average"] = np.nan
    return df


def parse_director(crew: Any) -> Any:
    """
    crew is expected to be a list of dicts from credits['crew'].
    """
    if not isinstance(crew, list):
        return np.nan
    for person in crew:
        if isinstance(person, dict) and person.get("job") == "Director":
            name = person.get("name")
            return empty_to_nan(name)
    return np.nan


def parse_cast(cast: Any, top_n: int = 30) -> Any:
    if not isinstance(cast, list) or len(cast) == 0:
        return np.nan
    # TMDb cast often has 'order'. If not, keep given order.
    def order_key(x):
        if isinstance(x, dict):
            return x.get("order", 10**9)
        return 10**9

    cast_sorted = sorted([c for c in cast if isinstance(c, dict)], key=order_key)
    names = []
    for person in cast_sorted[:top_n]:
        n = empty_to_nan(person.get("name"))
        if pd.notna(n):
            names.append(str(n))
    return "|".join(names) if names else np.nan


# ----------------------
# Bronze reader
# ----------------------
def read_bronze_json(bronze_dir: str | Path) -> pd.DataFrame:
    """
    Read TMDB Bronze JSON files (one per movie) into a pandas DataFrame.

    Expected each file contains a bundle:
      { "movie": {...}, "credits": {...}, "fetched_at": <int> }

    Returns a DataFrame with columns: movie_id, fetched_at, movie, credits, source_file
    Raises ValueError if no records found.
    """
    bronze_dir = Path(bronze_dir)
    logger.info("read_bronze_json: reading bronze JSON from %s", bronze_dir)

    if not bronze_dir.exists():
        raise ValueError(f"Bronze directory does not exist: {bronze_dir}")

    files = sorted(bronze_dir.glob("*.json"))
    logger.info("read_bronze_json: found %s json files", len(files))

    records: List[Dict[str, Any]] = []

    for fp in files:
        try:
            with fp.open("r", encoding="utf-8") as f:
                bundle = json.load(f)

            movie = bundle.get("movie") or {}
            credits = bundle.get("credits") 
            fetched_at = bundle.get("fetched_at")

            # movie id best-effort
            movie_id = None
            if isinstance(movie, dict):
                movie_id = movie.get("id")

            records.append(
                {
                    "movie_id": movie_id,
                    "fetched_at": fetched_at,
                    "movie": movie,
                    "credits": credits,
                    "source_file": fp.name,
                }
            )

        except Exception:
            logger.exception("read_bronze_json: failed reading %s", fp)
            raise

    if not records:
        msg = f"read_bronze_json: No JSON records found in path: {bronze_dir}"
        logger.error(msg)
        raise ValueError(msg)

    df = pd.DataFrame.from_records(records)
    logger.info("read_bronze_json: loaded records=%s columns=%s", len(df), list(df.columns))
    return df


# ----------------------
# Silver builder  
# ----------------------
def build_silver(df_bronze: pd.DataFrame) -> pd.DataFrame:
    """
    Build the Silver movies table from TMDB Bronze bundles.

    Expects df_bronze columns: movie (dict), credits (dict), fetched_at, source_file
    """
    if "movie" not in df_bronze.columns:
        raise ValueError("build_silver: missing required column 'movie'")

    logger.info("build_silver: flattening movie fields")

    # Flatten movie dict into columns
    movie_df = df_bronze["movie"].apply(lambda x: x if isinstance(x, dict) else {}).apply(pd.Series)

    out = pd.DataFrame()
    out["id"] = pd.to_numeric(movie_df.get("id"), errors="coerce")
    out["title"] = movie_df.get("title")
    out["release_date"] = pd.to_datetime(movie_df.get("release_date"), errors="coerce").dt.date
    out["original_language"] = movie_df.get("original_language")

    # Raw nested fields
    out["_belongs_to_collection_raw"] = movie_df.get("belongs_to_collection")
    out["_genres_raw"] = movie_df.get("genres")
    out["_spoken_languages_raw"] = movie_df.get("spoken_languages")
    out["_production_countries_raw"] = movie_df.get("production_countries")
    out["_production_companies_raw"] = movie_df.get("production_companies")

    out["budget"] = pd.to_numeric(movie_df.get("budget"), errors="coerce")
    out["revenue"] = pd.to_numeric(movie_df.get("revenue"), errors="coerce")
    out["runtime"] = pd.to_numeric(movie_df.get("runtime"), errors="coerce")
    out["vote_count"] = pd.to_numeric(movie_df.get("vote_count"), errors="coerce")
    out["vote_average"] = pd.to_numeric(movie_df.get("vote_average"), errors="coerce")
    out["popularity"] = pd.to_numeric(movie_df.get("popularity"), errors="coerce")

    out["overview"] = movie_df.get("overview")
    out["tagline"] = movie_df.get("tagline")
    out["poster_path"] = movie_df.get("poster_path")
    out["status"] = movie_df.get("status")

    # Clean / extract JSON-like columns
    out["belongs_to_collection"] = out["_belongs_to_collection_raw"].apply(
        lambda d: empty_to_nan(d.get("name")) if isinstance(d, dict) else np.nan
    )
    out["genres"] = out["_genres_raw"].apply(lambda arr: pipe_from_array(arr, field="name"))
    out["spoken_languages"] = out["_spoken_languages_raw"].apply(lambda arr: pipe_from_array(arr, field="english_name"))
    out["production_countries"] = out["_production_countries_raw"].apply(lambda arr: pipe_from_array(arr, field="name"))
    out["production_companies"] = out["_production_companies_raw"].apply(lambda arr: pipe_from_array(arr, field="name"))

    # Credits features
    credits_series = df_bronze.get("credits")
    if credits_series is None:
        out["cast"] = np.nan
        out["cast_size"] = np.nan
        out["director"] = np.nan
        out["crew_size"] = np.nan
    else:
        cast_arr = credits_series.apply(lambda c: (c or {}).get("cast") if isinstance(c, dict) else None)
        crew_arr = credits_series.apply(lambda c: (c or {}).get("crew") if isinstance(c, dict) else None)

        out["director"] = crew_arr.apply(parse_director)
        out["cast"] = cast_arr.apply(lambda arr: parse_cast(arr, top_n=30))
        out["cast_size"] = cast_arr.apply(lambda arr: len(arr) if isinstance(arr, list) else np.nan)
        out["crew_size"] = crew_arr.apply(lambda arr: len(arr) if isinstance(arr, list) else np.nan)

    # Clean text placeholders
    out["overview"] = nullify_text_placeholders(out["overview"])
    out["tagline"] = nullify_text_placeholders(out["tagline"])

    # Replace unrealistic 0s with NaN
    for c in ["budget", "revenue", "runtime"]:
        out[c] = zero_to_nan(out[c])

    # vote_average null when no votes
    out = nullify_vote_average_when_no_votes(out)

    # Add musd columns
    out = add_musd_columns(out)

    # Remove duplicates and bad ids/titles
    out["title"] = out["title"].apply(empty_to_nan)
    out = out.dropna(subset=["id", "title"])
    out = out[out["title"].astype("string").str.strip() != ""]
    out = out.drop_duplicates(subset=["id"], keep="first")

    # Keep only rows with at least 10 non-null columns
    non_null_count = out.notna().sum(axis=1)
    out = out.loc[non_null_count >= 10].copy()

    # Filter Released, then drop status
    out = out.loc[out["status"] == "Released"].drop(columns=["status"])

    # Reorder columns 
    ordered_cols = [
        "id", "title", "tagline", "release_date",
        "genres", "belongs_to_collection", "original_language",
        "budget_musd", "revenue_musd", "production_companies",
        "production_countries", "vote_count", "vote_average",
        "popularity", "runtime", "overview", "spoken_languages",
        "poster_path", "cast", "cast_size", "director", "crew_size",
    ]
    # keep only existing
    out = out[[c for c in ordered_cols if c in out.columns]].reset_index(drop=True)

    logger.info("build_silver: done rows=%s cols=%s", len(out), len(out.columns))
    return out


def main() -> None:
    paths = Paths().ensure()
    df_bronze = read_bronze_json(paths.bronze_dir)
    df_silver = build_silver(df_bronze)

    out_path = paths.silver_dir / "tmdb_movies_silver.parquet"
    paths.silver_dir.mkdir(parents=True, exist_ok=True)
    df_silver.to_parquet(out_path, index=False)
    logger.info("Saved silver to %s", out_path)


if __name__ == "__main__":
    main()