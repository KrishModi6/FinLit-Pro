"""The one place that talks to the network.

Every request goes through here and gets: a per-host rate limit, retries
with backoff on 429 and 5xx, a timeout, the on-disk cache, an optional
stale-copy fallback, and a DataError whose message says what to do next.

Rate limits are conservative on purpose. The SEC publishes a fair-access
limit of 10 requests per second; we stay at 5. Yahoo publishes none for
these endpoints, which are unofficial, so we stay at 2 per second and cache
aggressively.
"""

from __future__ import annotations

import threading
import time
from typing import Any
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from finlit_pro import __version__
from finlit_pro.data.cache import DiskCache
from finlit_pro.data.models import CACHE, LIVE, STALE, DataError

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    f"(KHTML, like Gecko) Chrome/124.0 Safari/537.36 FinLitPro/{__version__}"
)

RATE_LIMITS = {"sec.gov": 5.0, "yahoo.com": 2.0}  # requests per second, by domain suffix

_local = threading.local()
_cache: DiskCache | None = None


class RateLimiter:
    """Thread-safe minimum spacing between requests to one domain."""

    def __init__(self, per_second: float) -> None:
        self.interval = 1.0 / per_second
        self.lock = threading.Lock()
        self.next_at = 0.0

    def wait(self) -> None:
        with self.lock:
            now = time.monotonic()
            delay = self.next_at - now
            self.next_at = max(now, self.next_at) + self.interval
        if delay > 0:
            time.sleep(delay)


_limiters: dict[str, RateLimiter] = {}
_limiters_lock = threading.Lock()


def limiter_for(url: str) -> RateLimiter | None:
    host = urlparse(url).hostname or ""
    for suffix, rate in RATE_LIMITS.items():
        if host == suffix or host.endswith("." + suffix):
            with _limiters_lock:
                return _limiters.setdefault(suffix, RateLimiter(rate))
    return None


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
    # requests.Session is not thread safe and the UI fetches in parallel.
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
    """A payload plus how it was obtained."""

    def __init__(self, value: Any, status: str, saved_at: float, url: str) -> None:
        self.value = value
        self.status = status  # LIVE, CACHE or STALE
        self.saved_at = saved_at
        self.url = url


def _request(url: str, headers: dict[str, str] | None, timeout_s: float, not_found: str | None, service: str) -> requests.Response:
    limiter = limiter_for(url)
    if limiter:
        limiter.wait()
    try:
        resp = _session().get(url, headers=headers or {"User-Agent": BROWSER_UA}, timeout=timeout_s)
    except requests.exceptions.Timeout:
        raise DataError(f"{service} took too long to respond. Check the connection and try again.") from None
    except requests.exceptions.RetryError:
        raise DataError(f"{service} is rate limiting requests. Wait a minute, then refresh.") from None
    except requests.exceptions.ConnectionError:
        raise DataError(f"Could not reach {service}. Check the internet connection.") from None
    except requests.exceptions.RequestException as exc:
        raise DataError(f"The request to {service} failed ({exc.__class__.__name__}).") from None
    if resp.status_code == 404 and not_found:
        raise DataError(not_found)
    if resp.status_code in (401, 403):
        hint = " Set the SEC contact email in Settings." if "sec.gov" in url else ""
        raise DataError(f"{service} refused the request (HTTP {resp.status_code}).{hint}")
    if resp.status_code == 429:
        raise DataError(f"{service} is rate limiting requests. Wait a minute, then refresh.")
    if resp.status_code >= 400:
        raise DataError(f"{service} returned HTTP {resp.status_code}.")
    return resp


def get_json(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    ttl_s: float = 300,
    timeout_s: float = 15,
    not_found_message: str | None = None,
    service: str = "the data provider",
    allow_stale: bool = True,
) -> Fetched:
    store = cache()
    fresh = store.get(url, ttl_s)
    if fresh is not None:
        return Fetched(fresh[0], CACHE, fresh[1], url)
    try:
        resp = _request(url, headers, timeout_s, not_found_message, service)
        try:
            value = resp.json()
        except ValueError:
            raise DataError(f"{service} returned data that could not be read.") from None
    except DataError as exc:
        if not_found_message and str(exc) == not_found_message:
            raise
        stale = store.get(url, None) if allow_stale else None
        if stale is not None:
            return Fetched(stale[0], STALE, stale[1], url)
        raise
    store.put(url, value)
    return Fetched(value, LIVE, time.time(), url)


def get_text(url: str, *, headers: dict[str, str] | None = None, ttl_s: float = 7 * 86400, timeout_s: float = 30, service: str = "the data provider") -> Fetched:
    """Text documents (SEC filings). Filed documents never change, so they cache for a week."""
    store = cache()
    fresh = store.get("text:" + url, ttl_s)
    if fresh is not None:
        return Fetched(fresh[0], CACHE, fresh[1], url)
    try:
        resp = _request(url, headers, timeout_s, None, service)
    except DataError:
        stale = store.get("text:" + url, None)
        if stale is not None:
            return Fetched(stale[0], STALE, stale[1], url)
        raise
    resp.encoding = resp.encoding or "utf-8"
    store.put("text:" + url, resp.text)
    return Fetched(resp.text, LIVE, time.time(), url)
