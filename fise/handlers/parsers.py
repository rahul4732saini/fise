r"""
Parsers Module
--------------

This module comprises objects and methods for parsing user
queries extracting relevant data for further processing.
"""

from typing import override
from pathlib import Path
import re

from ..common import constants
from ..errors import QueryParseError
from ..shared import DeleteQuery, SearchQuery, FileSearchQuery


def _parse_path(subquery: list[str]) -> tuple[str, Path]:
    r"""
    Parses the file/directory path and its type from the specified sub-query.
    """
    return (
        (subquery[0].lower(), Path(subquery[1]))
        if subquery[0].lower() in constants.PATH_TYPES
        else ("relative", Path(subquery[0]))
    )


def _get_from_keyword_index(query: list[str]) -> int:
    r"""
    Returns the index of the 'from' keyword in the query.
    """

    match = {"from", "FROM"}

    for i, kw in enumerate(query):
        if kw in match:
            return i
    else:
        QueryParseError("Cannot find 'FROM' keyword in the query.")


class FileQueryParser:
    r"""
    FileQueryParser defines methods for parsing
    file search/manipulation operation queries.
    """

    __slots__ = "_query", "_operation", "_size_unit"

    _size_pattern = re.compile(
        rf"^size(\[({'|'.join(constants.SIZE_CONVERSION_MAP)})\]|)$"
    )

    def __init__(self, query: list[str], operation: constants.OPERATIONS) -> None:
        r"""
        Creates an instance of `FileQueryParser` class.

        #### Params:
        - query (list[str]): query to be parsed.
        - operation ['search' | 'delete']: the operation to be performed upon the query.
        """
        self._query = query
        self._operation = operation

        self._size_unit = "B"

    def _parse_fields(self, attrs: list[str] | str) -> list[str]:
        r"""
        Parses the search query fields.
        """

        if type(attrs) is list:
            attrs = "".join(attrs)

        fields = []

        file_fields: set[str] = (
            constants.FILE_FIELDS | constants.FILE_FIELD_ALIASES.keys()
        )

        for field in attrs.split(","):
            if field == "*":
                fields.extend(constants.FILE_FIELDS)

            elif field.startswith("size"):
                if not self._size_pattern.match(field):
                    QueryParseError(
                        f"Found an invalid field {field} in the search query."
                    )

                if field[5:-1]:
                    self._size_unit = field[5:-1]

                fields.append("size")

            elif field in file_fields:
                fields.append(field)

            else:
                QueryParseError(f"Found an invalid field {field} in the search query.")

        return fields

    @staticmethod
    def _parse_directory(subquery: list[str]) -> tuple[Path, str]:
        r"""
        Parses the directory path and its type from the specified sub-query.
        """
        type_, path = _parse_path(subquery)

        if not path.is_dir():
            QueryParseError("The specified path for lookup must be a directory.")

        return path, type_

    def _parse_remove_query(self) -> DeleteQuery:
        r"""
        Parses the file deletion query.
        """

        if self._query[0].lower() != "from":
            QueryParseError("Cannot find 'FROM' keyword in the query.")

        # TODO: condition parsing.

        return DeleteQuery(
            *self._parse_directory(self._query[1:]), lambda metadata: True
        )

    def _parse_search_query(self) -> FileSearchQuery:
        r"""
        Parses the file search query.
        """

        from_index: int = _get_from_keyword_index(self._query)

        fields: list[str] = self._parse_fields(self._query[:from_index])
        directory, path_type = self._parse_directory(self._query[from_index + 1 :])

        # TODO: condition parsing

        return FileSearchQuery(
            directory, path_type, lambda metadata: True, fields, self._size_unit
        )

    def parse_query(self) -> FileSearchQuery | DeleteQuery:
        r"""
        Parses the file search/deletion query.
        """
        return (
            self._parse_search_query()
            if self._operation == "search"
            else self._parse_remove_query()
        )


class FileDataQueryParser:
    r"""
    FileDataQueryParser defines methods for
    parsing file data search operation queries.
    """

    __slots__ = ("_query",)

    def __init__(self, query: str | list[str]) -> None:
        r"""
        Creates an instance of the `FileDataQueryParser` class.

        #### Params:
        - query (list[str]): query to be parsed.
        """
        self._query = query

    @staticmethod
    def _parse_fields(attrs: list[str] | str) -> list[str]:
        r"""
        Parses the data search query fields.
        """

        if type(attrs) is list:
            attrs = "".join(attrs)

        fields = []

        data_fields: set[str] = (
            constants.DATA_FIELDS | constants.DATA_FIELD_ALIASES.keys()
        )

        for field in attrs.split(","):
            if field == "*":
                fields.extend(constants.DATA_FIELDS)

            elif field in data_fields:
                fields.append(field)

            else:
                QueryParseError(f"Found an invalid field {field} in the search query.")

        return fields

    @staticmethod
    def _parse_path(subquery: list[str]) -> tuple[Path, str]:
        r"""
        Parses the file/directory path and its type from the specified sub-query.
        """
        type_, path = _parse_path(subquery)

        if (path.is_dir() or path.is_file()) is False:
            QueryParseError(
                "The specified path for lookup must be a file or directory."
            )

        return path, type_

    def parse_query(self) -> SearchQuery:
        r"""
        Parses the file data search query.
        """

        from_index: int = _get_from_keyword_index(self._query)

        fields: list[str] = self._parse_fields(self._query[:from_index])
        path, path_type = self._parse_path(self._query[from_index + 1 :])

        # TODO: condition parsing

        return SearchQuery(path, path_type, lambda metadata: True, fields)


class DirectoryQueryParser(FileQueryParser):
    r"""
    DirectoryQueryParser defines methods for parsing
    directory search/manipulation operation queries.
    """

    __slots__ = "_query", "_operation"

    @override
    def __init__(self, query: str | list[str], operation: constants.OPERATIONS) -> None:
        r"""
        Creates an instance of the `DirectoryQueryParser` class.

        #### Params:
        - query (list[str]): query to be parsed.
        - operation ['select' | 'delete']: the operation to be performed upon the query.
        """
        self._query = query
        self._operation = operation

    @override
    def _parse_fields(self, attrs: list[str] | str) -> list[str]:
        r"""
        Parses the directory search query fields.
        """

        if type(attrs) is list:
            attrs = "".join(attrs)

        fields = []

        dir_fields: set[str] = constants.DIR_FIELDS | constants.DIR_FIELD_ALIASES.keys()

        for field in attrs.split(","):
            if field == "*":
                fields.extend(constants.FILE_FIELDS)

            elif field in dir_fields:
                fields.append(field)

            else:
                QueryParseError(f"Found an invalid field {field} in the search query.")

        return fields

    @override
    def _parse_search_query(self) -> SearchQuery:
        r"""
        Parses the file search query.
        """

        from_index: int = _get_from_keyword_index(self._query)

        fields: list[str] = self._parse_fields(self._query[:from_index])
        directory, path_type = self._parse_directory(self._query[from_index + 1 :])

        # TODO: condition parsing

        return SearchQuery(directory, path_type, lambda metadata: True, fields)
