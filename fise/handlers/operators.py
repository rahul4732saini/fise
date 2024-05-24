"""
Operators Module
----------------

This module comprises classes for processing user queries and conducting
file/directory search/delete operations within a specified directory.
It also comprises objects for performing search operations within files.
"""

from typing import Generator, Callable, Any
from pathlib import Path
import shutil

import pandas as pd

from errors import OperationError
from notify import Message, Alert
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
        - directory (Path): Path to the directory.
        - recursive (bool): Boolean value to specify whether to include the files
        present within the subdirectories.
        - absolute (bool): Boolean value to specify whether to include the
        absolute path to the files.
        """

        self._directory = directory
        self._recursive = recursive

        if absolute:
            self._directory = self._directory.absolute()

    @staticmethod
    def _get_field(field: Field, file: File) -> Any:
        """
        Extracts the specified field from the specified `File` object.

        #### Params:
        - field (Field): `Field` object comprising the field to be extracted.
        - file (File): `File` object to extract data from.
        """

        # TODO: Extend the functionality to support custom
        # query functions evaluation in version 0.1.1

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
        Returns a pandas DataFrame comprising the search records of all the
        files matching the specified condition present within the directory.

        #### Params:
        - fields (list[Field]): list of desired file metadata `Field` objects.
        - columns (list[str]): list of columns names for the specified fields.
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

        # Renames the column `size` -> `size[<size_unit>]` to also include
        # the storage unit if not specified explicitly in the field name.
        records.rename(columns={"size": f"size[B]"}, inplace=True)

        return records

    def remove_files(self, condition: Callable[[File], bool], skip_err: bool) -> None:
        """
        Removes all the files present within the
        directory matching the specified condition.

        #### Params:
        - condition (Callable): function for filtering search records.
        - skip_err (bool): Boolean value to specify whether to supress
        permission errors while removing files.
        """

        # `ctr` counts the number of files removed whereas `skipped` counts
        # the number of skipped files if `skip_err` set to `True`.
        ctr = skipped = 0

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

                raise OperationError(
                    f"Not enough permissions to delete '{file.absolute()}'."
                )

            else:
                ctr += 1

        # Extracts the absolute path to the directory and stores it locally.
        directory: Path = self._directory.absolute()

        Message(f"Successfully removed {ctr} files from {directory}.")

        # Prints the skipped files message only is `skipped` is not 0.
        if skipped:
            Alert(f"Skipped {skipped} files from {directory} due to permission errors.")


class FileDataQueryOperator:
    """
    FileDataQueryOperator defines methods for performing
    file-content(text/bytes) search operations.
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
        - path (pathlib.Path): Path to the file/directory.
        - recursive (bool): Boolean value to specify whether to include the files
        present within the subdirectories (only if the specified path is a directory).
        - absolute (bool): Boolean value to specify whether to include the
        absolute path to the files.
        - filemode (str): desired filemode to read files.
        """

        self._path = path
        self._recursive = recursive
        self._filemode = constants.FILE_MODES_MAP[filemode]

        if absolute:
            self._path = self._path.absolute()

    def _get_filedata(self) -> Generator[tuple[Path, list[str | bytes]], None, None]:
        """
        Yields the file `pathlib.Path` object and a list of strings/bytes
        corresponding to individual lines of text/bytes in the file.
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
        yielding `DataLine` objects comprising the data and its metadata.
        """

        for file, data in self._get_filedata():
            yield from (
                DataLine(file, line, index + 1) for index, line in enumerate(data)
            )

    @staticmethod
    def _get_field(field: Field, data: DataLine) -> Any:
        """
        Extracts the specified field from the specified `DataLine` object.

        #### Params:
        - field (Field): `Field` object comprising the field to be extracted.
        - data (DataLine): `DataLine` object to extract data from.
        """

        # TODO: Extend the functionality to support custom
        # query functions evaluation in version 0.1.1
        return getattr(data, field.field)

    def get_dataframe(
        self,
        fields: list[Field],
        columns: list[str],
        condition: Callable[[DataLine], bool],
    ) -> pd.DataFrame:
        """
        Returns a pandas DataFrame comprising the search records of all the
        datalines matching the specified condition present within the file(s).

        #### Params:
        - fields (list[str]): list of the desired metadata fields.
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
    directory search/delete operations.
    """

    __slots__ = "_directory", "_recursive"

    def __init__(self, directory: Path, recursive: bool, absolute: bool) -> None:
        """
        Creates an instance of the `FileQueryOperator` class.

        #### Params:
        - directory (Path): Path to the directory.
        - recursive (bool): Boolean value to specify whether to include the
        files present within the subdirectories.
        - absolute (bool): Boolean value to specify whether to include the
        absolute path to the files.
        """

        self._directory = directory
        self._recursive = recursive

        if absolute:
            self._directory = self._directory.absolute()

    @staticmethod
    def _get_field(field: Field, directory: Directory) -> Any:
        """
        Extracts the specified field from the specified `Directory` object.

        #### Params:
        - field (Field): `Field` object comprising the field to be extracted.
        - directory (Directory): `Directory` object to extract data from.
        """

        # TODO: Extend the functionality to support custom
        # query functions evaluation in version 0.1.1
        return getattr(directory, field.field)

    def get_dataframe(
        self,
        fields: list[Field],
        columns: list[str],
        condition: Callable[[Directory], bool],
    ) -> pd.DataFrame:
        """
        Returns a pandas DataFrame comprising the search records of all the
        subdirectories matching the specified condition present within the directory.

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
        return pd.DataFrame(
            (
                [self._get_field(field, directory) for field in fields]
                for directory in directories
                if condition(directory)
            ),
            columns=columns,
        )

    def remove_directories(
        self, condition: Callable[[Directory], bool], skip_err: bool
    ) -> None:
        """
        Removes all the subdirectories present within the
        directory matching the specified condition.

        #### Params:
        - condition (Callable): function for filtering directory records.
        - skip_err (bool): Boolean value to specify whether to supress
        permission errors while removing subdirectories.
        """

        # `ctr` counts the number of directories removed whereas `skipped` counts
        # the number of skipped directories if `skip_err` set to `True`.
        ctr = skipped = 0

        # Iterates through the directories and removes them is the condition is met.
        for subdir in tools.get_directories(self._directory, self._recursive):
            if not condition(Directory(subdir)):
                continue

            try:
                shutil.rmtree(subdir)

            except PermissionError:
                if skip_err:
                    skipped += 1
                    continue

                raise OperationError(
                    f"Permission Error: Cannot delete file {subdir.absolute()}."
                )

            else:
                ctr += 1

        # Extracts the absolute path to the directory and stores it locally.
        directory: Path = self._directory.absolute()

        Message(f"Successfully removed {ctr} directories from {directory}.")

        # Prints the skipped files message only is `skipped` is not 0.
        if skipped:
            Alert(
                f"Skipped {skipped} directories from {directory} due to permission errors."
            )
