from typing import List, Union, Type

from sqlmodel import Field

from . import RelationType
from .base import Relationship
from .. import FastRecord
from sqlmodel import Relationship as SQLModelRelationship


class PolymorphicRelationship(Relationship):
    def __init__(
            self,
            models: List[Union[str, Type['FastRecord']]],
            as_: str,
            **kwargs
    ):
        super().__init__(
            model=models[0],  # Primary model
            relation_type=RelationType.POLYMORPHIC,
            **kwargs
        )
        self.models = models
        self.as_name = as_
        self.type_field = f"{as_}_type"
        self.id_field = f"{as_}_id"

    def setup_relationship(self, owner):
        # Add type and ID fields
        setattr(owner, self.type_field, Field(str))
        setattr(owner, self.id_field, Field(int))

        # Add SQLModel relationship for each model
        for model in self.models:
            relation_name = f"{model.__name__.lower()}_as_{self.as_name}"
            setattr(owner, relation_name, SQLModelRelationship(
                back_populates=self.back_populates,
                sa_relationship_kwargs={
                    'lazy': self.lazy,
                    'polymorphic_on': self.type_field,
                    'polymorphic_identity': model.__name__
                }
            ))


def polymorphic(
        *models: Type['FastRecord'],
        as_: str,
        **kwargs
) -> PolymorphicRelationship:
    """
    Creates a polymorphic relationship

    Example:
    ```python
    class Comment(FastRecord):
        commentable = polymorphic(Post, Image, as_='commentable')

    class Image(FastRecord):
        imageable = polymorphic(User, Post, as_='imageable')
    ```
    """
    return PolymorphicRelationship(list(models), as_=as_, **kwargs)
