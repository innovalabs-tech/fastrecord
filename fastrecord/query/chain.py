import math
from typing import Any, List, Optional, Type, Tuple
from typing import TypeVar

from sqlmodel import select, func, desc

from . import QueryBuilder
from ..config import get_settings, FastRecordSettings

T = TypeVar('T', bound='FastRecord')


class QueryChain:
    """
    Provides a chainable interface for building queries
    """

    def __init__(self, model_class: Type[T]):
        self.model_class = model_class
        self.query_builder = QueryBuilder(model_class)
        self._results = None
        self._loaded = False
        self._use_cache = False
        self._cache_ttl = None

    def _clone(self):
        """Create a copy of the current chain"""
        new = self.__class__(self.model_class)
        new.query_builder = self.query_builder
        return new

    def where(self, *args, **kwargs) -> 'QueryChain':
        """Filter records"""
        self.query_builder.where(*args, **kwargs)
        return self

    def or_where(self, *args, **kwargs) -> 'QueryChain':
        """Add OR conditions"""
        self.query_builder.or_where(*args, **kwargs)
        return self

    def not_where(self, *args, **kwargs) -> 'QueryChain':
        """Add NOT conditions"""
        self.query_builder.not_where(*args, **kwargs)
        return self

    def includes(self, *relations) -> 'QueryChain':
        """Eager load associations with limit check"""
        if len(relations) > get_settings().MAX_EAGER_LOAD_RELATIONS:
            raise ValueError(
                f"Maximum number of eager loaded relations exceeded "
                f"(max: {get_settings().MAX_EAGER_LOAD_RELATIONS})"
            )
        """Eager load associations"""
        self.query_builder.includes(*relations)
        return self

    def order(self, *args) -> 'QueryChain':
        """Order results"""
        self.query_builder.order(*args)
        return self

    def limit(self, value: int) -> 'QueryChain':
        """Limit results"""
        self.query_builder.limit(value)
        return self

    def offset(self, value: int) -> 'QueryChain':
        """Offset results"""
        self.query_builder.offset(value)
        return self

    def cache(self, ttl: Optional[int] = None) -> 'QueryChain':
        """Enable caching for this query"""
        self._use_cache = True
        self._cache_ttl = ttl or get_settings().CACHE_DEFAULT_TTL
        return self

    def paginate(self, page: int = 1, per_page=None) -> Tuple[List[T], dict]:
        """Paginate results using settings"""
        if per_page is None:
            per_page = get_settings().DEFAULT_PER_PAGE
        offset = (page - 1) * per_page

        records = self.offset(offset).limit(per_page).all()
        if page > 1:
            total = self.count()

            return records, {
                'current_page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': math.ceil(total / per_page)
            }
        else:
            return records, {
                'current_page': page,
                'per_page': per_page
            }

    def all(self) -> List[T]:
        """Execute query and return all results"""
        session = self.model_class._get_session()
        query = self.query_builder.build()
        if self._use_cache:
            key = self.model_class._cache.generate_key(self.model_class.__name__, query)
            cached_result = self.model_class._cache.fetch(key)
            if cached_result is not None:
                return cached_result
            else:
                result = session.exec(query).all()
                self.model_class._cache.write(key, result)
                return result
        else:
            return session.exec(query).all()

    def first(self) -> Optional[T]:
        """Get first record"""
        return self.limit(1).all()[0] if self.limit(1).all() else None

    def last(self) -> Optional[T]:
        """Get last record"""
        if not self.query_builder._order_values:
            self.query_builder.order(desc(self.model_class.id))
        return self.limit(1).all()[0] if self.limit(1).all() else None

    def find_each(self, batch_size: int = 1000):
        """Yield each record in batches"""
        offset = 0
        while True:
            batch = self.limit(batch_size).offset(offset).all()
            if not batch:
                break
            for record in batch:
                yield record
            offset += batch_size

    def count(self, column: str = '*') -> int:
        """Get record count"""
        session = self.model_class._get_session()
        if column == '*':
            count_expr = func.count()
        else:
            count_expr = func.count(getattr(self.model_class, column))
        query = select(count_expr).select_from(self.model_class)
        return session.exec(query).one()

    def pluck(self, *args) -> List[Any]:
        """Get array of values for specified columns"""
        session = self.model_class._get_session()
        columns = [getattr(self.model_class, arg) for arg in args]
        query = select(*columns).select_from(self.model_class)
        results = session.exec(query).all()
        return [result[0] if len(args) == 1 else result for result in results]
