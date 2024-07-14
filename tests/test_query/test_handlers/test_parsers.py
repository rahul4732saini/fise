"""
This module comprises test cases for verifying
the functionality of parser classes in FiSE.
"""

from pathlib import Path

import pytest

from fise.common import tools, constants
from fise.query.parsers import FileQueryParser
from fise.shared import SearchQuery


class TestFileQueryParser:
    """Tests the FileQueryParser class"""

    file_search_query_test_params = [
        "* FROM .",
        "name, path, parent FROM ABSOLUTE '.'",
        "access_time, modify_time from RELATIVE .",
        r"* FROM ABSOLUTE . WHERE type = '.txt' AND name LIKE '^report-[0-9]*\.txt$'",
        "name, path, access_time FROM . WHERE atime >= '2023-04-04' OR ctime >= '2023-12-04'",
        "* FROM '.' WHERE atime >= '2024-02-20'",
    ]

    file_search_query_with_size_fields_test_params = [
        "size, size[B] FROM . WHERE type = '.py' AND size[KiB] > 512",
        "size[b],size,size[TiB] FROM ABSOLUTE .",
        "size[MB], size[GB], size[B] FROM . WHERE size[MiB] > 10",
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

    file_search_query_with_size_fields_test_results = [
        [False, ["B", "B"], ["size", "size[B]"]],
        [True, ["b", "B", "TiB"], ["size[b]", "size", "size[TiB]"]],
        [False, ["MB", "GB", "B"], ["size[MB]", "size[GB]", "size[B]"]],
    ]

    @pytest.mark.parametrize(
        ("subquery", "results"),
        zip(file_search_query_test_params, file_search_query_test_results),
    )
    def test_file_search_query_parser(self, subquery, results) -> None:
        """Tests the file query parser with search queries."""

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

    @pytest.mark.parametrize(
        ("subquery", "results"),
        zip(
            file_search_query_with_size_fields_test_params,
            file_search_query_with_size_fields_test_results,
        ),
    )
    def test_file_search_query_parser_with_size_fields(self, subquery, results) -> None:
        """
        Tests the file query parser with search queries comprising size fields.
        """

        query: list[str] = tools.parse_query(subquery)

        parser = FileQueryParser(query, "search")
        search_query: SearchQuery = parser.parse_query()

        path: Path = Path(".")
        units: list[str] = results[1]
        columns: list[str] = results[2]

        if results[0]:
            path = path.resolve()

        assert search_query.path == path
        assert [field.unit for field in search_query.fields] == units
        assert search_query.columns == columns
