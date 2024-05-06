r"""
Query Module
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
from ..common import tools, constants


class FileQueryProcessor:
    r"""
    FileQueryProcessor defines methods used for
    performing all file search operations.
    """

    __slots__ = "_directory", "_recursive", "_files"

    def __init__(
        self, directory: str, recursive: bool = False, absolute: bool = False
    ) -> None:
        r"""
        Creates an instance of the `FileQueryProcessor` class.

        #### Params:
        - directory (str): string representation of the directory path to be processed.
        - recursive (bool): Boolean value to specify whether to include the files
        present in the subdirectories.
        - absolute (bool): Boolean value to specify whether to include the
        absolute path of the files.
        """

        self._directory = Path(directory)
        self._recursive = recursive

        # Verifies if the specified path is a directory.
        assert Path(self._directory).is_dir()

        if absolute:
            self._directory = self._directory.absolute()

        # Generator object of File objects for one-time usage.
        self._files: Generator[File, None, None] = (
            File(file) for file in tools.get_files(self._directory, recursive)
        )

    def get_fields(self, fields: tuple[str], size_unit: str = "B") -> pd.DataFrame:
        r"""
        Returns a pandas DataFrame comprising the fields specified
        of all the files present within the specified directory.

        #### Params:
        - fields (tuple[str]): tuple of all the desired file status fields.
        - size_unit (str): storage size unit.
        """

        records = pd.DataFrame(
            ([getattr(file, field) for field in fields] for file in self._files),
            columns=fields,
        )

        if "size" in fields:
            records["size"] = (
                records["size"].map(
                    lambda size: round(
                        size / constants.SIZE_CONVERSION_MAP[size_unit], 5
                    )
                )
            ).astype(np.float64)

            # Renames the column `size` -> `size(<size_unit>)` to also include the storage unit.
            records.rename(columns={"size": f"size({size_unit})"}, inplace=True)

        return records
