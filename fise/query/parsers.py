"""
Parsers Module
--------------

This module comprises classes and functions for parsing user queries
extracting relevant data for further processing and evaluation.
"""

from pathlib import Path
from typing import Callable

from shared import DeleteQuery, SearchQuery, Directory, DataLine, Field, File, Size
from errors import QueryParseError
from common import constants
from .conditions import ConditionHandler


def _parse_path(subquery: list[str]) -> tuple[bool, Path, int]:
    """
    Parses the file/directory path and its type from the specified sub-query.
    Also returns the index of the file/directory specification in the query
    relative to the specified subquery.
    """

    if subquery[0].lower() in constants.PATH_TYPES:
        # Returns a boolean value rather than a string to signify the file/directory type.
        is_absolute: bool = subquery[0].lower() == "absolute"

        return is_absolute, Path(subquery[1].strip("'\"")), 1

    # Returns `False` for a relative path type as not explicitly specified in query.
    return False, Path(subquery[0].strip("'\"")), 0


def _get_from_keyword_index(subquery: list[str]) -> int:
    """Returns the index of the `FROM` keyword in the specified subquery."""

    for i, kw in enumerate(subquery):
        if kw.lower() == "from":
            return i

    raise QueryParseError("Cannot find 'FROM' keyword in the query.")


def _get_condition_handler(
    subquery: list[str], operation_target: constants.OPERANDS
) -> Callable[[File | DataLine | Directory], bool]:
    """
    Parses the conditions defined in the specified subquery
    and returns a function for filtering records.

    #### Params:
    - subquery (list): Subquery comprising the query conditions.
    - operation_target (constants.OPERANDS): Targeted operand in the query operation.
    """

    # Returns a lambda function returning `True` by default to include all the records
    # during processing in no conditions are explicitly defined in the specified subquery.
    if not subquery:
        return lambda _: True

    if subquery[0].lower() != "where":
        raise QueryParseError(f"Invalid query syntax around {' '.join(subquery)!r}")

    conditions: list[str] = subquery[1:]
    handler = ConditionHandler(conditions, operation_target)

    # Returns the evaluation method for filtering records.
    return handler.eval_conditions


class FileQueryParser:
    """
    FileQueryParser defines methods for parsing file search and delete queries.
    """

    __slots__ = "_query", "_operation", "_from_index"

    _file_fields = set(constants.FILE_FIELDS) | constants.FILE_FIELD_ALIASES.keys()

    def __init__(self, subquery: list[str], operation: constants.OPERATIONS) -> None:

        # This parser class accepts the subquery and parses only the fields, path-type,
        # path, and conditions defined within the query. The initials are parsed beforehand.

        self._query = subquery
        self._operation = operation

        # Stores the index of the `FROM` keyword in the specified subquery.
        self._from_index = _get_from_keyword_index(subquery)

    def _parse_fields(
        self, attrs: str | list[str]
    ) -> tuple[list[Field | Size], list[str]]:
        """
        Parses the search query fields and returns an array of parsed fields and columns.

        #### Params:
        - attrs (str | list[str]): String or a list of strings of query fields.
        """

        fields: list[Field | Size] = []
        columns: list[str] = []

        # Iterates through the specified tokens, parses and stores them in the `fields` list.
        for field in "".join(attrs).split(","):

            # Keep a separate copy of the lowered string to avoid affecting
            # the case of the field string when adding it to the columns.
            col: str = field.lower()

            if field == "*":
                fields += (Field(i) for i in constants.FILE_FIELDS)
                columns += constants.FILE_FIELDS

            elif col.startswith("size"):
                # Parses size from the string and adds it to the `fields` list.
                fields.append(Size.from_string(field))
                columns.append(field)

            elif col in self._file_fields:
                fields.append(Field(constants.FILE_FIELD_ALIASES.get(col, col)))
                columns.append(field)

            else:
                raise QueryParseError(
                    f"Found an invalid field {field!r} in the search query."
                )

        return fields, columns

    def _parse_directory(self) -> tuple[Path, bool, int]:
        """
        Parses the directory path and its metadata.
        """
        is_absolute, path, index = _parse_path(self._query[self._from_index + 1 :])

        if not path.is_dir():
            raise QueryParseError("The specified path for lookup must be a directory.")

        return path, is_absolute, index

    def _parse_remove_query(self) -> DeleteQuery:
        """
        Parses the file delete query.
        """

        if self._from_index != 0:
            raise QueryParseError("Invalid query syntax.")

        path, is_absolute, index = self._parse_directory()

        # Extracts the function for filtering file records.
        condition: Callable[[File | DataLine | Directory], bool] = (
            _get_condition_handler(self._query[self._from_index + index + 2 :])
        )

        return DeleteQuery(path, is_absolute, condition)

    def _parse_search_query(self) -> SearchQuery:
        """
        Parses the file search query.
        """

        fields, columns = self._parse_fields(self._query[: self._from_index])
        path, is_absolute, index = self._parse_directory()

        # Extracts the function for filtering file records.
        condition: Callable[[File | DataLine | Directory], bool] = (
            _get_condition_handler(self._query[self._from_index + index + 2 :])
        )

        return SearchQuery(path, is_absolute, condition, fields, columns)

    def parse_query(self) -> SearchQuery | DeleteQuery:
        """
        Parses the file search/delete query.
        """
        return (
            self._parse_search_query()
            if self._operation == "search"
            else self._parse_remove_query()
        )


