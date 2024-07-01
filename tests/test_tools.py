"""
Tests the `common/tools.py` module.
"""

from pathlib import Path

import pandas as pd
import pytest

from fise.common import tools

TEST_DIRECTORY = Path(__file__).parent / "test_directory"

# Test parameters for individual functions defined below

PARSE_QUERY_FUNC_PARAMS = [
    r"SELECT[TYPE FILE] * FROM . WHERE name LIKE '^.*\.py$' AND ctime BETWEEN ('2020-01-01', '2022-01-01')",
    "DELETE[TYPE DIR] FROM '/home/user/Projects 2020' WHERE 'temp' IN name",
    "SELECT[TYPE DATA, MODE BYTES] lineno, dataline FROM ./fise/main.py WHERE '#TODO' IN dataline",
    "SELECT path, size FROM ./documents WHERE filetype='.docx' AND (ctime < '2022-01-01' OR ctime > '2023-12-31')",
]

GET_FILES_FUNC_PARAMS = [
    (1, TEST_DIRECTORY, True),
    (2, TEST_DIRECTORY / "file_dir", False),
    (3, TEST_DIRECTORY / "file_dir/docs", True),
]

GET_DIRS_FUNC_PARAMS = [
    (1, TEST_DIRECTORY, True),
    (2, TEST_DIRECTORY / "file_dir", False),
    (3, TEST_DIRECTORY / "file_dir/reports", True),
]

# Test results for individual functions defined below

PARSE_QUERY_TEST_RESULTS = [
    [
        "SELECT[TYPE FILE]", "*", "FROM", ".", "WHERE",
        "name", "LIKE", r"'^.*\.py$'", "AND", "ctime",
        "BETWEEN", "('2020-01-01', '2022-01-01')",
    ],
    [
        "DELETE[TYPE DIR]", "FROM",
        "'/home/user/Projects 2020'",
        "WHERE", "'temp'", "IN", "name",
    ],
    [
        "SELECT[TYPE DATA, MODE BYTES]", "lineno,",
        "dataline", "FROM", "./fise/main.py", "WHERE",
        "'#TODO'", "IN", "dataline",
    ],
    [
        "SELECT", "path,", "size", "FROM", "./documents",
        "WHERE", "filetype='.docx'", "AND",
        "(ctime < '2022-01-01' OR ctime > '2023-12-31')",
    ],
]


def read_tests_hdf(path: str) -> pd.Series | pd.DataFrame:
    """Reads test data from `test_tools.hdf` file."""

    with pd.HDFStore(Path(__file__).parent / "test_tools.hdf") as store:
        return store[path]


@pytest.mark.parametrize(
    ("query", "result"), zip(PARSE_QUERY_FUNC_PARAMS, PARSE_QUERY_TEST_RESULTS)
)
def test_parse_query_function(query: str, result: list[str]) -> None:
    """Tests the `tools.parse_query` function."""
    parsed_query: list[str] = tools.parse_query(query)
    assert parsed_query == result


@pytest.mark.parametrize(("ctr", "path", "recur"), GET_FILES_FUNC_PARAMS)
def test_get_files_function(ctr: int, path: Path, recur: bool) -> None:
    """Tests the `get_files` function."""
    files: pd.Series = pd.Series(str(path) for path in tools.get_files(path, recur))
    assert files.equals(read_tests_hdf(f"/function/get_files/test{ctr}"))


@pytest.mark.parametrize(("ctr", "path", "recur"), GET_DIRS_FUNC_PARAMS)
def test_get_directories_function(ctr: int, path: Path, recur: bool) -> None:
    """Tests the `get_files` function."""
    files: pd.Series = pd.Series(
        str(path) for path in tools.get_directories(path, recur)
    )
    assert files.equals(read_tests_hdf(f"/function/get_directories/test{ctr}"))
