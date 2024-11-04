"""
Extractors Module
-----------------

This module comprises utitlity functions for
parsing and extracting attributes and fields.
"""

from typing import Any
from datetime import datetime

from common import constants
from fields import BaseField, Field, Size
from errors import QueryParseError


# Maps field names with corresponding handler classes.
_fields_map: dict[str, BaseField] = {
    "size": Size,
}


def parse_string(attr: str, /) -> str:
    """Parses the string formatted attribute for a string literal."""

    if constants.STRING_PATTERN.match(attr) is None:
        raise QueryParseError(f"{attr!r} is not a valid string!")

    # Strings the leading and trailing quotes from the string.
    return attr[1:-1]


def parse_integer(attr: str, /) -> int:
    """Parses the string formatted attribute for an integer."""

    if not attr.isdigit():
        raise QueryParseError(f"{attr} is not a valid integer!")

    return int(attr)


def parse_float(attr: str, /) -> float:
    """Parses the string formatted attribute for a floating point integer."""

    if constants.FLOAT_PATTERN.match(attr) is None:
        raise QueryParseError(f"{attr} is not a valid floating point integer!")

    return float(attr)


def parse_datetime(attr: str) -> datetime | None:
    """
    Parses date/datetime from the specified string formatted attribute
    it matches the corresponding pattern, and returns None otherwise.
    """

    if not constants.DATETIME_PATTERN.match(attr):
        return None

    try:
        return datetime.strptime(attr, r"%Y-%m-%d %H:%M:%S")

    except ValueError:
        # Passes without raising an error if in case
        # the attribute matches the date format.
        ...

    try:
        return datetime.strptime(attr, r"%Y-%m-%d")

    except ValueError:
        raise QueryParseError(
            f"Invalid datetime specifications {attr!r} in query conditions."
        )


def parse_field(
    field: str, entity: int, fields_map: dict[str, BaseField] = _fields_map
) -> BaseField:
    """
    Parses the specified field specifications.

    #### Params:
    - field (str): String formatted field to be parsed.
    - entity (int): Entity being operated upon.
    """

    # 'label' stores the name of the field and 'args' stores the
    # arguments associated to the it if explicitly specified.
    label = args = ""

    for i in range(len(field)):
        if field[i] != "[":
            continue

        label, args = field[:i].lower(), field[i + 1 : -1]
        break

    else:
        label = field.lower()

    label = constants.ALIASES[entity].get(label, label)

    if label not in constants.FIELDS[entity]:
        raise QueryParseError(f"{field!r} is not a valid field!")

    return fields_map[label].parse(args) if label in fields_map else Field.parse(label)


def parse_attribute(attr: str, entity: int = -1) -> Any:
    """
    Parses the specified string formatted attribute.

    #### Params:
    - attr (str): String formatted attribute to be parsed.
    - entity (int): [OPTIONAL] Entity being operated upon.
    """

    if constants.STRING_PATTERN.match(attr):
        return parse_string(attr)

    elif attr.isdigit():
        return parse_integer(attr)

    elif constants.FLOAT_PATTERN.match(attr):
        return parse_float(attr)

    elif attr.lower() == "none":
        return None

    # If none of the above conditions are matched, the attribute
    # is assumed to be a query field and parsed accordingly.
    return parse_field(attr, entity)
