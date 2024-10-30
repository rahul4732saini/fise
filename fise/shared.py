"""
Shared Module
-------------

This module comprises data-classes shared across the project
assisting various other classes and functions defined within it.
"""

import re
import sys
from dataclasses import dataclass
from typing import ClassVar, Callable, Literal, Any
from pathlib import Path

import ospecs
from common import constants
from errors import QueryParseError

if sys.platform == "win32":
    from ospecs import WindowsEntity as Entity
else:
    from ospecs import PosixEntity as Entity


class File(Entity):
    """
    File class serves as a unified class for
    accessing all file metadata attributes.
    """

    __slots__ = "_path", "_stats"

    @property
    @ospecs.safe_extract_field
    def filetype(self) -> str | None:
        return self._path.suffix or None

    @property
    @ospecs.safe_extract_field
    def size(self) -> int | float:
        return self._stats.st_size


class DataLine:
    """
    DataLine class serves as a unified class for
    accessing all dataline metadata attributes.
    """

    __slots__ = "_file", "_data", "_lineno"

    def __init__(self, file: Path, data: str | bytes, lineno: int) -> None:
        """
        Creates an instance of the `DataLine` class.

        #### Params:
        - file (pathlib.Path): Path to the file.
        - data (str | bytes): Dataline to be stored.
        - lineno (int): Line number of the dataline.
        """

        # Strips the leading binary notation and quotes
        # if the specified data is a bytes object.
        if isinstance(data, bytes):
            data = str(data)[2:-1]

        self._file = file
        self._data = data
        self._lineno = lineno

    @property
    @ospecs.safe_extract_field
    def path(self) -> str:
        return str(self._file)

    @property
    @ospecs.safe_extract_field
    def name(self) -> str:
        return self._file.name

    @property
    @ospecs.safe_extract_field
    def dataline(self) -> str:
        return self._data

    @property
    @ospecs.safe_extract_field
    def lineno(self) -> int:
        return self._lineno

    @property
    @ospecs.safe_extract_field
    def filetype(self) -> str | None:
        return self._file.suffix or None


class Directory(Entity):
    """
    Directory class serves as a unified class for
    accessing all directory metadata attributes.
    """

    __slots__ = "_path", "_stats"


@dataclass(slots=True, frozen=True, eq=False)
class Size:
    """
    Size class stores the size unit of the file size
    field and defines a mechanism for parsing the field.
    """

    # Regex pattern for matching size field specifications.
    _size_field_pattern: ClassVar[re.Pattern] = re.compile(r"^size(\[.*])?$")

    unit: str

    @classmethod
    def from_string(cls, field: str):
        """
        Creates an instance of `Size` object from
        the specified size field specifications.
        """

        if not cls._size_field_pattern.match(field.lower()):
            raise QueryParseError(f"Found an invalid field {field!r} in the query.")

        # Assigns "B" -> bytes unit is not explicitly specified.
        unit: str = field[5:-1] or "B"

        # Only verifies the size unit if explicitly specified.
        if unit not in constants.SIZE_CONVERSION_MAP:
            raise QueryParseError(f"Invalid unit {unit!r} specified for 'size' field.")

        return cls(unit)

    def get_size(self, file: File) -> float:
        """
        Extracts the size from the specified `File` object and
        converts it in accordance with the stored size unit.
        """
        return round(file.size / constants.SIZE_CONVERSION_MAP.get(self.unit), 5)


@dataclass(slots=True, frozen=True, eq=False)
class Field:
    """Field class stores individual search query fields."""

    field: str


@dataclass(slots=True, frozen=True, eq=False)
class BaseQuery:
    """Base class for all query data-classes."""

    path: Path
    condition: Callable[[File | DataLine | Directory], bool]


@dataclass(slots=True, frozen=True, eq=False)
class SearchQuery(BaseQuery):
    """SearchQuery class stores search query attributes."""

    fields: list[Field | Size]
    columns: list[str]


class DeleteQuery(BaseQuery):
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

    operator1: Any
    operator: str
    operator2: Any
