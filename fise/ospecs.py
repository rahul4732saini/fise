"""
OS Specifications Module
------------------------

This module comprises class and utility functions tailored for different
operating system facilitating seamless integration and efficient handling
of platform-specific tasks across diverse environments.
"""

import os
from pathlib import Path


class BaseEntity:
    """
    BaseEntity class serves as the base class for accessing all methods and attributes
    related to the file/directory `pathlib.Path` and `os.stat_result` object.
    """

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
    def name(self) -> str:
        return self._path.name

    @property
    def path(self) -> Path:
        return self._path

    @property
    def parent(self) -> Path:
        return self._path.parent

    @property
    def permissions(self) -> int:
        return self._stats.st_mode


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
    def owner(self) -> str:
        return self._path.owner()

    @property
    def group(self) -> str:
        return self._path.group()
