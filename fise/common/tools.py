r"""
Tools module
------------

This module comprises functions and tools supporting other
objects and functions throughout the FiSE project.
"""

import getpass
from pathlib import Path
from typing import Generator

import pandas as pd
from sqlalchemy.exc import OperationalError
import sqlalchemy

from . import constants


def get_files(directory: Path, recursive: bool) -> Generator[Path, None, None]:
    r"""
    Returns a `typing.Generator` object of all files present within the specified
    directory. Also extracts the files present within the subdirectories if
    `recursive` is set to `True`.

    #### Params:
    - directory (pathlib.Path): Path of the directory to be processed.
    - recursive (bool): Boolean value to specify whether to include the files
    present in the subdirectories.
    """

    for path in directory.glob("*"):
        if path.is_file():
            yield path

        # Extracts files from sub-directories.
        elif recursive and path.is_dir():
            yield from get_files(path, recursive)


def get_directories(directory: Path, recursive: bool) -> Generator[Path, None, None]:
    r"""
    Returns a `typing.Generator` object of all subdirectories present within the
    specified directory. Also extracts the directories present within the subdirectories
    if `recursive` is set to `True`.

    #### Params:
    - directory (pathlib.Path): Path of the directory to be processed.
    - recursive (bool): Boolean value to specify whether to include the files
    present in the subdirectories.
    """

    for path in directory.glob("*"):
        if path.is_dir():
            if recursive:
                yield from get_directories(path, recursive)

            yield path


def export_to_file(data: pd.DataFrame, path: str) -> None:
    r"""
    Exports search data to the specified file in a suitable format.

    #### Params:
    - data (pd.DataFrame): pandas DataFrame containing search results.
    - path (str): string representation of the file path.
    """

    file: Path = Path(path)

    # Verifies the path's parent directory for existence.
    # Also verifies if the file is non-existent.
    assert file.parent.exists() and not file.exists()

    # String representation of the export method used for exporting
    # the pandas DataFrame comprising the search data records.
    export_method: str | None = constants.DATA_EXPORT_TYPES_MAP.get(file.suffix)

    # Exporting the search data to the specified file with a suitable method.
    getattr(data, export_method)(file)


def _connect_sqlite() -> sqlalchemy.Engine:
    r"""
    Connects to a SQLite database file.
    """

    database: Path = Path(input("Enter the path to database file: "))
    return sqlalchemy.create_engine(f"sqlite:///{database}")
