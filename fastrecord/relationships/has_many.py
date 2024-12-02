from typing import Optional, Type, Union

from . import RelationType
from .base import Relationship
from .. import FastRecord
from sqlmodel import Relationship as SQLModelRelationship


class HasMany(Relationship):
    def __init__(
            self,
            model: Union[str, Type['FastRecord']],
            through: Optional[Union[str, Type['FastRecord']]] = None,
            **kwargs
    ):
        super().__init__(
            model=model,
            relation_type=RelationType.HAS_MANY,
            **kwargs
        )
        self.through = through
        self.dependent = kwargs.get('dependent', None)
        self.counter_cache = kwargs.get('counter_cache', False)
        self.as_name = kwargs.get('as_', None)

    def setup_relationship(self, owner):
        if self.through:
            # Set up many-to-many relationship
            setattr(owner, self.name, SQLModelRelationship(
                back_populates=self.back_populates,
                link_model=self.through,
                sa_relationship_kwargs={'lazy': self.lazy}
            ))
        else:
            # Set up one-to-many relationship
            setattr(owner, self.name, SQLModelRelationship(
                back_populates=self.back_populates,
                sa_relationship_kwargs={'lazy': self.lazy}
            ))


def has_many(
        model: Union[str, Type['FastRecord']],
        **kwargs
) -> HasMany:
    """
    Creates a has_many relationship

    Example:
    ```python
    class User(FastRecord):
        posts = has_many(Post)
        comments = has_many(Comment, dependent='destroy')
        roles = has_many(Role, through='UserRole')
    ```
    """
    return HasMany(model, **kwargs)
