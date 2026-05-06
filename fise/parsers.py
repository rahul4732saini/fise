"""
Parsers Module
--------------

This module defines utitlity functions for parsing
and extracting query fields and attributes.
"""

from datetime import datetime
from pathlib import Path
from typing import TypeAlias

from common import constants, tools
from errors import QueryParseError
from fields import BaseField, Field, Size

# Defines all data types which can be used for representing search query
# projections, condition operands and much more while handling queries.
QueryAttribute: TypeAlias = (
    None | bool | str | int | float | datetime | list["QueryAttribute"] | BaseField
)

# Maps field names with corresponding handler classes.
_fields_map: dict[str, type] = {
    "size": Size,
}


def parse_datetime(source: str) -> datetime:
    """Parses a date/datetime object from the specified source string."""

    try:
        return datetime.strptime(source, constants.DATETIME_FORMAT)

    except ValueError:
        # Passes without raising an error if in case
        # the specified string matches the date format.
        ...

    try:
        return datetime.strptime(source, constants.DATE_FORMAT)

    except ValueError:
        raise QueryParseError(f"{source!r} is not a valid datetime specification.")


def parse_path(raw_path: str) -> Path:
    """
    Parses a Path object from the specified source string comprising
    a raw path which may also be explicitly enclosed within quotes.
    """

    if constants.STRING_PATTERN.fullmatch(raw_path):
        raw_path = raw_path[1:-1]

    return Path(raw_path)


def parse_field(field: str, entity: str) -> BaseField:
    """
    Parses the specified field specifications based on the
    specified entity name.

    #### Params:
    - field (str): String comprising the field specifications.
    - entity (int): Name of the entity being operated upon.
    """

    # Extracts the field name and its associated arguments if any.
    label, args = tools.tokenize_qualified_clause(field)
    name = constants.ALIASES[entity].get(label, label)

    if name not in constants.FIELDS[entity]:
        raise QueryParseError(f"{field!r} is not a valid field!")

    # Parses the field using its corresponding class from the fields map
    # or as a generic field if no such class exists.
    if name in _fields_map:
        return _fields_map[name].parse(args)

    # Raises an error if the specification comprise arguments, as generic
    # fields do not expect any arguments.
    if args:
        raise QueryParseError(f"{label!r} field does not expect any arguments!")

    return Field.parse(name)


def parse_attribute(source: str, entity: str | None = None) -> QueryAttribute:
    """
    Implements mechanism for parsing all available types of
    query attirbutes from the specified string specifications.

    #### Params:
    - source (str): String specifications for query attribute.
    - entity (str | None): [OPTIONAL] Name of the entity being
    operated upon. Defaults to None.
    """

    if constants.TUPLE_PATTERN.match(source):
        # Tokenizes the source string, parses the individual
        # tokens and returns a list of the parsed attributes.
        tokens = tools.tokenize(source[1:-1], delimiter=",")
        return [parse_attribute(token, entity) for token in tokens]

    elif constants.DATETIME_PATTERN.match(source):
        return parse_datetime(source)

    elif constants.STRING_PATTERN.match(source):
        return source[1:-1]

    elif source.isdigit():
        return int(source)

    elif constants.FLOAT_PATTERN.match(source):
        return float(source)

    elif source.lower() == constants.KEYWORD_NONE:
        return None

    # If none of the above conditions are matched, the specified
    # string is parsed for a query field based on wheather an entity
    # name has been explicitly specified.
    elif entity:
        return parse_field(source, entity)

    raise QueryParseError(f"{source!r} is not a valid query attribute!")
