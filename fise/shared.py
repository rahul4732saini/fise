"""
Shared Module
-------------

This modules comprises classes shared across the project
assisting various other classes and functions within its
definition.
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


class FileIterator:
    """
    FileIterator class defines methods for iterating through
    the data lines of a files in the text or bytes filemode.
    """

    __slots__ = "_path", "_filemode"

    def __init__(self, path: Path, filemode: str) -> None:
        """
        Creates an instance of the FileIterator class.

        #### Params:
        - path (Path): Path to the file to be iterated.
        - filemode (str): Filemode for reading the file.
        """

        self._path = path
        self._filemode = filemode

    @property
    def path(self) -> str:
        return self._path.as_posix()

    def _iterate(self) -> Generator[tuple[int, str | bytes], None, None]:
        """
        Iterates through the data lines of
        the file in the specified filemode.
        """

        # line stores the data line read from the file and ctr
        # stores the associated line number during iteration.
        line: str | bytes
        ctr: int = 0

        with self._path.open(self._filemode) as file:

            while line := file.readline():
                ctr += 1
                yield ctr, line

    def __iter__(self) -> Generator[tuple[int, str | bytes], None, None]:
        return self._iterate()
