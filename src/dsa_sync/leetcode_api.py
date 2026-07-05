"""LeetCode public API client: number->slug cache and per-problem topic tag lookup.

Only anonymous requests to leetcode.com/api/problems/all/ and leetcode.com/graphql
are made here. Any unexpected response shape raises LeetCodeAPIError so callers can
fall back to fully-offline manual entry.
"""

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from .config import CACHE_PATH
from .exceptions import LeetCodeAPIError

ALL_PROBLEMS_URL = "https://leetcode.com/api/problems/all/"
GRAPHQL_URL = "https://leetcode.com/graphql"
REQUEST_TIMEOUT_SECONDS = 10
CACHE_MAX_AGE_SECONDS = 30 * 24 * 60 * 60

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://leetcode.com",
    "Content-Type": "application/json",
}

_DIFFICULTY_BY_LEVEL = {1: "Easy", 2: "Medium", 3: "Hard"}

_QUESTION_QUERY = """
query getQuestion($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionFrontendId
    title
    titleSlug
    difficulty
    topicTags { name }
  }
}
"""


@dataclass
class CachedProblem:
    """A minimal cached record mapping a problem number to its slug/title/difficulty."""

    slug: str
    title: str
    difficulty: str


@dataclass
class ProblemDetails:
    """Full per-problem details fetched from the GraphQL endpoint."""

    number: int
    title: str
    slug: str
    difficulty: str
    topics: list[str]


def _request_with_retry(method: str, url: str, **kwargs: Any) -> requests.Response:
    """Perform a request with one retry on failure."""
    last_exc: Exception | None = None
    for attempt in range(2):
        try:
            response = requests.request(method, url, timeout=REQUEST_TIMEOUT_SECONDS, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            last_exc = exc
            if attempt == 0:
                time.sleep(0.5)
    raise LeetCodeAPIError(f"Request to {url} failed: {last_exc}") from last_exc


def _load_cache() -> dict[str, Any]:
    if not CACHE_PATH.exists():
        return {}
    try:
        with CACHE_PATH.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}


def _save_cache(cache: dict[str, Any]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = CACHE_PATH.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as fh:
        json.dump(cache, fh, indent=2)
    tmp_path.replace(CACHE_PATH)


def _cache_is_stale(cache: dict[str, Any]) -> bool:
    fetched_at = cache.get("fetched_at")
    if not isinstance(fetched_at, (int, float)):
        return True
    return (time.time() - fetched_at) > CACHE_MAX_AGE_SECONDS


def _parse_all_problems(payload: Any) -> dict[str, dict[str, Any]]:
    """Parse the /api/problems/all/ payload into {number_str: {slug, title, difficulty}}."""
    if not isinstance(payload, dict):
        raise LeetCodeAPIError("Unexpected response shape from problems.all endpoint.")
    pairs = payload.get("stat_status_pairs")
    if not isinstance(pairs, list):
        raise LeetCodeAPIError("Missing 'stat_status_pairs' in problems.all response.")

    problems: dict[str, dict[str, Any]] = {}
    for pair in pairs:
        try:
            stat = pair["stat"]
            number = stat["frontend_question_id"]
            title = stat["question__title"]
            slug = stat["question__title_slug"]
            level = pair["difficulty"]["level"]
        except (KeyError, TypeError) as exc:
            raise LeetCodeAPIError("Unexpected item shape in stat_status_pairs.") from exc
        problems[str(number)] = {
            "slug": slug,
            "title": title,
            "difficulty": _DIFFICULTY_BY_LEVEL.get(level, "Unknown"),
        }
    return problems


def refresh_cache() -> dict[str, dict[str, Any]]:
    """Fetch the full problem list and overwrite the local cache. Raises LeetCodeAPIError on failure."""
    response = _request_with_retry("GET", ALL_PROBLEMS_URL, headers=_HEADERS)
    try:
        payload = response.json()
    except (json.JSONDecodeError, ValueError) as exc:
        raise LeetCodeAPIError("Response from problems.all endpoint was not valid JSON.") from exc

    problems = _parse_all_problems(payload)
    cache = {"fetched_at": time.time(), "problems": problems}
    _save_cache(cache)
    return problems


def get_cached_problem(number: int) -> CachedProblem | None:
    """Look up a problem by number, refreshing the cache if missing or stale.

    Returns None (rather than raising) if the network is unavailable, signalling
    callers to fall back to offline manual entry.
    """
    cache = _load_cache()
    key = str(number)
    problems = cache.get("problems", {})

    if key not in problems or _cache_is_stale(cache):
        try:
            problems = refresh_cache()
        except LeetCodeAPIError:
            if key not in problems:
                return None

    entry = problems.get(key)
    if entry is None:
        return None
    return CachedProblem(slug=entry["slug"], title=entry["title"], difficulty=entry["difficulty"])


def fetch_problem_details(number: int, slug: str) -> ProblemDetails | None:
    """Fetch topic tags and canonical metadata for a single problem via GraphQL.

    Returns None if the request fails or the response shape is unexpected.
    """
    body = {"query": _QUESTION_QUERY, "variables": {"titleSlug": slug}}
    try:
        response = _request_with_retry("POST", GRAPHQL_URL, json=body, headers=_HEADERS)
        payload = response.json()
    except (LeetCodeAPIError, json.JSONDecodeError, ValueError):
        return None

    question = payload.get("data", {}).get("question") if isinstance(payload, dict) else None
    if not isinstance(question, dict):
        return None

    topics_raw = question.get("topicTags") or []
    topics = [t.get("name") for t in topics_raw if isinstance(t, dict) and t.get("name")]

    try:
        return ProblemDetails(
            number=number,
            title=question["title"],
            slug=question.get("titleSlug", slug),
            difficulty=question.get("difficulty", "Unknown"),
            topics=topics,
        )
    except KeyError:
        return None
