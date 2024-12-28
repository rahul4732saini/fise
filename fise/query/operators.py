"""
Operators Module
----------------

This module defines query operator classes for processing
user queries and performing search or delete operations.
"""

import shutil
from pathlib import Path
from typing import Generator, Callable, Any
from abc import ABC, abstractmethod

import pandas as pd

from errors import OperationError
from notify import Message, Alert
from shared import FileIterator
from entities import BaseEntity, File, Directory, DataLine
from .projections import Projection
from .paths import FileQueryPath, DataQueryPath, DirectoryQueryPath


class BaseOperator(ABC):
    """BaseOperator serves as the base class for all operator classes."""

    @abstractmethod
    def search(
        self,
        projections: list[Projection],
        condition: Callable[[BaseEntity], bool],
    ): ...


class FileSystemOperator(ABC):
    """
    FileSystemOperator serves as the base class
    for all file system operator classes.
    """

    @abstractmethod
    def delete(
        self,
        condition: Callable[[BaseEntity], bool],
        skip_err: bool,
    ): ...


class FileQueryOperator(FileSystemOperator):
    """
    FileQueryOperator defines methods for performing
    file search and delete operations.
    """

    __slots__ = "_path", "_recursive"

    def __init__(self, path: FileQueryPath, recursive: bool) -> None:
        """
        Creates an instance of the FileQueryOperator class.

        #### Params:
        - path (FileQueryPath): file query path object encapsulating the
        targeted directory path.
        - recursive (bool): Whether to include files from sub-directories.
        """

        self._path = path
        self._recursive = recursive

    def search(
        self,
        fields: list[BaseField],
        columns: list[str],
        condition: Callable[[File], bool],
    ) -> pd.DataFrame:
        """
        Returns a pandas DataFrame comprising search records of all the files
        present within the directory which match the specified condition.

        #### Params:
        - fields (list[Field]): List of desired metadata field objects.
        - columns (list[str]): List of columns names for the specified fields.
        - condition (Callable): Function for filtering data records.
        """

        files: Generator[File, None, None] = (
            File(file) for file in tools.get_files(self._directory, self._recursive)
        )

        # Generator object comprising search records of
        # the files matching the specified condition.
        records: Generator[list[Any], None, None] = (
            [field.evaluate(file) for field in fields]
            for file in files
            if condition(file)
        )

        return pd.DataFrame(records, columns=columns)

    @staticmethod
    def _delete_file(file: Path, skip_err: bool) -> bool:
        """
        Deletes the specified file and returns a boolean
        object signifying whether the operation was a success.
        """

        try:
            file.unlink()

        except PermissionError:
            if skip_err:
                return False

            raise OperationError(f"Permission Error: Cannot delete '{file}'")

        else:
            return True

    def delete(self, condition: Callable[[File], bool], skip_err: bool) -> None:
        """
        Deletes all the files present within the
        directory matching the specified conditions.

        #### Params:
        - condition (Callable): Function for filtering data records.
        - skip_err (bool): Whether to supress permission errors during operation.
        """

        # 'ctr' counts the number of files removed during the operation.
        # 'skipped' count the number of files skipped due to exceptions.
        ctr = skipped = 0

        for file in tools.get_files(self._directory, self._recursive):
            if not condition(File(file)):
                continue

            try:
                file.unlink()

            except PermissionError:
                if skip_err:
                    skipped += 1
                    continue

                raise OperationError(f"Permission Error: Cannot delete '{file}'")

            else:
                ctr += 1

        Message(f"Successfully removed {ctr} files from '{self._directory}'.")

        # Prints the skipped files message only is 'skipped' is not zero.
        if skipped:
            Alert(
                f"Skipped {skipped} files from '{self._directory}'"
                "due to permissions errors."
            )


