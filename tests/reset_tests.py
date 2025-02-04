"""
Reset Tests Module
------------------

This module defines utility functions to reset the test directories
by regenerating the files and sub-directories present within them based
on the records of the same stored in the `test_directory.hdf` file.

NOTE:
This module is dependent upon a HDF5 file with the same name located in
the hdf/ directory comprising records of the files and directories present
with the test directory to regenerate them whenever required and stores
the following at the below specified paths:


- /file_dir/files: Stores records of file present within the `file_dir` directory.
- /file_dir/dirs: Stores records of directories present within the `file_dir` directory.
"""

from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).parent
HDF_DIR = BASE_DIR / "hdf"

FILE_DIR_TEST_DIR = BASE_DIR / "test_directory/file_dir"
FILE_DIR_TEST_DIR_RECORDS = HDF_DIR / "test_directory.hdf"


def reset_file_dir_test_dir(directory: Path, records: Path):
    """
    Resets the `file_dir` test directory.

    Regenerates non-existing files and sub-directories present in the
    `file_dir` test directory based on the records of the same stored
    in the specified HDF5 file.
    """

    if not directory.exists():
        directory.mkdir()

    # Extracts and stores the corresponding records for regeneration.
    with pd.HDFStore(records.as_posix()) as store:

        file_records: pd.Series[str] = store["/file_dir/files"]
        dir_records: pd.Series[str] = store["/file_dir/dirs"]

    # Regenerates the non-existing sub-directories.
    for direc in dir_records:
        path = directory / direc

        if not path.exists():
            path.mkdir()

    # Regenerates the non-existing files.
    for file in file_records:
        path = directory / file

        if not path.exists():
            path.touch()


if __name__ == "__main__":

    # Resets the `file_dir` test directory.
    reset_file_dir_test_dir(FILE_DIR_TEST_DIR, FILE_DIR_TEST_DIR_RECORDS)
    print("Reset Successful!")
