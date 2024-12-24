"""
Shared Module
-------------

This module comprises data-classes shared across the project
assisting various other classes and functions defined within it.
"""

from dataclasses import dataclass
from typing import Iterable, Optional, Generator
from pathlib import Path

from common import tools


@dataclass(slots=True)
class QueueNode:
    """
    QueueNode class represents individual node in the query queue.
    Each node stores a query token as its value and a reference to
    the next node in the queue.
    """

    val: str
    next: Optional["QueueNode"] = None


class QueryQueue:
    """
    QueryQueue class implements the queue data structure for
    storing individual tokens of the user-specified query.
    """

    __slots__ = "_head", "_tail"

    def __init__(self, iterable: Iterable | None = None) -> None:
        """
        Creates an instance of the QueryQueue class.

        #### Params:
        - itertable (Iterable | None): [OPTIONAL] Iterable for
        initializing the queue. Defaults to None.
        """

        self._head = self._tail = None

        if iterable is not None:
            self._from_iterable(iterable)

    def __bool__(self) -> bool:
        return self._head is not None

    def __repr__(self) -> str:
        return f"QueryQueue(head={self._head.val!r})"

    @classmethod
    def from_string(cls, query: str) -> "QueryQueue":
        """Initializes the queue from the specified query string."""

        query: Generator[str, None, None] = tools.tokenize(query, skip_empty=True)
        return cls(query)

    def _from_iterable(self, iterable: Iterable) -> None:
        """Adds the tokens in the specified iterable to the queue."""

        for val in iterable:
            self.add(val)

    def add(self, token: str) -> None:
        """Adds the specified token at the end of the queue."""

        if self._head is None:
            self._head = self._tail = QueueNode(token)
            return

        self._tail.next = QueueNode(token)
        self._tail = self._tail.next

    def pop(self) -> str:
        """Pops out the token at the start of the queue."""

        if self._head is None:
            raise RuntimeError("Query queue is empty.")

        val: str = self._head.val
        self._head = self._head.next

        if self._head is None:
            self._tail = None

        return val

    def seek(self) -> str:
        """Returns the token at the start of the queue."""
        return self._head.val

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
