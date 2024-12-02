import threading
from datetime import datetime, timedelta
from typing import Any, Optional, Dict

from .base import CacheBackend


class MemoryCache(CacheBackend):
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._cache:
                return None

            cache_data = self._cache[key]
            if self._is_expired(cache_data):
                del self._cache[key]
                return None

            return cache_data['value']

    def set(self, key: str, value: Any, ttl: Optional[timedelta] = None):
        with self._lock:
            expires_at = datetime.utcnow() + ttl if ttl else None
            self._cache[key] = {
                'value': value,
                'expires_at': expires_at
            }

    def delete(self, key: str):
        with self._lock:
            self._cache.pop(key, None)

    def clear(self):
        with self._lock:
            self._cache.clear()

    def _is_expired(self, cache_data: Dict[str, Any]) -> bool:
        expires_at = cache_data.get('expires_at')
        return expires_at and expires_at < datetime.utcnow()