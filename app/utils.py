import re

from pydantic_core import PydanticCustomError


def validate_password(password: str):
    password_requirements = {
        r".{8,}": "Password must be at least 8 characters long",
        r".*\d.*": "Password must contain at least one digit",
        r".*[A-Z].*": "Password must contain at least one uppercase letter",
        r".*[a-z].*": "Password must contain at least one lowercase letter",
        r".*[!@#$%^&*(),.?\":{}|<>].*": "Password must contain at least one special character",
    }

    error_message_list = []

    for regex, error_message in password_requirements.items():
        if not re.match(regex, password):
            error_message_list.append(error_message)

    if error_message_list:
        raise PydanticCustomError(
            "password_validation_error",
            "Password is invalid",
            {"rules": error_message_list},
        )

    return password
