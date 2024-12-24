"""
Initials Module
---------------

This module defines classes and functions for parsing
the initial clauses of the user-specified query.
"""

from typing import ClassVar
from dataclasses import dataclass

from common import constants


@dataclass(slots=True, frozen=True, eq=False)
class BaseOperationData:
    """
    BaseOperationData serves as the base
    class for all operation data classes.
    """

    entity: ClassVar[str]
    operation: str


@dataclass(slots=True, frozen=True, eq=False)
class FileSystemOperationData(BaseOperationData):
    """
    FileSystemOperationData serves as the base class
    for all file system operation data classes.
    """

    skip_err: bool = False


@dataclass(slots=True, frozen=True, eq=False)
class FileOperationData(FileSystemOperationData):
    """
    FileOperationData class encapsulates
    the file operation data specifications.
    """

    entity = constants.ENTITY_FILE


@dataclass(slots=True, frozen=True, eq=False)
class DirectoryOperationData(FileSystemOperationData):
    """
    DirectoryOperationData class encapsulates
    the directory operation data specifications.
    """

    entity = constants.ENTITY_DIR


@dataclass(slots=True, frozen=True, eq=False)
class DataOperationData(BaseOperationData):
    """
    DataOperationData class encapsulates
    the data operation data specifications.
    """

    entity = constants.ENTITY_DATA
    mode: str = constants.READ_MODE_TEXT
