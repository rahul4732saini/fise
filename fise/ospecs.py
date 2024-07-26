"""
OS Specifications Module
------------------------

This module comprises class and utility functions tailored for different
operating system facilitating seamless integration and efficient handling
of platform-specific tasks across diverse environments.
"""

import os
from pathlib import Path
from typing import Callable, Any
from datetime import datetime

from notify import Alert


def _field_extraction_alert() -> None:
    """
    Raises an alert indicating an error in metadata fields
    extraction from the recorded files/directories.
    """

    if BaseEntity.field_alert:
        return

    Alert(
        "ExtractionError: Unable to access specific metadata fields from the "
        "recorded files/directories. These fields are being assigned as 'None'."
    )

    # Sets `field_alert` attribute to `True` to avoid repeating the alert.
    BaseEntity.field_alert = True


def safe_extract_field(func: Callable[..., Any]) -> Callable[..., Any] | None:
    """
    Safely executes the specified field extraction
    function and returns None in case of an Exception.
    """

    def wrapper(self) -> Any:
        try:
            return func(self)

        except Exception:
            _field_extraction_alert()
            return None

    return wrapper


class BaseEntity:
    """
    BaseEntity class serves as the base class for accessing all methods and attributes
    related to a file/directory `pathlib.Path` and `os.stat_result` object.
    """

    # Boolean value to specify whether a field extraction alert has already
    # been encountered to only alert the user once during the operation.
    field_alert = False

    __slots__ = "_path", "_stats"

    def __init__(self, path: Path) -> None:
        """
        Creates an instance of the `BaseEntity` class.

        #### Params:
        - file (pathlib.Path): path to the file/directory.
        """
        self._path: Path = path
        self._stats: os.stat_result = path.stat()

    @property
    @safe_extract_field
    def name(self) -> str:
        return self._path.name

    @property
    @safe_extract_field
    def path(self) -> str:
        return self._path.as_posix()

    @property
    @safe_extract_field
    def parent(self) -> str:
        return self._path.parent.as_posix()

    @property
    @safe_extract_field
    def access_time(self) -> datetime:
        return datetime.fromtimestamp(self._stats.st_atime).replace(microsecond=0)

    @property
    @safe_extract_field
    def create_time(self) -> datetime:
        return datetime.fromtimestamp(self._stats.st_ctime).replace(microsecond=0)

    @property
    @safe_extract_field
    def modify_time(self) -> datetime:
        return datetime.fromtimestamp(self._stats.st_mtime).replace(microsecond=0)


class WindowsEntity(BaseEntity):
    """
    WindowsEntity class serves as a unified class for accessing
    all methods and attributes related to a Windows file/directory
    `pathlib.Path` and `os.stat_result` object.
    """

    __slots__ = "_path", "_stats"


class PosixEntity(BaseEntity):
    """
    PosixEntity class serves as a unified class for accessing
    all methods and attributes related to a Posix file/directory
    `pathlib.Path` and `os.stat_result` object.
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
