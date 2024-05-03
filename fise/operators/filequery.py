r"""
Filequery Module
----------------

This module defines the FileQuery class used for
performing all file search related operations.
"""

from pathlib import Path


class FileQuery:
    r"""
    FileQuery defines methods used for
    performing all file search operations.
    """

    __slots__ = "_directory", "_recursive"

    def __init__(self, directory: Path, recursive: bool = False) -> None:
        self._directory = directory
        self._recursive = recursive