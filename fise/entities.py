"""
Entities Module
---------------

This module comprises classes and functions for
storing and handling file system metadata fields.
"""

import os
from typing import Callable, Any
from pathlib import Path
from datetime import datetime

from notify import Alert


def safe_extract_field(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator function for safely executes the specified field
    extraction method. Returns None in case of an exception during
    the field extraction process.
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
                "recorded files/directories. The fileds are being assigned"
                "explicitly as 'None'."
            )

            # Sets alert to False to avoid redundant alerts.
            alert = False

    return wrapper


def get_datetime(timestamp: float) -> datetime:
    """Constructs a `datetime.datetime` object from a POSIX timestamp."""
    return datetime.fromtimestamp(timestamp).replace(microsecond=0)


class BaseEntity:
    """BaseEntity serves as the base class for all other entity classes."""


class FileSystemEntity(BaseEntity):
    """
    FileSystemEntity serves as the base class
    for all file system entity classes.
    """

    def __init__(self, path: Path) -> None:
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
        return get_datetime(self._stats.st_atime)

    @property
    @safe_extract_field
    def create_time(self) -> datetime:
        return get_datetime(self._stats.st_ctime)

    @property
    @safe_extract_field
    def modify_time(self) -> datetime:
        return get_datetime(self._stats.st_mtime)
