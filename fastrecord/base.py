"""Base Record class implementation."""

from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional, Set, Type, TypeVar, cast
from sqlmodel import Field, SQLModel, Session, select
import inflect

from .cache import CacheBackend, CacheManager
from .callbacks import CallbackMixin
from .relationships import Relationship
from .validation.validator import ValidationMixin

T = TypeVar("T", bound="Record")
inflector = inflect.engine()


class RecordError(Exception):
    """Base exception for Record errors."""
    pass


class ValidationError(RecordError):
    """Raised when validation fails."""

    def __init__(self, errors: Dict[str, List[str]]):
        self.errors = errors
        super().__init__(str(errors))


class FastRecord(SQLModel, ValidationMixin, CallbackMixin):
    """Base class for all Record models."""

    # Default fields
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None, index=True)

    # Class configuration
    _validations: ClassVar[Dict[str, List[Dict[str, Any]]]] = {}
    _callbacks: ClassVar[Dict[str, List[str]]] = {}
    _scopes: ClassVar[Dict[str, Any]] = {}
    _relationships: ClassVar[Dict[str, 'Relationship']] = {}
    _cache: ClassVar['CacheBackend'] = CacheManager()

    # Instance state
    _new_record: bool = True
    _destroyed: bool = False
    _previously_changed: Set[str] = set()
    _changes: Dict[str, tuple] = {}
    _validation_errors: Dict[str, List[str]] = {}

    def __init__(self, **data):
        """Initialize a new Record instance."""
        super().__init__(**data)
        self._new_record = True
        self._destroyed = False
        self._previously_changed = set()
        self._changes = {}
        self._validation_errors = {}

    @classmethod
    def table_name(cls) -> str:
        """Get the table name for the model."""
        if cls.__tablename__:
            return cls.__tablename__
        return inflector.plural(cls.__name__.lower())

    @property
    def errors(self) -> Dict[str, List[str]]:
        """Get validation errors."""
        return self._validation_errors

    @property
    def new_record(self) -> bool:
        """Check if the record is new (not persisted)."""
        return self._new_record

    @property
    def destroyed(self) -> bool:
        """Check if the record has been destroyed."""
        return self._destroyed

    @property
    def persisted(self) -> bool:
        """Check if the record is persisted to the database."""
        return not self._new_record and not self._destroyed

    def save(self, validate: bool = True) -> bool:
        """
        Save the record to the database.

        Args:
            validate: Whether to run validations before saving.

        Returns:
            bool: True if save was successful, False otherwise.
        """
        if validate and not self.valid():
            return False

        session = self.get_session()
        try:
            self._run_callbacks('before_save')

            if self._new_record:
                self._run_callbacks('before_create')
            else:
                self._run_callbacks('before_update')

            self.updated_at = datetime.utcnow()
            session.add(self)
            session.flush()  # Get ID without committing

            if self.id is None:
                self._run_callbacks('after_create')
            else:
                self._run_callbacks('after_update')

            self._run_callbacks('after_save')
            session.commit()

            self._new_record = False
            return True
        except Exception:
            session.rollback()
            raise

    def save_strict(self, validate: bool = True) -> bool:
        """
        Save the record to the database, raising an error if validation fails.

        Args:
            validate: Whether to run validations before saving.

        Returns:
            bool: True if save was successful.

        Raises:
            ValidationError: If validation fails.
        """
        if not self.save(validate):
            raise ValidationError(self._validation_errors)
        return True

    def update(self, **attrs) -> bool:
        """
        Update the record with the given attributes.

        Args:
            **attrs: Attributes to update.

        Returns:
            bool: True if update was successful.
        """
        for key, value in attrs.items():
            setattr(self, key, value)
        return self.save()

    def delete(self) -> bool:
        """
        Soft delete the record.

        Returns:
            bool: True if deletion was successful.
        """
        if self.deleted_at:
            return False

        self.deleted_at = datetime.utcnow()
        return self.save()

    def destroy(self) -> bool:
        """
        Hard delete the record.

        Returns:
            bool: True if destruction was successful.
        """
        if self._destroyed:
            return False

        session = self.get_session()
        try:
            if not self._run_callbacks('before_destroy'):
                return False

            session.delete(self)
            session.commit()
            self._destroyed = True

            self._run_callbacks('after_destroy')
            return True
        except Exception:
            session.rollback()
            raise

    def restore(self) -> bool:
        """
        Restore a soft-deleted record.

        Returns:
            bool: True if restoration was successful.
        """
        if not self.deleted_at:
            return False

        self.deleted_at = None
        return self.save()

    @classmethod
    def create(cls: Type[T], **attrs) -> T:
        """
        Create and save a new record.

        Args:
            **attrs: Attributes for the new record.

        Returns:
            T: The created record.
        """
        instance = cls(**attrs)
        instance.save()
        return instance

    @classmethod
    def create_strict(cls: Type[T], **attrs) -> T:
        """
        Create and save a new record, raising an error if validation fails.

        Args:
            **attrs: Attributes for the new record.

        Returns:
            T: The created record.

        Raises:
            ValidationError: If validation fails.
        """
        instance = cls(**attrs)
        instance.save_strict()
        return instance

    @classmethod
    def find(cls: Type[T], id: int) -> Optional[T]:
        """
        Find a record by ID.

        Args:
            id: The ID to find.

        Returns:
            Optional[T]: The found record or None.
        """
        session = cls.get_session()
        return session.get(cls, id)

    @classmethod
    def find_strict(cls: Type[T], id: int) -> T:
        """
        Find a record by ID, raising an error if not found.

        Args:
            id: The ID to find.

        Returns:
            T: The found record.

        Raises:
            RecordError: If record is not found.
        """
        record = cls.find(id)
        if record is None:
            raise RecordError(f"{cls.__name__} with id={id} not found")
        return record

    @classmethod
    def where(cls: Type[T], *args, **kwargs):
        """Start a new query chain."""
        from .query.chain import QueryChain
        return QueryChain(cls).where(*args, **kwargs)

    @classmethod
    def all(cls: Type[T]) -> List[T]:
        """Get all records."""
        session = cls.get_session()
        return session.exec(select(cls).where(cls.deleted_at == None)).all()

    @classmethod
    def first(cls: Type[T]) -> Optional[T]:
        """Get the first record."""
        return cls.order_by(cls.id).limit(1).first()

    @classmethod
    def last(cls: Type[T]) -> Optional[T]:
        """Get the last record."""
        return cls.order_by(cls.id.desc()).limit(1).first()

    @staticmethod
    def get_session() -> Session:
        """Get the current database session."""
        from .utils.session import get_session
        return get_session()

    def _run_callbacks(self, event: str) -> bool:
        """
        Run callbacks for a given event.

        Args:
            event: The event name.

        Returns:
            bool: False if any callback returned False, True otherwise.
        """
        if event in self._callbacks:
            for method_name in self._callbacks[event]:
                method = getattr(self, method_name)
                if method() is False:
                    return False
        return True

    def valid(self) -> bool:
        """
        Check if the record is valid.

        Returns:
            bool: True if valid, False otherwise.
        """
        self._validation_errors.clear()

        # Run validations
        for field, validations in self._validations.items():
            value = getattr(self, field, None)
            for validation in validations:
                try:
                    method = getattr(self, validation["method"])
                    method(value, **validation.get("options", {}))
                except ValidationError as e:
                    if field not in self._validation_errors:
                        self._validation_errors[field] = []
                    self._validation_errors[field].extend(e.errors.get(field, []))

        return len(self._validation_errors) == 0

    def __repr__(self) -> str:
        """String representation of the record."""
        return f"<{self.__class__.__name__} id={self.id}>"
