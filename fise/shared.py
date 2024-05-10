r"""
Shared Module
--------------

This module comprises classes that serve as foundational
components for various objects and functionalities.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Callable
from pathlib import Path

from .common import constants


class File:
    r"""
    File class serves as a unified class for accessing all methods and attributes
    related to the file `pathlib.Path` and `os.stat_result` object.
    """

    __slots__ = "_file", "_stats", "_size_divisor"

    def __init__(self, file: Path, size_unit: str) -> None:
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
    condition: Callable[[File | Directory], bool]
