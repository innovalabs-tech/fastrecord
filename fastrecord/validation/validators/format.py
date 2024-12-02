import re


class FormatValidator(Validator):
    """Validates format of a value using regex"""

    def validate(self):
        value = self.get_value()
        if value is None:
            return

        with_ = self.options.get('with')
        without = self.options.get('without')

        if with_ and not re.match(with_, str(value)):
            self.add_error(
                self.options.get(
                    'message',
                    f"{self.field} is invalid"
                )
            )

        if without and re.match(without, str(value)):
            self.add_error(
                self.options.get(
                    'message',
                    f"{self.field} is invalid"
                )
            )
