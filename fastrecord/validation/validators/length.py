class LengthValidator(Validator):
    """Validates length of a value"""

    def validate(self):
        value = self.get_value()
        if value is None:
            return

        length = len(value)

        if 'minimum' in self.options and length < self.options['minimum']:
            self.add_error(
                self.options.get(
                    'too_short',
                    f"{self.field} is too short (minimum is {self.options['minimum']} characters)"
                )
            )

        if 'maximum' in self.options and length > self.options['maximum']:
            self.add_error(
                self.options.get(
                    'too_long',
                    f"{self.field} is too long (maximum is {self.options['maximum']} characters)"
                )
            )

        if 'is' in self.options and length != self.options['is']:
            self.add_error(
                self.options.get(
                    'wrong_length',
                    f"{self.field} is the wrong length (should be {self.options['is']} characters)"
                )
            )
