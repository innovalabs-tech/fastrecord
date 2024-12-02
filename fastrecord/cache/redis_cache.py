from typing import Any, Optional
from datetime import timedelta
import json
from redis import Redis
from .base import CacheBackend


class RedisCache(CacheBackend):
    def __init__(self, url: str = "redis://localhost:6379/0"):
        self.redis = Redis.from_url(url)

    def get(self, key: str) -> Optional[Any]:
        value = self.redis.get(key)
        return json.loads(value) if value else None

    def set(self, key: str, value: Any, ttl: Optional[timedelta] = None):
        serialized = json.dumps(value)
        if ttl:
            self.redis.setex(key, ttl, serialized)
        else:
            self.redis.set(key, serialized)

    def delete(self, key: str):
        self.redis.delete(key)

    def clear(self):
        self.redis.flushdb()
