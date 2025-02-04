"""
This module comprises functions for testing the parser
functions defined within the `parsers.py` file in FiSE.
"""

from datetime import date, datetime
import pytest

from fise import parsers
from fise.parsers import QueryAttribute
from fise.common import constants
from fise.fields import Field, Size


# The following block comprises constants
# required by the test functions for operation.


PARSE_DATETIME_FUNC_ARGS = [
    "2022-01-01 10:00:00",
    "1990-12-31",
    "2001-06-30 23:59:59",
]
PARSE_DATETIME_FUNC_RESULTS = [
    datetime(2022, 1, 1, 10),
    datetime(1990, 12, 31),
    datetime(2001, 6, 30, 23, 59, 59),
]

PARSE_GENERIC_FIELD_FUNC_ARGS = [
    ("parent", constants.ENTITY_DIR),
    ("dataline", constants.ENTITY_DATA),
    ("ctime", constants.ENTITY_FILE),
    ("type", constants.ENTITY_DATA),
]
PARSE_GENERIC_FIELD_FUNC_RESULTS = [
    "parent",
    "dataline",
    "create_time",
    "filetype",
]

PARSE_SIZE_FIELD_FUNC_ARGS = [
    "size[KB]",
    "size",
    "size[Tib]",
]
PARSE_SIZE_FIELD_FUNC_RESULTS = [
    constants.SIZE_CONVERSION_MAP["KB"],
    constants.SIZE_CONVERSION_MAP["B"],
    constants.SIZE_CONVERSION_MAP["Tib"],
]

PARSE_ATTRIBUTE_FUNC_ARGS = [
    "1",
    "'hello'",
    "5.44",
    "2022-01-01 02:02:02",
    "[1, 'select', none, 2021-01-02]",
]
PARSE_ATTRIBUTE_FUNC_RESULTS = [
    1,
    "hello",
    5.44,
    datetime(2022, 1, 1, 2, 2, 2),
    [1, "select", None, datetime(2021, 1, 2)],
]

PARSE_FIELD_ATTRIBUTE_FUNC_ARGS = [
    ("ctime", constants.ENTITY_DIR),
    ("filepath", constants.ENTITY_FILE),
    ("type", constants.ENTITY_DATA),
    ("filename", constants.ENTITY_FILE),
]
PARSE_FIELD_ATTRIBUTE_FUNC_RESULTS = [
    "create_time",
    "path",
    "filetype",
    "name",
]

# The following block comprise classes for testing
# the classes defined within the `shared` module.


@pytest.mark.parametrize(
    ("source", "result"),
    zip(PARSE_DATETIME_FUNC_ARGS, PARSE_DATETIME_FUNC_RESULTS),
)
def test_parse_datetime_func(source: str, result: date | datetime) -> None:
    """Tests the `parsers.parse_datetime` function."""

    parsed: date | datetime = parsers.parse_datetime(source)
    assert result == parsed


@pytest.mark.parametrize(
    ("args", "result"),
    zip(PARSE_GENERIC_FIELD_FUNC_ARGS, PARSE_GENERIC_FIELD_FUNC_RESULTS),
)
def test_parse_generic_field_func(args: tuple[str, str], result: str) -> None:
    """Tests the `parsers.parse_field` function with generic query fields."""

    parsed: Field = parsers.parse_field(*args)
    assert result == parsed.field


@pytest.mark.parametrize(
    ("source", "result"),
    zip(PARSE_SIZE_FIELD_FUNC_ARGS, PARSE_SIZE_FIELD_FUNC_RESULTS),
)
def test_parse_size_field_func(source: str, result: str) -> None:
    """Tests the `parsers.parse_field` function with size query fields."""

    parsed: Size = parsers.parse_field(source, constants.ENTITY_FILE)
    assert result == parsed.divisor


@pytest.mark.parametrize(
    ("source", "result"),
    zip(PARSE_ATTRIBUTE_FUNC_ARGS, PARSE_ATTRIBUTE_FUNC_RESULTS),
)
def test_parse_attrbiute_func(source: str, result: str) -> None:
    """Tests the `parsers.parse_attribute` function."""

    parsed: QueryAttribute = parsers.parse_attribute(source)
    assert result == parsed


@pytest.mark.parametrize(
    ("args", "result"),
    zip(PARSE_FIELD_ATTRIBUTE_FUNC_ARGS, PARSE_FIELD_ATTRIBUTE_FUNC_RESULTS),
)
def test_parse_field_attrbiute_func(args: tuple[str, str], result: str) -> None:
    """Tests the `parsers.parse_attribute` function with query fields."""

    parsed: Field = parsers.parse_attribute(*args)
    assert result == parsed.field
