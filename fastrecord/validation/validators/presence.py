from typing import Any
from ..validator import Validator


class PresenceValidator(Validator):
    """Validates presence of a value"""

    def validate(self):
        value = self.get_value()

        if value is None or (isinstance(value, str) and not value.strip()):
            self.add_error(self.options.get(
                'message',
                f"{self.field} can't be blank"
            ))

