from functools import wraps
from typing import Any, Optional, Type, TypeVar, List
from datetime import timedelta
import hashlib
import inspect
import json

from ..base import FastRecord
from ..config import get_settings

T = TypeVar('T', bound='FastRecord')


class CacheDecorator:
    """Cache decorator factory"""

    @staticmethod
    def generate_cache_key(prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from function arguments"""
        key_parts = [prefix]

        if args:
            key_parts.append('args:' + json.dumps(args, sort_keys=True))

        if kwargs:
            sorted_kwargs = json.dumps(kwargs, sort_keys=True)
            key_parts.append('kwargs:' + sorted_kwargs)

        key = ':'.join(key_parts)
        return hashlib.md5(key.encode()).hexdigest()

    @staticmethod
    def cached(ttl: Optional[int] = None):
        """
        Decorator to cache method results

        Args:
            ttl: Time to live in seconds. If None, uses default TTL from settings.
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Get instance/class and cache manager
                if inspect.ismethod(func):
                    instance = args[0]
                    cache_manager = instance._cache
                    prefix = [
                        get_settings().CACHE_PREFIX,
                        get_settings().CACHE_VERSION,
                        instance.__class__.__name__,
                        func.__name__
                    ]
                    args = args[1:]
                else:
                    instance = args[0]
                    cache_manager = instance._cache
                    prefix = [
                        get_settings().CACHE_PREFIX,
                        get_settings().CACHE_VERSION,
                        instance.__name__,
                        func.__name__
                    ]
                    args = args[1:]

                # Generate cache key
                cache_key = CacheDecorator.generate_cache_key(":".join(prefix), *args, **kwargs)

                # Try to get from cache
                cached_result = cache_manager.fetch(cache_key)
                if cached_result is not None:
                    if isinstance(cached_result, list):
                        return [instance(**item) if isinstance(item, dict) else item
                                for item in cached_result]
                    elif isinstance(cached_result, dict):
                        return instance(**cached_result)
                    return cached_result

                # Get fresh result
                result = func(*args, **kwargs)

                # Cache the result
                if result is not None:
                    cache_ttl = timedelta(seconds=ttl) if ttl else None

                    if isinstance(result, list):
                        cache_data = [item.to_dict() if isinstance(item, FastRecord) else item
                                      for item in result]
                    elif isinstance(result, FastRecord):
                        cache_data = result.to_dict()
                    else:
                        cache_data = result

                    cache_manager.write(cache_key, cache_data, ttl=cache_ttl)

                return result

            return wrapper

        return decorator


# Create a function instance of the decorator for easier usage
cached = CacheDecorator.cached
