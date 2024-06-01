"""
Tests the delete query with different test cases.
"""

from pathlib import Path
import pytest
from query_utils import eval_delete_query


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
