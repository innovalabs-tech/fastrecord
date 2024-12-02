from typing import Optional, Type, Union

from . import RelationType
from .base import Relationship
from .. import FastRecord
from sqlmodel import Relationship as SQLModelRelationship


class HasOne(Relationship):
    def __init__(
            self,
            model: Union[str, Type['FastRecord']],
            through: Optional[Union[str, Type['FastRecord']]] = None,
            **kwargs
    ):
        super().__init__(
            model=model,
            relation_type=RelationType.HAS_ONE,
            **kwargs
        )
        self.through = through
        self.dependent = kwargs.get('dependent', None)
        self.as_name = kwargs.get('as_', None)

    def setup_relationship(self, owner):
        if self.through:
            # Set up has_one_through relationship
            setattr(owner, self.name, SQLModelRelationship(
                back_populates=self.back_populates,
                link_model=self.through,
                sa_relationship_kwargs={'lazy': self.lazy, 'uselist': False}
            ))
        else:
            # Set up simple has_one relationship
            setattr(owner, self.name, SQLModelRelationship(
                back_populates=self.back_populates,
                sa_relationship_kwargs={'lazy': self.lazy, 'uselist': False}
            ))


def has_one(
        model: Union[str, Type['FastRecord']],
        **kwargs
) -> HasOne:
    """
    Creates a has_one relationship

    Example:
    ```python
    class User(FastRecord):
        profile = has_one(Profile)
        avatar = has_one(Image, as_='imageable')
    ```
    """
    return HasOne(model, **kwargs)
