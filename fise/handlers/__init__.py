r"""
Handlers Package
----------------

This package provides a collection of objects and methods designed for
parsing and processing user-specified search and manipulation queries.
"""

import re
from pathlib import Path
from typing import Callable

import pandas as pd

from ..errors import QueryParseError
from ..common import constants, tools
from ..shared import QueryInitials, ExportData
from .operators import (
    FileQueryOperator,
    FileDataQueryOperator,
    DirectoryQueryOperator,
)
from .parsers import (
    FileQueryParser,
    DirectoryQueryParser,
    FileDataQueryParser,
    FileSearchQuery,
    DeleteQuery,
    SearchQuery,
)


class QueryHandler:
    r"""
    QueryHandler defines methods for handling, parsing and
    processing user-specified search and manipulation queries.
    """

    __slots__ = ("_query",)

    _export_subquery_pattern = re.compile(rf"^sql(\[({"|".join(constants.DATABASES)})\]|)$")

    _search_subquery_pattern = re.compile(rf"^select(\[({"|".join(constants.SEARCH_QUERY_OPERANDS)})\])")
    _delete_subquery_pattern = re.compile(rf"^delete(\[({"|".join(constants.DELETE_QUERY_OPERANDS)})\])")

    def __init__(self, query: list[str]) -> None:
        r"""
        Creates an instance of the `QueryHandler` class.
        """
        self._query = query

    def _handle_file_query(self, initials: QueryInitials) -> pd.DataFrame | None:
        r"""
        Parses and processes the specified file search/deletion query.
        """

        parser = FileQueryParser(self._query, initials.operation)
        query: FileSearchQuery | DeleteQuery = parser.parse_query()

        operator = FileQueryOperator(
            query.path, initials.recursive, query.path_type, query.size_unit
        )

        if initials.operation == "search":
            return operator.get_fields(query.fields, query.condition)
        
        operator.remove_files(query.condition)

    def _handle_dir_query(self, initials: QueryInitials) -> pd.DataFrame | None:
        r"""
        Parses and processes the specified directory search/deletion query.
        """

        parser = DirectoryQueryParser(self._query, initials.operation)
        query: SearchQuery | DeleteQuery = parser.parse_query()

        operator = DirectoryQueryOperator(
            query.path, initials.recursive, query.path_type, query.size_unit
        )

        if initials.operation == "search":
            return operator.get_fields(query.fields, query.condition)
        
        operator.remove_directories(query.condition) 

    def _parse_initials(self) -> QueryInitials:
        r"""
        Parses the query initials.
        """

        recursive: bool = False
        export: ExportData | None = self._parse_export_data(self._query)

        if export:
            self._query = self._query[2:]

        if self._query[0].lower() in ("r", "recursive"):
            recursive = True
            self._query = self._query[1:]

        if not (
            self._search_subquery_pattern.match(self._query[0].lower())
            or self._delete_subquery_pattern.match(self._query[0].lower())
        ):
            QueryParseError(
                "Unable to parse query operation."
            )

        operation: str = constants.OPERATION_ALIASES[self._query[0][:6].lower()]
        operand: str = self._query[0][7:-1] or "file"

        if operation == "remove" and export:
            QueryParseError(
                "Cannot export data with delete operation."
            )

        return QueryInitials(operation, operand, recursive, export)

    def _parse_export_data(self, query: list[str]) -> ExportData | None:
        r"""
        Parses export data from the query if specified else returns `None`.
        """

        if query[0].lower() != "export":
            return
        
        if query[1].lower().startswith("sql"):
            if not self._export_subquery_pattern.match(query[1].lower()):
                QueryParseError(
                    "Unable to parse SQL database name."
                )

            return ExportData("database", query[1][4:-1])
        
        else:
            path: Path = Path(query[1])

            if path.is_file():
                QueryParseError(
                    "The path specified for exporting search records must not be an existing file."
                )

            return ExportData("file", path)
