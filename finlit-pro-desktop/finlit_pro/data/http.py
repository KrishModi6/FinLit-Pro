"""The one place that talks to the network.

Every request goes through here and gets: a per-host rate limit, retries
with backoff on 429 and 5xx, a timeout, the on-disk cache, an optional
stale-copy fallback, and a DataError whose message says what to do next.
A 404 the caller expects becomes NotFoundError, and a timeout or a failed
connection becomes NetworkError, so callers can tell "it does not exist"
and "the network is down" apart from other failures without reading text.

Rate limits are conservative on purpose. The SEC publishes a fair-access
limit of 10 requests per second; we stay at 5. Yahoo publishes none for
these endpoints, which are unofficial, so we stay at 2 per second and cache
aggressively.
"""

from __future__ import annotations

import re
import threading
import time
from collections.abc import Callable
from typing import Any
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from finlit_pro import __version__
from finlit_pro.data.cache import DiskCache
from finlit_pro.data.models import CACHE, LIVE, STALE, DataError, NetworkError, NotFoundError

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    f"(KHTML, like Gecko) Chrome/124.0 Safari/537.36 FinLitPro/{__version__}"
)

RATE_LIMITS = {"sec.gov": 5.0, "yahoo.com": 2.0}  # requests per second, by domain suffix
# (connect, read) seconds. The read timeout is the longest wait for the next bytes, not for the whole body.
TIMEOUT = (5.0, 15.0)
TEXT_TIMEOUT = (5.0, 30.0)  # filed documents can be several megabytes

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
        # First Version: Retry(total=3) and a single 15 s timeout retried a failed
        # connection or a silent server three times, so a host that accepted the
        # connection and never answered cost about 65 s, and the price chain about
        # 260 s. Current Version: a failed connection or read is retried once (with
        # the 5 s connect / 15 s read timeouts above); HTTP 429 and 5xx keep three
        # retries with backoff, honouring Retry-After.
        retry = Retry(
            total=3,
            connect=1,
            read=1,
            other=1,
            status=3,
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


Timeout = float | tuple[float, float]


def _request(url: str, headers: dict[str, str] | None, timeout_s: Timeout, not_found: str | None, service: str) -> requests.Response:
    limiter = limiter_for(url)
    if limiter:
        limiter.wait()
    try:
        resp = _session().get(url, headers=headers or {"User-Agent": BROWSER_UA}, timeout=timeout_s)
    except requests.exceptions.Timeout:
        raise NetworkError(f"{service} took too long to respond. Check the internet connection, then try again.") from None
    except requests.exceptions.RetryError as exc:
        if re.search(r"too many 5\d\d", str(exc)):
            raise DataError(f"{service} is having trouble right now (server errors). Try again in a few minutes.") from None
        raise DataError(f"{service} is rate limiting requests. Wait a minute, then refresh.") from None
    except requests.exceptions.ConnectionError as exc:
        if "timed out" in str(exc).lower():  # a read timeout after its retry arrives as ConnectionError
            raise NetworkError(f"{service} took too long to respond. Check the internet connection, then try again.") from None
        raise NetworkError(f"Could not reach {service}. Check the internet connection, then try again.") from None
    except requests.exceptions.RequestException as exc:
        raise DataError(f"The request to {service} failed ({exc.__class__.__name__}). Try again in a moment.") from None
    if resp.status_code == 404 and not_found:
        raise NotFoundError(not_found)
    if resp.status_code in (401, 403):
        hint = " Set the SEC contact email in Settings." if "sec.gov" in url else ""
        raise DataError(f"{service} refused the request (HTTP {resp.status_code}).{hint}")
    if resp.status_code == 429:
        raise DataError(f"{service} is rate limiting requests. Wait a minute, then refresh.")
    if resp.status_code >= 400:
        raise DataError(f"{service} returned HTTP {resp.status_code}. Try again later.")
    return resp


def get_json(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    ttl_s: float = 300,
    timeout_s: Timeout = TIMEOUT,
    not_found_message: str | None = None,
    service: str = "the data provider",
    allow_stale: bool = True,
    cache_key: str | None = None,
    check: Callable[[Any], object] | None = None,
) -> Fetched:
    """JSON from `url`, through the cache.

    cache_key stores the response under a logical name instead of the URL, for
    URLs that change over time but name the same data (Yahoo's period2 is "now").
    A NotFoundError is never hidden behind an old copy: the provider has said the
    thing does not exist. ttl_s of 0 or less asks the network without reading
    the cache first.

    First Version: any JSON that came back was saved, readable or not. With a
    stable cache_key, one HTTP 200 with an empty history replaced the only good
    copy: it was served as a fresh copy for 15 minutes, and offline the app then
    had no price data at all. Current Version: `check`, when given, is called with
    the payload before it is saved and raises DataError when the payload cannot be
    used; such a payload is never saved and counts as a failed request.
    """
    key = cache_key or url
    store = cache()
    fresh = store.get(key, ttl_s) if ttl_s > 0 else None
    if fresh is not None:
        return Fetched(fresh[0], CACHE, fresh[1], url)
    try:
        resp = _request(url, headers, timeout_s, not_found_message, service)
        try:
            value = resp.json()
        except ValueError:
            raise DataError(f"{service} returned data that could not be read. Try again later.") from None
        if check is not None:
            check(value)
    except NotFoundError:
        raise
    except DataError:
        stale = store.get(key, None) if allow_stale else None
        if stale is not None:
            return Fetched(stale[0], STALE, stale[1], url)
        raise
    store.put(key, value)
    return Fetched(value, LIVE, time.time(), url)


def get_text(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    ttl_s: float = 7 * 86400,
    timeout_s: Timeout = TEXT_TIMEOUT,
    service: str = "the data provider",
    not_found_message: str | None = None,
    cache_key: str | None = None,
) -> Fetched:
    """Text documents (SEC filings). Filed documents never change, so they cache for a week."""
    key = "text:" + (cache_key or url)
    store = cache()
    fresh = store.get(key, ttl_s)
    if fresh is not None:
        return Fetched(fresh[0], CACHE, fresh[1], url)
    try:
        resp = _request(url, headers, timeout_s, not_found_message, service)
    except NotFoundError:
        raise
    except DataError:
        stale = store.get(key, None)
        if stale is not None:
            return Fetched(stale[0], STALE, stale[1], url)
        raise
    resp.encoding = resp.encoding or "utf-8"
    store.put(key, resp.text)
    return Fetched(resp.text, LIVE, time.time(), url)
