"""
This module comprises test cases for verifying
the functionality of search queries in FiSE.
"""

from pathlib import Path

import pytest
import pandas as pd

from fise.query import QueryHandler

TEST_DIRECTORY = Path(__file__).parents[1] / "test_directory"


class TestFileSearchQuery:
    """
    Tests the file search queries.
    """

    basic_query_syntax_params = [
        f"R SELECT * FROM '{TEST_DIRECTORY / 'file_dir'}'",
        f"SELECT[TYPE FILE] name, filetype FROM '{TEST_DIRECTORY / 'file_dir'}'",
        f"RECURSIVE SELECT * FROM '{TEST_DIRECTORY}' WHERE filetype = '.py'",
    ]

    @pytest.mark.parametrize("query", basic_query_syntax_params)
    def test_basic_query_syntax(self, query: str) -> None:
        """
        Tests the basic file search query syntax.
        """

        # This test doesn't explicitly verifies the extracted data is flexible and
        # subject to change depending on the system and path it's executed from.

        data: pd.DataFrame = QueryHandler(query).handle()
        assert isinstance(data, pd.DataFrame)
