"""
Tests the search query with different test cases.
"""

import sys
import random
from pathlib import Path

import pytest
import pandas as pd

from fise.query import QueryHandler
from query_utils import eval_search_query


def _handle_query(query: str) -> pd.DataFrame | None:
    """Handles the specified query."""
    return QueryHandler(query).handle()


class TestFileSearchQuery:
    """
    Tests the file search query with different test cases.
    """

    # fmt: off
    _size_units = (
        "b", "B", "Kb", "KB", "Kib", "KiB", "Mb", "MB", "Mib",
        "MiB", "Gb", "GB", "Gib", "GiB", "Tb", "TB", "Tib", "TiB"
    )
    # fmt: on

    @staticmethod
    @pytest.mark.parametrize("ucase", (True, False))
    def test_basic_search_query_syntax(test_directory: Path, ucase: bool) -> None:
        """
        Tests the validity of query syntax.
        """
        eval_search_query(test_directory, ucase=ucase)

        # Explicitly mentions the file search operation and tests once for all fields.
        eval_search_query(test_directory, oparams="type file", ucase=ucase)

    @staticmethod
    @pytest.mark.parametrize("ucase", (True, False))
    def test_recursive_search(
        test_directory: Path, recursion_options: tuple[str, ...], ucase: bool
    ) -> None:
        """Tests the recursive operator in file search query."""

        for i in recursion_options:
            eval_search_query(test_directory, recur=i, ucase=ucase)

    @staticmethod
    @pytest.mark.parametrize("ucase", (True, False))
    def test_search_with_different_path_types(
        test_directory: Path, path_types: tuple[str, ...], ucase: bool
    ) -> None:
        """Tests the file search query with different path types."""

        for type_ in path_types:
            eval_search_query(test_directory, path_type=type_, ucase=ucase)

    @staticmethod
    def test_search_with_individual_fields(
        test_directory: Path, file_fields: tuple[str, ...]
    ) -> None:
        """Tests the file search query with individual fields."""

        for field in file_fields:
            eval_search_query(test_directory, fields=field)
            eval_search_query(test_directory, fields=field.upper())

    def test_size_field_width_different_params(self, test_directory: Path) -> None:
        """Tests the size field in the search query with different size unit parameters."""

        for unit in self._size_units:
            eval_search_query(test_directory, fields=f"size[{unit}]")

    @staticmethod
    def test_search_with_multiple_fields(
        test_directory: Path, file_fields: tuple[str, ...]
    ) -> None:
        """Tests the file search query with multiple field patterns."""

        # Adds `*` to also test with all fields together.
        file_fields += ("*",)

        for fields in (
            random.choices(file_fields, k=random.choice(range(1, 5))) for _ in range(5)
        ):
            eval_search_query(test_directory, fields=f"{', '.join(fields)}")

    @staticmethod
    def test_export_to_file(
        test_directory: Path, test_export_files: tuple[Path, ...]
    ) -> None:
        """Tests exporting file search records to files."""

        for file in test_export_files:
            eval_search_query(test_directory, export=f"'{file}'")

            # Verifies whether the export was successful.
            assert file.exists()
            file.unlink()

    @staticmethod
    @pytest.mark.parametrize(
        "conditions",
        (
            r"atime > '2000-01-05' or ctime < '1988-02-10' and size >= 0 and size[KB] < 1",
            r"NAME = 'main.py' AND PERMS != 16395 OR MTIME <= '2024-06-05' AND SIZE[Kib] < 1",
        ),
    )
    def test_search_conditions_with_comparison_operators(
        test_directory: Path, conditions: str
    ) -> None:
        """Tests the file search conditions with comparison operators."""
        eval_search_query(test_directory, recur="r", conditions=conditions)

    @staticmethod
    @pytest.mark.parametrize(
        "conditions",
        [
            r"size[Mib] < 1 and owner = 'none' and group != 'unknown'",
            r"OWNER != 'ArchUser' AND GROUP = 'FiSE-dev'",
        ],
    )
    def test_posix_search_conditions(test_directory: Path, conditions: str) -> None:
        """
        Tests the file search conditions with additional fields for Posix based systems.
        """
        if sys.platform == "win32":
            return

        eval_search_query(test_directory, conditions=conditions)

    @staticmethod
    @pytest.mark.parametrize(
        "conditions",
        [
            r"name like '^.*.\.py$' and ctime between ('1998-02-20', '2024-06-03')",
            r"NAME LIKE '^.*.\.py' OR ATIME BETWEEN ('1998-07-27', '2001-12-30')",
        ],
    )
    def test_search_conditions_with_conditional_operators(
        test_directory: Path, conditions: str
    ) -> None:
        """Tests the file search conditions with conditional operators."""
        eval_search_query(test_directory, conditions=conditions)

    @staticmethod
    @pytest.mark.parametrize(
        "conditions",
        [
            r"(size[KB] between (10, 100) or size[KiB] between (800, 1000)) and name = 'main.py'",
            r"path LIKE '^.*/Media/.*$' AND name IN ('main.py', 'array.py') OR NAME LIKE '^.*\.js$')",
        ],
    )
    def test_nested_search_conditions(test_directory: Path, conditions: str) -> None:
        """Tests the file search query with nested search conditions."""
        eval_search_query(test_directory, conditions=conditions)


