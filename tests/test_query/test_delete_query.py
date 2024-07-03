"""
This module comprises test cases for verifying
the functionality of delete queries in FiSE.
"""

from pathlib import Path

import pytest
import pandas as pd

import reset_tests
from fise.query import QueryHandler

DELETE_QUERY_TEST_RECORDS_FILE = Path(__file__).parent / "test_delete_query.hdf"
TEST_DIRECTORY = Path(__file__).parents[1] / "test_directory"
FILE_DIR_TEST_DIRECTORY = TEST_DIRECTORY / "file_dir"
TEST_DIRECTORY_LISTINGS_FILE = TEST_DIRECTORY.parent / "test_directory.hdf"


def read_hdf(file: str, path: str) -> pd.Series:
    """Reads records stored at the path mentioned from specified HDF5 file."""

    with pd.HDFStore(file) as store:
        return store[path]


# Pandas series comprising path of all the files and directories
# present within the `file_dir` directory within test directory.
FILE_DIR_TEST_DIRECTORY_LISTINGS = pd.concat(
    [
        read_hdf(TEST_DIRECTORY_LISTINGS_FILE, "/file_dir/dirs"),
        read_hdf(TEST_DIRECTORY_LISTINGS_FILE, "/file_dir/files"),
    ]
)


def verify_delete_query(path: str) -> None:
    """
    Verifies all the files or directories removed from the delete query by matching
    records stored at the specified path in the `test_delete_query.hdf` file.
    """

    # File and directories to be exempted during verification as
    # they are meant to be removed during the delete operation.
    records: pd.Series = read_hdf(DELETE_QUERY_TEST_RECORDS_FILE, path)

    for i in FILE_DIR_TEST_DIRECTORY_LISTINGS:
        if (FILE_DIR_TEST_DIRECTORY / i).exists() or i in records.values:
            continue

        # Resets the `file_dir` directory within test directory
        # in case a file or directory is not found unexpectedly.
        reset_tests.reset_file_dir_test_directory()

        raise FileNotFoundError(
            f"'{FILE_DIR_TEST_DIRECTORY / i}' was not found in the test directory."
        )

    else:
        # Resets the `file_dir` and reverts back all the changes made.
        reset_tests.reset_file_dir_test_directory()


def examine_delete_query(query: str, records_path: str) -> None:
    """
    Tests the specified delete query and verifies it with the file and directory
    records stored at the specified path in the `test_delete_query.hdf` file.
    """

    result: None = QueryHandler(query).handle()

    assert result is None
    verify_delete_query(records_path)


class TestFileDeleteQuery:
    """
    Tests the file delete queries.
    """

    basic_query_syntax_test_params = [
        (1, f"DELETE FROM '{FILE_DIR_TEST_DIRECTORY / 'project'}'"),
        (2, f"DELETE[TYPE FILE] FROM '{FILE_DIR_TEST_DIRECTORY / 'media'}' WHERE type = '.mp3'"),
        (3, rf"R DELETE FROM '{FILE_DIR_TEST_DIRECTORY / 'project'}' WHERE name like '.*\.py'"),
    ]

    recursive_command_test_params = [
        (1, f"R DELETE FROM '{FILE_DIR_TEST_DIRECTORY / 'reports'}' WHERE name = 'Q4.txt'"),
        (2, f"RECURSIVE DELETE FROM '{FILE_DIR_TEST_DIRECTORY / 'docs'}'"),
    ]

    @pytest.mark.parametrize(("index", "query"), basic_query_syntax_test_params)
    def test_basic_query_syntax(self, index: int, query: str) -> None:
        """
        Tests the basic file delete query syntax.
        """
        examine_delete_query(query, f"/file/basic/test{index}")
    
    @pytest.mark.parametrize(("index", "query"), recursive_command_test_params)
    def test_recursive_command(self, index: int, query: str) -> None:
        """
        Tests the recursive command in file delete query.
        """
        examine_delete_query(query, f"/file/recursive/test{index}")


class TestDirDeleteQuery:
    """
    Tests the directory delete queries.
    """

    basic_query_syntax_test_params = [
        (1, f"DELETE[TYPE DIR] FROM '{FILE_DIR_TEST_DIRECTORY / 'docs'}'"),
        (2, f"DELETE[TYPE DIR] FROM '{FILE_DIR_TEST_DIRECTORY / 'reports'}' WHERE name like '^report.*$'"),
        (3, f"DELETE[TYPE DIR] FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE name IN ('project', 'media')"),
    ]

    @pytest.mark.parametrize(("index", "query"), basic_query_syntax_test_params)
    def test_basic_query_syntax(self, index: int, query: str) -> None:
        """
        Tests the basic directory delete query syntax.
        """
        examine_delete_query(query, f"/dir/basic/test{index}")
