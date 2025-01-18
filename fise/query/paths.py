"""
Paths Module
------------

This modules defines classes and functions for storing, parsing and
handling file/directory paths defined within user-specified queries.
"""

from typing import Type, Generator
from pathlib import Path
from abc import ABC, abstractmethod

from common import tools, constants
from shared import QueryQueue
from errors import QueryParseError


class BaseQueryPath(ABC):
    """BaseQueryPath serves as the base class for all query path classes."""

    __slots__ = ("_path",)

    def __init__(self, path: Path) -> None:

        self._validate_path(path)
        self._path: Path = path

    @property
    def path(self) -> Path:
        return self._path

    @abstractmethod
    def _validate_path(self, path: Path) -> None: ...

    @abstractmethod
    def enumerate(self, recursive: bool) -> Generator[Path, None, None]: ...


class FileQueryPath(BaseQueryPath):
    """
    FileQueryPath class defines mechanism for storing the directory path
    specified within the query, and enumerating over files within the same.
    """

    __slots__ = ("_path",)

    def __repr__(self) -> str:
        return f"FileQueryPath(path={self._path.as_posix()!r})"

    def _validate_path(self, path: Path) -> None:
        """Validates the specified path for a file query."""

        if not path.is_dir():
            raise QueryParseError(
                f"The specified path {path.as_posix()!r}"
                " does not lead to a directory."
            )

    def enumerate(self, recursive: bool) -> Generator[Path, None, None]:
        """
        Enumerates over the files within the specified directory. Files within
        sub-directories are also include if `recursive` is set to True.

        #### Params:
        - recursive (bool): Whether to include files from sub-directories.
        """

        yield from tools.enumerate_files(self._path, recursive)


class DirectoryQueryPath(BaseQueryPath):
    """
    DirectoryQueryPath class defines mechanism for storing the directory
    path specified within the query and enumerating over sub-directories
    within the same.
    """

    __slots__ = ("_path",)

    def __repr__(self) -> str:
        return f"DirectoryQueryPath(path={self._path.as_posix()!r})"

    def _validate_path(self, path: Path) -> None:
        """Validates the specified path for a directory query."""

        if not path.is_dir():
            raise QueryParseError(
                f"The specified path {path.as_posix()!r}"
                " does not lead to a directory."
            )

    def enumerate(self, recursive: bool) -> Generator[Path, None, None]:
        """
        Enumerates over the sub-directories within the specified directory.
        Directories within sub-directories are also included if `recursive`
        is set to true.

        #### Params:
        - recursive (bool): Whether to include directories from sub-directories.
        """

        yield from tools.enumerate_directories(self._path, recursive)


class DataQueryPath(BaseQueryPath):
    """
    DataQueryPath class defines mechanism for storing the file or
    directory path specified within the query and enumerating over
    the targeted file(s).
    """

    __slots__ = ("_path",)

    def __repr__(self) -> str:
        return f"DataQueryPath(path={self._path.as_posix()!r})"

    def _validate_path(self, path: Path) -> None:
        """Validates the specified path for a data query."""

        if not (path.is_file() or path.is_dir()):
            raise QueryParseError(
                f"The specified path {path.as_posix()!r}"
                " does not lead to a file or directory."
            )

    def enumerate(self, recursive: bool = False) -> Generator[Path, None, None]:
        """
        Enumerates over the files within the specified directory
        or yields the specified file if the path leads to the same.

        #### Params:
        - recursive (bool): Whether to include files from sub-directories.
        Only applicable if the specified path leads to a directory.
        """

        if self._path.is_file():
            yield self._path

        yield from tools.enumerate_files(self._path, recursive)


class QueryPathParser:
    """
    QueryPathParser class defines methods for parsing
    path specifications from the user-specified query.
    """

    __slots__ = "_query", "_entity"

    # Maps entity names with their corresponding query path classes.
    _path_classes: dict[str, Type[BaseQueryPath]] = {
        constants.ENTITY_FILE: FileQueryPath,
        constants.ENTITY_DATA: DataQueryPath,
        constants.ENTITY_DIR: DirectoryQueryPath,
    }

    def __init__(self, query: QueryQueue, entity: str) -> None:
        """
        Creates an instance of the QueryPathParser class.

        #### Params:
        - query (QueryQueue): `QueryQueue` object comprising the query.
        - entity (str): Name of the entity being operated upon.
        """

        self._query = query
        self._entity = entity

    def _parse_specifications(self) -> Path:
        """Parses the path specifications defined within the query."""

        is_absolute: bool = False

        if self._query.peek().lower() in constants.PATH_TYPES:
            is_absolute = self._query.pop().lower() == constants.PATH_ABSOLUTE

        raw_path: str = self._query.pop()

        # Strips off the leading and trailing quotes from
        # the path specifications if explicitly specified.
        if constants.STRING_PATTERN.match(raw_path):
            raw_path = raw_path[1:-1]

        path = Path(raw_path)

        if is_absolute:
            path = path.resolve()

        return path

    def parse(self) -> BaseQueryPath:
        """
        Parses the path specifications, validates the path
        and returns a query path object for further usage.
        """

        path = self._parse_specifications()
        return self._path_classes[self._entity](path)
