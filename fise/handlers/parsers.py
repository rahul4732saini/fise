"""
Parsers Module
--------------

This module comprises objects and methods for parsing user
queries extracting relevant data for further processing.
"""

import re
from pathlib import Path
from typing import Callable, override

from errors import QueryParseError
from common import constants
from .conditions import ConditionHandler
from shared import FileSearchQuery, DeleteQuery, SearchQuery, Directory, DataLine, File


def _parse_path(subquery: list[str]) -> tuple[bool, Path, int]:
    """
    Parses the file/directory path and its type from the specified sub-query.
    Also returns the index of the file/directory relative to the specified subquery.
    """

    if subquery[0].lower() in constants.PATH_TYPES:
        is_absolute: bool = subquery[0].lower() == "absolute"

        return is_absolute, Path(subquery[1]), 1

    # Returns `False` for a relative path type if not specified in query.
    return False, Path(subquery[0]), 0


def _get_from_keyword_index(query: list[str]) -> int:
    """
    Returns the index of the 'from' keyword in the file query.
    """

    match: str[str] = {"from", "FROM"}

    for i, kw in enumerate(query):
        if kw in match:
            return i
    else:
        QueryParseError("Cannot find 'FROM' keyword in the query.")


def _get_condition_handler(
    subquery: list[str],
) -> Callable[[File | DataLine | Directory], bool]:
    """
    Parses the query conditions subquery and returns a function for filitering records.
    """

    # Returns a lambda function returning `True` by default if no conditions
    # are explicitly defined to include all the records during operation.
    if not subquery:
        return lambda _: True

    if subquery[0].lower() != "where":
        QueryParseError(f"Invalid query syntax around {" ".join(subquery)!r}")

    conditions: list[str] = subquery[1:]
    handler = ConditionHandler(conditions)

    # Returns the evaluation method to be called for filtering records.
    return handler.eval_conditions


class FileQueryParser:
    """
    FileQueryParser defines methods for parsing
    file search/delete operation queries.
    """

    __slots__ = "_query", "_operation", "_size_unit", "_from_index"

    _size_field_pattern = re.compile(
        rf"^size(\[({'|'.join(constants.SIZE_CONVERSION_MAP)})\]|)$"
    )

    def __init__(self, subquery: list[str], operation: constants.OPERATIONS) -> None:
        """
        Creates an instance of `FileQueryParser` class.

        #### Params:
        - subquery (list[str]): subquery to be parsed.
        - operation (constants.OPERATIONS): the operation to be performed upon the query.
        """

        # This parser object accepts the subquery and parses only the fields, directory/file
        # and conditions defined within the query. The initials are parsed before-hand and
        # the remaining is handed and parsed here.

        self._query = subquery
        self._operation = operation
        self._from_index = _get_from_keyword_index(subquery)

        # Default size unit for file search queries.
        self._size_unit = "B"

    def _parse_fields(self, attrs: list[str] | str) -> list[str]:
        """
        Parses the search query fields.
        """

        if type(attrs) is list:
            attrs = "".join(attrs)

        fields = []

        file_fields: set[str] = (
            constants.FILE_FIELDS | constants.FILE_FIELD_ALIASES.keys()
        )

        # Iteratres through the specified tokens, parses and stores them in the `fields` list.
        for field in attrs.split(","):
            if field == "*":
                fields.extend(constants.FILE_FIELDS)

            elif field.startswith("size"):
                if not self._size_field_pattern.match(field):
                    QueryParseError(
                        f"Found an invalid field {field} in the search query."
                    )

                # Parses the size unit.
                if field[5:-1]:
                    self._size_unit = field[5:-1]

                fields.append("size")

            elif field in file_fields:
                fields.append(field)

            else:
                QueryParseError(
                    f"Found an invalid field {field!r} in the search query."
                )

        return fields

    @staticmethod
    def _parse_directory(subquery: list[str]) -> tuple[Path, bool, int]:
        """
        Parses the directory path and its type from the specified sub-query.
        """
        is_absolute, path, index = _parse_path(subquery)

        if not path.is_dir():
            QueryParseError("The specified path for lookup must be a directory.")

        return path, is_absolute, index

    def _parse_remove_query(self) -> DeleteQuery:
        """
        Parses the file deletion query.
        """

        if self._from_index != 0:
            QueryParseError("Cannot find 'FROM' keyword in the query.")

        path, is_absolute, index = self._parse_directory(self._query[1:])
        condition: Callable[[File], bool] = _get_condition_handler(
            self._query[self._from_index + index + 2 :]
        )

        return DeleteQuery(path, is_absolute, condition)

    def _parse_search_query(self) -> FileSearchQuery:
        """
        Parses the file search query.
        """

        fields: list[str] = self._parse_fields(self._query[: self._from_index])
        path, is_absolute, index = self._parse_directory(
            self._query[self._from_index + 1 :]
        )

        condition: Callable[[File], bool] = _get_condition_handler(
            self._query[self._from_index + index + 2 :]
        )

        return FileSearchQuery(path, is_absolute, condition, fields, self._size_unit)

    def parse_query(self) -> FileSearchQuery | DeleteQuery:
        """
        Parses the file search/deletion query.
        """
        return (
            self._parse_search_query()
            if self._operation == "search"
            else self._parse_remove_query()
        )