class FileDataQueryParser:
    """
    FileDataQueryParser defines methods for parsing file data search queries.
    """

    __slots__ = "_query", "_from_index"

    _data_fields = set(constants.DATA_FIELDS) | constants.DATA_FIELD_ALIASES.keys()

    def __init__(self, subquery: list[str]) -> None:

        # This parser class accepts the subquery and parses only the fields, path-type,
        # path, and conditions defined within the query. The initials are parsed beforehand.

        self._query = subquery

        # Stores the index of the `FROM` keyword in the specified subquery.
        self._from_index = _get_from_keyword_index(subquery)

    def _parse_fields(self, attrs: list[str] | str) -> tuple[list[Field], list[str]]:
        """
        Parses the search query fields and returns an array of parsed fields and columns.

        #### Params:
        - attrs (str | list[str]): String or a list of strings of query fields.
        """

        fields: list[Field] = []
        columns: list[str] = []

        # Iterates through the specified tokens, parses and stores them in the `fields` list.
        for field in "".join(attrs).lower().split(","):
            if field == "*":
                fields += (Field(i) for i in constants.DATA_FIELDS)
                columns += constants.DATA_FIELDS

            elif field in self._data_fields:
                fields.append(Field(constants.DATA_FIELD_ALIASES.get(field, field)))
                columns.append(field)

            else:
                raise QueryParseError(
                    f"Found an invalid field {field!r} in the search query."
                )

        return fields, columns

    def _parse_path(self) -> tuple[Path, bool, int]:
        """
        Parses the file/directory path and its metadata.
        """

        is_absolute, path, index = _parse_path(self._query[self._from_index + 1 :])

        if not (path.is_dir() or path.is_file()):
            raise QueryParseError(
                "The specified path for lookup must be a file or directory."
            )

        return path, is_absolute, index

    def parse_query(self) -> SearchQuery:
        """
        Parses the file data search query.
        """

        fields, columns = self._parse_fields(self._query[: self._from_index])
        path, is_absolute, index = self._parse_path()

        # Extracts the function for filtering file records.
        condition: Callable[[File | DataLine | Directory], bool] = (
            _get_condition_handler(self._query[self._from_index + index + 2 :])
        )

        return SearchQuery(path, is_absolute, condition, fields, columns)


class DirectoryQueryParser(FileQueryParser):
    """
    DirectoryQueryParser defines methods for parsing directory search/delete queries.
    """

    __slots__ = "_query", "_operation", "_from_index"

    _dir_fields = constants.DIR_FIELDS | constants.DIR_FIELD_ALIASES.keys()

    def _parse_fields(self, attrs: list[str] | str) -> tuple[list[Field], list[str]]:
        """
        Parses the search query fields and returns an array of parsed fields and columns.

        #### Params:
        - attrs (str | list[str]): String or a list of strings of query fields to be parsed.
        """

        fields: list[Field] = []
        columns: list[str] = []

        # Iterates through the specified tokens, parses and stores them in the `fields` list.
        for field in "".join(attrs).lower().split(","):
            if field == "*":
                fields += (Field(i) for i in constants.DIR_FIELDS)
                columns += constants.DIR_FIELDS

            elif field in self._dir_fields:
                fields.append(Field(constants.DIR_FIELD_ALIASES.get(field, field)))
                columns.append(field)

            else:
                raise QueryParseError(
                    f"Found an invalid field {field!r} in the search query."
                )

        return fields, columns

    def _parse_search_query(self) -> SearchQuery:
        """
        Parses the directory search query.
        """

        fields, columns = self._parse_fields(self._query[: self._from_index])
        path, is_absolute, index = self._parse_directory()

        # Extracts the function for filtering file records.
        condition: Callable[[File | DataLine | Directory], bool] = (
            _get_condition_handler(self._query[self._from_index + index + 2 :])
        )

        return SearchQuery(path, is_absolute, condition, fields, columns)
