from typing import Type, Union

from sqlmodel import Field

from . import RelationType, DeleteStrategy
from .base import Relationship
from .. import FastRecord
from sqlmodel import Relationship as SQLModelRelationship


class BelongsTo(Relationship):
    def __init__(
            self,
            model: Union[str, Type['FastRecord']],
            **kwargs
    ):
        super().__init__(
            model=model,
            relation_type=RelationType.BELONGS_TO,
            delete_strategy=DeleteStrategy.NULLIFY,
            **kwargs
        )
        self.required = kwargs.get('required', False)
        self.touch = kwargs.get('touch', False)

    def setup_relationship(self, owner):
        # Add foreign key field
        fk_name = self.foreign_key or f"{self.name}_id"
        setattr(owner, fk_name, Field(
            default=None,
            foreign_key=f"{self.model.__tablename__}.id",
            nullable=not self.required
        ))

        # Add SQLModel relationship
        setattr(owner, self.name, SQLModelRelationship(
            back_populates=self.back_populates,
            sa_relationship_kwargs={'lazy': self.lazy}
        ))


def belongs_to(
        model: Union[str, Type['FastRecord']],
        **kwargs
) -> BelongsTo:
    """
    Creates a belongs_to relationship

    Example:
    ```python
    class Comment(FastRecord):
        author = belongs_to(User)
        post = belongs_to(Post, touch=True)
    ```
    """
    return BelongsTo(model, **kwargs)
