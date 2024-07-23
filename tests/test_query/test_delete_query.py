"""
This module comprises test cases for verifying
the functionality of delete queries in FiSE.
"""

from pathlib import Path

import pytest
import pandas as pd

import reset_tests
from fise.query import QueryHandler

TEST_DIRECTORY = Path(__file__).parents[1] / "test_directory"
FILE_DIR_TEST_DIRECTORY = TEST_DIRECTORY / "file_dir"

TEST_DIRECTORY_LISTINGS_FILE = TEST_DIRECTORY.parent / "test_directory.hdf"
TEST_RECORDS_FILE = Path(__file__).parent / "test_delete_query.hdf"


def read_hdf(file: Path, path: str) -> pd.Series:
    """Reads records stored at the path mentioned from specified HDF5 file."""

    with pd.HDFStore(str(file)) as store:
        return store[path]


# Pandas series comprising path of all the files and directories
# present within the `file_dir` directory within test directory.
FILE_DIR_TEST_DIRECTORY_LISTINGS = pd.concat(
    [
        read_hdf(TEST_DIRECTORY_LISTINGS_FILE, "/file_dir/dirs"),
        read_hdf(TEST_DIRECTORY_LISTINGS_FILE, "/file_dir/files"),
    ],
    ignore_index=True
)


def verify_delete_query(path: str) -> None:
    """
    Verifies all the files and directories removed from the delete query by matching
    records stored at the specified path in the `test_delete_query.hdf` file.
    """
    global FILE_DIR_TEST_DIRECTORY, FILE_DIR_TEST_DIRECTORY_LISTINGS, TEST_RECORDS_FILE

    # File and directories to be exempted during verification as
    # they are meant to be removed during the delete operation.
    records: pd.Series = read_hdf(TEST_RECORDS_FILE, path)

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
        # Resets the `file_dir` and reverts back all the changes made within the directory.
        reset_tests.reset_file_dir_test_directory()


def examine_delete_query(query: str, records_path: str) -> None:
    """
    Tests the specified delete query and verifies it with the file and directory
    records stored at the specified path in the `test_delete_query.hdf` file.
    """

    QueryHandler(query).handle()
    verify_delete_query(records_path)


