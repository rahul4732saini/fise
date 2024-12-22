"""
Parsers Module
--------------

This module comprises utitlity functions for
parsing and extracting fields and attributes.
"""

from typing import TypeAlias
from datetime import datetime

from common import tools, constants
from fields import BaseField, Field, Size
from errors import QueryParseError


# Defines all data types which can be used for representing search query
# projections, condition operands and much more while handling queries.
QueryAttribute: TypeAlias = (
    None | bool | str | int | float | datetime | list["QueryAttribute"] | BaseField
)

# Maps field names with corresponding handler classes.
_fields_map: dict[str, BaseField] = {
    "size": Size,
}


def parse_field(field: str, entity: str) -> BaseField:
    """
    Parses the specified field specifications
    based on the specified entity name.

    #### Params:
    - field (str): String formatted field to be parsed.
    - entity (int): Name of the entity being operated upon.
    """

    # Extracts the field name and its associated arguments if any.
    name, args = tools.tokenize_qualified_clause(field, mandate_args=False)
    name = constants.ALIASES[entity].get(name, name)

    if name not in constants.FIELDS[entity]:
        raise QueryParseError(f"{field!r} is not a valid field!")

    if name in _fields_map:
        return _fields_map[name].parse(args)

    return Field.parse(name)
