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
        self, projections: list[Projection], condition: Callable[[File], bool]
    ) -> pd.DataFrame:
        """
        Returns a pandas DataFrame comprising search records of all the
        files within the directory that satisfy the specified condition.

        #### Params:
        - projections (list[Projection]): List comprising the search projections.
        - condition (Callable): Function for filtering data records.
        """

        files: Generator[File, None, None] = (
            File(file) for file in self._path.enumerate(self._recursive)
        )

        # Generator object comprising search records of
        # the files matching the specified condition.
        records: Generator[list[Any], None, None] = (
            [proj.evaluate(file) for proj in projections]
            for file in files
            if condition(file)
        )

        return pd.DataFrame(records, columns=projections)

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
        Deletes all the files within the directory
        that satisfy the specified condition.

        #### Params:
        - condition (Callable): Function for filtering data records.
        - skip_err (bool): Whether to supress permission errors during operation.
        """

        # 'ctr' counts the number of files removed during the operation.
        # 'skipped' count the number of files skipped due to exceptions.
        ctr = skipped = 0

        # Indicates whether the file was successfully deleted.
        success: bool

        for file in self._path.enumerate(self._recursive):
            if not condition(File(file)):
                continue

            success = self._delete_file(file, skip_err)

            ctr += success
            skipped += not success

        Message(f"Successfully removed {ctr} files from '{self._path.path}'.")

        # Prints the skipped files message only is 'skipped' is a non-zero integer.
        if skipped:
            Alert(
                f"Skipped {skipped} files from '{self._path.path}'"
                " due to permissions errors."
            )


class DataQueryOperator(BaseOperator):
    """
    FileDataQueryOperator defines methods for performing
    text and byte search operations within files.
    """

    __slots__ = "_path", "_recursive", "_filemode"

    def __init__(self, path: DataQueryPath, recursive: bool, filemode: str) -> None:
        """
        Creates an instance of the DataQueryOperator class.

        #### Params:
        - path (DataQueryPath): data query path object encapsulating the
        targeted file or directory path.
        - recursive (bool): Whether to include files from subdirectories.
        - filemode (str): Desired filemode for reading files.
        """

        self._path = path
        self._recursive = recursive
        self._filemode = filemode

    def _get_datalines(self) -> Generator[DataLine, None, None]:
        """
        Extracts the datalines within the files present in the
        directory or within the specific file if the path leads
        to the same.
        """

        iterators: Generator[FileIterator, None, None] = (
            FileIterator(file, self._filemode)
            for file in self._path.enumerate(self._recursive)
        )

        # Extracts individual datalines from the file iterators.
        for iterator in iterators:
            for line_no, data in iterator:
                yield DataLine(iterator.path, data, line_no)

    def search(
        self, projections: list[Projection], condition: Callable[[DataLine], bool]
    ) -> pd.DataFrame:
        """
        Return a pandas DataFrame comprising search records of
        all the datalines that satisfy the specified condition.

        #### Params:
        - projections (list[Projections]): List comprising the search projections.
        - condition (Callable): Function for filtering data records.
        """

        # Generator object comprising search records of
        # the files matching the specified condition.
        records: Generator[list[Any], None, None] = (
            [proj.evaluate(dataline) for proj in projections]
            for dataline in self._get_datalines()
            if condition(dataline)
        )

        return pd.DataFrame(records, columns=projections)


class DirectoryQueryOperator(FileSystemOperator):
    """
    DirectoryQueryOperator defines methods for performing
    directory search and delete operations.
    """

    __slots__ = "_path", "_recursive"

    def __init__(self, path: DirectoryQueryPath, recursive: bool) -> None:
        """
        Creates an instance of the DirectoryQueryOperator class.

        #### Params:
        - path (DirectoryQueryPath): directory query path object encapsulating
        the targeted directory path.
        - recursive (bool): Whether to include files from subdirectories.
        """

        self._path = path
        self._recursive = recursive

    def search(
        self,
        projections: list[Projection],
        condition: Callable[[Directory], bool],
    ) -> pd.DataFrame:
        """
        Returns a pandas DataFrame comprising search records of all
        the sub-directories all satisfy the specified condition.

        #### Params:
        - projections (list[Projection]): List comprising the search projections.
        - condition (Callable): Function for filtering data records.
        """

        directories: Generator[Directory, None, None] = (
            Directory(directory) for directory in self._path.enumerate(self._recursive)
        )

        # Generator object comprising search records of
        # the directories matching the specified condition.
        records: Generator[list[Any], None, None] = (
            [proj.evaluate(directory) for proj in projections]
            for directory in directories
            if condition(directory)
        )

        return pd.DataFrame(records, columns=projections)

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
