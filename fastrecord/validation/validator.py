from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Type, Callable


class ValidationError(Exception):
    def __init__(self, errors: Dict[str, List[str]]):
        self.errors = errors
        super().__init__(str(errors))


@dataclass
class ValidationRule:
    validator: Type['Validator']
    field: str
    options: Dict[str, Any]
    condition: Optional[Callable] = None
    if_field: Optional[str] = None
    unless_field: Optional[str] = None
    message: Optional[str] = None


class ValidationMixin:
    """Provides validation functionality for models"""
    _validation_rules: List[ValidationRule] = []
    _errors: Dict[str, List[str]] = {}

    @classmethod
    def validates(
            cls,
            field: str,
            validator: Type['Validator'],
            **options
    ):
        """Decorator for adding validation rules"""

        def decorator(func):
            rule = ValidationRule(
                validator=validator,
                field=field,
                options=options,
                condition=func if callable(func) else None
            )
            cls._validation_rules.append(rule)
            return func

        return decorator

    def valid(self) -> bool:
        """Rails-like valid? method"""
        self._errors.clear()
        self._run_validations()
        return len(self._errors) == 0

    def validate(self):
        """Rails-like validate! method"""
        if not self.valid():
            raise ValidationError(self._errors)

    def _run_validations(self):
        """Run all validations"""
        for rule in self._validation_rules:
            if self._should_run_validation(rule):
                validator = rule.validator(
                    self,
                    rule.field,
                    **rule.options
                )
                validator.validate()

    def _should_run_validation(self, rule: ValidationRule) -> bool:
        """Check if validation should run based on conditions"""
        if rule.condition and not rule.condition(self):
            return False

        if rule.if_field and not getattr(self, rule.if_field):
            return False

        if rule.unless_field and getattr(self, rule.unless_field):
            return False

        return True

    @property
    def errors(self) -> Dict[str, List[str]]:
        """Get validation errors"""
        return self._errors.copy()

    def add_error(self, field: str, message: str):
        """Add a validation error"""
        if field not in self._errors:
            self._errors[field] = []
        self._errors[field].append(message)


class Validator:
    def __init__(self, record, field, **options):
        self.record = record
        self.field = field
        self.options = options

    def get_value(self):
        return getattr(self.record, self.field, None)

    def add_error(self, message):
        if self.field not in self.record._errors:
            self.record._errors[self.field] = []
        self.record._errors[self.field].append(message)
