"""One place that talks to the network.

Every outbound request goes through `get_json`, which adds retries with
backoff, a timeout, the cache, and the offline fallback, and turns every
failure into a DataError with a sentence the user can act on.
"""

from __future__ import annotations

import threading
import time
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from finlit_quant import __version__
from finlit_quant.data.cache import DiskCache
from finlit_quant.data.models import DataError

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    f"(KHTML, like Gecko) Chrome/124.0 Safari/537.36 FinLitQuant/{__version__}"
)

_local = threading.local()
_cache: DiskCache | None = None


def cache() -> DiskCache:
    global _cache
    if _cache is None:
        _cache = DiskCache()
    return _cache


def set_cache(instance: DiskCache) -> None:
    """Tests point the cache at a temporary folder."""
    global _cache
    _cache = instance


def _session() -> requests.Session:
    # requests.Session is not thread safe, and the UI fetches in parallel.
    session = getattr(_local, "session", None)
    if session is None:
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.8,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
            respect_retry_after_header=True,
        )
        session.mount("https://", HTTPAdapter(max_retries=retry))
        _local.session = session
    return session


class Fetched:
    """A JSON payload plus where it came from."""

    def __init__(self, value: Any, source: str, saved_at: float) -> None:
        self.value = value
        self.source = source  # "live", "cache" or "stale"
        self.saved_at = saved_at

    @property
    def age_s(self) -> float:
        return max(0.0, time.time() - self.saved_at)


def get_json(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    ttl_s: float = 300,
    timeout_s: float = 12,
    not_found_message: str | None = None,
    service: str = "the data provider",
) -> Fetched:
    store = cache()
    fresh = store.get(url, ttl_s)
    if fresh is not None:
        return Fetched(fresh[0], "cache", fresh[1])

    try:
        resp = _session().get(url, headers=headers or {"User-Agent": BROWSER_UA}, timeout=timeout_s)
    except requests.exceptions.Timeout:
        return _fallback(url, f"{service} took too long to answer. Check your connection and try again.")
    except requests.exceptions.ConnectionError:
        return _fallback(url, f"Could not reach {service}. Check your internet connection and try again.")
    except requests.exceptions.RetryError:
        return _fallback(url, f"{service} is rate limiting requests right now. Wait a minute and try again.")
    except requests.exceptions.RequestException as exc:
        return _fallback(url, f"The request to {service} failed ({exc.__class__.__name__}). Try again.")

    if resp.status_code == 404 and not_found_message:
        raise DataError(not_found_message)
    if resp.status_code == 403:
        return _fallback(url, f"{service} refused the request (HTTP 403). If this is the SEC, set your contact email in Settings.")
    if resp.status_code >= 400:
        return _fallback(url, f"{service} returned an error (HTTP {resp.status_code}). Try again in a minute.")

    try:
        value = resp.json()
    except ValueError:
        return _fallback(url, f"{service} sent back something that was not valid data. Try again.")

    store.put(url, value)
    return Fetched(value, "live", time.time())


def _fallback(url: str, message: str) -> Fetched:
    stale = cache().get(url, None)
    if stale is not None:
        return Fetched(stale[0], "stale", stale[1])
    raise DataError(message)
