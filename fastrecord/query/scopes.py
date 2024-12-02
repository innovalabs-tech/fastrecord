from dataclasses import dataclass
from typing import Callable, Dict
from typing import List

from . import QueryChain


@dataclass
class Scope:
    name: str
    callable: Callable
    default: bool = False


class ScopeMixin:
    """
    Provides scope functionality for models
    """
    _scopes: Dict[str, Scope] = {}
    _default_scopes: List[Scope] = []

    @classmethod
    def scope(cls, name: str, default: bool = False):
        """Decorator to define a scope"""

        def decorator(func):
            scope = Scope(name=name, callable=func, default=default)
            cls._scopes[name] = scope
            if default:
                cls._default_scopes.append(scope)
            return func

        return decorator

    @classmethod
    def default_scope(cls):
        """Decorator to define default scope"""
        return cls.scope(name='default', default=True)

    @classmethod
    def unscoped(cls) -> QueryChain:
        """Get a query chain without default scopes"""
        chain = QueryChain(cls)
        chain._skip_default_scopes = True
        return chain

    def apply_scopes(self, query: QueryChain) -> QueryChain:
        """Apply all applicable scopes to query"""
        # Apply default scopes
        if not getattr(query, '_skip_default_scopes', False):
            for scope in self._default_scopes:
                query = scope.callable(query)

        return query
