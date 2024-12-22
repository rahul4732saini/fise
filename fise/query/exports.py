"""
Exports Module
--------------

This module defines classes and functions for parsing
and handling exports to DBMS and external file formats.
"""

from typing import ClassVar
from pathlib import Path
from dataclasses import dataclass

from common import constants


class BaseExportData:
    """
    ExportData serves as the base class for all classes
    responsible for storing export data specifications.
    """

    __slots__ = ()

    type_: ClassVar[str]


@dataclass(slots=True, frozen=True, eq=False)
class FileExportData(BaseExportData):
    """
    FileExportData class encapsulates
    file export data specifications.
    """

    type_ = constants.EXPORT_FILE
    file: Path


@dataclass(slots=True, frozen=True, eq=False)
class DBMSExportData(BaseExportData):
    """
    DBMSExportData class encapsulates
    DBMS export data specifications.
    """

    type_ = constants.EXPORT_DBMS
    dbms: str
