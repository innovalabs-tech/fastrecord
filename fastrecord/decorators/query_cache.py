# File: fastrecord/decorators/query_cache.py
from typing import Optional, List, TypeVar
from datetime import timedelta

from ..base import FastRecord
from .cache import CacheDecorator

T = TypeVar('T', bound='FastRecord')


class QueryCacheMixin:
    """Mixin to add caching capabilities to QueryChain"""

    def __init__(self):
        self._use_cache = False
        self._cache_ttl = None

    def cache(self, ttl: Optional[int] = None) -> 'QueryChain':
        """Enable caching for this query"""
        self._use_cache = True
        self._cache_ttl = ttl
        return self

    def _execute_cached(self, method_name: str, *args, **kwargs):
        """Execute a query method with caching"""
        if not self._use_cache:
            method = getattr(super(), method_name)
            return method(*args, **kwargs)

            # Generate cache key
            cache_key = self._cache_manager.generate_key(
                f"{self.model_class.__name__}:{method_name}",
                f"{self.query_builder._where_values}:{self.query_builder._order_values}:" \
                f"{self.query_builder._limit_value}:{self.query_builder._offset_value}:" \
                f"{args}:{kwargs}"
            )

            # Try cache
            cached_result = self._cache_manager.fetch(cache_key)
            if cached_result is not None:
                return self._deserialize_cached(cached_result)

            # Get fresh result
            method = getattr(super(), method_name)
            result = method(*args, **kwargs)

            # Cache result
            if result is not None:
                ttl = timedelta(seconds=self._cache_ttl) if self._cache_ttl else None
                self._cache_manager.write(cache_key, self._serialize_for_cache(result), ttl=ttl)

            return result

    def _serialize_for_cache(self, result):
        """Serialize result for caching"""
        if isinstance(result, list):
            return [item.dict() for item in result]
        return result.dict() if result else None

    def _deserialize_cached(self, cached):
        """Deserialize cached result"""
        if isinstance(cached, list):
            return [self.model_class(**item) for item in cached]
        return self.model_class(**cached) if cached else None
