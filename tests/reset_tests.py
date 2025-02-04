"""
Reset Tests Module
------------------

This module defines utility functions to reset the test directories
by regenerating the files and sub-directories present within them based
on the records of the same stored in the `test_directory.hdf` file.
"""

from pathlib import Path
import pandas as pd



def reset_file_dir_test_directory(
    directory: Path = FILE_DIR_TEST_DIRECTORY,
    listings: Path = FILE_DIR_TEST_DIRECTORY_LISTINGS_FILE,
):
    """
    Resets the `file_dir` test directory.

    Regenerates non-existing files and sub-directories present in the
    `file_dir` test directory based on the records of the same stored
    in the specified HDF5 file.
    """

    if directory.exists():
        shutil.rmtree(directory)

    # Extracts and stores the corresponding listings for regeneration.
    with pd.HDFStore(str(listings)) as store:
        file_listings: pd.Series[str] = store["/file_dir/files"]
        dir_listings: pd.Series[str] = store["/file_dir/dirs"]

    for direc in dir_listings:
        (directory / direc).mkdir()

    for file in file_listings:
        (directory / file).touch()


if __name__ == "__main__":
    reset_file_dir_test_directory()
