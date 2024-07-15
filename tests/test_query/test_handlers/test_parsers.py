"""
This module comprises test cases for verifying
the functionality of parser classes in FiSE.
"""

from pathlib import Path
from typing import Any

import pytest

from fise.common import tools, constants
from fise.shared import SearchQuery
from fise.query.parsers import (
    FileQueryParser,
    FileDataQueryParser,
    DirectoryQueryParser,
)


def examine_search_query(
    parser: FileQueryParser | FileDataQueryParser | DirectoryQueryParser,
    results: list[Any],
) -> SearchQuery:
    """
    Tests the search query based on the specified sub-query and results and
    returns the `SearchQuery` object for performing additional tests.
    """

    search_query: SearchQuery = parser.parse_query()

    path: Path = Path(".")
    columns: list[str] = results[-1]

    if results[0]:
        path = path.resolve()

    assert callable(search_query.condition)
    assert search_query.path == path
    assert search_query.columns == columns

    return search_query


class TestFileQueryParser:
    """Tests the FileQueryParser class"""

    search_query_test_params = [
        "* FROM .",
        "name, path, parent FROM ABSOLUTE '.'",
        "access_time,modify_time from RELATIVE .",
        r"* FROM ABSOLUTE . WHERE type = '.txt' AND name LIKE '^report-[0-9]*\.txt$'",
        "name, path,access_time FROM . WHERE atime >= '2023-04-04' OR ctime >= '2023-12-04'",
        "* FROM '.' WHERE atime >= '2024-02-20'",
    ]

    search_query_with_size_fields_test_params = [
        "size, size[B] FROM . WHERE type = '.py' AND size[KiB] > 512",
        "size[b],size,size[TiB] FROM ABSOLUTE .",
        "size[MB], size[GB], size[B] FROM . WHERE size[MiB] > 10",
    ]

    # The following list comprises results for the file search query test comprising sub-lists,
    # each with a length of 2. The first element of each sub-list signifies whether the path is
    # absolute (True) or relative (False) whereas the second element is a list comprising names
    # of the search fields.
    search_query_test_results = [
        [False, list(constants.FILE_FIELDS)],
        [True, ["name", "path", "parent"]],
        [False, ["access_time", "modify_time"]],
        [True, list(constants.FILE_FIELDS)],
        [False, ["name", "path", "access_time"]],
        [False, list(constants.FILE_FIELDS)],
    ]

    search_query_with_size_fields_test_results = [
        [False, ["B", "B"], ["size", "size[B]"]],
        [True, ["b", "B", "TiB"], ["size[b]", "size", "size[TiB]"]],
        [False, ["MB", "GB", "B"], ["size[MB]", "size[GB]", "size[B]"]],
    ]

    @pytest.mark.parametrize(
        ("subquery", "results"),
        zip(search_query_test_params, search_query_test_results),
    )
    def test_search_query(self, subquery, results) -> None:
        """Tests the file query parser with search queries."""

        query: list[str] = tools.parse_query(subquery)
        parser = FileQueryParser(query, "search")

        search_query: SearchQuery = examine_search_query(parser, results)
        columns: list[str] = results[1]

        assert [field.field for field in search_query.fields] == columns

    @pytest.mark.parametrize(
        ("subquery", "results"),
        zip(
            search_query_with_size_fields_test_params,
            search_query_with_size_fields_test_results,
        ),
    )
    def test_search_query_with_size_fields(self, subquery, results) -> None:
        """
        Tests the file query parser with search queries comprising size fields.
        """

        query: list[str] = tools.parse_query(subquery)
        parser = FileQueryParser(query, "search")

        search_query: SearchQuery = examine_search_query(parser, results)
        units: list[str] = results[1]

        assert [field.unit for field in search_query.fields] == units


class TestDirectoryQueryParser:
    """Tests the DirectoryQueryParser class"""

    search_query_test_params = [
        "* FROM .",
        "name, path, parent FROM ABSOLUTE '.'",
        "access_time,modify_time from RELATIVE . WHERE name in ('docs', 'documents')",
        "name, path,access_time FROM . WHERE atime >= '2023-04-04' OR ctime >= '2023-12-04'",
        "* FROM ABSOLUTE '.' WHERE atime >= '2024-02-20'",
    ]

    # The following list comprises results for the file search query test comprising sub-lists,
    # each with a length of 2. The first element of each sub-list signifies whether the path is
    # absolute (True) or relative (False) whereas the second element is a list comprising names
    # of the search fields.
    search_query_test_results = [
        [False, list(constants.DIR_FIELDS)],
        [True, ["name", "path", "parent"]],
        [False, ["access_time", "modify_time"]],
        [False, ["name", "path", "access_time"]],
        [True, list(constants.DIR_FIELDS)],
    ]

    @pytest.mark.parametrize(
        ("subquery", "results"),
        zip(search_query_test_params, search_query_test_results),
    )
    def test_search_query(self, subquery, results) -> None:
        """Tests the directory query parser with search queries."""

        query: list[str] = tools.parse_query(subquery)
        parser = DirectoryQueryParser(query, "search")

        search_query: SearchQuery = examine_search_query(parser, results)
        columns: list[str] = results[1]

        assert [field.field for field in search_query.fields] == columns
