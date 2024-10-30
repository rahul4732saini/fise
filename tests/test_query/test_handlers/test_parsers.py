"""
This module comprises test cases for verifying
the functionality of parser classes in FiSE.
"""

# NOTE:
# The structural format of the attributes comprising test parameters
# and results defined within this module are as described below:
#
#   1. Test parameters for search and delete queries:
#
# The attributes comprising parameters for search and delete query tests
# comprise strings containing the test queries.
#
#   2. Test results for search queries:
#
# The attributes comprising results for search query tests comprise sub-arrays, each
# with a variable length where the first element of each of them signifies whether the
# path is absolute (True) or relatve (False) whereas the last element is another array
# comprising column names. The remaining elements in the array are test specific and may
# different with different tests.
#
#   3. Test results for delete queries:
#
# The attributes comprising parameters for delete query tests comprise boolean objects
# signifying whether the specified path-type is absolute (True) or relative (False).


from pathlib import Path
from typing import Any

import pytest

from fise.shared import SearchQuery, DeleteQuery
from fise.common import tools, constants
from fise.query.parsers import (
    DirectoryQueryParser,
    FileQueryParser,
    FileDataQueryParser,
)


def examine_search_query(
    parser: FileQueryParser | FileDataQueryParser | DirectoryQueryParser,
    results: list[Any],
) -> SearchQuery:
    """
    Tests the seach query based on the specified query parser and returns the
    `SearchQuery` object for cases where additional tests are to be performed.
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


def examine_delete_query(
    parser: FileQueryParser | DirectoryQueryParser, is_absolute: bool
) -> None:
    """Tests the delete query based on the specified parser and results."""

    delete_query: DeleteQuery = parser.parse_query()
    path: Path = Path(".")

    if is_absolute:
        path = path.resolve()

    assert delete_query.path == path
    assert callable(delete_query.condition)


class TestFileQueryParser:
    """Tests the FileQueryParser class"""

    search_query_test_params = [
        "* FROM .",
        "name, path, parent FROM ABSOLUTE '.'",
        "access_time,modify_time from RELATIVE .",
        r"* FROM ABSOLUTE . WHERE filetype = '.txt' AND name LIKE '^report-[0-9]*\.txt$'",
        "name, path,access_time FROM . WHERE access_time >= '2023-04-04'",
        "* FROM '.' WHERE create_time >= '2024-02-20'",
    ]

    search_query_with_size_fields_test_params = [
        "size, size[B] FROM . WHERE filetype = '.py' AND size[KiB] > 512",
        "size[b],size,size[TiB] FROM ABSOLUTE .",
        "size[MB], size[GB], size[B] FROM . WHERE size[MiB] > 10",
    ]

    search_query_with_field_aliases_test_params = [
        "filename, filepath FROM ABSOLUTE .",
        "filepath, ctime,atime FROM . WHERE atime <= '2023-01-01' AND ctime >= '2006-02-20'",
        "filename, type, mtime FROM RELATIVE . WHERE type = '.png'",
    ]

    delete_query_test_params = [
        "FROM ABSOLUTE .",
        "FROM . WHERE type = '.py' and 'fise' in parent",
        "FROM RELATIVE . WHERE atime <= '2012-02-17' OR ctime <= '2015-03-23'",
    ]

    search_query_test_results = [
        [False, list(constants.FILE_FIELDS)],
        [True, ["name", "path", "parent"]],
        [False, ["access_time", "modify_time"]],
        [True, list(constants.FILE_FIELDS)],
        [False, ["name", "path", "access_time"]],
        [False, list(constants.FILE_FIELDS)],
    ]

    search_query_with_size_fields_test_results = [
        [False, [1, 1], ["size", "size[B]"]],
        [True, [0.125, 1, 1024**4], ["size[b]", "size", "size[TiB]"]],
        [False, [1e6, 1e9, 1], ["size[MB]", "size[GB]", "size[B]"]],
    ]

    search_query_with_field_aliases_test_results = [
        [True, ["name", "path"], ["filename", "filepath"]],
        [False, ["path", "create_time", "access_time"], ["filepath", "ctime", "atime"]],
        [False, ["name", "filetype", "modify_time"], ["filename", "type", "mtime"]],
    ]

    delete_query_test_results = [True, False, False]

    @pytest.mark.parametrize(
        ("subquery", "results"),
        zip(search_query_test_params, search_query_test_results),
    )
    def test_search_query(self, subquery: str, results: list[Any]) -> None:
        """Tests the file query parser with search queries."""

        query: list[str] = tools.parse_query(subquery)
        parser = FileQueryParser(query, "search")

        search_query: SearchQuery = examine_search_query(parser, results)
        fields: list[str] = results[1]

        assert [field.field for field in search_query.fields] == fields

    @pytest.mark.parametrize(
        ("subquery", "results"),
        zip(
            search_query_with_size_fields_test_params,
            search_query_with_size_fields_test_results,
        ),
    )
    def test_search_query_with_size_fields(
        self, subquery: str, results: list[Any]
    ) -> None:
        """
        Tests the file query parser with search queries comprising size fields.
        """

        query: list[str] = tools.parse_query(subquery)
        parser = FileQueryParser(query, "search")

        search_query: SearchQuery = examine_search_query(parser, results)
        divisors: list[int | float] = results[1]

        assert [field.divisor for field in search_query.fields] == divisors

    @pytest.mark.parametrize(
        ("subquery", "results"),
        zip(
            search_query_with_field_aliases_test_params,
            search_query_with_field_aliases_test_results,
        ),
    )
    def test_search_query_with_field_aliases(
        self, subquery: str, results: list[Any]
    ) -> None:
        """
        Tests the file query parser with search queries comprising field aliases.
        """

        query: list[str] = tools.parse_query(subquery)
        parser = FileQueryParser(query, "search")

        search_query: SearchQuery = examine_search_query(parser, results)
        fields: list[str] = results[1]

        assert [field.field for field in search_query.fields] == fields

    @pytest.mark.parametrize(
        ("subquery", "is_absolute"),
        zip(delete_query_test_params, delete_query_test_results),
    )
    def test_delete_query(self, subquery: str, is_absolute: bool) -> None:
        """Tests the file query parser with delete queries."""

        query: list[str] = tools.parse_query(subquery)
        parser = FileQueryParser(query, "delete")

        examine_delete_query(parser, is_absolute)


class TestFileDataQueryParser:
    """Tests the FileDataQueryParser class."""

    search_query_test_params = [
        "* FROM .",
        "name, path, dataline FROM ABSOLUTE '.'",
        "path, lineno, dataline FROM RELATIVE . WHERE type = '.py'",
        "* FROM '.' WHERE lineno BETWEEN (0, 100)",
    ]

    search_query_with_field_aliases_test_params = [
        "filename, data FROM .",
        "filename, type, line FROM RELATIVE . WHERE type = '.py' AND line > 10",
        "filename, filepath FROM ABSOLUTE . WHERE 'test' in data",
    ]

    search_query_test_results = [
        [False, list(constants.DATA_FIELDS)],
        [True, ["name", "path", "dataline"]],
        [False, ["path", "lineno", "dataline"]],
        [False, list(constants.DATA_FIELDS)],
    ]

    search_query_with_field_aliases_test_results = [
        [False, ["name", "dataline"], ["filename", "data"]],
        [False, ["name", "filetype", "dataline"], ["filename", "type", "line"]],
        [True, ["name", "path"], ["filename", "filepath"]],
    ]

    @pytest.mark.parametrize(
        ("subquery", "results"),
        zip(search_query_test_params, search_query_test_results),
    )
    def test_search_query(self, subquery: str, results: list[Any]) -> None:
        """
        Tests the file data query parser with search queries.
        """

        query: list[str] = tools.parse_query(subquery)
        parser = FileDataQueryParser(query)

        search_query: SearchQuery = examine_search_query(parser, results)
        fields: list[str] = results[1]

        assert [field.field for field in search_query.fields] == fields

    @pytest.mark.parametrize(
        ("subquery", "results"),
        zip(
            search_query_with_field_aliases_test_params,
            search_query_with_field_aliases_test_results,
        ),
    )
    def test_search_query(self, subquery: str, results: list[Any]) -> None:
        """
        Tests the file data query parser with search queries comprising field aliases.
        """

        query: list[str] = tools.parse_query(subquery)
        parser = FileDataQueryParser(query)

        search_query: SearchQuery = examine_search_query(parser, results)
        fields: list[str] = results[1]

        assert [field.field for field in search_query.fields] == fields


class TestDirectoryQueryParser:
    """Tests the DirectoryQueryParser class"""

    search_query_test_params = [
        "* FROM .",
        "name, path, parent FROM ABSOLUTE '.'",
        "access_time,modify_time from RELATIVE . WHERE name in ('docs', 'documents')",
        "name, path,access_time FROM . WHERE atime >= '2023-04-04' OR ctime >= '2023-12-04'",
        "* FROM ABSOLUTE '.' WHERE atime >= '2024-02-20'",
    ]

    search_query_with_field_aliases_test_params = [
        "ctime,atime FROM . WHERE atime <= '2023-01-01' AND ctime >= '2006-02-20'",
        "mtime, ctime FROM RELATIVE . WHERE mtime BETWEEN ('2021-03-12', '2021-04-12')",
    ]

    delete_query_test_params = [
        "FROM ABSOLUTE .",
        "FROM . WHERE name IN ('reports', 'media') AND 'fise' in parent",
        "FROM RELATIVE . WHERE atime <= '2012-02-17' OR ctime <= '2015-03-23'",
    ]

    search_query_test_results = [
        [False, list(constants.DIR_FIELDS)],
        [True, ["name", "path", "parent"]],
        [False, ["access_time", "modify_time"]],
        [False, ["name", "path", "access_time"]],
        [True, list(constants.DIR_FIELDS)],
    ]

    search_query_with_field_aliases_test_results = [
        [False, ["create_time", "access_time"], ["ctime", "atime"]],
        [False, ["modify_time", "create_time"], ["mtime", "ctime"]],
    ]

    delete_query_test_results = [True, False, False]

    @pytest.mark.parametrize(
        ("subquery", "results"),
        zip(search_query_test_params, search_query_test_results),
    )
    def test_search_query(self, subquery: str, results: list[Any]) -> None:
        """Tests the directory query parser with search queries."""

        query: list[str] = tools.parse_query(subquery)
        parser = DirectoryQueryParser(query, "search")

        search_query: SearchQuery = examine_search_query(parser, results)
        fields: list[str] = results[1]

        assert [field.field for field in search_query.fields] == fields

    @pytest.mark.parametrize(
        ("subquery", "results"),
        zip(
            search_query_with_field_aliases_test_params,
            search_query_with_field_aliases_test_results,
        ),
    )
    def test_search_query_with_field_aliases(
        self, subquery: str, results: list[Any]
    ) -> None:
        """
        Tests the file query parser with search queries comprising field aliases.
        """

        query: list[str] = tools.parse_query(subquery)
        parser = FileQueryParser(query, "search")

        search_query: SearchQuery = examine_search_query(parser, results)
        fields: list[str] = results[1]

        assert [field.field for field in search_query.fields] == fields

    @pytest.mark.parametrize(
        ("subquery", "is_absolute"),
        zip(delete_query_test_params, delete_query_test_results),
    )
    def test_delete_query(self, subquery: str, is_absolute: bool) -> None:
        """Tests the file query parser with delete queries."""

        query: list[str] = tools.parse_query(subquery)
        parser = FileQueryParser(query, "delete")

        examine_delete_query(parser, is_absolute)
