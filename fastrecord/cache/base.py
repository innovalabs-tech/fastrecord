import hashlib
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Optional

from . import MemoryCache, RedisCache
from .disabled import DisabledCache
from ..config import get_settings, FastRecordSettings


class CacheBackend(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[timedelta] = None):
        pass

    @abstractmethod
    def delete(self, key: str):
        pass

    @abstractmethod
    def clear(self):
        pass


class CacheManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.enabled = get_settings().CACHE_ENABLED

        if self.enabled:
            if get_settings().CACHE_TYPE == "redis":
                self.backend = RedisCache(get_settings().CACHE_REDIS_URL)
            else:
                self.backend = MemoryCache()
        else:
            self.backend = DisabledCache()

        self.default_ttl = timedelta(seconds=get_settings().CACHE_DEFAULT_TTL)
        self.version = get_settings().CACHE_VERSION
        self._initialized = True

    def generate_key(self, model: str, query_hash: str) -> str:
        """Generate a cache key"""
        components = [
            get_settings().CACHE_PREFIX,
            self.version,
            model,
            query_hash
        ]
        key = ":".join(components)
        return hashlib.md5(key.encode()).hexdigest()

    def fetch(self, key: str) -> Optional[Any]:
        """Fetch from cache with optional TTL"""
        return self.backend.get(key) if self.enabled else None

    def write(self, key: str, value: Any, ttl: Optional[timedelta] = None):
        """Write to cache with optional TTL"""
        if self.enabled:
            self.backend.set(key, value, ttl or self.default_ttl)

    def delete(self, key: str):
        """Delete from cache"""
        if self.enabled:
            self.backend.delete(key)

    def clear(self):
        """Clear entire cache"""
        if self.enabled:
            self.backend.clear()