class TestTextDataSearchQuery:
    """
    Tests the text data search query with different test cases.
    """

    @staticmethod
    @pytest.mark.parametrize("oparams", ("type data", "type data, mode text"))
    def test_basic_query_syntax(text_test_directory: Path, oparams: str) -> None:
        """
        Tests basic text data search query syntax with uppercase and lowercase characters.
        """
        eval_search_query(text_test_directory, oparams=oparams)
        eval_search_query(text_test_directory, oparams=oparams, ucase=True)

    @staticmethod
    @pytest.mark.parametrize("ucase", (True, False))
    def test_recursive_search(
        text_test_directory: Path, recursion_options: tuple[str, ...], ucase: bool
    ) -> None:
        """Tests the recursive operator in text data search query."""

        for i in recursion_options:
            eval_search_query(
                text_test_directory, recur=i, oparams="type data", ucase=ucase
            )

    @staticmethod
    @pytest.mark.parametrize("ucase", (True, False))
    def test_search_with_different_path_types(
        text_test_directory: Path, path_types: tuple[str, ...], ucase: bool
    ) -> None:
        """Tests the text data search query with different path types."""

        for type_ in path_types:
            eval_search_query(text_test_directory, path_type=type_, oparams="type data")

    @staticmethod
    def test_individual_search_fields(
        data_fields: tuple[str, ...], text_test_directory: Path
    ) -> None:
        """Tests the text data search query with individual fields."""

        for field in data_fields:
            eval_search_query(text_test_directory, fields=field, oparams="type data")
            eval_search_query(
                text_test_directory, fields=field.upper(), oparams="type data"
            )

    @staticmethod
    def test_multiple_search_field_patterns(
        data_fields: tuple[str, ...], text_test_directory: Path
    ) -> None:
        """Tests the text data search query with multiple field patterns."""

        for fields in (
            random.choices(data_fields, k=random.choice(range(1, 5))) for _ in range(5)
        ):
            eval_search_query(
                text_test_directory, ", ".join(fields), oparams="type data"
            )

    @staticmethod
    def test_export_to_file(
        text_test_directory: Path, test_export_files: tuple[Path, ...]
    ) -> None:
        """Tests exporting text data search records to different file types."""

        for file in test_export_files:
            eval_search_query(
                text_test_directory, export=f"'{file}'", oparams="type data"
            )

            # Verifies whether the export was successful.
            assert file.exists()
            file.unlink()

    @staticmethod
    @pytest.mark.parametrize(
        "conditions",
        (
            r"name = 'Lorem.txt' and lineno != 5",
            r"NAME = 'ML.txt' OR NAME = 'Lorem.txt'",
        ),
    )
    def test_search_conditions_with_comparison_operators(
        text_test_directory: Path, conditions: str
    ) -> None:
        """Tests the text data search query conditions with comparison operators."""
        eval_search_query(
            text_test_directory, oparams="type data", conditions=conditions
        )

    @staticmethod
    @pytest.mark.parametrize(
        "conditions",
        (
            r"name like '^(Lorem|ML).txt$' and path like '^.*/test_directory/Text/.*$'",
            r"NAME IN ('Lorem.txt', 'ML.txt') AND LINENO BETWEEN (1, 24) AND DATA LIKE '^Lorem.*$'",
        ),
    )
    def test_search_conditions_with_conditional_operators(
        text_test_directory: Path, conditions: str
    ) -> None:
        """Tests the text data search query conditions with conditional operators."""
        eval_search_query(
            text_test_directory, oparams="type data", conditions=conditions
        )

    @staticmethod
    @pytest.mark.parametrize(
        "conditions",
        (
            r"(name = 'M1.txt' or name = 'Lorem.txt') and path like '^.*/Text/.*$'",
            r"(DATA LIKE '^Lorem.*$' OR DATA LIKE '^netus.*$') AND NAME = 'Lorem.txt'",
        ),
    )
    def test_nested_search_conditions(
        text_test_directory: Path, conditions: str
    ) -> None:
        """Tests the data search query with nested conditions."""
        eval_search_query(
            text_test_directory, oparams="type data", conditions=conditions
        )

    @staticmethod
    def miscellaneous_tests(
        text_test_directory: Path, test_export_files: tuple[Path, ...]
    ) -> None:
        """Tests various aspects of the text data search query."""

        for file in test_export_files:
            _handle_query(
                f"EXPORT '{file}' r SELECT[Type Data] * from ABSOlUTE '{text_test_directory}'"
                " WHERE name IN ('Lorem.txt', 'ML.txt') AND LINENO in (1, 13, 10, 7)"
            )

            # Verifies whether the export was successful.
            assert file.exists()
            file.unlink()


