"""
Entities Module
---------------

This modules comprises classes and functions for
extracting metadata fields for file system entities.
"""

import os
import sys
from pathlib import Path
from typing import Callable, Any
from datetime import datetime

from notify import Alert


def safe_extract_field(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator function for safely executing the specified field
    extraction method. Returns None in case of an exception during
    the process.

    Displays an alert message on the CLI for the first exception.
    Subsequent exceptions are ignored to avoid redundant alerts.
    """

    alert: bool = True

    def wrapper(self) -> Any:
        nonlocal alert

        try:
            return func(self)

        except Exception:
            if not alert:
                return

            Alert(
                "Warning: Unable to access specific metadata fields of the"
                " recorded files/directories. The fields are being assigned"
                " explicitly as 'None'."
            )

            # Sets alert to False to avoid redundant alerts.
            alert = False

    return wrapper


def get_datetime(timestamp: float) -> datetime:
    """
    Constructs a `datetime.datetime` object
    from the specified UNIX timestamp.
    """
    return datetime.fromtimestamp(timestamp).replace(microsecond=0)


class BaseEntity:
    """BaseEntity serves as the base class for all entity classes."""

    __slots__ = ("_path",)

    def __init__(self, path: Path) -> None:
        self._path: Path = path

    @property
    @safe_extract_field
    def name(self) -> str:
        return self._path.name

    @property
    @safe_extract_field
    def path(self) -> str:
        return self._path.as_posix()


class FileSystemEntity(BaseEntity):
    """
    FileSystemEntity serves as the base class
    for all file and directory entity classes.
    """

    __slots__ = "_path", "_stats"

    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self._stats: os.stat_result = path.stat()

    @property
    @safe_extract_field
    def parent(self) -> str:
        return self._path.parent.as_posix()

    @property
    @safe_extract_field
    def access_time(self) -> datetime:
        return get_datetime(self._stats.st_atime)

    @property
    @safe_extract_field
    def create_time(self) -> datetime:
        return get_datetime(self._stats.st_ctime)

    @property
    @safe_extract_field
    def modify_time(self) -> datetime:
        return get_datetime(self._stats.st_mtime)


class WindowsEntity(FileSystemEntity):
    """
    WindowsEntity class serves as the base class
    for windows file and directory entity classes.
    """

    __slots__ = "_path", "_stats"


class PosixEntity(FileSystemEntity):
    """
    PosixEntity class serves as the base class
    for POSIX file and directory entity classes.
    """

    __slots__ = "_path", "_stats"

    @property
    @safe_extract_field
    def owner(self) -> str:
        return self._path.owner()

    @property
    @safe_extract_field
    def group(self) -> str:
        return self._path.group()

    @property
    @safe_extract_field
    def permissions(self) -> int:
        return self._stats.st_mode


class Entity(PosixEntity if sys.platform != "win32" else WindowsEntity):
    """
    Entity class serves as the base class
    for file and directory entity classes.
    """

    __slots__ = "_path", "_stats"


class File(Entity):
    """
    File class for accessing all metadata
    fields associated with a specific file.
    """

    __slots__ = "_path", "_stats"

    def __repr__(self) -> str:
        return f"File(path={self._path.as_posix()})"

    @property
    @safe_extract_field
    def filetype(self) -> str | None:
        return self._path.suffix or None

    @property
    @safe_extract_field
    def size(self) -> int | float:
        return self._stats.st_size


class Directory(Entity):
    """
    Directory class for accessing all metadata
    fields associated with a specific directory.
    """

    __slots__ = "_path", "_stats"

    def __repr__(self) -> str:
        return f"Directory(path={self._path.as_posix()})"


class DataLine(BaseEntity):
    """
    DataLine class for accessing all metadata fields
    associated with a specific line of data in a file.
    """

    __slots__ = "_path", "_data", "_lineno"

    def __init__(self, path: Path, data: str | bytes, lineno: int) -> None:

        # Strips the leading binary notation and quotes
        # if the specified data is a bytes object.
        if isinstance(data, bytes):
            data = str(data)[2:-1]

        super().__init__(path)
        self._data = data
        self._lineno = lineno

    def __repr__(self) -> str:
        return f"DataLine(path={self._path}, lineno={self._lineno})"

    @property
    @safe_extract_field
    def dataline(self) -> str:
        return self._data

    @property
    @safe_extract_field
    def lineno(self) -> int:
        return self._lineno

    @property
    @safe_extract_field
    def filetype(self) -> str | None:
        return self._path.suffix or None
