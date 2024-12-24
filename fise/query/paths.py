"""
Paths Module
------------

This modules defines classes and functions for storing, parsing and
handling file/directory paths defined within user-specified queries.
"""

from typing import Generator
from pathlib import Path
from abc import ABC, abstractmethod


class BaseQueryPath(ABC):
    """BaseQueryPath serves as the base class for all query path classes."""

    __slots__ = ("_path",)

    def __init__(self, path: Path) -> None:

        self._validate_path(path)
        self._path: Path = path

    @property
    def path(self) -> Path:
        return self._path

    @abstractmethod
    def _validate_path(self, path: Path) -> None: ...

    @abstractmethod
    def enumerate(self, recursive: bool) -> Generator[Path, None, None]: ...
