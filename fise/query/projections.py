"""
Projections Module
------------------

This module comprises classes and functions for parsing
projections defined within user-specified search queries.
"""

from typing import Generator, Any

import parsers
from fields import BaseField
from entities import BaseEntity
from common import tools, constants
from shared import QueryQueue
from errors import QueryParseError


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

    def _parse_projection(self, source: str) -> Projection:
        """
        Parses the specified source string specifications
        for a search query projection.

        #### Params:
        - source (str): String comprising the projection specifications.
        """

        field = parsers.parse_field(source, self._entity)
        return Projection(source, field)

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
                    self._parse_projection(field)
                    for field in constants.FIELDS[self._entity]
                )
                continue

            projections.append(self._parse_projection(token))

        return projections

    def parse(self) -> list[Projection]:
        """Parses the projections defined in the query."""

        tokens: list[str] = []

        # Extracts tokens from the query until
        # the `FROM` keyword is encountered.
        while self._query.seek().lower() != constants.KEYWORD_FROM:
            tokens.append(self._query.pop())

        return self._parse_projections("".join(tokens))
