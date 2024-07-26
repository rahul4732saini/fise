"""
This module comprises test cases for verifying
the functionality of search queries in FiSE.
"""

# NOTE:
# The tests defined within this module don't explicitly verify the extracted
# search data as it is flexible and subject to change depending on the system
# and path the tests are executed from.


from pathlib import Path

import pytest
import pandas as pd

from fise.common import constants
from fise.query import QueryHandler

TEST_DIRECTORY = Path(__file__).parents[1] / "test_directory"
FILE_DIR_TEST_DIRECTORY = TEST_DIRECTORY / "file_dir"
TEST_RECORDS_FILE = Path(__file__).parent / "test_search_query.hdf"


def examine_search_query(query: str) -> None:
    """
    Tests the specified search query.

    The extracted data is also verified with the test records stored at the specified path
    in the `test_search_query.hdf` file if `verify` is explicitly set to `True`.
    """

    data: pd.DataFrame = QueryHandler(query).handle()
    assert isinstance(data, pd.DataFrame)


class TestFileSearchQuery:
    """Tests the QueryHandler class with file search queries"""

    basic_query_syntax_test_params = [
        f"R SELECT * FROM '{FILE_DIR_TEST_DIRECTORY}'",
        f"SELECT[TYPE FILE] name, filetype FROM '{FILE_DIR_TEST_DIRECTORY}'",
        f"RECURSIVE SELECT * FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE filetype = '.py'",
    ]

    recursive_command_test_params = [
        f"R SELECT name, atime, mtime FROM '{FILE_DIR_TEST_DIRECTORY / 'docs'}'",
        f"R SELECT name, filetype FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE filetype = None",
        f"RECURSIVE SELECT path, ctime FROM '{FILE_DIR_TEST_DIRECTORY / 'project'}'",
    ]

    path_types_test_params = [
        f"SELECT name, filetype FROM ABSOLUTE '{FILE_DIR_TEST_DIRECTORY / 'project'}'",
        f"R SELECT name, atime, ctime FROM RELATIVE '{FILE_DIR_TEST_DIRECTORY}'",
        f"SELECT path, mtime FROM ABSOLUTE '{FILE_DIR_TEST_DIRECTORY}' WHERE type != None",
    ]

    query_conditions_test_params = [
        f"R SELECT name FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE filetype = None",
        f"SELECT atime FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE name in ('REAME.md', 'TODO')",
        f"R SELECT path FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE name = 'Q1' AND size[b] = 0",
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

    @pytest.mark.parametrize("query", recursive_command_test_params)
    def test_recursive_command(self, query: str) -> None:
        """Tests file search queries with the recursive command"""
        examine_search_query(query)

    @pytest.mark.parametrize("query", path_types_test_params)
    def test_path_types(self, query: str) -> None:
        """Tests file search queries with different path types"""
        examine_search_query(query)

    @pytest.mark.parametrize("query", query_conditions_test_params)
    def test_query_conditions(self, query: str) -> None:
        """Tests file search query conditions"""
        examine_search_query(query)

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

    recursive_command_test_params = [
        f"R SELECT[TYPE DIR] name, atime, ctime FROM '{FILE_DIR_TEST_DIRECTORY / 'docs'}'",
        f"R SELECT[TYPE DIR] name FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE atime > '2022-01-01'",
        f"RECURSIVE SELECT[TYPE DIR] path, mtime FROM '{FILE_DIR_TEST_DIRECTORY / 'project'}'",
    ]

    path_types_test_params = [
        f"SELECT[TYPE DIR] path, atime FROM ABSOLUTE '{FILE_DIR_TEST_DIRECTORY}'",
        f"R SELECT[TYPE DIR] name, ctime FROM RELATIVE '{FILE_DIR_TEST_DIRECTORY / 'docs'}'",
        f"SELECT[TYPE DIR] name FROM ABSOLUTE '{FILE_DIR_TEST_DIRECTORY}'",
    ]

    query_conditions_test_params = [
        f"SELECT[TYPE DIR] path, ctime FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE "
        "ctime >= '2022-02-14' AND name IN ('docs', 'reports', 'media')",
        f"R SELECT[TYPE DIR] name, mtime FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE name LIKE '.*'",
        f"SELECT[TYPE DIR] name FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE "
        "atime < '2024-01-01' OR ctime >= '2024-01-01' AND ctime = mtime",
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

    @pytest.mark.parametrize("query", recursive_command_test_params)
    def test_recursive_command(self, query: str) -> None:
        """Tests directory search queries with the recursive command"""
        examine_search_query(query)

    @pytest.mark.parametrize("query", path_types_test_params)
    def test_path_types(self, query: str) -> None:
        """Tests directory search queries with different path types"""
        examine_search_query(query)

    @pytest.mark.parametrize("query", query_conditions_test_params)
    def test_query_conditions(self, query: str) -> None:
        """Tests directory search query conditions"""
        examine_search_query(query)

    @pytest.mark.parametrize("query", mixed_case_query_test_params)
    def test_mixed_case_query(self, query: str) -> None:
        """Tests directory search queries comprising mixed case characters."""
        examine_search_query(query)