class DataQueryOperator(BaseOperator):
    """
    FileDataQueryOperator defines methods for performing
    text and byte search operations within files.
    """

    __slots__ = "_path", "_recursive", "_filemode"

    def __init__(
        self, path: Path, recursive: bool, filemode: constants.FILE_MODES
    ) -> None:
        """
        Creates an instance of the `FileDataQueryOperator` class.

        #### Params:
        - path (pathlib.Path): Path to the file or directory.
        - recursive (bool): Whether to include files from subdirectories.
        - filemode (str): Desired filemode for reading files.
        """

        self._path = path
        self._recursive = recursive
        self._filemode = constants.FILE_MODES_MAP[filemode]

    def _get_filedata(self) -> Generator[tuple[Path, list[str | bytes]], None, None]:
        """
        Yields the file paths along with a list comprising datalines
        of the corresponding file in the form of strings or bytes.
        """

        # The following variable stores a Generator object of all the files present within
        # the directory if the specified path is a directory or creates a tuple comprising
        # the `pathlib.Path` object of the specified file.
        files: tuple[Path] | Generator[Path, None, None] = (
            (self._path,)
            if self._path.is_file()
            else tools.get_files(self._path, self._recursive)
        )

        for i in files:
            with i.open(self._filemode) as file:
                try:
                    yield i, file.readlines()

                except UnicodeDecodeError:
                    raise OperationError(
                        "Cannot read bytes with 'text' filemode. Set "
                        "filemode to 'bytes' to read byte data within files."
                    )

    def _search_datalines(self) -> Generator[DataLine, None, None]:
        """
        Iterates through the files and their corresponding data-lines, and
        yields `DataLine` objects comprising the dataline and its metadata.
        """

        for file, data in self._get_filedata():
            yield from (
                DataLine(file, line, index + 1) for index, line in enumerate(data)
            )

    def search(
        self,
        fields: list[BaseField],
        columns: list[str],
        condition: Callable[[DataLine], bool],
    ) -> pd.DataFrame:
        """
        Returns a pandas DataFrame comprising the search records of all the
        datalines matching the specified condition present within the file(s).

        #### Params:
        - fields (list[str]): List of the desired metadata fields.
        - condition (Callable): Function for filtering data records.
        """

        # Generator object comprising search records of
        # the files matching the specified condition.
        records: Generator[list[Any], None, None] = (
            [field.evaluate(data) for field in fields]
            for data in self._search_datalines()
            if condition(data)
        )

        return pd.DataFrame(records, columns=columns)


class DirectoryQueryOperator(FileSystemOperator):
    """
    DirectoryQueryOperator defines methods for performing
    directory search and delete operations.
    """

    __slots__ = "_directory", "_recursive"

    def __init__(self, directory: Path, recursive: bool) -> None:
        """
        Creates an instance of the `FileQueryOperator` class.

        #### Params:
        - directory (Path): Path to the directory.
        - recursive (bool): Whether to include files from subdirectories.
        """

        self._directory = directory
        self._recursive = recursive

    def search(
        self,
        fields: list[BaseField],
        columns: list[str],
        condition: Callable[[Directory], bool],
    ) -> pd.DataFrame:
        """
        Returns a pandas DataFrame comprising search records of
        all the subdirectories matching the specified condition.

        #### Params:
        - fields (list[Field]): List of desired directory metadata `Field` objects.
        - columns (list[str]): List of columns names for the specified fields.
        - condition (Callable): Function for filtering data records.
        """

        directories: Generator[Directory, None, None] = (
            Directory(directory)
            for directory in tools.get_directories(self._directory, self._recursive)
        )

        # Generator object comprising search records of
        # the files matching the specified condition.
        records: Generator[list[Any], None, None] = (
            [field.evaluate(directory) for field in fields]
            for directory in directories
            if condition(directory)
        )

        return pd.DataFrame(records, columns=columns)

    def delete(self, condition: Callable[[Directory], bool], skip_err: bool) -> None:
        """
        Removes all the subdirectories matching the specified condition.

        #### Params:
        - condition (Callable): Function for filtering data records.
        - skip_err (bool): Whether to supress permission errors during operation.
        """

        # `ctr` counts the number of directories removed whereas `skipped` counts
        # the number of skipped directories if `skip_err` is set to `True`.
        ctr = skipped = 0

        # Iterates through the subdirectories and deletes
        # individual directory tree(s) if the condition is met.
        for subdir in tools.get_directories(self._directory, self._recursive):
            if not condition(Directory(subdir)):
                continue

            try:
                shutil.rmtree(subdir)

            except PermissionError:
                if skip_err:
                    skipped += 1
                    continue

                raise OperationError(f"Permission Error: Cannot delete '{subdir}'")

            else:
                ctr += 1

        Message(f"Successfully removed {ctr} directories from '{self._directory}'.")

        # Prints the skipped files message only is `skipped` is not zero.
        if skipped:
            Alert(
                f"Skipped {skipped} directories from '{self._directory}' due to permission errors."
            )
