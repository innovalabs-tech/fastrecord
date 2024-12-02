from sqlalchemy.orm import joinedload
from typing import Type

from sqlalchemy.orm import joinedload
from sqlmodel import select, or_, and_, not_, desc, asc

from .. import FastRecord


class QueryBuilder:
    """
    Core query builder that handles SQL generation
    """

    def __init__(self, model_class: Type['FastRecord']):
        self.model_class = model_class
        self.query = select(model_class)
        self._where_values = []
        self._or_values = []
        self._not_values = []
        self._includes = []
        self._joins = []
        self._order_values = []
        self._group_values = []
        self._having_values = []
        self._limit_value = None
        self._offset_value = None
        self._lock_value = None
        self._distinct = False

    def where(self, *args, **kwargs) -> 'QueryBuilder':
        """Add WHERE conditions"""
        for arg in args:
            self._where_values.append(arg)

        for key, value in kwargs.items():
            if isinstance(value, (list, tuple)):
                self._where_values.append(getattr(self.model_class, key).in_(value))
            elif value is None:
                self._where_values.append(getattr(self.model_class, key).is_(None))
            else:
                self._where_values.append(getattr(self.model_class, key) == value)

        return self

    def or_where(self, *args, **kwargs) -> 'QueryBuilder':
        """Add OR conditions"""
        conditions = []
        for arg in args:
            conditions.append(arg)

        for key, value in kwargs.items():
            conditions.append(getattr(self.model_class, key) == value)

        self._or_values.append(or_(*conditions))
        return self

    def not_where(self, *args, **kwargs) -> 'QueryBuilder':
        """Add NOT conditions"""
        conditions = []
        for arg in args:
            conditions.append(arg)

        for key, value in kwargs.items():
            conditions.append(getattr(self.model_class, key) == value)

        self._not_values.append(not_(and_(*conditions)))
        return self

    def includes(self, *relations) -> 'QueryBuilder':
        """Add eager loading"""
        self._includes.extend(relations)
        return self

    def joins(self, *relations) -> 'QueryBuilder':
        """Add JOIN clauses"""
        self._joins.extend(relations)
        return self

    def order(self, *args) -> 'QueryBuilder':
        """Add ORDER BY"""
        for arg in args:
            if isinstance(arg, str):
                if arg.startswith('-'):
                    self._order_values.append(desc(getattr(self.model_class, arg[1:])))
                else:
                    self._order_values.append(asc(getattr(self.model_class, arg)))
            else:
                self._order_values.append(arg)
        return self

    def group(self, *args) -> 'QueryBuilder':
        """Add GROUP BY"""
        self._group_values.extend(args)
        return self

    def having(self, *conditions) -> 'QueryBuilder':
        """Add HAVING clause"""
        self._having_values.extend(conditions)
        return self

    def limit(self, value: int) -> 'QueryBuilder':
        """Add LIMIT"""
        self._limit_value = value
        return self

    def offset(self, value: int) -> 'QueryBuilder':
        """Add OFFSET"""
        self._offset_value = value
        return self

    def distinct(self) -> 'QueryBuilder':
        """Add DISTINCT"""
        self._distinct = True
        return self

    def lock(self) -> 'QueryBuilder':
        """Add FOR UPDATE"""
        self._lock_value = True
        return self

    def build(self):
        """Build the final query"""
        query = self.query

        # Apply WHERE conditions
        if self._where_values:
            query = query.where(and_(*self._where_values))

        # Apply OR conditions
        if self._or_values:
            query = query.where(or_(*self._or_values))

        # Apply NOT conditions
        for condition in self._not_values:
            query = query.where(condition)

        # Apply JOINs
        for join in self._joins:
            query = query.join(join)

        # Apply eager loading
        for relation in self._includes:
            if '.' in relation:
                # Handle nested includes (e.g., 'posts.comments')
                parts = relation.split('.')
                query = query.options(
                    joinedload(getattr(self.model_class, parts[0]))
                    .joinedload(parts[1])
                )
            else:
                query = query.options(
                    joinedload(getattr(self.model_class, relation))
                )

        # Apply ORDER BY
        for order in self._order_values:
            query = query.order_by(order)

        # Apply GROUP BY
        if self._group_values:
            query = query.group_by(*self._group_values)

        # Apply HAVING
        if self._having_values:
            query = query.having(*self._having_values)

        # Apply LIMIT/OFFSET
        if self._limit_value is not None:
            query = query.limit(self._limit_value)
        if self._offset_value is not None:
            query = query.offset(self._offset_value)

        # Apply DISTINCT
        if self._distinct:
            query = query.distinct()

        # Apply FOR UPDATE
        if self._lock_value:
            query = query.with_for_update()

        return query