class TestBinaryDataSearchQuery:
    """
    Tests the binary data search query with different test cases.
    """

    @staticmethod
    @pytest.mark.parametrize("ucase", (True, False))
    def test_basic_query_syntax(binary_test_directory: Path, ucase: bool) -> None:
        """
        Tests basic binary data search query syntax with uppercase and lowercase characters.
        """
        eval_search_query(
            binary_test_directory, oparams="type data, mode bytes", ucase=ucase
        )

    @staticmethod
    @pytest.mark.parametrize("ucase", (True, False))
    def test_recursive_search(
        binary_test_directory: Path, recursion_options: tuple[str, ...], ucase: bool
    ) -> None:
        """Tests the recursive operator in binary data search query."""

        for i in recursion_options:
            eval_search_query(
                binary_test_directory, oparams="type data, mode bytes", recur=i
            )

    @staticmethod
    @pytest.mark.parametrize("ucase", (True, False))
    def test_search_with_different_path_types(
        binary_test_directory: Path, path_types: tuple[str, ...], ucase: bool
    ) -> None:
        """Tests the binary data search query with different path types."""

        for type_ in path_types:
            eval_search_query(
                binary_test_directory, oparams="type data, mode bytes", path_type=type_
            )

    @staticmethod
    def test_individual_search_fields(
        data_fields: tuple[str, ...], binary_test_directory: Path
    ) -> None:
        """Tests the binary data search query with individual fields."""

        for field in data_fields:
            eval_search_query(
                binary_test_directory, oparams="type data, mode bytes", fields=field
            )
            eval_search_query(
                binary_test_directory,
                oparams="type data, mode bytes",
                fields=field.upper(),
            )

    @staticmethod
    def test_multiple_search_field_patterns(
        data_fields: tuple[str, ...], binary_test_directory: Path
    ) -> None:
        """Tests the binary data search query with multiple field patterns."""

        for fields in (
            random.choices(data_fields, k=random.choice(range(1, 5))) for _ in range(5)
        ):
            eval_search_query(
                binary_test_directory,
                oparams="type data, mode bytes",
                fields=", ".join(fields),
            )

    @staticmethod
    def test_export_to_file(
        binary_test_directory: Path, test_export_files: tuple[Path, ...]
    ) -> None:
        """Tests exporting binary data search records to different file types."""

        for file in test_export_files:
            eval_search_query(
                binary_test_directory,
                oparams="type data, mode bytes",
                export=f"'{file}'",
            )

            # Verifies whether the export was successful.
            assert file.exists()
            file.unlink()

    @staticmethod
    @pytest.mark.parametrize(
        "conditions",
        (
            r"name = 'Lorem.txt' and lineno != 5",
            r"NAME = 'ML.txt' OR NAME = 'Lorem.txt' AND LINENO = 10",
        ),
    )
    def test_search_conditions_with_comparison_operators(
        binary_test_directory: Path, conditions: str
    ) -> None:
        """Tests the binary data search query conditions with comparison operators."""
        eval_search_query(
            binary_test_directory,
            oparams="type data, mode bytes",
            conditions=conditions,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "conditions",
        (
            r"name like '^(Lorem|ML).txt$' and path like '^.*/test_directory/Text/.*$'",
            r"NAME IN ('Lorem.txt', 'ML.txt') AND LINENO BETWEEN (1, 24) AND DATA LIKE '^Lorem.*$'",
        ),
    )
    def test_search_conditions_with_conditional_operators(
        binary_test_directory: Path, conditions: str
    ) -> None:
        """Tests the binary data search query conditions with conditional operators."""
        eval_search_query(
            binary_test_directory,
            oparams="type data, mode bytes",
            conditions=conditions,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "conditions",
        (
            r"(name = 'M1.txt' or name = 'Lorem.txt') and path like '^.*/Text/.*$' and lineno = 15",
            r"(DATA LIKE '^Lorem.*$' OR DATA LIKE '^netus.*$') AND LINENO BETWEEN (1, 50)",
        ),
    )
    def test_nested_search_conditions(
        binary_test_directory: Path, conditions: str
    ) -> None:
        """Tests the binary data search query with nested conditions."""
        eval_search_query(
            binary_test_directory,
            oparams="type data, mode bytes",
            conditions=conditions,
        )

    @staticmethod
    def miscellaneous_tests(
        binary_test_directory: Path, test_export_files: tuple[Path, ...]
    ) -> None:
        """Tests various aspects of the binary data search query."""

        for file in test_export_files:
            _handle_query(
                f"EXPORT '{file}' r SELECT[Type Data, MODE Bytes] * from "
                f"ABSOlUTE '{binary_test_directory}' WHERE name IN ('Lorem.txt', "
                "'ML.txt') AND LINENO in (1, 13, 10, 7)"
            )

            # Verifies whether the export was successful.
            assert file.exists()
            file.unlink()


