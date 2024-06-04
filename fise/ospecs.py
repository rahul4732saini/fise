"""
OS Specifications Module
------------------------

This module comprises class and utility functions tailored for different
operating system facilitating seamless integration and efficient handling
of platform-specific tasks across diverse environments.
"""

import os
from typing import Callable, Any
from pathlib import Path

from notify import Alert


def field_extraction_alert() -> None:
    """
    Raises an alert indicating an error in metadata fields
    extraction from the recorded files/directories.
    """

    if BaseEntity.field_alert:
        return

    Alert(
        "ExtractionError: Unable to access specific metdata fields from the "
        "recorded files/directories. These fields are being assigned as 'None'."
    )

    # Sets `field_alert` attribute to `True` to avoid repeating the alert.
    BaseEntity.field_alert = True


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

    @staticmethod
    def safe_execute(func: Callable[..., Any]) -> Callable[..., Any] | None:
        """
        Safely executes the specified function and
        returns None in case of an Exception.
        """

        def wrapper(self) -> Any:
            try:
                return func(self)

            except Exception:
                field_extraction_alert()
                return None

        return wrapper

    @property
    @safe_execute
    def name(self) -> str:
        return self._path.name

    @property
    @safe_execute
    def path(self) -> str:
        return str(self._path)

    @property
    @safe_execute
    def parent(self) -> str:
        return str(self._path.parent)


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
    @BaseEntity.safe_execute
    def owner(self) -> str:
        return self._path.owner()

    @property
    @BaseEntity.safe_execute
    def group(self) -> str:
        return self._path.group()

    @property
    @BaseEntity.safe_execute
    def permissions(self) -> int:
        return self._stats.st_mode
