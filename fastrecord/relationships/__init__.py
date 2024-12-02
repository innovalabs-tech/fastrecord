from enum import Enum
from .base import Relationship, RelationshipManager
from .belongs_to import BelongsTo, belongs_to
from .has_many import HasMany, has_many
from .has_one import HasOne, has_one
from .polymorphic import PolymorphicRelationship, polymorphic


class RelationType(Enum):
    BELONGS_TO = "belongs_to"
    HAS_ONE = "has_one"
    HAS_MANY = "has_many"
    HAS_MANY_THROUGH = "has_many_through"
    HAS_ONE_THROUGH = "has_one_through"
    POLYMORPHIC = "polymorphic"


class DeleteStrategy(Enum):
    CASCADE = "cascade"  # Delete/destroy children
    NULLIFY = "nullify"  # Set foreign key to null
    RESTRICT = "restrict"  # Prevent deletion if children exist


__all__ = [
    'RelationType', 'DeleteStrategy',
    'Relationship', 'RelationshipManager',
    'BelongsTo', 'belongs_to',
    'HasMany', 'has_many',
    'HasOne', 'has_one',
    'PolymorphicRelationship', 'polymorphic'
]
