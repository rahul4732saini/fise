r"""
Operators Module
------------

This module comprises objects and methods for processing user queries and
conducting file/directory search/delete operations within a specified directory.
It also comprises objects for performing search operations within files.
"""

from typing import Generator, Callable
from pathlib import Path
import shutil

import pandas as pd

from ..errors import OperationError
from ..common import tools, constants
from ..shared import File, Directory, DataLine


class FileQueryOperator:
    r"""
    FileQueryOperator defines methods for performing file search/delete operations.
    """

    __slots__ = "_directory", "_recursive"

    def __init__(self, directory: Path, recursive: bool, absolute: bool) -> None:
        r"""
        Creates an instance of the `FileQueryOperator` class.

        #### Params:
        - directory (Path): Path of the directory to be processed.
        - recursive (bool): Boolean value to specify whether to include the files
        present within the subdirectories.
        - absolute (bool): Boolean value to specify whether to include the
        absolute path of the files.
        """

        self._directory = directory
        self._recursive = recursive

        if absolute:
            self._directory = self._directory.absolute()

    def get_fields(
        self, fields: list[str], condition: Callable[[File], bool], size_unit: str
    ) -> pd.DataFrame:
        r"""
        Returns a pandas DataFrame comprising the fields specified
        of all the files present within the specified directory.

        #### Params:
        - fields (lsit[str]): list of desired file metadata fields.
        - condition (Callable): function for filtering search records.
        - size_unit (str): storage size unit.
        """

        files: Generator[File, None, None] = (
            File(file, size_unit)
            for file in tools.get_files(self._directory, self._recursive)
        )

        # Creates a pandas DataFrame out of a Generator object
        # comprising records of the specified fields.
        records = pd.DataFrame(
            (
                [
                    getattr(file, constants.FILE_FIELD_ALIASES.get(field, field))
                    for field in fields
                ]
                for file in files
                if condition(file)
            ),
            columns=fields,
        )

        # Renames the column `size` -> `size(<size_unit>)` to also include the storage unit.
        records.rename(columns={"size": f"size({size_unit})"}, inplace=True)

        return records

    def remove_files(self, condition: Callable[[File], bool]) -> None:
        r"""
        Removes all the files present within the specified directory.

        #### Params:
        - condition (Callable): function for filtering search records.
        """

        for file in tools.get_files(self._directory, self._recursive):
            if not condition(File(file)):
                continue

            try:
                file.unlink()

            except PermissionError:
                OperationError(f"Not enough permissions to delete {file.absolute()}.")


class FileDataQueryOperator:
    r"""
    FileDataQueryOperator defines methods for performing
    text data search operations within files.
    """

    __slots__ = "_path", "_recursive"

    def __init__(self, path: Path, recursive: bool, absolute: bool) -> None:
        r"""
        Creates an instance of the `FileDataQueryOperator` class.

        #### Params:
        - path (pathlib.Path): Path of the file/directory to be processed.
        - recursive (bool): Boolean value to specify whether to include the files
        present within the subdirectories if the specified path is a directory.
        - absolute (bool): Boolean value to specify whether to include the
        absolute path of the files.
        """

        self._path = path
        self._recursive = recursive

        if absolute:
            self._path = self._path.absolute()

    def _get_filedata(self) -> Generator[tuple[Path, list[str]], None, None]:
        r"""
        Yields the file `pathlib.Path` object and a list of strings
        representing the lines of text from each file. Each string in
        the list corresponds to an individual line of text in the file.
        """

        # Generator object of `pathlib.Path` objects of all the files present within
        # the directory if the specified path is a directory else a tuple comprising
        # the `pathlib.Path` object of the specified file.
        files: tuple[Path] | Generator[Path, None, None] = (
            (self._path,)
            if self._path.is_file()
            else tools.get_files(self._path, self._recursive)
        )

        for i in files:
            with i.open("r") as file:
                yield i, file.readlines()

    def _search_datalines(self) -> Generator[DataLine, None, None]:
        r"""
        Iterates through each file and its corresponding data-lines,
        yielding `DataLine` objects comprising the metadata of the
        data-lines.
        """

        for file, data in self._get_filedata():
            yield from (DataLine(file, line, index) for index, line in enumerate(data))

    def get_fields(
        self, fields: list[str], condition: Callable[[DataLine], bool]
    ) -> pd.DataFrame:
        r"""
        Returns a pandas DataFrame comprising the specified fields
        of all the datalines present within the specified file(s)
        matching the specified condition.

        #### Params:
        - fields (list[str]): list of desired file metadata fields.
        - condition (Callable): function for filtering search records.
        """

        # Creates a pandas DataFrame out of a Generator object
        # comprising records of the specified fields.
        records = pd.DataFrame(
            (
                [
                    getattr(data, constants.DATA_FIELD_ALIASES.get(field, field))
                    for field in fields
                    if condition(data)
                ]
                for data in self._search_datalines()
            ),
            columns=fields,
        )

        return records


class DirectoryQueryOperator:
    r"""
    DirectoryQueryOperator defines methods for performing
    directory search/delete operations within files.
    """

    __slots__ = "_directory", "_recursive"

    def __init__(self, directory: Path, recursive: bool, absolute: bool) -> None:
        r"""
        Creates an instance of the `FileQueryOperator` class.

        #### Params:
        - directory (Path): Path of the directory to be processed.
        - recursive (bool): Boolean value to specify whether to include the
        files present withinin the subdirectories.
        - absolute (bool): Boolean value to specify whether to include the
        absolute path of the files.
        """

        self._directory = directory
        self._recursive = recursive

        if absolute:
            self._directory = self._directory.absolute()

    def get_fields(
        self, fields: list[str], condition: Callable[[Directory], bool]
    ) -> pd.DataFrame:
        r"""
        Returns a pandas DataFrame comprising the specified metadata fields
        of all the subdirectories present within the specified directory.

        #### Params:
        - fields (list[str]): list of desired directory metadata fields.
        - condition (Callable): function for filtering search records.
        """

        directories: Generator[Directory, None, None] = (
            Directory(directory)
            for directory in tools.get_directories(self._directory, self._recursive)
        )

        # Creates a pandas DataFrame out of a Generator object
        # comprising records of the specified fields.
        records = pd.DataFrame(
            (
                [
                    getattr(directory, constants.DIR_FIELD_ALIASES.get(field, field))
                    for field in fields
                ]
                for directory in directories
                if condition(directory)
            ),
            columns=fields,
        )

        return records

    def remove_directories(self, condition: Callable[[Directory], bool]) -> None:
        r"""
        Removes all the subdirectories present within the
        specified directory matching the specified condition.

        #### Params:
        - condition (Callable): function for filtering directory records.
        """

        for directory in tools.get_directories(self._directory, self._recursive):
            if condition(Directory(directory)) is False:
                continue

            try:
                shutil.rmtree(directory)

            except PermissionError:
                OperationError(
                    f"Not enough permissions to delete {directory.absolute()}."
                )