class FileDataQueryParser:
    """
    FileDataQueryParser defines methods for
    parsing file data search operation queries.
    """

    __slots__ = "_query", "_from_index"

    def __init__(self, subquery: list[str]) -> None:
        """
        Creates an instance of the `FileDataQueryParser` class.

        #### Params:
        - subquery (list[str]): query to be parsed.
        """

        # This parser object accepts the subquery and parses only the fields, directory/file
        # and conditions defined within the query. The initials are parsed before-hand and
        # the remaining is handed and parsed here.

        self._query = subquery
        self._from_index = _get_from_keyword_index(subquery)

    @staticmethod
    def _parse_fields(attrs: list[str] | str) -> list[str]:
        """
        Parses the data search query fields.
        """

        if type(attrs) is list:
            attrs = "".join(attrs)

        fields = []

        data_fields: set[str] = (
            constants.DATA_FIELDS | constants.DATA_FIELD_ALIASES.keys()
        )

        # Iteratres through the specified tokens, parses and stores them in the `fields` list.
        for field in attrs.split(","):
            if field == "*":
                fields.extend(constants.DATA_FIELDS)

            elif field in data_fields:
                fields.append(field)

            else:
                QueryParseError(
                    f"Found an invalid field {field!r} in the search query."
                )

        return fields

    @staticmethod
    def _parse_path(subquery: list[str]) -> tuple[Path, bool, int]:
        """
        Parses the file/directory path, its type, and index from the specified sub-query.
        """
        is_absolute, path, index = _parse_path(subquery)

        if (path.is_dir() or path.is_file()) is False:
            QueryParseError(
                "The specified path for lookup must be a file or directory."
            )

        return path, is_absolute, index

    def parse_query(self) -> SearchQuery:
        """
        Parses the file data search query.
        """

        from_index: int = _get_from_keyword_index(self._query)

        fields: list[str] = self._parse_fields(self._query[:from_index])
        path, path_type = self._parse_path(self._query[from_index + 1 :])

        # TODO: condition parsing

        return SearchQuery(path, path_type, lambda metadata: True, fields)


class DirectoryQueryParser(FileQueryParser):
    """
    DirectoryQueryParser defines methods for parsing
    directory search/manipulation operation queries.
    """

    __slots__ = "_query", "_operation"

    @override
    def __init__(
        self, subquery: str | list[str], operation: constants.OPERATIONS
    ) -> None:
        """
        Creates an instance of the `DirectoryQueryParser` class.

        #### Params:
        - subquery (list[str]): query to be parsed.
        - operation (constants.OPERATIONS): the operation to be performed upon the query.
        """

        # This parser object accepts the subquery and parses only the fields, directory/file
        # and conditions defined within the query. The initials are parsed before-hand and
        # the remaining is handed and parsed here.

        self._query = subquery
        self._operation = operation

    @override
    def _parse_fields(self, attrs: list[str] | str) -> list[str]:
        """
        Parses the directory search query fields.
        """

        if type(attrs) is list:
            attrs = "".join(attrs)

        fields = []

        dir_fields: set[str] = constants.DIR_FIELDS | constants.DIR_FIELD_ALIASES.keys()

        # Iteratres through the specified tokens, parses and stores them in the `fields` list.
        for field in attrs.split(","):
            if field == "*":
                fields.extend(constants.FILE_FIELDS)

            elif field in dir_fields:
                fields.append(field)

            else:
                QueryParseError(
                    f"Found an invalid field {field!r} in the search query."
                )

        return fields

    @override
    def _parse_search_query(self) -> SearchQuery:
        """
        Parses the file search query.
        """

        from_index: int = _get_from_keyword_index(self._query)

        fields: list[str] = self._parse_fields(self._query[:from_index])
        directory, path_type = self._parse_directory(self._query[from_index + 1 :])

        # TODO: condition parsing

        return SearchQuery(directory, path_type, lambda metadata: True, fields)
