"""
This module comprises test cases for verifying
the functionality of parser classes in FiSE.
"""

from pathlib import Path

import pytest

from fise.common import tools, constants
from fise.query.parsers import FileQueryParser
from fise.shared import Field, SearchQuery


class TestFileQueryParser:
    """Tests the FileQueryParser class"""

    file_fields = [Field(field) for field in constants.FILE_FIELDS]

    file_search_query_test_params = [
        "* FROM .",
        "name, path, parent FROM ABSOLUTE '.'",
        "access_time, modify_time from RELATIVE .",
        r"* FROM ABSOLUTE . WHERE type = '.txt' AND name LIKE '^report-[0-9]*\.txt$'",
        "name, path, access_time FROM . WHERE atime >= '2023-04-04' OR ctime >= '2023-12-04'",
        "* FROM '.' WHERE atime >= '2024-02-20'",
    ]

    # The following list comprises results for the file search query test comprising sub-lists,
    # each with a length of 2. The first element of each sub-list signifies whether the path is
    # absolute (True) or relative (False) whereas the second element is a list comprising names
    # of the search fields.
    file_search_query_test_results = [
        [False, list(constants.FILE_FIELDS)],
        [True, ["name", "path", "parent"]],
        [False, ["access_time", "modify_time"]],
        [True, list(constants.FILE_FIELDS)],
        [False, ["name", "path", "access_time"]],
        [False, list(constants.FILE_FIELDS)],
    ]

    @pytest.mark.parametrize(
        ("subquery", "results"),
        zip(file_search_query_test_params, file_search_query_test_results),
    )
    def test_file_search_query_parser(self, subquery, results):
        """
        Tests the file query parser with search queries.
        """

        query: list[str] = tools.parse_query(subquery)

        parser = FileQueryParser(query, "search")
        search_query: SearchQuery = parser.parse_query()

        path: Path = Path(".")
        columns: list[str] = results[1]

        if results[0]:
            path = path.resolve()

        assert search_query.path == path
        assert [field.field for field in search_query.fields] == columns
        assert search_query.columns == columns
