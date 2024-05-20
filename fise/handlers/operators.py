"""
Operators Module
------------

This module comprises objects and methods for processing user queries and
conducting file/directory search/delete operations within a specified directory.
It also comprises objects for performing search operations within files.
"""

from typing import Generator, Callable, Any
from pathlib import Path
import shutil

import pandas as pd

from errors import OperationError
from common import tools, constants
from shared import File, Directory, DataLine, Field, Size


class FileQueryOperator:
    """
    FileQueryOperator defines methods for performing file search/delete operations.
    """

    __slots__ = "_directory", "_recursive"

    def __init__(self, directory: Path, recursive: bool, absolute: bool) -> None:
        """
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

    @staticmethod
    def _get_field(field: Field, file: File) -> Any:
        """
        Extracts individual fields from the specified `File` object.

        #### Params:
        - field (Field): `Field` object comprising the field to be extracted.
        - file (File): `File` object to extract data from.
        """

        if isinstance(field.field, Size):
            # Extracts the size in bytes and converts into the parsed size unit.
            return getattr(file, "size") / constants.SIZE_CONVERSION_MAP.get(
                field.field.unit
            )

        else:
            return getattr(file, field.field)

    def get_dataframe(
        self,
        fields: list[Field],
        columns: list[str],
        condition: Callable[[File], bool],
    ) -> pd.DataFrame:
        """
        Returns a pandas DataFrame comprising the fields specified
        of all the files present within the specified directory.

        #### Params:
        - fields (list[Field]): list of desired file metadata `Field` objects.
        - columns (list[str]): list of columns to be used in records dataframe.
        - condition (Callable): function for filtering search records.
        """

        files: Generator[File, None, None] = (
            File(file) for file in tools.get_files(self._directory, self._recursive)
        )

        # Creates a pandas DataFrame out of a Generator object
        # comprising records of the specified fields.
        records = pd.DataFrame(
            (
                [self._get_field(field, file) for field in fields]
                for file in files
                if condition(file)
            ),
            columns=columns,
        )

        # Renames the column `size` -> `size[<size_unit>]` to
        # also include the storage unit if not done explicitly.
        records.rename(columns={"size": f"size[B]"}, inplace=True)

        return records

    def remove_files(self, condition: Callable[[File], bool], skip_err: bool) -> None:
        """
        Removes all the files present within the specified directory.

        #### Params:
        - condition (Callable): function for filtering search records.
        - skip_err (bool): Boolean value to specify whether to supress
        permission errors while removing files.
        """

        # `ctr` counts the number of files removed.
        # `skipped` counts the number of skipped files if `skip_err` set to `True`.
        ctr = 0
        skipped = 0

        # Iterates through the files and removes them is the condition is met.
        for file in tools.get_files(self._directory, self._recursive):
            if not condition(File(file)):
                continue

            try:
                file.unlink()

            except PermissionError:
                if skip_err:
                    skipped += 1
                    continue

                OperationError(f"Not enough permissions to delete '{file.absolute()}'.")

            else:
                ctr += 1

        # Extracts the absolute path to the directory and stores it locally.
        directory: Path = self._directory.absolute()

        print(
            constants.COLOR_GREEN
            % f"Successfully removed {ctr} files from {directory}."
        )

        # Prints the skipped files message only is `skipped` is not 0.
        if skipped:
            print(
                constants.COLOR_YELLOW
                % f"Skipped {skipped} files from {directory} due to permission errors."
            )


class FileDataQueryOperator:
    """
    FileDataQueryOperator defines methods for performing
    text data search operations within files.
    """

    __slots__ = "_path", "_recursive", "_filemode"

    def __init__(
        self,
        path: Path,
        recursive: bool,
        absolute: bool,
        filemode: constants.FILE_MODES,
    ) -> None:
        """
        Creates an instance of the `FileDataQueryOperator` class.

        #### Params:
        - path (pathlib.Path): Path of the file/directory to be processed.
        - recursive (bool): Boolean value to specify whether to include the files
        present within the subdirectories if the specified path is a directory.
        - absolute (bool): Boolean value to specify whether to include the
        absolute path of the files.
        - filemode (str): desired filemode to read files.
        """

        self._path = path
        self._recursive = recursive
        self._filemode = constants.FILE_MODES_MAP[filemode]

        if absolute:
            self._path = self._path.absolute()

    def _get_filedata(self) -> Generator[tuple[Path, list[str]], None, None]:
        """
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
            with i.open(self._filemode) as file:
                yield i, file.readlines()

    def _search_datalines(self) -> Generator[DataLine, None, None]:
        """
        Iterates through each file and its corresponding data-lines,
        yielding `DataLine` objects comprising the metadata of the
        data-lines.
        """

        for file, data in self._get_filedata():
            yield from (
                DataLine(file, line, index + 1) for index, line in enumerate(data)
            )

    @staticmethod
    def _get_field(field: Field, data: DataLine) -> Any:
        """
        Extracts individual fields from the specified `DataLine` object.

        #### Params:
        - field (Field): `Field` object comprising the field to be extracted.
        - data (DataLine): `DataLine` object to extract data from.
        """

        # TODO: Extend the functionality to support custom query functions evaluation.
        return getattr(data, field.field)

    def get_dataframe(
        self,
        fields: list[Field],
        columns: list[str],
        condition: Callable[[DataLine], bool],
    ) -> pd.DataFrame:
        """
        Returns a pandas DataFrame comprising the specified fields
        of all the datalines present within the specified file(s)
        matching the specified condition.

        #### Params:
        - fields (list[str]): list of desired file metadata fields.
        - condition (Callable): function for filtering search records.
        """

        # Returns a pandas DataFrame out of a Generator object
        # comprising records of the specified fields.
        return pd.DataFrame(
            (
                [self._get_field(field, data) for field in fields]
                for data in self._search_datalines()
                if condition(data)
            ),
            columns=columns,
        )


