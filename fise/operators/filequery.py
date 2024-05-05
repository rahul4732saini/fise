r"""
Filequery Module
----------------

This module defines the FileQuery class used for
performing all file search related operations.
"""

from os import stat_result
from typing import Generator
from pathlib import Path


class FileQuery:
    r"""
    FileQuery defines methods used for
    performing all file search operations.
    """

    __slots__ = "_directory", "_recursive", "_stats"

    def __init__(self, directory: str, recursive: bool = False) -> None:
        r"""
        Creates an instance of the `FileQuery` class.

        #### Params:
        - directory (str): string representation of the directory path to be processed.
        - recursive (bool): Boolean value to specify whether or not
        to include the files present in the sub-directories.
        """

        self._directory = Path(directory)
        self._recursive = recursive

        # Verifies if the specified path is a directory.
        assert Path(self._directory).is_dir()

        # Dictionary of file paths with their coressponding `os.stat_result` objects.
        self._stats: dict[Path, stat_result] = {
            i: i.stat() for i in self._get_files(self._directory)
        }

    def _get_files(self, directory: Path) -> Generator[Path, None, None]:
        r"""
        Returns a `typing.Generator` object of all files present within the
        specified directory. Also extracts the files present within the
        sub-directories if `self._recursive` is set `True` at initialization.

        #### Params:
        - directory (pathlib.Path): Path of the directory to be processed.
        """

        for i in directory.glob('*'):
            if i.is_file():
                yield i

            # Extracts files from sub-directories.
            elif self._recursive and i.is_dir():
                yield from self._get_files(i)
