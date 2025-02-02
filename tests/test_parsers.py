"""
This module comprises functions for testing the parser
functions defined within the `parsers.py` file in FiSE.
"""

from datetime import date, datetime
import pytest
from fise import parsers


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