class TestFileDeleteQuery:
    """
    Tests the file delete queries.
    """

    basic_query_syntax_test_params = [
        (1, f"DELETE FROM '{FILE_DIR_TEST_DIRECTORY / 'project'}'"),
        (2, f"DELETE[TYPE FILE] FROM '{FILE_DIR_TEST_DIRECTORY / 'media'}' WHERE type = '.mp3'"),
        (3, rf"R DELETE FROM '{FILE_DIR_TEST_DIRECTORY / 'project'}' WHERE name LIKE '.*\.py'"),
    ]

    recursive_command_test_params = [
        (1, f"R DELETE FROM '{FILE_DIR_TEST_DIRECTORY / 'reports'}' WHERE name = 'Q4.txt'"),
        (2, f"RECURSIVE DELETE FROM '{FILE_DIR_TEST_DIRECTORY / 'docs'}'"),
    ]

    path_types_test_params = [
        (1, f"R DELETE FROM ABSOLUTE '{FILE_DIR_TEST_DIRECTORY / 'reports'}' WHERE name = 'Q2.txt'"),
        (2, f"DELETE FROM ABSOLUTE '{FILE_DIR_TEST_DIRECTORY / 'project'}'"),
        (3, f"DELETE FROM RELATIVE '{FILE_DIR_TEST_DIRECTORY / 'media'}' WHERE type = '.mp4'"),
    ]

    mixed_case_query_test_params = [
        (1, f"DeLeTE FRoM '{FILE_DIR_TEST_DIRECTORY / 'project'}'"),
        (2, f"DelETE[TYPE FiLE] FrOM '{FILE_DIR_TEST_DIRECTORY / 'media'}' Where type = '.mp3'"),
        (3, rf"r dELETe FrOM '{FILE_DIR_TEST_DIRECTORY / 'project'}' wHERe name liKe '.*\.py'"),
    ]

    query_conditions_test_params = [
        (1, f"R DELETE FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE name = 'Q1.txt'"),
        (2, rf"R DELETE FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE type='.txt' AND name LIKE '^IN.*\.txt$'"),
        (3, f"R DELETE FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE type IN ('.mp4', '.avi') OR type='.mp3'"),
    ]

    nested_conditions_test_params = [
        (
            1, f"R DELETE FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE "
            "size[b] = 0 AND (filetype = '.txt' or type = '.mp3')"
        ),
        (
            2, f"R DELETE FROM '{FILE_DIR_TEST_DIRECTORY / 'project'}' WHERE size[b]"
            "= 0 AND (type = None OR (type in ('.txt', '.py'))) AND name != 'LICENSE'"
        ),
        (
            3, f"R DELETE FROM '{FILE_DIR_TEST_DIRECTORY / 'reports'}' WHERE"
            " type = '.txt' AND  (((name = 'Q1.txt' OR name = 'Q3.txt')))"
        ),
    ]

    @pytest.mark.parametrize(("index", "query"), basic_query_syntax_test_params)
    def test_basic_query_syntax(self, index: int, query: str) -> None:
        """Tests the basic file delete query syntax."""
        examine_delete_query(query, f"/file/basic/test{index}")

    @pytest.mark.parametrize(("index", "query"), recursive_command_test_params)
    def test_recursive_command(self, index: int, query: str) -> None:
        """Tests the recursive command in file delete query."""
        examine_delete_query(query, f"/file/recursive/test{index}")

    @pytest.mark.parametrize(("index", "query"), path_types_test_params)
    def test_path_types(self, index: int, query: str) -> None:
        """Tests all the available path types in file delete query."""
        examine_delete_query(query, f"/file/path_types/test{index}")

    @pytest.mark.parametrize(("index", "query"), query_conditions_test_params)
    def test_query_conditions(self, index: int, query: str) -> None:
        """Tests file delete query conditions."""
        examine_delete_query(query, f"/file/conditions/test{index}")

    @pytest.mark.parametrize(("index", "query"), nested_conditions_test_params)
    def test_nested_query_conditions(self, index: int, query: str) -> None:
        """Tests nested conditions in file delete query."""
        examine_delete_query(query, f"/file/nested_conditions/test{index}")

    # The following test uses the same delete queries defined for basic query syntax test
    # comprising characters of mixed cases, and hence uses the file and directory records
    # stored at the same path in the `test_delete_query.hdf` file.

    @pytest.mark.parametrize(("index", "query"), mixed_case_query_test_params)
    def test_mixed_case_query(self, index: int, query: str) -> None:
        """Tests file delete queries comprising characters of mixed cases."""
        examine_delete_query(query, f"/file/basic/test{index}")


