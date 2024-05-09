r"""
Query Module
------------

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

    __slots__ = "_directory", "_recursive"

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

    def get_fields(
        self,
        fields: tuple[str],
        condition: Callable[[File], bool] | None = None,
        size_unit: str = "B",
    ) -> pd.DataFrame:
        r"""
        Returns a pandas DataFrame comprising the fields specified
        of all the files present within the specified directory.

        #### Params:
        - fields (tuple[str]): tuple of all the desired file status fields.
        - condition (Callable | None): function for filtering search records.
        - size_unit (str): storage size unit.
        """

        files: Generator[File, None, None] = (
            File(file, size_unit)
            for file in tools.get_files(self._directory, self._recursive)
        )

        if condition is None:
            condition = lambda file: True

        records = pd.DataFrame(
            (
                [
                    getattr(file, constants.FILE_QUERY_FIELD_ALIAS.get(field, field))
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

    def remove_files(self, skip_err: bool) -> None:
        r"""
        Removes all the files present within the specified directory.

        #### Params:
        - skip_err (bool): Boolean value to specifiy whether to terminate deletion
        upon encountering an error with file deletion.
        """

        for file in tools.get_files(self._directory, self._recursive):
            try:
                file.unlink()

            except PermissionError as e:
                if skip_err:
                    continue

                raise e


class FileDataQueryProcessor:
    r"""
    FileDataQueryProcessor defines methods used for performing
    all data (text/bytes) search operations within files.
    """

    __slots__ = "_path", "_recursive", "_filemode"

    def __init__(
        self, path: str, filemode: constants.FILE_MODES, recursive: bool, absolute: bool
    ) -> None:
        r"""
        Creates an instance of the FileDataQueryProcessor class.

        #### Params:
        - path (pathlib.Path): string representation of the file/directory path to be processed.
        - filemode (str): file mode to the access the file contents; must be 'text' or 'bytes'.
        - recursive (bool): Boolean value to specify whether to include the files
        present in the subdirectories if the path specified is a directory.
        - absolute (bool): Boolean value to specify whether to include the
        absolute path of the files.
        """

        self._path: Path = Path(path)
        self._filemode: str = constants.FILE_MODES_MAP.get(filemode)
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
            with i.open(self._filemode) as file:
                yield i, file.readlines()

    def _search_datalines(
        self, match: str
    ) -> Generator[dict[str, str | int], None, None]:
        r"""
        Iterates through each file and its corresponding data-lines,
        yielding dictionaries containing metadata about the data-lines
        which contain the `match` sub-string.

        #### Params:
        - match (str): sub-string to be searched within the data-lines.
        """

        for file, data in self._get_filedata():
            yield from (
                {"name": file.name, "path": file, "dataline": data[i], "lineno": i + 1}
                for i in range(len(data))
                if match in data[i]
            )

    def get_fields(self, fields: tuple[str], match: str) -> pd.DataFrame:
        r"""
        Returns a pandas DataFrame comprising the fields specified
        of all the datalines present within the specified file(s)
        matching the specified condition.

        #### Params:
        - fields (tuple[str]): tuple of all the desired file status fields.
        - match (str): sub-string to be searched within the data-lines.
        """

        # Creates a pandas DataFrame out of a Generator object
        # comprising records of the specified fields.
        records = pd.DataFrame(
            (
                [
                    data[constants.DATA_QUERY_FIELD_ALIAS.get(field, field)]
                    for field in fields
                ]
                for data in self._search_datalines(match)
            ),
            columns=fields,
        )

        return records
