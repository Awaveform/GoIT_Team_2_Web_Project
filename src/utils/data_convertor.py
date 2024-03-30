import enum
from typing import Any


def get_enum_value(value: Any) -> Any:
    """
    Method gets the enum value if the passed parameter is an instance of enum.Enum class.

    :param value: instance of enum.Enum class or any other type.
    :type value: Any.
    :return: Enum value or initial value.
    :rtype: Any.
    """
    if isinstance(value, enum.Enum):
        return value.value
    return value
