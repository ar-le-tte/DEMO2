from __future__ import annotations

import time
import requests
from typing import Any, Optional, Dict

from src.logging_utils import get_logger

logger = get_logger()

BASE_URL = "https://api.themoviedb.org/3"


def get_tmdb_json(url: str, api_key: str, params: Optional[dict] = None, timeout: int = 30,
    session: Optional[requests.Session] = None,  max_retries: int = 3,  backoff_sec: float = 1.0,
) -> Optional[dict]:
    """
    GET a TMDB endpoint and return JSON dict, or None if request fails.
    Retries lightly on 429 and 5xx.
    """
    p = dict(params or {})
    p["api_key"] = api_key

    s = session or requests.Session()
    r = None 

    for attempt in range(1, max_retries + 1):
        try:
            r = s.get(url, params=p, timeout=timeout)
            if r.status_code == 404:
                logger.warning(
                    "TMDB 404 Not Found: url=%s params=%s",
                    url, {k: v for k, v in p.items() if k != "api_key"},
                )
                return None
            # retry on rate limit / server errors
            if r.status_code in (429, 500, 502, 503, 504):
                logger.warning(
                    "TMDB retryable status=%s attempt=%s/%s url=%s",
                    r.status_code, attempt, max_retries, url,
                )
                if attempt < max_retries:
                    time.sleep(backoff_sec * attempt)
                    continue
                return None
            r.raise_for_status()
            return r.json()
        except requests.Timeout:
            logger.error("TMDB Timeout: url=%s timeout=%ss attempt=%s/%s", url, timeout, attempt, max_retries)
            if attempt < max_retries:
                time.sleep(backoff_sec * attempt)
                continue
            return None
        except requests.RequestException as e:
            status = getattr(r, "status_code", None)
            body = None
            try:
                body = r.json() if r is not None else None
            except Exception:
                body = r.text if r is not None else None
            logger.error("TMDB RequestException status=%s url=%s error=%s response=%s", status, url, str(e), body)
            return None
        except Exception:
            logger.exception("TMDB Unexpected error: url=%s", url)
            return None


def fetch_movie_with_credits(
    movie_id: int,
    api_key: str,
    sleep_time: float = 0.25,
    session: Optional[requests.Session] = None,
) -> Optional[Dict[str, Any]]:
    """
    Fetch TMDB movie details + credits bundle.
    Returns None if details not found or request fails.
    """
    details_url = f"{BASE_URL}/movie/{movie_id}"
    credits_url = f"{BASE_URL}/movie/{movie_id}/credits"

    s = session or requests.Session()

    try:
        details = get_tmdb_json(details_url, api_key, session=s)
        if not details:
            logger.warning("Movie not found or failed fetch: movie_id=%s", movie_id)
            return None

        credits = get_tmdb_json(credits_url, api_key, session=s)

        bundle = {
            "movie": details,
            "credits": credits,
            "fetched_at": int(time.time()),
        }

        logger.info("Fetched movie bundle: movie_id=%s credits_ok=%s", movie_id, credits is not None)
        return bundle

    except Exception:
        logger.exception("fetch_movie_with_credits failed: movie_id=%s", movie_id)
        return None

    finally:
        if sleep_time:
            time.sleep(sleep_time)