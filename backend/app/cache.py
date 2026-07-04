"""
Lightweight in-memory TTL cache.

Good enough for a single-instance deployment (Render/Railway free tier).
If you scale to multiple instances, swap this for Redis without changing
the call sites (get/set/make_key).
"""
import time
import hashlib
import json
from threading import Lock
from typing import Any, Optional


class TTLCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            expires_at, value = entry
            if time.time() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._store[key] = (time.time() + self.ttl, value)

    @staticmethod
    def make_key(*parts: str) -> str:
        raw = json.dumps(parts, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()


research_cache = TTLCache()
