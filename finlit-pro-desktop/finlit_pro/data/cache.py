"""A small on-disk JSON cache.

Two jobs: keep us well inside Yahoo's and the SEC's rate limits, and let the
app keep working offline by falling back to the last good copy of anything it
has seen before. Entries are never deleted on expiry, only ignored, precisely
so that the stale copy is still there when the network is not.
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from pathlib import Path
from typing import Any

from finlit_pro.config import app_dir


class DiskCache:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or (app_dir("cache") / "http")
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        digest = hashlib.sha1(key.encode("utf-8")).hexdigest()
        return self.root / f"{digest}.json"

    def get(self, key: str, max_age_s: float | None) -> tuple[Any, float] | None:
        """Return (value, saved_at) if present and younger than max_age_s.

        max_age_s=None accepts any age, which is the offline fallback.
        """
        path = self._path(key)
        try:
            entry = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        saved_at = float(entry.get("saved_at", 0))
        if max_age_s is not None and time.time() - saved_at > max_age_s:
            return None
        return entry.get("value"), saved_at

    def put(self, key: str, value: Any) -> None:
        path = self._path(key)
        # First Version: every writer used "<digest>.tmp", so two threads saving the
        # same key at once (the price load and the Returns view both fetching the
        # benchmark) could interleave their writes and corrupt the saved copy.
        # Current Version: each process and thread writes its own temporary file.
        tmp = path.with_name(f"{path.stem}.{os.getpid()}.{threading.get_ident()}.tmp")
        try:
            tmp.write_text(json.dumps({"saved_at": time.time(), "key": key, "value": value}), encoding="utf-8")
            tmp.replace(path)
        except OSError:
            # A full disk should cost us the cache, not the request.
            pass

    def clear(self) -> int:
        count = 0
        for path in self.root.glob("*.json"):
            try:
                path.unlink()
                count += 1
            except OSError:
                pass
        return count
