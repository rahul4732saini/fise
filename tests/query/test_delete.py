"""
Tests the delete query with different test cases.
"""

import functools
from pathlib import Path
from typing import Literal

import pytest
import pandas as pd

from query_utils import eval_delete_query, reset_test_directory, read_delete_record


def _handle_test_case(func):
    """Handles the specified delete query test case."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> pd.DataFrame | None:
        try:
            data: pd.DataFrame | None = func(*args, **kwargs)

        except Exception as error:
            reset_test_directory()

            # Raises the error after resetting the test directory
            # to make the test cases marked `FAILED`.
            raise error

        else:
            return data

    return wrapper


def match_delete_records(
    test_directory_contents: list[Path],
    records_path: str,
    type_: Literal["file", "dir"] = "file",
) -> None:
    """
    Matches the existence of the files and directories present within the test
    directory based on the delete records extracted from the specified `records_path`
    comprising the files/directories deleted during the delete opertion.
    """

    records: set[Path] = read_delete_record(records_path)

    for path in test_directory_contents:

        # Creates the path if not in existence and is
        # a part of the deleted file/directory records.
        if path in records:
            assert not path.exists()
            path.touch() if type_ == "file" else path.mkdir()

            continue

        # Asserts the path existence if it isn't a part of the delete query.
        assert path.exists()


class TestFileDeleteQuery:
    """
    Tests the file delete query with different test cases.
    """

    @staticmethod
    @pytest.mark.parametrize("ucase", (True, False))
    def test_basic_query_syntax(test_directory: Path, ucase: bool) -> None:
        """
        Tests basic syntax for file delete query.
        """
        eval_delete_query(test_directory, ucase=ucase)
        eval_delete_query(test_directory, oparams="type file", ucase=ucase)

    @staticmethod
    @pytest.mark.parametrize("ucase", (True, False))
    def test_recursive_delete(
        test_directory: Path, recursion_options: tuple[str, ...], ucase: bool
    ) -> None:
        """
        Tests the recursive operator in file delete query.
        """
        for i in recursion_options:
            eval_delete_query(test_directory / "Media", recur=i, ucase=ucase)

    @staticmethod
    @pytest.mark.parametrize("ucase", (True, False))
    def test_delete_query_path_types(
        test_directory: Path, path_types: tuple[str, ...], ucase: bool
    ):
        """
        Tests the file delete query with different path types.
        """
        for i in path_types:
            eval_delete_query(test_directory, path_type=i, ucase=ucase)

    @staticmethod
    @pytest.mark.parametrize("conditions", ())
    def test_query_conditions_with_comparison_operators(
        test_directory: Path, conditions: str
    ) -> None:
        """
        Tests the file delete query conditions with comparison operators.
        """
        eval_delete_query(test_directory, conditions=conditions)

    @staticmethod
    @pytest.mark.parametrize("conditions", ())
    def test_query_conditions_with_conditional_operators(
        test_directory: Path, conditions: str
    ) -> None:
        """
        Tests the file delete query conditions with conditional operators.
        """
        eval_delete_query(test_directory, conditions=conditions)

    @staticmethod
    @pytest.mark.parametrize("conditions", ())
    def test_nested_query_conditions(test_directory: Path, conditions: str) -> None:
        """
        Tests the file delete query with nested conditions.
        """
        eval_delete_query(test_directory, conditions=conditions)
