"""
Initials Module
---------------

This module defines classes and functions for parsing
the initial clauses of the user-specified query.
"""

from abc import ABC, abstractmethod
from typing import Callable, ClassVar, Any
from dataclasses import dataclass

from common import constants
from errors import QueryParseError


@dataclass(slots=True, frozen=True, eq=False)
class BaseOperationData:
    """
    BaseOperationData serves as the base
    class for all operation data classes.
    """

    entity: ClassVar[str]
    operation: str


@dataclass(slots=True, frozen=True, eq=False)
class FileSystemOperationData(BaseOperationData):
    """
    FileSystemOperationData serves as the base class
    for all file system operation data classes.
    """

    skip_err: bool = False


@dataclass(slots=True, frozen=True, eq=False)
class FileOperationData(FileSystemOperationData):
    """
    FileOperationData class encapsulates
    the file operation data specifications.
    """

    entity = constants.ENTITY_FILE


@dataclass(slots=True, frozen=True, eq=False)
class DirectoryOperationData(FileSystemOperationData):
    """
    DirectoryOperationData class encapsulates
    the directory operation data specifications.
    """

    entity = constants.ENTITY_DIR


@dataclass(slots=True, frozen=True, eq=False)
class DataOperationData(BaseOperationData):
    """
    DataOperationData class encapsulates
    the data operation data specifications.
    """

    entity = constants.ENTITY_DATA
    mode: str = constants.READ_MODE_TEXT


@dataclass(slots=True, frozen=True, eq=False)
class QueryInitials:
    """
    QueryInitials class encapsulates
    the initial query specifications.
    """

    operation: BaseOperationData
    recursive: bool


class BaseOperationParser(ABC):
    """
    BaseOperationParser serves as the base
    class for all operation parser classes.
    """

    __slots__ = "_operation", "_args", "_parser_map"

    def __init__(self, operation: str, args: dict[str, str]) -> None:
        self._operation = operation
        self._args = args

        # The following instance attribute must be explicitly defined
        # by the child parser classes for parsing operation arguments.
        self._parser_map: dict[str, Callable[[str], Any]]

    def _parse_arguments(self) -> dict[str, Any]:
        """
        Parses the operation arguments and returns a
        new dictionary comprising the parsed values.
        """

        parsed_args: dict[str, Any] = {}

        for key, val in self._args.items():
            parser = self._parser_map.get(key)

            if parser is None:
                raise QueryParseError(
                    f"{key!r} is not a valid operation "
                    "parameter for the specified query."
                )

            parsed_args[key] = parser(val)

        return parsed_args

    @abstractmethod
    def parse(self) -> BaseOperationData: ...
