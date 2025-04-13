import re
from decimal import ROUND_HALF_EVEN, Decimal

from pydantic_core import PydanticCustomError

from app.constants.messages import Messages


def validate_password(password: str):
    password_requirements = {
        r".{8,}": Messages.Password.Validation.LENGTH,
        r".*\d.*": Messages.Password.Validation.DIGIT,
        r".*[A-Z].*": Messages.Password.Validation.UPPERCASE,
        r".*[a-z].*": Messages.Password.Validation.LOWERCASE,
        r".*[!@#$%^&*(),.?\":{}|<>].*": Messages.Password.Validation.SPECIAL_CHARACTER,
    }

    error_message_list = []

    for regex, error_message in password_requirements.items():
        if not re.match(regex, password):
            error_message_list.append(error_message)

    if error_message_list:
        raise PydanticCustomError(
            "password_validation_error",
            Messages.Password.INVALID,
            {"rules": error_message_list},
        )

    return password


def get_average_price(cost_basis: Decimal, position: Decimal):
    return cost_basis / position if position != 0 else Decimal("0")


def round_decimal(value: Decimal, decimal_places: int):
    rounding_factor = Decimal("1." + "0" * decimal_places)
    return value.quantize(Decimal(rounding_factor), ROUND_HALF_EVEN)
