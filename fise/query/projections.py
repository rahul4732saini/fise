"""
Projections Module
------------------

This module comprises classes and functions for parsing
projections defined within user-specified search queries.
"""

from typing import Any, Generator

import parsers
from common import constants, tools
from entities import BaseEntity
from errors import QueryParseError
from fields import BaseField
from shared import QueryQueue


class Projection:
    """
    Projection class defines mechanism for storing the name and
    field associated with a projection defined in the query, and
    evaluating the projection for a given entity.
    """

    __slots__ = "_name", "_field"

    def __init__(self, name: str, field: BaseField) -> None:
        """
        Creates an instance of the Projection class.

        #### Params:
        - name (str): Name of the projection.
        - field (BaseField): Field associated with the projection.
        """

        self._name = name
        self._field = field

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"Projection(name={self._name!r})"

    @classmethod
    def from_string(cls, source: str, entity: str) -> "Projection":
        """
        Initializes a Projection from the specified source string
        comprising the query field specifications.

        #### Params:
        - source (str): String comprising the field specifications.
        - entity (str): Name of the entity being operated upon.
        """

        field = parsers.parse_field(source, entity)
        return cls(source, field)

    def evaluate(self, entity: BaseEntity) -> Any:
        """
        Evaluates the field associated with the
        projection based on the specified entity.
        """

        return self._field.evaluate(entity)


class ProjectionsParser:
    """
    ProjectionsParser class defines methods for parsing
    projections defined within the user-specified query
    specifically for the search operation.
    """

    __slots__ = "_query", "_entity"

    def __init__(self, query: QueryQueue, entity: str) -> None:
        """
        Creates an instance of the ProjectionsParser class.

        #### Params:
        - query (QueryQueue): `QueryQueue` object comprising the query.
        - entity (str): Name of the entity being operated upon.
        """

        self._query = query
        self._entity = entity

    def _parse_projections(self, source: str) -> list[Projection]:
        """
        Parses search query projections from the specified source string.

        #### Params:
        - source (str): String comprising the projections.
        """

        projections: list[Projection] = []
        tokens: Generator[str, None, None] = tools.tokenize(source, delimiter=",")

        for token in tokens:
            # Raises a parse error if an empty token is encountered
            # during iteration suggesting inconsistency in the query
            # syntax around the projection specifications.
            if not token:
                raise QueryParseError("Invalid query syntax!")

            elif token == constants.KEYWORD_ASTERISK:
                # Parses all the query fields associated with the
                # entity and extends the projections for the same
                # to the projections list.
                projections.extend(
                    Projection.from_string(field, self._entity)
                    for field in constants.FIELDS[self._entity]
                )
                continue

            projections.append(Projection.from_string(token, self._entity))

        return projections

    def parse(self) -> list[Projection]:
        """Parses the projections defined in the query."""

        tokens: list[str] = []

        # Extracts tokens from the query until the
        # FROM keyword is encountered.
        while self._query.peek().lower() != constants.KEYWORD_FROM:
            tokens.append(self._query.pop())

        return self._parse_projections("".join(tokens))
