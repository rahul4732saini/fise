"""
Test Tools Module
-----------------

This module defines functions for testing the utility functions defined
within the common/tools.py module in FiSE.

NOTE:
This module is dependent upon a HDF5 file with the same name located in
the hdf/ directory comprising file and directory records for testing the
`tools.enumerate_files` and `tools.enumerate_directories` function and
stores the following at the below specified paths:

- /enum_files/t<x>: Stores file records for the
`tools.enumerate_files` function.

- /enum_directories/t<x>: Stores directory records for the
`tools.enumerate_directories` function.

where `<x>` denotes the 1-indexed positon of the test case in the associated
constant comprising the results for testing the function below in the module.
"""

from pathlib import Path

import pytest
import pandas

from fise.common import tools, constants


BASE_DIR = Path(__file__).parent
HDF_DIR = BASE_DIR / "hdf"

TEST_DIR = BASE_DIR / "test_directory/file_dir/"
TEST_TOOLS_HDF_FILE = HDF_DIR / "test_tools.hdf"


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
    ("(ctime = atime and atime = mtime)", constants.CONDITION_OPERATORS),
]
FIND_BASE_STRING_FUNC_RESULTS = [
    (5, 8),
    (5, 9),
    (29, 30),
    (32, 34),
    None,
]

ENUM_FILES_FUNC_ARGS = [
    (TEST_DIR, False),
    (TEST_DIR / "project", False),
    (TEST_DIR / "docs", True),
]
ENUM_FILES_FUNC_RESULTS = [
    "/enum_files/t1",
    "/enum_files/t2",
    "/enum_files/t3",
]

ENUM_DIRS_FUNC_ARGS = [
    (TEST_DIR, True),
    (TEST_DIR / "reports", False),
    (TEST_DIR / "docs", True),
]
ENUM_DIRS_FUNC_RESULTS = [
    "/enum_dirs/t1",
    "/enum_dirs/t2",
    "/enum_dirs/t3",
]


# The following block comprises utility functions
# for assisting the test functions defined below.


def read_hdf(key: str) -> pandas.Series | pandas.DataFrame:
    """
    Reads the HDF5 file associated with the test
    functions defined for the tools module.
    """

    global TEST_TOOLS_HDF_FILE
    return pandas.read_hdf(TEST_TOOLS_HDF_FILE, key)


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
    ("args", "result"),
    zip(TOKENIZE_QCLAUSE_FUNC_ARGS, TOKENIZE_QCLAUSE_FUNC_RESULTS),
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


@pytest.mark.parametrize(
    ("args", "result"),
    zip(ENUM_FILES_FUNC_ARGS, ENUM_FILES_FUNC_RESULTS),
)
def test_enum_files_func(args: tuple[str, bool], result: str) -> None:
    """Tests the `tools.enumerate_files` function."""

    files = tools.enumerate_files(Path(args[0]), args[1])
    expected: pandas.Series = read_hdf(result)

    # Extracts the absolute path of the files to check for equality as the
    # function is also specified with an absolute path to the target directory.
    expected_files = (BASE_DIR / file for file in expected)

    assert list(files) == list(expected_files)


@pytest.mark.parametrize(
    ("args", "result"),
    zip(ENUM_DIRS_FUNC_ARGS, ENUM_DIRS_FUNC_RESULTS),
)
def test_enum_dirs_func(args: tuple[str, bool], result: str) -> None:
    """Tests the `tools.enumerate_directories` function."""

    dirs = tools.enumerate_directories(Path(args[0]), args[1])
    expected: pandas.Series = read_hdf(result)

    # Extracts the absolute path of the directories to check for equality as the
    # function is also specified with an absolute path to the target directory.
    expected_dirs = (BASE_DIR / file for file in expected)

    assert list(dirs) == list(expected_dirs)
