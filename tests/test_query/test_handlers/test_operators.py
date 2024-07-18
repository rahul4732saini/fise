"""
This module comprises test cases for verifying
the functionality of operator classes in FiSE.
"""

from pathlib import Path
from typing import Any

import pytest
import pandas as pd

from fise.shared import File, Field, Size
from fise.common import constants
from fise.query.operators import FileQueryOperator


FILE_DIR_TEST_DIRECTORY = Path(__file__).parents[2] / "test_directory/file_dir"
TEST_RECORDS_FILE = Path(__file__).parent / "test_operators.hdf"


def read_hdf(file: str, path: str) -> pd.Series:
    """Reads records stored at the path mentioned from specified HDF5 file."""

    with pd.HDFStore(file) as store:
        return store[path]


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


class TestFileQueryOperator:
    """Tests the FileQueryOperator class"""

    def condition1(file: File) -> bool:
        return file.filetype is not None

    def condition2(file: File) -> bool:
        return not file.size

    def condition3(file: File) -> bool:
        return file.name in ("unknown.mp3", "runaway.mp3", "birthday.avi")

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

    @pytest.mark.parametrize(
        ("index", "verify", "params"), search_operation_test_params
    )
    def test_search_operation(
        self, index: int, verify: bool, params: list[Any]
    ) -> None:
        """Tests file query operator with the search operation."""

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
        Tests file query operator with the search
        operation comprising field aliases.
        """

        fields: list[Size] = [Field(constants.FILE_FIELD_ALIASES[i]) for i in params[2]]

        operator = FileQueryOperator(FILE_DIR_TEST_DIRECTORY / params[0], params[1])
        data: pd.DataFrame = operator.get_dataframe(fields, params[2], params[3])

        if verify:
            verify_search_operation(f"/file/search2/test{index}", data)
