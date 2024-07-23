"""
This module comprises test cases for verifying
the functionality of operator classes in FiSE.
"""

# The structural format of the attributes comprising test parameters
# defined within test classes in this module is as described below:
#
#   1. Test parameters for search operations
#
# The attributes comprising test parameters for the search operations within the test
# classes comprise sub-arrays, each with a length of 4 where the first element of each
# of them signifies the index, the second signifies whether the test is verifiable (True)
# or non-verifiable (False). The third element is an array comprising parameters for the
# search operation in the following order (sub-directory, recursive, fields) wherease the
# last element is a reference to the function comprising the filtering conditions.
#
# Some attributes may not adhere to these structures due to some exceptions in
# the tests and will have an explicit structural description along with them.


from pathlib import Path
from typing import Any

import pytest
import pandas as pd

import reset_tests
from fise.common import constants
from fise.shared import File, Directory, Field, DataLine
from fise.query.operators import (
    FileDataQueryOperator,
    FileQueryOperator,
    DirectoryQueryOperator,
)


TEST_DIRECTORY = Path(__file__).parents[2] / "test_directory"

DATA_TEST_DIRECTORY = TEST_DIRECTORY / "data"
FILE_DIR_TEST_DIRECTORY = TEST_DIRECTORY / "file_dir"

TEST_DIRECTORY_LISTINGS_FILE = TEST_DIRECTORY.parent / "test_directory.hdf"
TEST_RECORDS_FILE = Path(__file__).parent / "test_operators.hdf"


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
    ],
    ignore_index=True,
)


def verify_search_operation(path: str, data: pd.DataFrame) -> None:
    """
    Verifies the pandas dataframe extracted from the search operation with the
    records stored at the specified path in the `test_operators.hdf` file.
    """
    global TEST_RECORDS_FILE

    assert isinstance(data, pd.DataFrame)

    results: pd.DataFrame = read_hdf(TEST_RECORDS_FILE, path)

    data_set: set[tuple[Any]] = set(tuple(row) for row in data.values)
    results_set: set[tuple[Any]] = set(tuple(row) for row in results.values)

    assert data_set == results_set


def verify_delete_operation(path: str) -> None:
    """
    Verifies all the files and directories removed from the delete query by matching
    records stored at the specified path in the `test_delete_query.hdf` file.
    """
    global TEST_RECORDS_FILE, FILE_DIR_TEST_DIRECTORY_LISTINGS

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


class TestFileQueryOperator:
    """Tests the FileQueryOperator class"""

    def condition1(file: File) -> bool:
        return file.filetype is not None

    def condition2(file: File) -> bool:
        return not file.size

    def condition3(file: File) -> bool:
        return file.name in ("unknown.mp3", "runaway.mp3", "birthday.avi")

    def condition4(file: File) -> bool:
        return file.name in ("Q1.txt", "Q2.txt")

    search_operation_test_params = [
        (1, True, ["", False, ["name", "filetype"], condition1]),
        (2, True, ["reports", True, ["name"], condition2]),
        (3, False, ["", False, ["path", "access_time"], condition2]),
        (4, False, ["", False, ["parent", "create_time"], condition1]),
    ]

    search_operation_with_fields_alias_test_params = [
        (1, True, ["", True, ["filename", "type"], condition3]),
        (2, False, ["media", False, ["ctime", "atime", "mtime"], condition1]),
        (3, False, ["docs", True, ["filepath", "type", "ctime"], condition2]),
    ]

    delete_operation_test_params = [
        (1, ["", False, condition1, False]),
        (2, ["reports", True, condition4, False]),
        (3, ["media", False, condition3, True]),
    ]

    @pytest.mark.parametrize(
        ("index", "verify", "params"), search_operation_test_params
    )
    def test_search_operation(
        self, index: int, verify: bool, params: list[Any]
    ) -> None:
        """Tests file query operator with search operations."""

        fields: list[Field] = [Field(name) for name in params[2]]

        operator = FileQueryOperator(FILE_DIR_TEST_DIRECTORY / params[0], params[1])
        data: pd.DataFrame = operator.get_dataframe(fields, params[2], params[3])

        if verify:
            verify_search_operation(f"/file/search/test{index}", data)

    @pytest.mark.parametrize(
        ("index", "verify", "params"), search_operation_with_fields_alias_test_params
    )
    def test_search_operation_with_field_aliases(
        self, index: int, verify: bool, params: list[Any]
    ) -> None:
        """
        Tests file query operator with search
        operations comprising field aliases.
        """

        fields: list[Field] = [
            Field(constants.FILE_FIELD_ALIASES[i]) for i in params[2]
        ]

        operator = FileQueryOperator(FILE_DIR_TEST_DIRECTORY / params[0], params[1])
        data: pd.DataFrame = operator.get_dataframe(fields, params[2], params[3])

        if verify:
            verify_search_operation(f"/file/search2/test{index}", data)

    @pytest.mark.parametrize(("index", "params"), delete_operation_test_params)
    def test_delete_operation(self, index: int, params: str) -> None:
        """Tests file query operation with delete operations."""

        operator = FileQueryOperator(FILE_DIR_TEST_DIRECTORY / params[0], params[1])
        data: None = operator.remove_files(params[2], params[3])

        assert data is None

        verify_delete_operation(f"/file/delete/test{index}")


