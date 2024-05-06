r"""
Filequery Module
----------------

This module comprises objects and methods for processing user queries and
conducting file/directory search operations within a specified directory.
It also includes objects for performing search operations within files.
"""

from typing import Generator
from pathlib import Path

import numpy as np
import pandas as pd

from .shared import File
from ..common import constants


class FileQueryProcessor:
    r"""
    FileQueryProcessor defines methods used for
    performing all file search operations.
    """

    __slots__ = "_directory", "_recursive", "_files"

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

        # Generator object of File objects for one-time usage.
        self._files: Generator[File, None, None] = (
            File(file) for file in self._get_files(self._directory)
        )

    def _get_files(self, directory: Path) -> Generator[Path, None, None]:
        r"""
        Returns a `typing.Generator` object of all files present within the
        specified directory. Also extracts the files present within the
        sub-directories if `self._recursive` is set `True` at initialization.

        #### Params:
        - directory (pathlib.Path): Path of the directory to be processed.
        """

        for path in directory.glob('*'):
            if path.is_file():
                yield path

            # Extracts files from sub-directories.
            elif self._recursive and path.is_dir():
                yield from self._get_files(path)

    def get_fields(self, fields: tuple[str], size_unit: str = "B") -> pd.DataFrame:
        r"""
        Returns a pandas DataFrame comprising the fields specified
        of all the files present within the specified directory.

        #### Params:
        - fields (tuple[str]): tuple of all the desired file status fields.
        - size_unit (str): storage size unit.
        """
        
        records =  pd.DataFrame(
            ([getattr(file, field) for field in fields] for file in self._files),
            columns=fields,
        )

        if "size" in fields:
            records["size"] = records["size"].map(
                lambda size: round(size / constants.SIZE_CONVERSION_MAP[size_unit], 5)
            ).astype(np.float64)

            # Renames the column `size` -> `size(<size_unit>)` to also include the storage unit.
            records.rename(columns={"size": f"size({size_unit})"}, inplace=True)

        return records