"""
Reset Tests Module

This module provides a utilities to reset the test directories
by regenerating them based on listings stored in an HDF5 file.
"""

import shutil
from pathlib import Path

import pandas as pd

FILE_DIR_TEST_DIRECTORY = Path(__file__).parent / "test_directory" / "file_dir"
FILE_DIR_TEST_DIRECTORY_LISTINGS = Path(__file__).parent / "test_directory.hdf"


def reset_file_dir_test_directory(
    directory: Path = FILE_DIR_TEST_DIRECTORY,
    listings: Path = FILE_DIR_TEST_DIRECTORY_LISTINGS,
):
    """
    Resets the `file_dir` test directory.

    Deletes the existing `file_dir` test directory and recreates it based
    on the directory and file listings stored in the specified HDF5 file.
    """

    if directory.exists():
        shutil.rmtree(directory)

    # Extracts and stores the corresponding listings for regeneration.
    with pd.HDFStore(listings) as store:
        file_listings: pd.Series[str] = store["/file_dir/files"]
        dir_listings: pd.Series[str] = store["/file_dir/dirs"]

    for direc in dir_listings:
        directory.joinpath(direc).mkdir()

    for file in file_listings:
        directory.joinpath(file).touch()


if __name__ == "__main__":
    reset_file_dir_test_directory()