class DirectoryQueryOperator:
    """
    DirectoryQueryOperator defines methods for performing
    directory search/delete operations within files.
    """

    __slots__ = "_directory", "_recursive"

    def __init__(self, directory: Path, recursive: bool, absolute: bool) -> None:
        """
        Creates an instance of the `FileQueryOperator` class.

        #### Params:
        - directory (Path): Path of the directory to be processed.
        - recursive (bool): Boolean value to specify whether to include the
        files present within the subdirectories.
        - absolute (bool): Boolean value to specify whether to include the
        absolute path of the files.
        """

        self._directory = directory
        self._recursive = recursive

        if absolute:
            self._directory = self._directory.absolute()

    @staticmethod
    def _get_field(field: Field, directory: Directory) -> Any:
        """
        Extracts individual fields from the specified `Directory` object.

        #### Params:
        - field (Field): `Field` object comprising the field to be extracted.
        - directory (Directory): `Directory` object to extract data from.
        """

        # TODO: Extend the functionality to support custom query functions evaluation.
        return getattr(directory, field.field)

    def get_dataframe(
        self,
        fields: list[Field],
        columns: list[str],
        condition: Callable[[Directory], bool],
    ) -> pd.DataFrame:
        """
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
                [self._get_field(field, directory) for field in fields]
                for directory in directories
                if condition(directory)
            ),
            columns=columns,
        )

        return records

    def remove_directories(
        self, condition: Callable[[Directory], bool], skip_err: bool
    ) -> None:
        """
        Removes all the subdirectories present within the
        specified directory matching the specified condition.

        #### Params:
        - condition (Callable): function for filtering directory records.
        - skip_err (bool): Boolean value to specify whether to supress
        permission errors while removing files.
        """

        # `ctr` counts the number of files removed.
        # `skipped` counts the number of skipped files if `skip_err` set to `True`.
        ctr = 0
        skipped = 0

        # Iterates through the directories and removes them is the condition is met.
        for directory in tools.get_directories(self._directory, self._recursive):
            if not condition(Directory(directory)):
                continue

            try:
                shutil.rmtree(directory)

            except PermissionError:
                if skip_err:
                    continue

                OperationError(
                    f"Not enough permissions to delete '{directory.absolute()}'."
                )

            else:
                ctr += 1

        # Extracts the absolute path to the directory and stores it locally.
        directory: Path = self._directory.absolute()

        print(
            constants.COLOR_GREEN
            % f"Successfully removed {ctr} directories from {directory}."
        )

        # Prints the skipped files message only is `skipped` is not 0.
        if skipped:
            print(
                constants.COLOR_YELLOW
                % f"Skipped {skipped} directories from {directory} due to permission errors."
            )
