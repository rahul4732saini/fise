"""
Projections Module
------------------

This module comprises classes and functions for parsing
projections defined within user-specified search queries.
"""

from typing import Any

from fields import BaseField
from entities import BaseEntity


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
