"""
Core Module
-----------

This module implements the core mechanism for
parsing and handling the user-specified query.
"""

from typing import Callable, Type
from dataclasses import dataclass

import pandas as pd

from common import constants
from shared import QueryQueue
from errors import QueryParseError
from .initials import QueryInitials, QueryInitialsParser
from .conditions import ConditionListNode, ConditionParser, ConditionHandler
from .projections import Projection, ProjectionsParser
from .paths import BaseQueryPath, QueryPathParser

from .exports import (
    BaseExportData,
    ExportParser,
    BaseExportHandler,
    FileExportHandler,
    DBMSExportHandler,
)

from .operators import (
    BaseOperator,
    FileQueryOperator,
    DataQueryOperator,
    DirectoryQueryOperator,
)


@dataclass(slots=True, eq=False, frozen=True)
class SearchQuery:
    """
    SearchQuery class encapsulates the search query specifications.
    """

    export: BaseExportData | None
    initials: QueryInitials
    projections: list[Projection]
    path: BaseQueryPath
    conditions: ConditionListNode | None


@dataclass(slots=True, eq=False, frozen=True)
class DeleteQuery:
    """
    DeleteQuery class encapsulates the delete query specifications.
    """

    initials: QueryInitials
    path: BaseQueryPath
    conditions: ConditionListNode | None


class QueryParser:
    """
    QueryParser class implements mechanism
    for parsing the user-specified query.
    """

    __slots__ = ("_query",)

    def __init__(self, query: QueryQueue) -> None:
        """
        Creates an instance of the QueryParser class.

        #### Params:
        - query (QueryQueue): `QueryQueue` object comprising the query.
        """

        self._query = query

    def _parse_export_specs(self) -> BaseExportData | None:
        """
        Parses and returns the export specifications defined in the query
        or returns None if no export specifications are explicitly defined.
        """

        if self._query.seek().lower() != constants.KEYWORD_EXPORT:
            return None

        parser = ExportParser(self._query)
        return parser.parse()

    def _parse_query_initials(self) -> QueryInitials:
        """Parses the query intials defined in the query."""

        parser = QueryInitialsParser(self._query)
        return parser.parse()

    def _parse_projections(self, entity: str) -> list[Projection]:
        """Parses the search projections defined in the search query."""

        parser = ProjectionsParser(self._query, entity)
        return parser.parse()

    def _parse_path(self, entity: str) -> BaseQueryPath:
        """Parses the path specifications defined in the query."""

        parser = QueryPathParser(self._query, entity)
        return parser.parse()

    def _parse_conditions(self, entity: str) -> ConditionListNode | None:
        """
        Parse and returns the condition specifications defined in
        the query or returns None if the query terminates before.
        """

        if not self._query:
            return None

        parser = ConditionParser(self._query, entity)
        return parser.parse()

    def _parse_search_query(self, export: BaseExportData, initials: QueryInitials):
        """Parses the search query specifications."""

        entity: str = initials.operation.entity
        projections = self._parse_projections(entity)

        # Pops out the `FROM` keyword from the query queue.
        self._query.pop()

        path = self._parse_path(entity)
        conditions = self._parse_conditions(entity)

        return SearchQuery(export, initials, projections, path, conditions)

    def _parse_delete_query(self, initials: QueryInitials):
        """Parses the delete query specifications."""

        entity: str = initials.operation.entity

        # Pops out the `FROM` keyword from the query queue.
        self._query.pop()

        path = self._parse_path(entity)
        conditions = self._parse_conditions(entity)

        return DeleteQuery(initials, path, conditions)

    def parse(self) -> SearchQuery | DeleteQuery:
        """Parses the user-specified query."""

        export = self._parse_export_specs()
        initials = self._parse_query_initials()

        if initials.operation.type_ == constants.OPERATION_SEARCH:
            return self._parse_search_query(export, initials)

        elif export is not None:
            raise QueryParseError(
                "Export operation is not compatible with deletion queries."
            )

        return self._parse_delete_query(initials)


class QueryHandler:
    """
    QueryHandler class implements mechanism for handling
    and evaluating the user-specified query.
    """

    __slots__ = "_query", "_operator_map"

    # Maps export types with their corresponding export handler classes.
    _export_handler_map: dict[str, Type[BaseExportHandler]] = {
        constants.EXPORT_FILE: FileExportHandler,
        constants.EXPORT_DBMS: DBMSExportHandler,
    }

    def __init__(self, query: SearchQuery | DeleteQuery) -> None:
        """
        Creates an instance of the QueryHandler class.

        #### Params:
        - query (SearchQuery | DeleteQuery): Query specifications.
        """

        self._query = query

        # Maps entity names with their corresponding operator extractor methods.
        self._operator_map: dict[str, Callable[[], BaseOperator]] = {
            constants.ENTITY_FILE: self._get_file_operator,
            constants.ENTITY_DIR: self._get_dir_operator,
            constants.ENTITY_DATA: self._get_data_operator,
        }

    def _get_file_operator(self) -> FileQueryOperator:
        """Returns an instance of the FileQueryOperator class."""

        return FileQueryOperator(
            self._query.path,
            self._query.initials.recursive,
        )

    def _get_data_operator(self) -> DataQueryOperator:
        """Returns an instance of the DataQueryOperator class."""

        return DataQueryOperator(
            self._query.path,
            self._query.initials.recursive,
            self._query.initials.operation.mode,
        )

    def _get_dir_operator(self) -> DirectoryQueryOperator:
        """Returns an instance of the DirectoryQueryOperator class."""

        return DirectoryQueryOperator(
            self._query.path,
            self._query.initials.recursive,
        )

    def _export_data(self, data: pd.DataFrame) -> None:
        """
        Exports the specified dataframe to a file or DBMS
        based on the encapsulated export specifications.

        #### Params:
        - data (pd.DataFrame): Dataframe comprising the search records.
        """

        handler_cls = self._export_handler_map[self._query.export.type_]
        handler = handler_cls(self._query.export, data)

        handler.export()

    def _evaluate_search_query(self) -> pd.DataFrame | None:
        """Evaluates the encapsulated query for the search operation."""

        condition = ConditionHandler(self._query.conditions)

        entity: str = self._query.initials.operation.entity
        operator = self._operator_map[entity]()

        data: pd.DataFrame = operator.search(self._query.projections, condition)

        if self._query.export is None:
            return data

        self._export_data(data)

    def _evaluate_delete_query(self) -> None:
        """Evaluatse the encapsulated query for the delete operation."""

        condition = ConditionHandler(self._query.conditions)

        entity: str = self._query.initials.operation.entity
        operator = self._operator_map[entity]()

        return operator.delete(condition, self._query.initials.operation.skip_err)

    def evaluate(self) -> pd.DataFrame | None:
        """Evaluates the encapsulated query."""

        operation: str = self._query.initials.operation.type_

        return (
            self._evaluate_search_query()
            if operation == constants.OPERATION_SEARCH
            else self._evaluate_delete_query()
        )