class TestDirSearchQuery:
    """
    Tests the directory search query with different test cases.
    """

    @staticmethod
    @pytest.mark.parametrize("ucase", (True, False))
    def test_basic_query_syntax(test_directory: Path, ucase: bool) -> None:
        """
        Tests basic directory search query syntax with uppercase and lowercase characters.
        """
        eval_search_query(test_directory, oparams="type dir", ucase=True)

    @staticmethod
    @pytest.mark.parametrize("ucase", (True, False))
    def test_recursive_search(
        test_directory: Path, recursion_options: tuple[str, ...], ucase: bool
    ) -> None:
        """Tests the recursive operator in directory search query."""

        for i in recursion_options:
            eval_search_query(test_directory, recur=i)

    @staticmethod
    @pytest.mark.parametrize("ucase", (True, False))
    def test_search_with_different_path_types(
        test_directory: Path, path_types: tuple[str, ...], ucase: bool
    ) -> None:
        """Tests the directory search query with different path types."""

        for type_ in path_types:
            eval_search_query(test_directory, oparams="type dir", path_type=type_)

    @staticmethod
    def test_individual_search_fields(
        test_directory: Path, dir_fields: tuple[str, ...]
    ) -> None:
        """Tests the directory search query with individual fields."""

        for field in dir_fields:
            eval_search_query(test_directory, fields=field, oparams="type dir")
            eval_search_query(test_directory, fields=field.upper(), oparams="type dir")

    @staticmethod
    def test_multiple_search_field_patterns(
        test_directory: Path, dir_fields: tuple[str, ...]
    ) -> None:
        """Tests the directory search query with multiple field patterns."""

        dir_fields += ("*",)

        for fields in (
            random.choices(dir_fields, k=random.choice(range(1, 5))) for _ in range(5)
        ):
            eval_search_query(
                test_directory, fields=", ".join(fields), oparams="type dir"
            )

    @staticmethod
    def test_export_to_file(
        test_directory: Path, test_export_files: tuple[Path, ...]
    ) -> None:
        """Tests exporting directory search records to different file types."""

        for file in test_export_files:
            eval_search_query(test_directory, oparams="type dir", export=f"'{file}'")

            # Verifies whether the export was successful.
            assert file.exists()
            file.unlink()

    @staticmethod
    def test_search_conditions_with_comparison_operators(test_directory: Path) -> None:
        """Tests the directory search query conditions with comparison operators."""

        eval_search_query(
            test_directory,
            oparams="type dir",
            recur="r",
            conditions="name = 'Software'",
        )
        eval_search_query(
            test_directory,
            oparams="type dir",
            recur="r",
            conditions="NAME = 'Media' OR NAME = 'Archive' AND PERMS = 16395",
        )

        if sys.platform != "win32":
            eval_search_query(
                test_directory,
                oparams="type dir",
                recur="r",
                conditions="name = 'Documents' and owner = 'none' and group != 'unknown'",
            )

    @staticmethod
    @pytest.mark.parametrize(
        "conditions",
        (
            r"name like '^(Documents|Software)$'and parent in ('test_directory', 'tests')",
            r"NAME IN ('Software', 'Documents') AND PARENT LIKE '^.*/test_directory'",
        ),
    )
    def test_search_conditions_with_conditional_operators(
        test_directory: Path, conditions: str
    ) -> None:
        """Tests the directory search query conditions with conditional operators."""
        eval_search_query(test_directory, oparams="type dir", conditions=conditions)

    @staticmethod
    @pytest.mark.parametrize(
        "conditions",
        (
            r"(name = 'Software' and parent like '^.*/test_directory')",
            r"(PATH LIKE '^.*/Media/.*$' OR PATH LIKE '^.*/Docs/.*$')",
        ),
    )
    def test_nested_search_conditions(test_directory: Path, conditions: str) -> None:
        """Tests the directory search query with nested conditions."""
        eval_search_query(test_directory, oparams="type dir", conditions=conditions)

    @staticmethod
    def miscellaneous_tests(
        test_directory: Path, test_export_files: tuple[Path, ...]
    ) -> None:
        """Tests various aspects of the directory search query."""

        for file in test_export_files:
            _handle_query(
                f"EXPORT '{file}' r SELECT[Type DIR] * from ABSOlUTE '{test_directory}' WHERE name "
                "IN ('Software', 'Libraries', 'Documents', 'Music') OR pAth like '^.*(Media|Archive)'"
            )

            # Verifies whether the export was successful.
            assert file.exists()
            file.unlink()
