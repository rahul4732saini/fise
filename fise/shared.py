"""
Shared Module
--------------

This module comprises classes shared across the project
assisting various classes and functions defined within it.
"""

import re
import sys
from datetime import datetime
from typing import ClassVar, Callable, Literal, Any
from dataclasses import dataclass
from pathlib import Path

from common import constants
from errors import QueryParseError

if sys.platform == "win32":
    from ospecs import WindowsEntity as Entity
else:
    from ospecs import PosixEntity as Entity


class File(Entity):
    """
    File class serves as a unified class for accessing all attributes
    related to a file `pathlib.Path` and `os.stat_result` object.
    """

    __slots__ = "_path", "_stats"

    @property
    def filetype(self) -> str | None:
        return self._path.suffix or None

    @property
    def size(self) -> int | float:
        return self._stats.st_size

    @property
    def access_time(self) -> datetime | None:
        return self._get_datetime(self._stats.st_atime)

    @property
    def create_time(self) -> datetime | None:
        return self._get_datetime(self._stats.st_ctime)

    @property
    def modify_time(self) -> datetime | None:
        return self._get_datetime(self._stats.st_mtime)

    @staticmethod
    def _get_datetime(timestamp: float) -> datetime | None:
        """Creates a `datetime.datetime` object from the specified timestamp."""
        try:
            return datetime.fromtimestamp(timestamp).replace(microsecond=0)
        except OSError:
            return None


class DataLine:
    """
    DataLine class serves as a unified class for accessing
    all attributes related to the metadata of a dataline.
    """

    __slots__ = "_file", "_data", "_lineno"

    def __init__(self, file: Path, data: str, lineno: int) -> None:
        """
        Creates an instance of the `DataLine` class.

        #### Params:
        - file (pathlib.Path): path to the file.
        - data (str): dataline to be stored.
        - lineno (int): line number of the dataline.
        """
        self._file = file
        self._data = data
        self._lineno = lineno

    @property
    def path(self) -> Path:
        return self._file

    @property
    def name(self) -> str:
        return self._file.name

    @property
    def dataline(self) -> str:
        return self._data

    @property
    def lineno(self) -> int:
        return self._lineno


class Directory(Entity):
    """
    Directory class serves as a unified class for accessing all attributes
    related to a directory `pathlib.Path` and `os.stat_result` object.
    """

    __slots__ = "_path", "_stats"


@dataclass(slots=True, frozen=True, eq=False)
class Size:
    """
    Size class stores the size unit of the size field
    and also defines a mechanism for parsing the field.
    """

    _size_field_pattern: ClassVar[re.Pattern] = re.compile(
        rf"^size(\[({'|'.join(constants.SIZE_CONVERSION_MAP)})]|)$"
    )

    unit: str

    @classmethod
    def from_string(cls, field: str):
        """
        Parses the string and creates an instance of
        `Size` object from the specified size field.
        """

        if not cls._size_field_pattern.match(field):
            raise QueryParseError(f"Found an invalid field {field!r} in the query.")

        # Initializes with "B" -> bytes unit if not explicitly specified.
        return cls(field[5:-1] or "B")


@dataclass(slots=True, frozen=True, eq=False)
class Field:
    """
    Field class stores individual query condition fields.
    """

    field: str


@dataclass(slots=True, frozen=True, eq=False)
class BaseQuery:
    """
    Base class for all query data classes.
    """

    path: Path
    is_absolute: bool
    condition: Callable[[File | DataLine | Directory], bool]


@dataclass(slots=True, frozen=True, eq=False)
class SearchQuery(BaseQuery):
    """
    SearchQuery class stores attributes related to search queries.
    """

    fields: list[Field]
    columns: list[str]


class DeleteQuery(BaseQuery):
    """
    DeleteQuery class stores attributes related to file/directory deletion queries.
    """


@dataclass(slots=True, frozen=True, eq=False)
class ExportData:
    """
    ExportData class stores export data related attributes.
    """

    type_: Literal["file", "database"]
    target: str | Path


@dataclass(slots=True, frozen=True, eq=False)
class OperationData:
    """
    OperationData class stores attributes related to the query operation.
    """

    operation: constants.OPERATIONS
    operand: constants.OPERANDS

    # The following attributes are optional and are only used for some specific
    # operations. `filemode` attribute is only used with a data search operation
    # and `skip_err` attribute is only used in file/directory deletion operation.
    filemode: constants.FILE_MODES | None = None
    skip_err: bool = False


@dataclass(slots=True, frozen=True, eq=False)
class QueryInitials:
    """
    QueryInitials class stores attributes related to query initials.
    """

    operation: OperationData
    recursive: bool
    export: ExportData | None = None


@dataclass(slots=True, frozen=True, eq=False)
class Condition:
    """
    Condition class stores attributes related to individual query conditions.
    """

    operand1: Any
    operator: str
    operand2: Any
