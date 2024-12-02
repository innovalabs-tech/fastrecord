from typing import Any

from ..validator import Validator


class CustomValidator(Validator):
    """Base class for custom validators"""

    def validate(self):
        value = self.get_value()
        self.validate_value(value)

    def validate_value(self, value: Any):
        """Override this method in custom validators"""
        raise NotImplementedError
