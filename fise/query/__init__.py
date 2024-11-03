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
from errors import QueryParseError, OperationError

__all__ = ("QueryHandler",)


class QueryHandler:
    """
    QueryHandler defines methods for parsing and
    processing user-specified search and delete queries.
    """

    __slots__ = "_query", "_ctr", "_handler_map"

    # Regular expression patterns for parsing sub-queries.
    _export_subquery_pattern = re.compile(r"^(sql|file)\[.*]$")
    _operation_params_pattern = re.compile(r"^(\[.*])?$")

    def __init__(self, query: str) -> None:
        """
        Creates an instance of the `QueryHandler` class.

        #### Params:
        - query (str): Query to be handled.
        """

        # Maps targeted operands names with corresponding methods for handling the query.
        self._handler_map: dict[str, Callable[[QueryInitials], pd.DataFrame | None]] = {
            "file": self._handle_file_query,
            "dir": self._handle_dir_query,
            "data": self._handle_data_query,
        }

        # Keeps track of the current position of the token to be parsed in the query.
        self._ctr = 0

        self._query = tools.parse_query(query)

    def handle(self) -> pd.DataFrame | None:
        """
        Handles the specified search/delete query.
        """

        self._ctr = 0

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
        """Parses and handles the specified file search or delete query"""

        parser = FileQueryParser(self._query[self._ctr :], initials.operation.operation)
        query: SearchQuery | DeleteQuery = parser.parse_query()

        operator = FileQueryOperator(query.path, initials.recursive)

        if initials.operation.operation == "search":
            return operator.search(query.fields, query.columns, query.condition)

        operator.delete(query.condition, initials.operation.skip_err)

    def _handle_data_query(self, initials: QueryInitials) -> pd.DataFrame:
        """Parses and handles the specified data search query"""

        if (
            initials.export
            and initials.operation.filemode == "bytes"
            and initials.export.type_ == "database"
        ):
            raise QueryParseError(
                "Exporting binary data to SQL databases is currently unsupported"
            )

        parser = FileDataQueryParser(self._query[self._ctr :])
        query: SearchQuery = parser.parse_query()

        operator = FileDataQueryOperator(
            query.path, initials.recursive, initials.operation.filemode
        )

        return operator.search(query.fields, query.columns, query.condition)

    def _handle_dir_query(self, initials: QueryInitials) -> pd.DataFrame | None:
        """
        Parses and handles the specified directory search/delete query.
        """

        parser = DirectoryQueryParser(
            self._query[self._ctr :], initials.operation.operation
        )

        query: SearchQuery | DeleteQuery = parser.parse_query()
        operator = DirectoryQueryOperator(query.path, initials.recursive)

        if initials.operation.operation == "search":
            return operator.search(query.fields, query.columns, query.condition)

        operator.delete(query.condition, initials.operation.skip_err)

    def _parse_initials(self) -> QueryInitials:
        """
        Parses the query initials.
        """

        recursive: bool = False
        export: ExportData | None = self._parse_export_data()

        if self._query[self._ctr].lower() in ("r", "recursive"):
            recursive = True
            self._ctr += 1

        # Parses the query operation
        operation: OperationData = self._parse_operation()
        self._ctr += 1

        if export and operation.operation == "remove":
            raise QueryParseError("Cannot export data with delete operation.")

        return QueryInitials(operation, recursive, export)

    @staticmethod
    def _parse_operation_type(type_: str) -> str:
        """
        Parses the query operation type.
        """
        if type_ not in constants.SEARCH_QUERY_OPERANDS:
            raise QueryParseError(f"Invalid value {type_!r} for 'type' parameter.")

        return type_

    def _parse_search_operation(
        self, params: Generator[list[str], None, None]
    ) -> OperationData:
        """
        Parses the search operation parameters.
        """

        operand: str = "file"
        filemode: str | None = None

        # Iterates through the parameters and parses them.
        for param in params:
            if len(param) != 2:
                raise QueryParseError(
                    f"Invalid query syntax around {self._query[self._ctr]!r}"
                )

            # Splits the key-value pair in the list into variables for better readability.
            key, value = param

            if key == "type":
                operand = self._parse_operation_type(value)

            elif key == "mode":
                if value not in constants.FILE_MODES_MAP:
                    raise QueryParseError(
                        f"Invalid value {value!r} for 'mode' parameter."
                    )

                filemode = value

            else:
                raise QueryParseError(
                    f"Invalid parameter {key!r} for search operation."
                )

        if operand != "data" and filemode:
            raise QueryParseError(
                "The 'mode' parameter is only valid for filedata search operations."
            )

        elif operand == "data" and not filemode:
            filemode = "text"

        return OperationData("search", operand, filemode)

    def _parse_delete_operation(
        self, params: Generator[list[str], None, None]
    ) -> OperationData:
        """
        Parses the delete operation parameters.
        """

        operand: str = "file"
        skip_err: bool = False

        # Iterates through the parameters and parses them.
        for param in params:

            if param[0] == "type":
                operand = self._parse_operation_type(param[1])

            elif param[0] == "skip_err":
                if len(param) != 1:
                    raise QueryParseError(
                        f"Invalid query syntax around {self._query[self._ctr]!r}"
                    )

                skip_err = True
            else:
                raise QueryParseError(
                    f"Invalid parameter {param[0]!r} for delete operation."
                )

        if operand == "data":
            raise QueryParseError(
                "Delete operation upon file contents is not supported."
            )

        return OperationData("remove", operand, skip_err=skip_err)

    def _parse_operation(self) -> OperationData:
        """
        Parses the query operation specifications.
        """

        # Extracts and stores the operation and its parameter specifications.
        operation, oparams = (
            self._query[self._ctr][:6].lower(),
            self._query[self._ctr][6:].lower(),
        )

        if operation not in constants.OPERATION_ALIASES:
            raise QueryParseError(
                f"Invalid operation {operation!r} specified in the query"
            )

        # Verifying operation parameters syntax.
        if not self._operation_params_pattern.match(oparams):
            raise QueryParseError(
                f"Invalid query syntax around {self._query[self._ctr]!r}."
            )

        # Splits the parameters subquery about commas, and iterates
        # through it striping whitespaces from individual parameters.
        params: Generator[list[str], None, None] = (
            i.strip().split(" ") for i in oparams[1:-1].split(",") if i
        )

        try:
            data: OperationData = (
                self._parse_search_operation(params)
                if operation == "select"
                else self._parse_delete_operation(params)
            )

        except IndexError:
            raise QueryParseError(
                f"Invalid query syntax around {self._query[self._ctr]!r}"
            )

        else:
            return data

    @staticmethod
    def _parse_file_export_specs(export_specs: str) -> ExportData:
        """
        Parses and returns the file export specifications.
        """

        file: Path = Path(export_specs[5:-1])

        if file.suffix not in constants.DATA_EXPORT_TYPES_MAP:
            raise QueryParseError(
                f"{file.suffix!r} file type is not supported for exporting search records."
            )

        if file.is_file():
            raise OperationError(
                "The specified path for exporting search "
                "records must not point to an existing file."
            )

        elif not file.parent.exists():
            raise OperationError(
                f"The specified directory '{file.parent}' "
                "for exporting search records cannot be found."
            )

        return ExportData("file", file)

    @staticmethod
    def _parse_sql_export_specs(export_specs: str) -> ExportData:
        """
        Parses and returns the SQL export specifications.
        """

        database: str = export_specs[4:-1]

        if database not in constants.DATABASES:
            raise QueryParseError(
                f"Invalid database {database!r} specified for exporting search records."
            )

        return ExportData("database", database)

    def _parse_export_data(self) -> ExportData | None:
        """
        Parses export specifications from the query if specified else returns `None`.
        """

        # The method doesn't make much use of the `ctr` attribute
        # as it only parses the very initial tokens of the query.

        if self._query[0].lower() != "export":
            return None

        # Increments the counter by 2, as the initial two tokens are to be
        # parsed here and won't be required by the other parser methods.
        self._ctr += 2
        low_target: str = self._query[1].lower()

        if not self._export_subquery_pattern.match(low_target):
            raise QueryParseError(
                "Unable to parse the export specifications in the query."
            )

        if low_target.startswith("file"):
            return self._parse_file_export_specs(self._query[1])

        # Character case of the specifications is ensured to be lowered for proper parsing.
        return self._parse_sql_export_specs(low_target)
