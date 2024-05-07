r"""
Query Module
----------------

This module comprises objects and methods for processing user queries and
conducting file/directory search operations within a specified directory.
It also includes objects for performing search operations within files.
"""

from typing import Generator, Callable
from pathlib import Path

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
            File(file, size_unit)
            for file in tools.get_files(self._directory, recursive)
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
        self,
        path: str,
        filemode: constants.FILE_MODES = "text",
        recursive: bool = False,
        absolute: bool = False,
    ) -> None:
        r"""
        Creates an instance of the FileDataQueryProcessor class.

        #### Params:
        - path (pathlib.Path): string representation of the
        file/directory path to be processed.
        - filemode (str): file mode to the access the file contents; must be 'text' or 'bytes'.
        - recursive (bool): Boolean value to specify whether to include the files
        present in the subdirectories if the path specified is a directory.
        - absolute (bool): Boolean value to specify whether to include the
        absolute path of the files.
        """

        pathway: Path = Path(path)
        self._filemode: str = constants.FILE_MODES_MAP.get(filemode)

        if absolute:
            pathway = pathway.absolute()

        if pathway.is_file():
            self._files = (pathway,)

        elif pathway.is_dir():
            self._files = tools.get_files(pathway, recursive)

    def _get_filedata(self) -> Generator[tuple[Path, list[str]], None, None]:
        r"""
        Yields the file `pathlib.Path` object and a list of strings
        representing the lines of text from each file. Each string in
        the list corresponds to an individual line of text in the file.
        """

        for i in self._files:
            with i.open(self._filemode) as file:
                yield i, file.readlines()

    def _search_datalines(
        self, condition: Callable[[str], bool]
    ) -> Generator[dict[str, str | int], None, None]:
        r"""
        Iterates through each file and its corresponding data-lines,
        yielding dictionaries containing metadata about the data-lines
        that meet the specified condition.

        #### Params:
        - condititon (Callable | None): function for filtering search records.
        """

        for file, data in self._get_filedata():
            yield from (
                {"name": file.name, "path": file, "dataline": data[i], "lineno": i + 1}
                for i in range(len(data))
                if condition(data[i])
            )

    def get_fields(
        self, fields: tuple[str], condition: Callable[[str], bool] | None = None
    ) -> pd.DataFrame:
        r"""
        Returns a pandas DataFrame comprising the fields specified
        of all the datalines present within the specified file(s)
        matching the specified condition.

        #### Params:
        - fields (tuple[str]): tuple of all the desired file status fields.
        - condititon (Callable | None): function for filtering search records.
        """

        if condition is None:
            condition = lambda data: True

        # Creates a pandas DataFrame out of a Generator
        # object comprising records of the specified fields.
        records = pd.DataFrame(
            (
                [data[field] for field in fields]
                for data in self._search_datalines(condition)
            ),
            columns=fields,
        )

        return records
