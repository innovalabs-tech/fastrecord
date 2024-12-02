import re
from typing import Any

from . import CustomValidator


class EmailValidator(CustomValidator):
    """Validates email format"""

    def validate_value(self, value: str):
        if value and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            self.add_error(
                self.options.get(
                    'message',
                    "is not a valid email address"
                )
            )


class NumericValidator(CustomValidator):
    """Validates numeric values"""

    def validate_value(self, value: Any):
        if not isinstance(value, (int, float)):
            self.add_error("must be a number")
            return

        if 'greater_than' in self.options and value <= self.options['greater_than']:
            self.add_error(f"must be greater than {self.options['greater_than']}")

        if 'less_than' in self.options and value >= self.options['less_than']:
            self.add_error(f"must be less than {self.options['less_than']}")


class InclusionValidator(CustomValidator):
    """Validates inclusion in a list"""

    def validate_value(self, value: Any):
        if value not in self.options.get('in', []):
            self.add_error(
                self.options.get(
                    'message',
                    f"is not included in the list"
                )
            )


class ExclusionValidator(CustomValidator):
    """Validates exclusion from a list"""

    def validate_value(self, value: Any):
        if value in self.options.get('in', []):
            self.add_error(
                self.options.get(
                    'message',
                    f"is reserved"
                )
            )