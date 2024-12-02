from typing import Optional, Type, Union

from . import RelationType, DeleteStrategy
from .. import FastRecord


class Relationship:
    """Base class for all relationship types"""

    def __init__(
            self,
            model: Union[str, Type['FastRecord']],
            relation_type: RelationType,
            delete_strategy: DeleteStrategy = DeleteStrategy.CASCADE,
            foreign_key: Optional[str] = None,
            primary_key: Optional[str] = None,
            back_populates: Optional[str] = None,
            lazy: str = 'select'
    ):
        self.model = model
        self.relation_type = relation_type
        self.delete_strategy = delete_strategy
        self.foreign_key = foreign_key
        self.primary_key = primary_key
        self.back_populates = back_populates
        self.lazy = lazy
        self.name = None  # Set when relationship is bound to class

    def __set_name__(self, owner, name):
        self.name = name
        self.setup_relationship(owner)

    def setup_relationship(self, owner):
        """Set up the SQLModel relationship and any necessary fields"""
        raise NotImplementedError

    def contribute_to_class(self, cls, name):
        """Add relationship metadata to the model class"""
        if not hasattr(cls, '_relationships'):
            cls._relationships = {}
        cls._relationships[name] = self


class RelationshipManager:
    """Manages relationship collections and operations"""

    def __init__(self, owner: 'FastRecord', relationship: Relationship):
        self.owner = owner
        self.relationship = relationship
        self._loaded = False
        self._target = None

    def load_target(self):
        """Load the related records"""
        raise NotImplementedError
