"""
Initials Module
---------------

This module defines classes and functions for parsing
the initial clauses of the user-specified query.
"""

from abc import ABC, abstractmethod
from typing import Type, Callable, ClassVar, Any
from dataclasses import dataclass

from common import tools, constants
from shared import QueryQueue
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
    mode: str = constants.READ_MODES_MAP[constants.READ_MODE_TEXT]


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


class FileSystemOperationParser(BaseOperationParser):
    """
    FileSystemOperationParser serves as the base class
    for all file system operation parser classes.
    """

    def __init__(self, operation: str, args: dict[str, str]) -> None:
        super().__init__(operation, args)

        # Maps argument names with their corresponding parser methods.
        self._parser_map: dict[str, Callable[[str], Any]] = {
            "skip_err": self._parse_skip_err,
        }

    def _parse_skip_err(self, skip_err: str) -> bool:
        """
        Parses the `skip_err` operation parameter
        for file and directory delete queries.
        """

        if self._operation != constants.OPERATION_DELETE:
            raise QueryParseError(
                "'skip_err' parameter is only valid for delete operations."
            )

        skip_err = skip_err.lower()

        if skip_err not in constants.BOOLEANS:
            raise QueryParseError(
                f"{skip_err!r} is not a valid argument "
                "for the 'skip_err' operation parameter."
            )

        return skip_err == constants.BOOLEAN_TRUE


class FileOperationParser(FileSystemOperationParser):
    """
    FileOperationParser class defines methods
    for parsing file operation specifications.
    """

    def parse(self) -> FileOperationData:
        """Parses operation arguments for file queries."""

        args = self._parse_arguments()
        return FileOperationData(self._operation, **args)


class DirectoryOperationParser(FileSystemOperationParser):
    """
    DirectoryOperationParser class defines methods
    for parsing directory operation specifications.
    """

    def parse(self) -> DirectoryOperationData:
        """Parses operation arguments for directory queries."""

        args = self._parse_arguments()
        return DirectoryOperationData(self._operation, **args)


class DataOperationParser(BaseOperationParser):
    """
    DataOperationParser class defines methods
    for parsing data operation specifications.
    """

    def __init__(self, operation: str, args: dict[str, str]) -> None:
        if operation == constants.OPERATION_DELETE:
            raise QueryParseError(
                "Delete operation is not compatible with data queries."
            )

        super().__init__(operation, args)

        # Maps argument names with their corresponding parser methods.
        self._parser_map: dict[str, Callable[[str], Any]] = {
            "mode": self._parse_mode,
        }

    @staticmethod
    def _parse_mode(mode: str) -> str:
        """Parses the `mode` operation parameter for data search queries."""

        filemode: str | None = constants.READ_MODES_MAP.get(mode.lower())

        if filemode is None:
            raise QueryParseError(
                f"{mode!r} is not a valid argument "
                "for the 'mode' operation parameter."
            )

        return filemode

    def parse(self) -> DataOperationData:
        """Parses operation arguments for data queries."""

        args = self._parse_arguments()
        return DataOperationData(self._operation, **args)


class QueryInitialsParser:
    """
    QueryInitialsParser class defines methods for parsing the
    initials clauses of the user-specified query comrpising the
    operation specifications and the nature of the query.
    """

    __slots__ = ("_query",)

    # Maps entity names with their corresponding parser classes.
    _parser_map: dict[str, Type[BaseOperationParser]] = {
        constants.ENTITY_FILE: FileOperationParser,
        constants.ENTITY_DIR: DirectoryOperationParser,
        constants.ENTITY_DATA: DataOperationParser,
    }

    def __init__(self, query: QueryQueue) -> None:
        """
        Creates an instance of the InitialsParser class.

        #### Params:
        - query (QueryQueue): `QueryQueue` object comprising the query.
        """

        self._query = query

    def _parse_recursive_clause(self) -> bool:
        """
        Returns a boolean value signifying whether the recursive
        keyword was explicitly specified in the query.
        """

        token: str = self._query.seek().lower()

        if (
            token == constants.KEYWORD_RECURSIVE
            or token == constants.KEYWORD_RECURSIVE_SHORT
        ):
            self._query.pop()
            return True

        return False

    @staticmethod
    def _parse_operation_arguments(args: str) -> dict[str, str]:
        """
        Parses the operation arguments.

        #### Params:
        - args (str): String comprising the operation arguments.
        """

        if not args:
            return {}

        tokens = tools.tokenize(args, delimiter=",")
        args_map: dict[str, str] = {}

        # Populates the arguments mapping based on the extracted tokens.
        pair: list[str]
        for token in tokens:

            pair = token.split(" ", maxsplit=1)
            args_map[pair[0].lower()] = pair[1].lstrip(" ")

        return args_map

    def _get_operation_specifications(self) -> tuple[str, dict[str, str]]:
        """Extracts operation specifications from the query."""

        # Extracts the name of the operation and the associated arguments.
        operation, args = tools.tokenize_qualified_clause(self._query.pop())

        if operation not in constants.OPERATIONS:
            raise QueryParseError(f"{operation!r} is not a valid operation!")

        args_map: dict[str, str] = self._parse_operation_arguments(args)

        return operation, args_map

    def _parse_operation(self) -> BaseOperationData:
        """Parses the operation specifications in the query."""

        operation, args = self._get_operation_specifications()
        entity: str = args.pop("type", constants.DEFAULT_OPERATION_ENTITY).lower()

        if entity not in constants.ENTITIES:
            raise QueryParseError(f"{entity!r} is not a valid operation type!")

        parser: BaseOperationParser = self._parser_map[entity](operation, args)
        data: BaseOperationData = parser.parse()

        return data

    def parse(self) -> QueryInitials:
        """Parses the query initials."""

        recursive: bool = self._parse_recursive_clause()
        operation: BaseOperationData = self._parse_operation()

        return QueryInitials(operation, recursive)