class TestFileDataQueryOperator:
    """Tests the FileDataQueryOperator class"""

    def condition1(data: DataLine) -> bool:
        return data.name in ("todo.txt", "specs.txt") and data.lineno in range(20)

    def condition2(data: DataLine) -> bool:
        return data.name in (
            "Annual Financial Report 2023.txt",
            "Customer Satisfaction Survey Results.txt",
        ) and data.lineno in range(10)

    def condition3(data: DataLine) -> bool:
        return data.lineno in range(10)

    def condition4(data: DataLine) -> bool:
        return data.name in ("todo.txt", "report-2020.xlsx") and data.lineno in range(8)

    text_search_operation_test_params = [
        (1, True, ["", False, ["name", "lineno", "dataline"], condition1]),
        (2, True, ["documents", False, ["lineno", "dataline"], condition2]),
    ]

    bytes_search_operation_test_params = [
        (1, True, ["reports", False, ["dataline"], condition3]),
        (2, True, ["", True, ["name", "dataline", "filetype"], condition4]),
    ]

    @pytest.mark.parametrize(
        ("index", "verify", "params"), text_search_operation_test_params
    )
    def test_text_search_operation(
        self, index: int, verify: bool, params: list[Any]
    ) -> None:
        """Tests file data query operator with text search operations."""

        fields: list[Field] = [Field(name) for name in params[2]]

        operator = FileDataQueryOperator(
            DATA_TEST_DIRECTORY / params[0], params[1], "text"
        )
        data: pd.DataFrame = operator.get_dataframe(fields, params[2], params[3])

        if verify:
            verify_search_operation(f"/data/text/search/test{index}", data)

    @pytest.mark.parametrize(
        ("index", "verify", "params"), bytes_search_operation_test_params
    )
    def test_bytes_search_operation(
        self, index: int, verify: bool, params: list[Any]
    ) -> None:
        """Tests file data query operator with bytes search operations."""

        fields: list[Field] = [Field(name) for name in params[2]]

        operator = FileDataQueryOperator(
            DATA_TEST_DIRECTORY / params[0], params[1], "bytes"
        )
        data: pd.DataFrame = operator.get_dataframe(fields, params[2], params[3])

        if verify:
            verify_search_operation(f"/data/bytes/search/test{index}", data)


class TestDirectoryQueryOperator:
    """Tests the DirectoryQueryOperator class"""

    def condition1(directory: Directory) -> bool:
        return directory.name in ("docs", "media", "reports")

    def condition2(directory: Directory) -> bool:
        return directory.name in ("report-2021", "report-2022")

    def condition3(directory: Directory) -> bool:
        return directory.name == "media"

    def condition4(directory: Directory) -> bool:
        return directory.name == "src"

    search_operation_test_params = [
        (1, True, ["", False, ["name"], condition1]),
        (2, False, ["reports", True, ["name", "access_time"], condition2]),
        (3, False, ["", True, ["path", "parent", "create_time"], condition1]),
        (4, False, ["reports", False, ["name", "modify_time"], condition2]),
    ]

    search_operation_with_fields_alias_test_params = [
        (["", False, ["atime", "mtime", "ctime"], condition1]),
        (["reports", True, ["atime", "ctime"], condition2]),
    ]

    delete_operation_test_params = [
        (1, ["", False, condition3, False]),
        (2, ["reports", False, condition2, True]),
        (3, ["", True, condition4, False]),
    ]

    @pytest.mark.parametrize(
        ("index", "verify", "params"), search_operation_test_params
    )
    def test_search_operation(
        self, index: int, verify: bool, params: list[Any]
    ) -> None:
        """Tests directory query operator with search operations."""

        fields: list[Field] = [Field(name) for name in params[2]]

        operator = DirectoryQueryOperator(
            FILE_DIR_TEST_DIRECTORY / params[0], params[1]
        )
        data: pd.DataFrame = operator.get_dataframe(fields, params[2], params[3])

        if verify:
            verify_search_operation(f"/directory/search/test{index}", data)

    # The following method does not verify its tests as the generated data results
    # are flexible and subject to change based on the execution environment.

    @pytest.mark.parametrize(("params"), search_operation_with_fields_alias_test_params)
    def test_search_operation_with_field_aliases(self, params: list[Any]) -> None:
        """
        Tests directory query operator with search
        operations comprising field aliases.
        """

        fields: list[Field] = [
            Field(constants.DIR_FIELD_ALIASES[name]) for name in params[2]
        ]

        operator = DirectoryQueryOperator(
            FILE_DIR_TEST_DIRECTORY / params[0], params[1]
        )
        data: pd.DataFrame = operator.get_dataframe(fields, params[2], params[3])

        assert isinstance(data, pd.DataFrame)

    @pytest.mark.parametrize(("index", "params"), delete_operation_test_params)
    def test_delete_operation(self, index: int, params: str) -> None:
        """Tests file query operation with delete operations."""

        operator = DirectoryQueryOperator(
            FILE_DIR_TEST_DIRECTORY / params[0], params[1]
        )
        data: None = operator.remove_directories(params[2], params[3])

        assert data is None

        verify_delete_operation(f"/directory/delete/test{index}")
