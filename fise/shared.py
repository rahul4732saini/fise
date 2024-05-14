r"""
Shared Module
--------------

This module comprises classes that serve as foundational
components for various objects and functionalities.
"""

from typing import Callable, Literal
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

from .common import constants


class File:
    r"""
    File class serves as a unified class for accessing all methods and attributes
    related to the file `pathlib.Path` and `os.stat_result` object.
    """

    __slots__ = "_file", "_stats", "_size_divisor"

    def __init__(self, file: Path, size_unit: str = "B") -> None:
        r"""
        Creates an instance of the `File` class.

        #### Params:
        - file (pathlib.Path): path of the file.
        - size_unit (str): storage size unit.
        """

        self._file = file
        self._stats = file.stat()

        # Divisor for storage size conversion.
        size_divisor: int | float | None = constants.SIZE_CONVERSION_MAP.get(size_unit)

        # Verifies if the size divisor is not None.
        assert size_divisor

        self._size_divisor = size_divisor

    @property
    def path(self) -> Path:
        return self._file

    @property
    def parent(self) -> Path:
        return self._file.parent

    @property
    def name(self) -> str:
        return self._file.name

    @property
    def owner(self) -> str:
        return self._file.owner()

    @property
    def group(self) -> str:
        return self._file.group()

    @property
    def size(self) -> float:
        return round(self._stats.st_size / self._size_divisor, 5)

    @property
    def permissions(self) -> int:
        return self._stats.st_mode

    @property
    def access_time(self) -> datetime:
        try:
            return datetime.fromtimestamp(self._stats.st_atime).replace(microsecond=0)
        except OSError:
            ...

    @property
    def create_time(self) -> datetime:
        try:
            return datetime.fromtimestamp(self._stats.st_birthtime).replace(
                microsecond=0
            )
        except OSError:
            ...

    @property
    def modify_time(self) -> datetime:
        try:
            return datetime.fromtimestamp(self._stats.st_mtime).replace(microsecond=0)
        except OSError:
            ...


class DataLine:
    r"""
    DataLine class serves as a unified class for accessing
    all attributes related to the metadata of the dataline.
    """

    __slots__ = "_file", "_data", "_lineno"

    def __init__(self, file: Path, data: str, lineno: int) -> None:
        r"""
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


class Directory:
    r"""
    Directory class serves as a unified class for accessing all methods and attributes
    related to the directory `pathlib.Path` and `os.stat_result` object.
    """

    __slots__ = "_directory", "_stats", "_size_divisor"

    def __init__(self, directory: Path) -> None:
        r"""
        Creates an instance of the `Directory` class.

        #### Params:
        - direcotry (pathlib.Path): path of the directory.
        - size_unit (str): storage size unit.
        """

        self._directory = directory
        self._stats = directory.stat()

    @property
    def path(self) -> Path:
        return self._directory

    @property
    def parent(self) -> Path:
        return self._directory.parent

    @property
    def name(self) -> str:
        return self._directory.name

    @property
    def owner(self) -> str:
        return self._directory.owner()

    @property
    def group(self) -> str:
        return self._directory.group()

    @property
    def permissions(self) -> int:
        return self._stats.st_mode


@dataclass(slots=True, frozen=True, eq=False)
class BaseQuery:
    r"""
    Base class for all query data classes.
    """

    path: Path
    is_absolute: bool
    condition: Callable[[File | Directory], bool]


@dataclass(slots=True, frozen=True, eq=False)
class SearchQuery(BaseQuery):
    r"""
    SearchQuery class serves as a data classes for
    storing attributes related to search queries.
    """

    fields: list[str]


@dataclass(slots=True, frozen=True, eq=False)
class DeleteQuery(BaseQuery):
    r"""
    DeleteQuery class serves as a data class for storing
    attributes related to file/directory deletion queries.
    """

    skip_err: bool


@dataclass(slots=True, frozen=True, eq=False)
class FileSearchQuery(SearchQuery):
    r"""
    SearchQuery class serves as a data classes for storing
    attributes related to file search queries.
    """

    size_unit: str


@dataclass(slots=True, frozen=True, eq=False)
class ExportData:
    r"""
    ExportData class serves as a data class for
    storing export data related attributes.
    """

    type_: Literal["file", "database"]
    target: str | Path


@dataclass(slots=True, frozen=True, eq=False)
class OperationData:
    r"""
    OperationData class serves as a data class for
    storing attributes related to the query operation.
    """

    operation: constants.OPERATIONS
    operand: Literal["file", "data", "dir"]

    # The following attributes are optional and are only used for some specific
    # operations. `filemode` attribute is only used with a data search operation
    # and `skip_err` attribute is only used in file/directory deletion operation.
    filemode: constants.FILE_MODES = "text"
    skip_err: bool = False


@dataclass(slots=True, frozen=True, eq=False)
class QueryInitials:
    r"""
    QueryInitials class serves as a data class for
    storing attribute related to query initials.
    """

    operation: OperationData
    operand: Literal["file", "data", "dir"]
    recursive: bool
    export: ExportData | None = None
