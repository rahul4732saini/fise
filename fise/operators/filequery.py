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

    def __init__(self, directory: Path) -> None:
        self._directory = directory
