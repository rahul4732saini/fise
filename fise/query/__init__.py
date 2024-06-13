"""
Query Package
-------------

This package provides a collection of classes and functions
designed for handling user-specified search and delete queries.
"""

import re
from pathlib import Path
from typing import Callable, Generator

import pandas as pd

from common import constants, tools
from .parsers import FileQueryParser, DirectoryQueryParser, FileDataQueryParser
from .operators import FileQueryOperator, FileDataQueryOperator, DirectoryQueryOperator
from shared import QueryInitials, ExportData, OperationData, DeleteQuery, SearchQuery
from errors import QueryParseError

__all__ = ("QueryHandler",)


class QueryHandler:
    """
    QueryHandler defines methods for parsing and
    processing user-specified search and delete queries.
    """

    __slots__ = "_query", "_current_query", "_handler_map"

    # Regular expression patterns for parsing sub-queries.
    _export_subquery_pattern = re.compile(r"^(sql|file)\[.*]$")
    _operation_params_pattern = re.compile(r"^(\[.*])?$")

    def __init__(self, query: str) -> None:
        """
        Creates an instance of the `QueryHandler` class.

        #### Params:
        - query (str): Query to be handled.
        """

        # Maps targeted operands names with coressponding methods for handling the query.
        self._handler_map: dict[str, Callable[[QueryInitials], pd.DataFrame | None]] = {
            "file": self._handle_file_query,
            "dir": self._handle_dir_query,
            "data": self._handle_data_query,
        }

        # Keeps another copy of the query to avoid changes in it during every runtime.
        self._query = self._current_query = tools.parse_query(query)

    def handle(self) -> pd.DataFrame | None:
        """
        Handles the specified search/delete query.
        """

        # Updates current query with the specified query.
        self._current_query = self._query

        try:
            initials: QueryInitials = self._parse_initials()

        except IndexError:
            raise QueryParseError("Invalid query syntax.")

        # Calls the corresponding handler method, extracts, and stores the
        # search records if search operation is specified else stores `None`.
        data: pd.DataFrame | None = self._handler_map[initials.operation.operand](
            initials
        )

        if not initials.export:
            return data

        if initials.export.type_ == "file":
            tools.export_to_file(data, initials.export.target)

        else:
            tools.export_to_sql(data, initials.export.target)

    def _handle_file_query(self, initials: QueryInitials) -> pd.DataFrame | None:
        """
        Parses and handles the specified file search/delete query.
        """

        parser = FileQueryParser(self._current_query, initials.operation.operation)
        query: SearchQuery | DeleteQuery = parser.parse_query()

        operator = FileQueryOperator(query.path, initials.recursive, query.is_absolute)

        if initials.operation.operation == "search":
            return operator.get_dataframe(query.fields, query.columns, query.condition)

        operator.remove_files(query.condition, initials.operation.skip_err)

    def _handle_data_query(self, initials: QueryInitials) -> pd.DataFrame:
        """
        Parses and handles the specified data search query.
        """

        parser = FileDataQueryParser(self._current_query)
        query: SearchQuery = parser.parse_query()

        operator = FileDataQueryOperator(
            query.path,
            initials.recursive,
            query.is_absolute,
            initials.operation.filemode,
        )

        return operator.get_dataframe(query.fields, query.columns, query.condition)

    def _handle_dir_query(self, initials: QueryInitials) -> pd.DataFrame | None:
        """
        Parses and handles the specified directory search/delete query.
        """

        parser = DirectoryQueryParser(self._current_query, initials.operation.operation)
        query: SearchQuery | DeleteQuery = parser.parse_query()

        operator = DirectoryQueryOperator(
            query.path, initials.recursive, query.is_absolute
        )

        if initials.operation.operation == "search":
            return operator.get_dataframe(query.fields, query.columns, query.condition)

        operator.remove_directories(query.condition, initials.operation.skip_err)

    def _parse_initials(self) -> QueryInitials:
        """
        Parses the query initials.
        """

        recursive: bool = False
        export: ExportData | None = self._parse_export_data()

        if self._current_query[0].lower() in ("r", "recursive"):
            recursive = True
            self._current_query.pop(0)

        # Parses the query operation
        operation: OperationData = self._parse_operation()
        self._current_query.pop(0)

        if export:
            if operation.operation == "remove":
                raise QueryParseError("Cannot export data with delete operation.")

            elif operation.filemode == "bytes" and export.type_ == "database":
                raise QueryParseError(
                    "Exporting binary data to SQL databases is currently unsupported."
                )

        return QueryInitials(operation, recursive, export)

    @staticmethod
    def _parse_operation_type(type_: str) -> str:
        """
        Parses the query operation type.
        """
        if type_ not in constants.SEARCH_QUERY_OPERANDS:
            raise QueryParseError(f"Invalid value {type_!r} for 'type' parameter.")

        return type_

    def _parse_search_operation(self) -> OperationData:
        """
        Parses the search operation subquery.
        """

        operand: str = "file"
        filemode: str | None = None

        # Verifying operation parameters syntax.
        if not self._operation_params_pattern.match(self._current_query[0][6:]):
            raise QueryParseError(
                f"Invalid query syntax around {self._current_query[0]!r}."
            )

        # Generator of operation parameters.
        params: Generator[str, None, None] = (
            # Splits the parameters subquery about commas, and iterates
            # through it striping whitespaces from individual parameters.
            i.strip()
            for i in self._current_query[0][7:-1].split(",")
            if i
        )

        # Iterates through the parameters and parses them.
        for param in params:
            param = param.split(" ")

            if len(param) != 2:
                raise QueryParseError(
                    f"Invalid query syntax around {self._current_query[0]!r}"
                )

            if param[0] == "type":
                operand = self._parse_operation_type(param[1])

            elif param[0] == "mode":
                if param[1] not in constants.FILE_MODES_MAP:
                    raise QueryParseError(
                        f"Invalid value {param[1]!r} for 'mode' parameter."
                    )

                filemode = param[1]

            else:
                raise QueryParseError(
                    f"Invalid parameter {param[0]!r} for search operation."
                )

        if operand != "data" and filemode:
            raise QueryParseError(
                "The 'mode' parameter is only valid for filedata search operations."
            )

        elif operand == "data" and not filemode:
            filemode = "text"

        return OperationData("search", operand, filemode)

    def _parse_delete_operation(self) -> OperationData:
        """
        Parses the delete operation subquery.
        """

        operand: str = "file"
        skip_err: bool = False

        # Verifying operation parameters syntax.
        if not self._operation_params_pattern.match(self._current_query[0][6:]):
            raise QueryParseError(
                f"Invalid query syntax around {self._current_query[0]!r}."
            )

        # Generator of operation parameters.
        params: Generator[str, None, None] = (
            # Splits the parameters subquery about commas, and iterates
            # through it striping whitespaces from individual parameters.
            i.strip()
            for i in self._current_query[0][7:-1].split(",")
            if i
        )

        # Iterates through the parameters and parses them.
        for param in params:
            param = param.split(" ")

            if param[0] == "type":
                operand = self._parse_operation_type(param[1])

            elif param[0] == "skip_err":
                if len(param) > 1:
                    raise QueryParseError(
                        f"Invalid query syntax around {self._current_query[0]!r}"
                    )

                skip_err = True
            else:
                raise QueryParseError(
                    f"Invalid parameter {param[0]!r} for search operation."
                )

        return OperationData("remove", operand, skip_err=skip_err)

    def _parse_operation(self) -> OperationData:
        """
        Parses the query operation data.
        """

        self._current_query[0] = self._current_query[0].lower()

        # Only extracts the query operation, operators parameters are
        # parsed explicitly by the specific operation parser method.
        operation: str = self._current_query[0][:6]

        if operation not in constants.OPERATION_ALIASES:
            raise QueryParseError(f"Invalid operation specified: {operation!r}")

        try:
            data: OperationData = (
                self._parse_search_operation()
                if operation == "select"
                else self._parse_delete_operation()
            )

        except IndexError:
            raise QueryParseError(
                f"Invalid query syntax around {self._current_query[0]!r}"
            )

        else:
            return data

    def _parse_export_data(self) -> ExportData | None:
        """
        Parses export specifications from the query if specified else returns `None`.
        """

        if self._current_query[0].lower() != "export":
            return None

        target: str = self._current_query[1]
        self._current_query = self._current_query[2:]

        if not self._export_subquery_pattern.match(target.lower()):
            raise QueryParseError(
                "Unable to parse the export specifications in the query."
            )

        if target.lower().startswith("file"):
            return ExportData("file", Path(target[5:-1]))

        database: str = target.lower()[4:-1]

        if database not in constants.DATABASES:
            raise QueryParseError(
                f"Invalid database {database!r} specified for exporting search records."
            )

        return ExportData("database", database)
