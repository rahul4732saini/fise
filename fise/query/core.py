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


@dataclass
class SearchQuery:
    """
    SearchQuery class encapsulates the search query specifications.
    """

    export: BaseExportData | None
    initials: QueryInitials
    projections: list[Projection]
    path: BaseQueryPath
    conditions: ConditionListNode | None


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

        if initials.operation.operation == constants.OPERATION_SEARCH:
            return self._parse_search_query(export, initials)

        elif export is not None:
            raise QueryParseError(
                "Export operation is not compatible with the delete operation."
            )

        return self._parse_delete_query(initials)