class TestDirDeleteQuery:
    """
    Tests the directory delete queries.
    """

    basic_query_syntax_test_params = [
        (1, f"DELETE[TYPE DIR] FROM '{FILE_DIR_TEST_DIRECTORY / 'docs'}'"),
        (2, f"DELETE[TYPE DIR] FROM '{FILE_DIR_TEST_DIRECTORY / 'reports'}' WHERE name LIKE '^report.*$'"),
        (3, f"DELETE[TYPE DIR] FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE name IN ('project', 'media')"),
    ]

    recursive_command_test_params = [
        (1, f"R DELETE[TYPE DIR] FROM '{FILE_DIR_TEST_DIRECTORY / 'project'}'"),
        (2, f"R DELETE[TYPE DIR] FROM '{FILE_DIR_TEST_DIRECTORY / 'reports'}' WHERE name='report-2023'"),
        (3, f"R DELETE[TYPE DIR] FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE name IN ('media', 'orders')"),
    ]

    path_types_test_params = [
        (1, f"DELETE[TYPE DIR] FROM ABSOLUTE '{FILE_DIR_TEST_DIRECTORY / 'docs'}'"),
        (2, f"DELETE[TYPE DIR] FROM RELATIVE '{FILE_DIR_TEST_DIRECTORY / 'reports'}'"),
        (3, f"DELETE[TYPE DIR] FROM ABSOLUTE '{FILE_DIR_TEST_DIRECTORY / 'project'}'"),
    ]

    mixed_case_query_test_params = [
        (1, f"DeLEtE[TYPe DIR] froM '{FILE_DIR_TEST_DIRECTORY / 'docs'}'"),
        (2, f"DElEtE[tYPE DiR] From '{FILE_DIR_TEST_DIRECTORY / 'reports'}' Where name LikE '^report.*$'"),
        (3, f"Delete[Type diR] FroM '{FILE_DIR_TEST_DIRECTORY}' WheRE name In ('project', 'media')"),
    ]

    query_conditions_test_params = [
        (
            1, f"DELETE[TYPE DIR] FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE name = 'media'"
        ),
        (
            2, f"DELETE[TYPE DIR] FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE "
            "name IN ('orders', 'media') AND parent LIKE '^.*file_dir[/]?$'"
        ),
        (
            3, f"DELETE[TYPE DIR] FROM '{FILE_DIR_TEST_DIRECTORY / 'reports'}' WHERE"
            " name = 'report-2021' OR name = 'report-2022' OR name = 'report-2023'"
        )
    ]

    nested_conditions_test_params = [
        (
            1, f"DELETE[TYPE DIR] FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE parent"
            " LIKE '^.*file_dir[/]?$' AND (name = 'orders' OR name = 'media')"
        ),
        (
            2, f"R DELETE[TYPE DIR] FROM '{FILE_DIR_TEST_DIRECTORY}' WHERE"
            " ((name IN ('src'))) AND path LIKE '^.*file_dir/src[/]?$'"
        ),
        (
            3, f"DELETE[TYPE DIR] FROM '{FILE_DIR_TEST_DIRECTORY / 'reports'}' WHERE path LIKE "
            "'^.*report-20(23|24)[/]?$' AND ((name = 'report-2023') OR ((name = 'report-2024')))"
        ),
    ]

    @pytest.mark.parametrize(("index", "query"), basic_query_syntax_test_params)
    def test_basic_query_syntax(self, index: int, query: str) -> None:
        """Tests the basic directory delete query syntax."""
        examine_delete_query(query, f"/dir/basic/test{index}")

    @pytest.mark.parametrize(("index", "query"), recursive_command_test_params)
    def test_recursive_command(self, index: int, query: str) -> None:
        """Tests the recursive command in directory delete query."""
        examine_delete_query(query, f"/dir/recursive/test{index}")

    @pytest.mark.parametrize(("index", "query"), path_types_test_params)
    def test_path_types(self, index: int, query: str) -> None:
        """Tests all the available path types in directory delete query."""
        examine_delete_query(query, f"/dir/path_types/test{index}")

    @pytest.mark.parametrize(("index", "query"), query_conditions_test_params)
    def test_query_conditions(self, index: int, query: str) -> None:
        """Tests directory delete query conditions."""
        examine_delete_query(query, f"/dir/conditions/test{index}")
    
    @pytest.mark.parametrize(("index", "query"), nested_conditions_test_params)
    def test_nested_query_conditions(self, index: int, query: str) -> None:
        """Tests nested conditions in directory delete query."""
        examine_delete_query(query, f"/dir/nested_conditions/test{index}")

    # The following test uses the same delete queries defined for basic query syntax test
    # comprising characters of mixed cases, and hence uses the file and directory records
    # stored at the same path in the `test_delete_query.hdf` file.

    @pytest.mark.parametrize(("index", "query"), mixed_case_query_test_params)
    def test_mixed_case_query(self, index: int, query: str) -> None:
        """Tests directory delete queries comprising characters of mixed cases."""
        examine_delete_query(query, f"/dir/basic/test{index}")
