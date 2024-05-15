"""
Handlers Package
----------------

This package provides a collection of objects and methods designed for
parsing and processing user-specified search and manipulation queries.
"""

import re
from pathlib import Path
from typing import Callable, Generator

import pandas as pd

from ..shared import QueryInitials, ExportData, OperationData
from ..common import constants, tools
from ..errors import QueryParseError
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
    """
    QueryHandler defines methods for handling, parsing and
    processing user-specified search and manipulation queries.
    """

    __slots__ = ("_query",)

    # Regular expression patterns for parsing subqueries.
    _export_subquery_pattern = re.compile(rf"^sql(\[({"|".join(constants.DATABASES)})\]|)$")
    _operation_params_pattern = re.compile(r"^\[.*\]$")

    def __init__(self, query: str) -> None:
        """
        Creates an instance of the `QueryHandler` class.

        #### Params:
        - query (str): Query to be parsed and processed.
        """
        self._query = tools.parse_query(query)

    def handle(self) -> pd.DataFrame:
        """
        Parses and processes the specified search/deletion query.
        """

        try:
            initials: QueryInitials = self._parse_initials()

        except IndexError:
            QueryParseError("Invalid query syntax.")

        handler_map: dict[str, Callable[[QueryInitials], pd.DataFrame | None]] = {
            "file": self._handle_file_query,
            "dir": self._handle_dir_query,
            "data": self._handle_data_query,
        }

        # Calls the coressponding handler method, extracts, and stores the
        # search records if search operation is specified else stores `None`.
        data: pd.DataFrame | None = handler_map[initials.operation.operand](initials)

        if not initials.export or initials.operation == "remove":
            return data
      
        if initials.export.type_ == "file":
            tools.export_to_file(data, initials.export.target)

        else:
            tools.export_to_sql(data, initials.export.target)

    def _handle_file_query(self, initials: QueryInitials) -> pd.DataFrame | None:
        """
        Parses and processes the specified file search/deletion query.
        """

        parser = FileQueryParser(self._query, initials.operation.operation)
        query: FileSearchQuery | DeleteQuery = parser.parse_query()

        operator = FileQueryOperator(
            query.path, initials.recursive, query.is_absolute
        )

        if initials.operation.operation == "search":
            return operator.get_fields(query.fields, query.condition, query.size_unit)

        operator.remove_files(query.condition, initials.operation.skip_err)

    def _handle_data_query(self, initials: QueryInitials) -> pd.DataFrame:
        """
        Parses and processes the specified file data search query.
        """

        parser = FileDataQueryParser(self._query)
        query: SearchQuery = parser.parse_query()

        operator = FileDataQueryOperator(
            query.path,
            initials.recursive,
            query.is_absolute,
            initials.operation.filemode,
        )

        return operator.get_fields(query.fields, query.condition)

    def _handle_dir_query(self, initials: QueryInitials) -> pd.DataFrame | None:
        """
        Parses and processes the specified directory search/deletion query.
        """

        parser = DirectoryQueryParser(self._query, initials.operation.operation)
        query: SearchQuery | DeleteQuery = parser.parse_query()

        operator = DirectoryQueryOperator(
            query.path, initials.recursive, query.is_absolute
        )

        if initials.operation.operation == "search":
            return operator.get_fields(query.fields, query.condition)

        operator.remove_directories(query.condition, initials.operation.skip_err)

    def _parse_initials(self) -> QueryInitials:
        """
        Parses the query initials.
        """

        recursive: bool = False
        export: ExportData | None = self._parse_export_data(self._query)

        if export:
            self._query = self._query[2:]

        if self._query[0].lower() in ("r", "recursive"):
            recursive = True
            self._query = self._query[1:]

        operation: OperationData = self._parse_operation()
        self._query = self._query[1:]

        if operation == "remove" and export:
            QueryParseError(
                "Cannot export data with delete operation."
            )

        return QueryInitials(operation, recursive, export)

    def _parse_search_operation(self):
        """
        Parses the search operation subquery.
        """

        operand: str = "file"
        filemode: str | None = None

        # Verifying operation parameters syntax.
        if not self._operation_params_pattern.match(self._query[0][6:]):
            QueryParseError(f"Invalid query syntax around {self._query[0]!r}.")

        # Generator of operation parameters.
        params: Generator[str, None, None] = (
            # Lowers and splits the parameters subquery about commas, and iterates
            # through it striping whitespaces from individual parameters.
            i.strip() for i in self._query[0][7:-1].lower().split(",")
        )

        # Iterates through the parameters and parses them.
        for param in params:
            param = param.split(" ")

            if len(param) != 2:
                QueryParseError(f"Invalid query syntax around {self._query[0]!r}")

            if param[0] == "type":
                if param[1] not in constants.SEARCH_QUERY_OPERANDS:
                    QueryParseError(
                        f"Invalid value {param[1]!r} for 'type' parameter."
                    )

                operand = param[1]

            elif param[0] == "mode":
                if param[1] not in constants.FILE_MODES_MAP:
                    QueryParseError(
                        f"Invalid value {param[1]!r} for 'mode' parameter."
                    )

                filemode = param[1]

            else:
                QueryParseError(f"Invalid parameter {param[0]!r} for search operation.")

        if filemode and operand != "data":
            QueryParseError(
                "The 'mode' parameter is only valid for filedata search operations."
            )

        return OperationData("search", operand, filemode)
    
    def _parse_delete_operation(self):
        """
        Parses the delete operation subquery.
        """

        operand: str = "file"
        skip_err: bool = False

        # Verifying operation parameters syntax.
        if not self._operation_params_pattern.match(self._query[0][6:]):
            QueryParseError(f"Invalid query syntax around {self._query[0]!r}.")

        # Generator of operation parameters.
        params: Generator[str, None, None] = (
            # Lowers and splits the parameters subquery about commas, and iterates
            # through it striping whitespaces from individual parameters.
            i.strip() for i in self._query[0][7:-1].lower().split(",")
        )

        # Iterates through the parameters and parses them.
        for param in params:
            param = param.split(" ")

            if len(param) != 2:
                QueryParseError(f"Invalid query syntax around {self._query[0]!r}")

            if param[0] == "type":
                if param[1] not in constants.DELETE_QUERY_OPERANDS:
                    QueryParseError(
                        f"Invalid value {param[1]!r} for 'type' parameter."
                    )

                operand = param[1]

            elif param[0] == "skip_err":
                skip_err = True
            else:
                QueryParseError(f"Invalid parameter {param[0]!r} for search operation.")

        return OperationData("remove", operand, skip_err=skip_err)

    def _parse_operation(self) -> OperationData:
        """
        Parses the query operation data.
        """

        parser_map: dict[str, Callable[[], OperationData]] = {
            "select": self._parse_search_operation, "delete": self._parse_delete_operation
        }

        operation: str = self._query[0][:6].lower()
        data: OperationData | None = parser_map.get(operation)()

        if data is None:
            QueryParseError(f"Invalid operation specified: '{operation}'")

        return data

    def _parse_export_data(self, query: list[str]) -> ExportData | None:
        """
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
