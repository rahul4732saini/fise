"""
This module comprises test cases for verifying
the functionality of search queries in FiSE.
"""

# NOTE:
# Some of the tests defined within this module don't explicitly verify the
# extracted search data as it is flexible and subject to change depending
# on the system and path the tests are executed from.


from pathlib import Path
from typing import Any

import pytest
import pandas as pd

import utils

from fise.common import constants
from fise.query import QueryHandler

TEST_DIRECTORY = Path(__file__).parents[1] / "test_directory"
FILE_DIR_TEST_DIRECTORY = TEST_DIRECTORY / "file_dir"
TEST_RECORDS_FILE = Path(__file__).parent / "test_search_query.hdf"


def verify_search_query(path: str, data: pd.DataFrame) -> None:
    """
    Verifies the pandas dataframe extracted from the search operation with the
    records stored at the specified path in the `test_operators.hdf` file.
    """
    global TEST_RECORDS_FILE

    results: pd.DataFrame = utils.read_hdf(TEST_RECORDS_FILE, path)

    data_set: set[tuple[Any]] = set(tuple(row) for row in data.values)
    results_set: set[tuple[Any]] = set(tuple(row) for row in results.values)

    assert data_set == results_set


def examine_search_query(
    query: str, verify: bool = False, path: str | None = None
) -> None:
    """
    Tests the specified search query.

    The extracted data is also verified with the test records stored at the specified path
    in the `test_search_query.hdf` file if `verify` is explicitly set to `True`.
    """

    data: pd.DataFrame = QueryHandler(query).handle()
    assert isinstance(data, pd.DataFrame)

    if verify:
        verify_search_query(path, data)


class TestFileSearchQuery:
    """Tests the QueryHandler class with file search queries"""

    basic_query_syntax_test_params = [
        f"R SELECT * FROM '{FILE_DIR_TEST_DIRECTORY}'",
        f"SELECT[TYPE FILE] name, filetype FROM '{FILE_DIR_TEST_DIRECTORY}'",
        f"RECURSIVE SELECT * FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE filetype = '.py'",
    ]

    recursive_command_test_params = [
        (1, f"R SELECT name, filetype FROM '{FILE_DIR_TEST_DIRECTORY / 'docs'}'"),
        (2, f"R SELECT name FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE filetype = None"),
        (3, f"RECURSIVE SELECT filetype FROM '{FILE_DIR_TEST_DIRECTORY / 'project'}'"),
    ]

    mixed_case_query_test_params = [
        f"r Select * FroM '{FILE_DIR_TEST_DIRECTORY}'",
        f"sELect[TYPE FILE] Name, FileType From '{FILE_DIR_TEST_DIRECTORY}'",
        f"RecURSive sELECt * From '{FILE_DIR_TEST_DIRECTORY}' wHErE FilETypE = '.py'",
    ]

    individual_fields_test_params = constants.FILE_FIELDS + ("*",)

    @pytest.mark.parametrize("query", basic_query_syntax_test_params)
    def test_basic_query_syntax(self, query: str) -> None:
        """Tests basic syntax for file search queries"""
        examine_search_query(query)

    @pytest.mark.parametrize("field", individual_fields_test_params)
    def test_individual_fields(self, field: str) -> None:
        """Tests file search queries with all file fields individually"""

        query: str = f"SELECT {field} FROM '{FILE_DIR_TEST_DIRECTORY}'"
        examine_search_query(query)

    @pytest.mark.parametrize(("index", "query"), recursive_command_test_params)
    def test_recursive_command(self, index: int, query: str) -> None:
        """Tests file search queries with the recursive command"""
        examine_search_query(query, True, f"/file/search/test{index}")

    @pytest.mark.parametrize("query", mixed_case_query_test_params)
    def test_mixed_case_query(self, query: str) -> None:
        """Tests file search queries comprising mixed case characters"""
        examine_search_query(query)


class TestDirSearchQuery:
    """Tests the QueryHandler class with directory search queries"""

    basic_query_syntax_test_params = [
        f"R SELECT[TYPE DIR] * FROM '{FILE_DIR_TEST_DIRECTORY}'",
        f"RECURSIVE SELECT[TYPE DIR] name, parent, ctime FROM '{FILE_DIR_TEST_DIRECTORY}'",
        f"SELECT[TYPE DIR] * FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE name IN ('orders', 'reports')",
    ]

    mixed_case_query_test_params = [
        f"r SELECT[Type DiR] * fROm '{FILE_DIR_TEST_DIRECTORY}'",
        f"Recursive sEleCt[typE dIr] name, parent, ctime FroM '{FILE_DIR_TEST_DIRECTORY}'",
        f"Select[TYPE DIR] * From '{FILE_DIR_TEST_DIRECTORY}' Where name In ('orders', 'reports')",
    ]

    individual_fields_test_params = constants.DIR_FIELDS + ("*",)

    @pytest.mark.parametrize("query", basic_query_syntax_test_params)
    def test_basic_query_syntax(self, query: str) -> None:
        """Tests basic syntax for directory search queries"""
        examine_search_query(query)

    @pytest.mark.parametrize("field", individual_fields_test_params)
    def test_individual_fields(self, field: str) -> None:
        """Tests file search queries with all directory fields individually"""

        query: str = f"SELECT[TYPE DIR] {field} FROM '{FILE_DIR_TEST_DIRECTORY}'"
        examine_search_query(query)

    @pytest.mark.parametrize("query", mixed_case_query_test_params)
    def test_mixed_case_query(self, query: str) -> None:
        """Tests directory search queries comprising mixed case characters."""
        examine_search_query(query)
