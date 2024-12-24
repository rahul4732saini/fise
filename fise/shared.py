"""
Shared Module
-------------

This module comprises data-classes shared across the project
assisting various other classes and functions defined within it.
"""

from dataclasses import dataclass
from typing import Iterable, Optional, Generator
from pathlib import Path

from common import constants
from entities import BaseEntity
from fields import BaseField


@dataclass(slots=True)
class QueueNode:
    """
    QueueNode class represents individual node in the query queue.
    Each node stores a query token as its value and a reference to
    the next node in the queue.
    """

    val: str
    next: Optional["QueueNode"] = None


@dataclass(slots=True, frozen=True, eq=False)
class SearchQuery(Query):
    """SearchQuery class stores search query attributes."""

    fields: list[BaseField]
    columns: list[str]


class DeleteQuery(Query):
    """DeleteQuery class stores delete query attributes."""


@dataclass(slots=True, frozen=True, eq=False)
class ExportData:
    """ExportData class stores export data attributes."""

    type_: Literal["file", "database"]
    target: str | Path


@dataclass(slots=True, frozen=True, eq=False)
class OperationData:
    """OperationData class stores query operation attributes."""

    operation: constants.OPERATIONS
    operand: constants.OPERANDS

    # The following attributes are optional and are only used for specific
    # operations. The `filemode` attribute is only used with data search
    # operations and the `skip_err` attributes is only used in delete operations.
    filemode: constants.FILE_MODES | None = None
    skip_err: bool = False


@dataclass(slots=True, frozen=True, eq=False)
class QueryInitials:
    """QueryInitials class stores attributes related to query initials."""

    operation: OperationData
    recursive: bool
    export: ExportData | None = None


@dataclass(slots=True, frozen=True, eq=False)
class Condition:
    """Condition class stores individual query condition attributes."""

    operand1: Any
    operator: str
    operand2: Any
