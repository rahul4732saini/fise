r"""
Query Module
----------------

This module comprises objects and methods for processing user queries and
conducting file/directory search operations within a specified directory.
It also includes objects for performing search operations within files.
"""

from typing import Generator, Callable, Literal
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

    __slots__ = "_directory", "_recursive", "_files", "_size_unit"

    def __init__(
        self,
        directory: str,
        recursive: bool = False,
        absolute: bool = False,
        size_unit: str = "B",
    ) -> None:
        r"""
        Creates an instance of the `FileQueryProcessor` class.

        #### Params:
        - directory (str): string representation of the directory path to be processed.
        - recursive (bool): Boolean value to specify whether to include the files
        present in the subdirectories.
        - absolute (bool): Boolean value to specify whether to include the
        absolute path of the files.
        - size_unit (str): storage size unit.
        """

        self._directory = Path(directory)
        self._recursive = recursive
        self._size_unit = size_unit

        # Verifies if the specified path is a directory.
        assert Path(self._directory).is_dir()

        if absolute:
            self._directory = self._directory.absolute()

        # Generator object of File objects for one-time usage.
        self._files: Generator[File, None, None] = (
            File(file) for file in tools.get_files(self._directory, recursive)
        )

    def get_fields(
        self, fields: tuple[str], condition: Callable[[File], bool] | None = None
    ) -> pd.DataFrame:
        r"""
        Returns a pandas DataFrame comprising the fields specified
        of all the files present within the specified directory.

        #### Params:
        - fields (tuple[str]): tuple of all the desired file status fields.
        - condititon (Callable | None): function for filtering search records.
        """

        if condition is None:
            condition = lambda file: True

        records = pd.DataFrame(
            (
                [getattr(file, field) for field in fields]
                for file in self._files
                if condition(file)
            ),
            columns=fields,
        )

        # Renames the column `size` -> `size(<size_unit>)` to also include the storage unit.
        records.rename(columns={"size": f"size({self._size_unit})"}, inplace=True)

        return records


class FileDataQueryProcessor:
    r"""
    FileDataQueryProcessor defines methods used for performing
    all data (text/bytes) search operations within files.
    """

    __slots__ = "_path", "_recursive", "_files", "_filemode"

    def __init__(
        self, path: str, filemode: constants.FILE_MODES, recursive: bool = False
    ) -> None:
        r"""
        Creates an instance of the FileDataQueryProcessor class.

        #### Params:
        - path (pathlib.Path): string representation of the
        file/directory path to be processed.
        - filemode (str): file mode to the access the file contents; must be 'text' or 'bytes'.
        - recursive (bool): Boolean value to specify whether to include the files
        present in the subdirectories if the path specified is a directory.
        """

        pathway: Path = Path(path)
        self._filemode: str = constants.FILE_MODES_MAP.get(filemode)

        if pathway.is_file():
            self._files = (pathway,)

        elif pathway.is_dir():
            self._files = tools.get_files(pathway, recursive)
