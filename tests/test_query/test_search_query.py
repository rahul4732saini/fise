"""
This module comprises test cases for verifying
the functionality of search queries in FiSE.
"""

# NOTE:
# Some of the tests defined within this module don't explicitly verify the
# extracted search data as it is flexible and subject to change depending
# on the system and path the tests are executed from.


from pathlib import Path

import pytest
import pandas as pd

from fise.common import constants
from fise.query import QueryHandler

TEST_DIRECTORY = Path(__file__).parents[1] / "test_directory"
FILE_DIR_TEST_DIRECTORY = TEST_DIRECTORY / "file_dir"


class TestFileSearchQuery:
    """Tests the file search queries"""

    basic_query_syntax_test_params = [
        f"R SELECT * FROM '{FILE_DIR_TEST_DIRECTORY}'",
        f"SELECT[TYPE FILE] name, filetype FROM '{FILE_DIR_TEST_DIRECTORY}'",
        f"RECURSIVE SELECT * FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE filetype = '.py'",
    ]

    mixed_case_query_test_params = [
        f"r Select * FroM '{FILE_DIR_TEST_DIRECTORY}'",
        f"sELect[TYPE FILE] Name, FileType From '{FILE_DIR_TEST_DIRECTORY}'",
        f"RecURSive sELECt * From '{FILE_DIR_TEST_DIRECTORY}' wHErE FilETypE = '.py'",
    ]

    individual_fields_test_params = constants.FILE_FIELDS + ("*",)

    @pytest.mark.parametrize("query", basic_query_syntax_test_params)
    def test_basic_query_syntax(self, query: str) -> None:
        """Tests the basic file search query syntax."""

        data: pd.DataFrame = QueryHandler(query).handle()
        assert isinstance(data, pd.DataFrame)

    @pytest.mark.parametrize("field", individual_fields_test_params)
    def test_individual_fields(self, field: str) -> None:
        """Tests file search queries with all file fields individually."""

        query: str = f"SELECT {field} FROM '{FILE_DIR_TEST_DIRECTORY}'"

        data: pd.DataFrame = QueryHandler(query).handle()
        assert isinstance(data, pd.DataFrame)

    @pytest.mark.parametrize("query", mixed_case_query_test_params)
    def test_mixed_case_query(self, query: str) -> None:
        """Tests file search queries comprising characters of mixed cases."""

        data: pd.DataFrame = QueryHandler(query).handle()
        assert isinstance(data, pd.DataFrame)


class TestDirSearchQuery:
    """Tests the directory search queries"""

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
        """Tests the basic directory search query syntax."""

        data: pd.DataFrame = QueryHandler(query).handle()
        assert isinstance(data, pd.DataFrame)

    @pytest.mark.parametrize("field", individual_fields_test_params)
    def test_individual_fields(self, field: str) -> None:
        """Tests individual fields in directory search queries."""

        query: str = f"SELECT[TYPE DIR] {field} FROM '{FILE_DIR_TEST_DIRECTORY}'"

        data: pd.DataFrame = QueryHandler(query).handle()
        assert isinstance(data, pd.DataFrame)

    @pytest.mark.parametrize("query", mixed_case_query_test_params)
    def test_mixed_case_query(self, query: str) -> None:
        """Tests directory search queries comprising characters of mixed cases."""

        data: pd.DataFrame = QueryHandler(query).handle()
        assert isinstance(data, pd.DataFrame)
