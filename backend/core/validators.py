import re


REGEX_EMAIL = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


class SchemaValidator:
    @staticmethod
    def validate_email(value):
        if not re.match(REGEX_EMAIL, value):
            raise ValueError("Invalid email")
        return value
