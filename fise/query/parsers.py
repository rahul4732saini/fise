"""
Parsers Module
--------------

This module comprises classes and functions for parsing user queries
extracting relevant data for further processing and evaluation.
"""

# NOTE
# The parser classes defined within this module only parse the search fields
# (explicilty for search operation), path, path-type and the conditions defined
# within the query. The initials are parsed beforehand.

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable

from errors import QueryParseError
from common import constants
from entities import BaseEntity
from .conditions import ConditionHandler
from shared import Query, DeleteQuery, SearchQuery
from fields import BaseField, parse_field


class BaseQueryParser(ABC):
    """
    BaseQueryParser serves as the base
    class for all query parser classes.
    """

    # The following class attributes are essential for operation
    # and must be explicitly defined by the child classes.
    _entity: int
    _fields: tuple[str, ...]

    @abstractmethod
    def parse_query(self) -> Query: ...

    @staticmethod
    def _parse_path(subquery: list[str]) -> tuple[Path, int]:
        """
        Parses the file/directory path and its type from the specified sub-query.
        Also returns the index of the file/directory specifications in the query.

        NOTE:
        The index of the path specifications is relative to the specified
        sub-query, not the overall user query.
        """

        path_type: str = constants.PATH_RELATIVE
        path_specs_index: int = 0

        if subquery[0].lower() in constants.PATH_TYPES:
            path_type = subquery[0].lower()
            path_specs_index = 1

        raw_path: str = subquery[path_specs_index]

        # Removes the leading and trailing quotes if explicitly specified within the path.
        if constants.STRING_PATTERN.match(raw_path):
            raw_path = raw_path[1:-1]

        path: Path = Path(raw_path)

        if path_type == constants.PATH_ABSOLUTE:
            path = path.resolve()

        return path, path_specs_index

    @staticmethod
    def _get_from_keyword_index(subquery: list[str]) -> int:
        """Returns the index of the `FROM` keyword in the specified subquery."""

        for i, kw in enumerate(subquery):
            if kw.lower() == constants.KEYWORD_FROM:
                return i

        raise QueryParseError("Cannot find the 'FROM' keyword in the query.")

    def _get_condition_handler(
        self, subquery: list[str]
    ) -> Callable[[BaseEntity], bool]:
        """
        Parses the conditions defined within the specified
        subquery and returns a function for evluating them.

        #### Params:
        - subquery (list): Subquery comprising the query conditions.
        """

        # Returns a hard-coded lambda function to return 'True' to include all
        # the records during evaluation if no conditions are explicitly defined.
        if not subquery:
            return lambda _: True

        if subquery[0].lower() != constants.KEYWORD_WHERE:
            raise QueryParseError(f"Invalid query syntax around {' '.join(subquery)!r}")

        conditions: list[str] = subquery[1:]
        handler = ConditionHandler(conditions, self._entity)

        # Returns the evaluation method for filtering records.
        return handler.eval_conditions

    def _parse_fields(self, attrs: list[str]) -> tuple[list[BaseField], list[str]]:
        """
        Parses the search query fields and returns an
        tuple of the parsed fields and column labels.

        #### Params:
        - attrs (list[str]): List of query fields.
        """

        if not attrs:
            raise QueryParseError("No search fields were specified!")

        fields: list[BaseField] = []
        columns: list[str] = []

        for field in "".join(attrs).split(","):
            if field == "*":
                fields += (parse_field(i, self._entity) for i in self._fields)
                columns += self._fields

            else:
                fields.append(parse_field(field, self._entity))
                columns.append(field)

        return fields, columns


class FileQueryParser(BaseQueryParser):
    """
    FileQueryParser defines methods for parsing file search and delete queries.
    """

    __slots__ = "_query", "_operation", "_from_index"

    _entity = constants.ENTITY_FILE
    _fields = constants.FILE_FIELDS

    def __init__(self, subquery: list[str], operation: constants.OPERATIONS) -> None:
        self._query = subquery
        self._operation = operation

        # Stores the index of the `FROM` keyword in the specified subquery.
        self._from_index = self._get_from_keyword_index(subquery)

    def _parse_directory_specs(self) -> tuple[Path, int]:
        """Parses the directory path and its metadata specifications."""

        path, index = self._parse_path(self._query[self._from_index + 1 :])

        if not path.is_dir():
            raise QueryParseError("The specified path for lookup must be a directory.")

        return path, index

    def _parse_remove_query(self) -> DeleteQuery:
        """Parses the delete query."""

        if self._from_index:
            raise QueryParseError("Invalid query syntax.")

        path, index = self._parse_directory_specs()

        # Extracts the function for filtering file records.
        condition: Callable[[BaseEntity], bool] = self._get_condition_handler(
            self._query[self._from_index + index + 2 :]
        )

        return DeleteQuery(path, condition)

    def _parse_search_query(self) -> SearchQuery:
        """Parses the search query."""

        fields, columns = self._parse_fields(self._query[: self._from_index])
        path, index = self._parse_directory_specs()

        # Extracts the function for filtering file records.
        condition: Callable[[BaseEntity], bool] = self._get_condition_handler(
            self._query[self._from_index + index + 2 :]
        )

        return SearchQuery(path, condition, fields, columns)

    def parse_query(self) -> SearchQuery | DeleteQuery:
        """
        Parses the search or delete query based upon
        the operation specified during initialization.
        """

        return (
            self._parse_search_query()
            if self._operation == "search"
            else self._parse_remove_query()
        )


class DirectoryQueryParser(FileQueryParser):
    """
    DirectoryQueryParser defines methods for
    parsing directory search and delete queries.
    """

    __slots__ = "_query", "_operation", "_from_index"

    _entity = constants.ENTITY_DIR
    _fields = constants.DIR_FIELDS


class FileDataQueryParser(BaseQueryParser):
    """
    FileDataQueryParser defines methods for parsing file data search queries.
    """

    __slots__ = "_query", "_from_index"

    _entity = constants.ENTITY_DATA
    _fields = constants.DATA_FIELDS

    def __init__(self, subquery: list[str]) -> None:
        self._query = subquery

        # Stores the index of the `FROM` keyword in the specified subquery.
        self._from_index = self._get_from_keyword_index(subquery)

    def _parse_path_specs(self) -> tuple[Path, int]:
        """Parses the file or directory path and its metadata specifications."""

        path, index = self._parse_path(self._query[self._from_index + 1 :])

        if not (path.is_dir() or path.is_file()):
            raise QueryParseError(
                "The specified path for lookup must be a file or directory."
            )

        return path, index

    def parse_query(self) -> SearchQuery:
        """Parses the file data search query."""

        fields, columns = self._parse_fields(self._query[: self._from_index])
        path, index = self._parse_path_specs()

        # Extracts the function for filtering file records.
        condition: Callable[[BaseEntity], bool] = self._get_condition_handler(
            self._query[self._from_index + index + 2 :]
        )

        return SearchQuery(path, condition, fields, columns)
