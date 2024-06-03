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
    comprising the files/directories deleted during the delete operation.
    """

    records: set[Path] = read_delete_record(records_path)

    for path in test_directory_contents:

        # Creates the path if not in existence and is
        # a part of the deleted file/directory records.
        if path in records:
            assert not path.exists()
            continue

        # Asserts the path existence if it isn't a part of the delete query.
        assert path.exists()

    # Resets the test directory after verification.
    reset_test_directory()


class TestFileDeleteQuery:
    """
    Tests the file delete query with different test cases.
    """

    @staticmethod
    @_handle_test_case
    @pytest.mark.parametrize("ucase", (True, False))
    def test_basic_query_syntax(
        test_directory: Path, test_directory_contents: list[Path], ucase: bool
    ) -> None:
        """
        Tests the validity of file delete query basic syntax.
        """

        for oparams in (None, "type file"):
            eval_delete_query(test_directory, oparams=oparams, ucase=ucase)
            match_delete_records(test_directory_contents, "/file/basic")

    @staticmethod
    @_handle_test_case
    @pytest.mark.parametrize("ucase", (True, False))
    def test_recursive_delete(
        test_directory: Path,
        test_directory_contents: list[Path],
        recursion_options: tuple[str, ...],
        ucase: bool,
    ) -> None:
        """
        Tests the recursive operator in file delete query.
        """
        for i in recursion_options:
            eval_delete_query(test_directory / "Media", recur=i, ucase=ucase)
            match_delete_records(test_directory_contents, "/file/recursive")

    @staticmethod
    @_handle_test_case
    @pytest.mark.parametrize("ucase", (True, False))
    def test_delete_query_path_types(
        test_directory: Path,
        test_directory_contents: list[Path],
        path_types: tuple[str, ...],
        ucase: bool,
    ):
        """
        Tests the file delete query with different path types.
        """
        for i in path_types:
            eval_delete_query(test_directory, path_type=i, ucase=ucase)
            match_delete_records(test_directory_contents, "/file/basic")

    @staticmethod
    @_handle_test_case
    @pytest.mark.parametrize(
        ("ctr", "conditions"),
        (
            (1, r"size[B] <= 1 and filetype = '.mp4'"),
            (2, r"TYPE = '.pdf' AND SIZE[KB] = 0"),
        ),
    )
    def test_query_conditions_with_comparison_operators(
        test_directory: Path,
        test_directory_contents: list[Path],
        conditions: str,
        ctr: int,
    ) -> None:
        """
        Tests the file delete query conditions with comparison operators.
        """
        eval_delete_query(test_directory, recur="r", conditions=conditions)
        match_delete_records(
            test_directory_contents, f"/file/conditions/comparison/df{ctr}"
        )

    @staticmethod
    @_handle_test_case
    @pytest.mark.parametrize(
        ("ctr", "conditions"),
        (
            (1, r"name like '^report.*\.pdf$' and size[B] between (0, 100)"),
            (2, r"TYPE = '.docx' AND NAME LIKE '^.*Report.docx$'"),
        ),
    )
    def test_query_conditions_with_conditional_operators(
        test_directory: Path,
        test_directory_contents: list[Path],
        conditions: str,
        ctr: int,
    ) -> None:
        """
        Tests the file delete query conditions with conditional operators.
        """
        eval_delete_query(test_directory, recur="r", conditions=conditions)
        match_delete_records(
            test_directory_contents, f"/file/conditions/conditional/df{ctr}"
        )

    @staticmethod
    @_handle_test_case
    @pytest.mark.parametrize(
        ("ctr", "conditions"),
        (
            (1, r"(filetype = '.pdf' or type = '.docx') and size[b] = 0"),
            (2, r"(SIZE IN (0, 1) OR SIZE BETWEEN (5, 10)) AND NAME LIKE '^.*\.xlsx$'"),
        ),
    )
    def test_nested_query_conditions(
        test_directory: Path,
        test_directory_contents: list[Path],
        conditions: str,
        ctr: int,
    ) -> None:
        """
        Tests the file delete query with nested conditions.
        """
        eval_delete_query(test_directory / "Archive", conditions=conditions)
        match_delete_records(
            test_directory_contents, f"/file/conditions/nested/df{ctr}"
        )
