class DisabledCache(CacheBackend):
    """No-op cache backend for when caching is disabled"""

    def get(self, key: str) -> None:
        return None

    def set(self, key: str, value: Any, ttl: Optional[timedelta] = None):
        pass

    def delete(self, key: str):
        pass

    def clear(self):
        pass

