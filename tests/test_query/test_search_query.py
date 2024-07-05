"""
This module comprises test cases for verifying
the functionality of search queries in FiSE.
"""

from pathlib import Path

import pytest
import pandas as pd

from fise.common import constants
from fise.query import QueryHandler

TEST_DIRECTORY = Path(__file__).parents[1] / "test_directory"


class TestFileSearchQuery:
    """Tests the file search queries."""

    basic_query_syntax_params = [
        f"R SELECT * FROM '{TEST_DIRECTORY / 'file_dir'}'",
        f"SELECT[TYPE FILE] name, filetype FROM '{TEST_DIRECTORY / 'file_dir'}'",
        f"RECURSIVE SELECT * FROM '{TEST_DIRECTORY}' WHERE filetype = '.py'",
    ]

    mixed_case_query_params = [
        f"r Select * FroM '{TEST_DIRECTORY / 'file_dir'}'",
        f"sELect[TYPE FILE] Name, FileType From '{TEST_DIRECTORY / 'file_dir'}'",
        f"RecURSive sELECt * From '{TEST_DIRECTORY}' wHErE FilETypE = '.py'",
    ]

    # Some of the test don't explicitly verify the extracted data as it is flexible and
    # subject to change depending on the system and path the tests are executed from.

    @pytest.mark.parametrize("query", basic_query_syntax_params)
    def test_basic_query_syntax(self, query: str) -> None:
        """Tests the basic file search query syntax."""

        data: pd.DataFrame = QueryHandler(query).handle()
        assert isinstance(data, pd.DataFrame)

    @pytest.mark.parametrize("field", constants.FILE_FIELDS)
    def test_individual_fields(self, field: str) -> None:
        """Tests file search queries with all file fields individually."""

        query: str = f"select {field} from '{TEST_DIRECTORY}'"

        data: pd.DataFrame = QueryHandler(query).handle()
        assert isinstance(data, pd.DataFrame)

    # The following test uses the same delete queries defined for basic query syntax test
    # comprising characters of mixed cases, and hence uses the file and directory records
    # stored at the same path in the `test_delete_query.hdf` file.

    @pytest.mark.parametrize("query", mixed_case_query_params)
    def test_mixed_case_query(self, query: str) -> None:
        """Tests file search queries comprising characters of mixed cases."""

        data: pd.DataFrame = QueryHandler(query).handle()
        assert isinstance(data, pd.DataFrame)


class TestDirSearchQuery:
    """Tests the directory search queries."""

    basic_query_syntax_params = [
        f"R SELECT[TYPE DIR] * FROM '{TEST_DIRECTORY / 'file_dir'}'",
        f"SELECT[TYPE DIR] name, parent, ctime FROM '{TEST_DIRECTORY / 'file_dir'}'",
        f"RECURSIVE SELECT[TYPE DIR] * FROM '{TEST_DIRECTORY}' WHERE name in ('orders', 'reports')",
    ]

    mixed_case_query_params = [
        f"r SELECT[Type DiR] * fROm '{TEST_DIRECTORY / 'file_dir'}'",
        f"sEleCt[typE dIr] name, parent, ctime FroM '{TEST_DIRECTORY / 'file_dir'}'",
        f"Recursive Select[TYPE DIR] * From '{TEST_DIRECTORY}' Where name In ('orders', 'reports')",
    ]

    # Some of the test don't explicitly verify the extracted data as it is flexible and
    # subject to change depending on the system and path the tests are executed from.

    @pytest.mark.parametrize("query", basic_query_syntax_params)
    def test_basic_query_syntax(self, query: str) -> None:
        """Tests the basic directory search query syntax."""

        data: pd.DataFrame = QueryHandler(query).handle()
        assert isinstance(data, pd.DataFrame)

    @pytest.mark.parametrize("field", constants.DIR_FIELDS)
    def test_individual_fields(self, field: str) -> None:
        """Tests individual fields in directory search queries."""

        query: str = f"select[type dir] {field} from '{TEST_DIRECTORY}'"

        data: pd.DataFrame = QueryHandler(query).handle()
        assert isinstance(data, pd.DataFrame)

    # The following test uses the same delete queries defined for basic query syntax test
    # comprising characters of mixed cases, and hence uses the file and directory records
    # stored at the same path in the `test_delete_query.hdf` file.

    @pytest.mark.parametrize("query", mixed_case_query_params)
    def test_mixed_case_query(self, query: str) -> None:
        """Tests directory search queries comprising characters of mixed cases."""

        data: pd.DataFrame = QueryHandler(query).handle()
        assert isinstance(data, pd.DataFrame)
