"""
This module comprises test cases for verifying the utility
functions defined within the common/tools.py module in FiSE.
"""

from pathlib import Path

import pytest
from fise.common import tools, constants


BASE_DIR = Path(__file__).parent

TEST_DIR = BASE_DIR / Path("test_directory/file_dir/")
TEST_TOOLS_HDF_FILE = BASE_DIR / Path("test_tools.hdf").as_posix()


# The following block comprises constants used
# by the test functions for smoother opeation.


TOKENIZE_FUNC_ARGS = [
    ("select * from .", " ", True),
    ("select[TYPE data, MODE bytes] name, atime FROM .", " ", True),
    ("name, parent, ctime, atime", ",", False),
    ("ctime < 2020-01-01 AND ( name = 'hello.py' OR parent = 'dir' )", " ", True),
]
TOKENIZE_FUNC_RESULTS = [
    ("select", "*", "from", "."),
    ("select[TYPE data, MODE bytes]", "name,", "atime", "FROM", "."),
    ("name", "parent", "ctime", "atime"),
    ("ctime", "<", "2020-01-01", "AND", "( name = 'hello.py' OR parent = 'dir' )"),
]

TOKENIZE_QCLAUSE_FUNC_ARGS = [
    ("select[TYPE data, MODE bytes]", False),
    ("File[./hello.xlsx]", True),
    ("delete", False),
    ("SIZE[Kb]", True),
]
TOKENIZE_QCLAUSE_FUNC_RESULTS = [
    ("select", "TYPE data, MODE bytes"),
    ("file", "./hello.xlsx"),
    ("delete", ""),
    ("size", "Kb"),
]

FIND_BASE_STRING_FUNC_ARGS = [
    ("name AND (atime OR ctime)", constants.LOGICAL_OPERATORS),
    (r"name Like '^.*\.py$'", constants.CONDITION_OPERATORS),
    ("(atime > 2020-01-01) OR name = 'hello.py'", constants.SYMBOLIC_OPERATORS),
    ("(name like 'main.py') AND atime in [2020-01-01]", constants.LEXICAL_OPERATORS),
]
FIND_BASE_STRING_FUNC_RESULTS = [
    (5, 8),
    (5, 9),
    (29, 30),
    (32, 34),
]


# The following block comprise functions for testing
# the functions defined within the `tools` module.


@pytest.mark.parametrize(
    ("args", "result"),
    zip(TOKENIZE_FUNC_ARGS, TOKENIZE_FUNC_RESULTS),
)
def test_tokenize_func(args: tuple[str, str, bool], result: tuple[str]) -> None:
    """Tests the `tools.tokenize` function."""

    parsed = tuple(tools.tokenize(*args))
    assert result == parsed


@pytest.mark.parametrize(
    ("args", "result"), zip(TOKENIZE_QCLAUSE_FUNC_ARGS, TOKENIZE_QCLAUSE_FUNC_RESULTS)
)
def test_tokenize_qualified_clause_func(
    args: tuple[str, bool], result: tuple[str, str]
) -> None:
    """Tests the `tools.tokenize_qualified_clause` function."""

    parsed = tools.tokenize_qualified_clause(*args)
    assert result == parsed


@pytest.mark.parametrize(
    ("args", "result"),
    zip(FIND_BASE_STRING_FUNC_ARGS, FIND_BASE_STRING_FUNC_RESULTS),
)
def test_find_base_string_func(
    args: tuple[str, tuple[str]], result: tuple[int, int] | None
) -> None:
    """Tests the `tools.find_base_string` function."""

    indices = tools.find_base_string(*args)
    assert result == indices
