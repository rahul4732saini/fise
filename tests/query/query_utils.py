"""
Query Utilities Module
----------------------

This module comprises utility functions supporting
classes and functions for testing queries.
"""

import sys
import shutil
from pathlib import Path
from typing import Generator

import pandas as pd

# Adds the project directories to sys.path at runtime.
sys.path.append(str(Path(__file__).parents[2]))
sys.path.append(str(Path(__file__).parents[2] / "fise"))

from fise.query import QueryHandler


def eval_search_query(
    path: Path,
    fields: str = "*",
    ucase: bool = False,
    path_type: str | None = None,
    export: str | None = None,
    recur: str | None = None,
    oparams: str | None = None,
    conditions: str | None = None,
) -> pd.DataFrame | None:
    """
    Evaluates the search query.
    """

    export = f"export {export}" if export else ""
    recur = recur or ""
    operation: str = "select" + (f"[{oparams}]" if oparams else "")
    path_type = path_type or ""
    fields = fields or ""
    from_ = "FROM" if ucase else "from"
    conditions = "where " + conditions if conditions else ""

    if ucase:
        export, recur, operation, path_type = (
            export.upper(),
            recur.upper(),
            operation.upper(),
            path_type.upper(),
        )

    # Joins the query segments into a single string.
    query: str = " ".join(
        [export, recur, operation, fields, from_, path_type, f"'{path}'", conditions]
    )

    # Handles the specified query.
    return QueryHandler(query).handle()


def eval_delete_query(
    path: str,
    ucase: bool = False,
    path_type: str | None = None,
    recur: str | None = None,
    oparams: str | None = None,
    conditions: str | None = None,
) -> pd.DataFrame | None:
    """
    Evaluates the delete query.
    """

    recur = recur or ""
    operation: str = "delete" + (f"[{oparams}]" if oparams else "")
    path_type = path_type or ""
    from_ = "FROM" if ucase else "from"
    conditions = "where" + conditions if conditions else ""

    if ucase:
        recur, operation, path_type = (
            recur.upper(),
            operation.upper(),
            path_type.upper(),
        )

    # Joins the query segments into a single string.
    query: str = " ".join([recur, operation, from_, path_type, f"'{path}'", conditions])

    # Handles the specified query.
    return QueryHandler(query).handle()


def read_delete_record(path: str) -> set[Path]:
    """
    Extracts test delete records from `delete_records.hdf`.
    """
    with pd.HDFStore(Path(__file__).parent / "delete_records.hdf") as store:
        data: pd.Series = store[path]

    return {Path(path) for path in data}


def get_test_directory_contents(path: str) -> Generator[Path, None, None]:
    """
    Yields `pathlib.Path` objects of paths extracted
    from the dataframe at the specified `path`.
    """

    with pd.HDFStore(Path(__file__).parents[1] / "test_directory.hdf") as store:
        # Extracts `pandas.Series` object of the `path` column in the extracted dataframe.
        contents: pd.Series = store[path]

    test_directory: Path = Path(__file__).parents[1] / "test_directory"
    yield from (test_directory / i for i in contents)


def get_test_files() -> Generator[Path, None, None]:
    """
    Yields `pathlib.Path` objects of all the files present within `test_directory`.
    """
    yield from get_test_directory_contents("/files")


def get_test_subdirs() -> Generator[Path, None, None]:
    """
    Yields `pathlib.Path` objects of all the subdirectories present within `test_directory`.
    """
    yield from get_test_directory_contents("/dirs")


def reset_test_directory() -> None:
    """
    Resets `test_directory` re-creating the files and directories originally defined in it.
    """

    test_directory: Path = Path(__file__).parents[1] / "test_directory"

    # Removes the directory tree if already in existence.
    if test_directory.exists():
        shutil.rmtree(test_directory)

    test_directory.mkdir()

    for direc in get_test_subdirs():
        direc.mkdir()

    for file in get_test_files():
        file.touch()

    # Extracts `pd.Series` objects comprising binary/text file contents.
    with pd.HDFStore(Path(__file__).parents[1] / "test_directory.hdf") as store:
        bin_file_contents: pd.Series = store["/file_contents/bin"]
        text_file_contents: pd.Series = store["/file_contents/text"]

    for file, contents in bin_file_contents.items():
        Path(test_directory / file).write_bytes(contents)

    for file, contents in text_file_contents.items():
        Path(test_directory / file).write_text(contents)
