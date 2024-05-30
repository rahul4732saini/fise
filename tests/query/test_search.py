"""
Tests the search query with different test cases.
"""

import sys
import random
from pathlib import Path

import pandas as pd
from fise.query import QueryHandler


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
    def test_basic_search_query_syntax(test_directory: Path) -> None:
        """
        Tests the validity of query syntax with uppercase and lowercase characters.
        """
        _handle_query(f"select * from '{test_directory}'")
        _handle_query(f"SELECT * FROM '{test_directory}'")

        # Explicitly mentions the file search operation and tests once for all fields.
        _handle_query(f"select[type file] * from '{test_directory}'")
        _handle_query(f"SELECT[TYPE FILE] * FROM '{test_directory}'")

    @staticmethod
    def test_recursive_search(
        test_directory: Path, recursion_options: tuple[str, ...]
    ) -> None:
        """Tests the recursive operator in file search query."""

        for i in recursion_options:
            _handle_query(f"{i} select * from '{test_directory}'")

    @staticmethod
    def test_search_with_different_path_types(
        test_directory: Path, path_types: tuple[str, ...]
    ) -> None:
        """Tests the file search query with different path types."""

        for type_ in path_types:
            _handle_query(f"r select * from {type_} '{test_directory}'")

    @staticmethod
    def test_search_with_individual_fields(
        test_directory: Path, file_fields: tuple[str, ...]
    ) -> None:
        """Tests the file search query with individual fields."""

        for field in file_fields:
            _handle_query(f"select {field} from '{test_directory}'")
            _handle_query(f"select {field.upper()} from '{test_directory}'")

    def test_size_field_width_different_params(self, test_directory: Path) -> None:
        """Tests the size field in the search query with different size unit parameters."""

        for unit in self._size_units:
            _handle_query(f"select size[{unit}] from '{test_directory}'")

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
            _handle_query(f"select {', '.join(fields)} from '{test_directory}'")

    @staticmethod
    def test_export_to_file(
        test_directory: Path, test_export_files: tuple[Path, ...]
    ) -> None:
        """Tests exporting file search records to files."""

        for file in test_export_files:
            _handle_query(f"export '{file}' select * from '{test_directory}'")

            # Verifies whether the export was successful.
            assert file.exists()
            file.unlink()

    @staticmethod
    def test_search_conditions_with_comparison_operators(test_directory: Path) -> None:
        """Tests the file search conditions with comparison operators."""

        _handle_query(
            f"r select * from '{test_directory}' where atime > '2000-01-05' "
            "or ctime < '1988-02-10' and size >= 0 and size[KB] < 1"
        )
        _handle_query(
            f"SELECT * FROM '{test_directory}' WHERE NAME = 'main.py' "
            "and PERMS != 16395 or MTIME <= '2024-06-05' and SIZE[Kib] < 1"
        )

        if sys.platform != "win32":
            _handle_query(
                f"select * from '{test_directory}' where owner = 'none' and group != 'unknown'"
            )

    @staticmethod
    def test_search_conditions_with_conditional_operators(test_directory: Path) -> None:
        """Tests the file search conditions with conditional operators."""

        _handle_query(
            rf"select * from '{test_directory}' where name like '^.*.\.py$' and ctime "
            "between ('1998-02-20', '2024-06-03') or mtime in ('2024-05-24', '2022-08-13')"
        )
        _handle_query(
            rf"SELECT * FROM '{test_directory}' WHERE NAME LIKE '^.*.\.py' "
            "OR ATIME BETWEEN ('1998-07-27', '2001-12-30')"
        )

    @staticmethod
    def test_nested_search_conditions(test_directory: Path) -> None:
        """Tests the file search query with nested search conditions."""

        _handle_query(
            rf"select * from '{test_directory}' where name like '^.*\.py$' and (size[KB] "
            "between (10, 100) or size[KiB] between (800, 1000)) and ctime > '2020-05-15'"
        )
        _handle_query(
            rf"R SELECT * FROM '{test_directory}' WHERE PATH LIKE '^.*/Software/.*$' AND "
            r"(NAME IN ('main.py', 'array.py', 'random.py') OR NAME LIKE '^.*\.js$') AND "
            "MTIME BETWEEN ('2022-12-07', '2024-07-03')"
        )


class TestTextDataSearchQuery:
    """
    Tests the text data search query with different test cases.
    """

    @staticmethod
    def test_basic_query_syntax(text_test_directory: Path) -> None:
        """
        Tests basic text data search query syntax with uppercase and lowercase characters.
        """

        for query in (
            f"select[type data] * from '{text_test_directory}'",
            f"SELECT[TYPE DATA] * FROM '{text_test_directory}'",
            f"select[type data, mode text] * from '{text_test_directory}'",
            f"SELECT[TYPE DATA, MODE TEXT] * FROM '{text_test_directory}'",
        ):
            _handle_query(query)

    @staticmethod
    def test_individual_search_fields(
        data_fields: tuple[str, ...], text_test_directory: Path
    ) -> None:
        """Tests the text data search query with individual fields."""

        for field in data_fields:
            _handle_query(f"select[type data] {field} from '{text_test_directory}'")
            _handle_query(
                f"select[type data] {field.upper()} from '{text_test_directory}'"
            )

    @staticmethod
    def test_multiple_search_field_patterns(
        data_fields: tuple[str, ...], text_test_directory: Path
    ) -> None:
        """Tests the text data search query with multiple field patterns."""

        for fields in (
            random.choices(data_fields, k=random.choice(range(1, 5))) for _ in range(5)
        ):
            for query in (
                f"select[type data] {', '.join(fields)} from '{text_test_directory}'",
                f"SELECT[TYPE DATA] {', '.join(fields)} FROM '{text_test_directory}'",
            ):
                _handle_query(query)

    @staticmethod
    def test_export_to_file(
        text_test_directory: Path, test_export_files: tuple[Path, ...]
    ) -> None:
        """Tests exporting text data search records to different file types."""

        for file in test_export_files:
            _handle_query(
                f"export '{file}' select[type data] * from '{text_test_directory}'"
            )

            # Verifies whether the export was successful.
            assert file.exists()
            file.unlink()

    @staticmethod
    def test_recursive_search(
        text_test_directory: Path, recursion_options: tuple[str, ...]
    ) -> None:
        """Tests the recursive operator in text data search query."""

        for i in recursion_options:
            _handle_query(f"{i} select[type data] * from '{text_test_directory}'")

    @staticmethod
    def test_search_with_different_path_types(
        text_test_directory: Path, path_types: tuple[str, ...]
    ) -> None:
        """Tests the text data search query with different path types."""

        for type_ in path_types:
            _handle_query(f"select[type data] * from {type_} '{text_test_directory}'")

    @staticmethod
    def test_search_conditions_with_comparison_operators(
        text_test_directory: Path,
    ) -> None:
        """Tests the text data search query conditions with comparison operators."""

        _handle_query(
            f"select[type data] * from '{text_test_directory}' "
            "where name = 'Lorem.txt' and lineno != 5"
        )
        _handle_query(
            f"SELECT[TYPE DATA] * FROM '{text_test_directory}' "
            "WHERE NAME = 'ML.txt' OR NAME = 'Lorem.txt'"
        )

    @staticmethod
    def test_search_conditions_with_conditional_operators(
        text_test_directory: Path,
    ) -> None:
        """Tests the text data search query conditions with conditional operators."""

        _handle_query(
            f"select[type data] * from '{text_test_directory}' where name like "
            "'^(Lorem|ML).txt$' and path like '^.*/test_directory/Text/.*$'"
        )
        _handle_query(
            f"SELECT[TYPE DATA] * FROM '{text_test_directory}' WHERE NAME IN ('Lorem.txt',"
            " 'ML.txt') AND LINENO BETWEEN (1, 24) AND DATA LIKE '^Lorem.*$'"
        )

    @staticmethod
    def test_nested_search_conditions(text_test_directory: Path) -> None:
        """Tests the data search query with nested conditions."""

        _handle_query(
            f"select[type data] * from '{text_test_directory}' where (name = 'M1.txt'"
            " or name = 'Lorem.txt') and path like '^.*/Text/.*$' and lineno = 15"
        )
        _handle_query(
            f"SELECT[TYPE DATA] * FROM '{text_test_directory}' WHERE (DATA LIKE '^Lorem.*$'"
            " OR DATA LIKE '^netus.*$') AND NAME = 'Lorem.txt' AND LINENO BETWEEN (1, 50)"
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
    def test_basic_query_syntax(binary_test_directory: Path) -> None:
        """
        Tests basic binary data search query syntax with uppercase and lowercase characters.
        """

        for query in (
            f"select[type data, mode bytes] * from '{binary_test_directory}'",
            f"SELECT[TYPE DATA, MODE BYTES] * FROM '{binary_test_directory}'",
        ):
            _handle_query(query)

    @staticmethod
    def test_individual_search_fields(
        data_fields: tuple[str, ...], binary_test_directory: Path
    ) -> None:
        """Tests the binary data search query with individual fields."""

        for field in data_fields:
            for query in (
                f"select[type data, mode bytes] {field} from '{binary_test_directory}'",
                f"select[type data, mode bytes] {field.upper()} from '{binary_test_directory}'",
            ):
                _handle_query(query)

    @staticmethod
    def test_multiple_search_field_patterns(
        data_fields: tuple[str, ...], binary_test_directory: Path
    ) -> None:
        """Tests the binary data search query with multiple field patterns."""

        for fields in (
            random.choices(data_fields, k=random.choice(range(1, 5))) for _ in range(5)
        ):
            for query in (
                f"select[type data, mode bytes] {', '.join(fields)} from '{binary_test_directory}'",
                f"SELECT[TYPE DATA, MODE BYTES] {', '.join(fields)} FROM '{binary_test_directory}'",
            ):
                _handle_query(query)

    @staticmethod
    def test_export_to_file(
        binary_test_directory: Path, test_export_files: tuple[Path, ...]
    ) -> None:
        """Tests exporting binary data search records to different file types."""

        for file in test_export_files:
            _handle_query(
                f"export '{file}' select[type data, mode bytes] * from '{binary_test_directory}'"
            )

            # Verifies whether the export was successful.
            assert file.exists()
            file.unlink()

    @staticmethod
    def test_recursive_search(
        binary_test_directory: Path, recursion_options: tuple[str, ...]
    ) -> None:
        """Tests the recursive operator in binary data search query."""

        for i in recursion_options:
            _handle_query(
                f"{i} select[type data, mode bytes] * from '{binary_test_directory}'"
            )

    @staticmethod
    def test_search_with_different_path_types(
        binary_test_directory: Path, path_types: tuple[str, ...]
    ) -> None:
        """Tests the binary data search query with different path types."""

        for type_ in path_types:
            _handle_query(
                f"select[type data, mode bytes] * from {type_} '{binary_test_directory}'"
            )

    @staticmethod
    def test_search_conditions_with_comparison_operators(
        binary_test_directory: Path,
    ) -> None:
        """Tests the binary data search query conditions with comparison operators."""

        _handle_query(
            f"select[type data, mode bytes] * from '{binary_test_directory}' "
            "where name = 'Lorem.txt' and lineno != 5"
        )
        _handle_query(
            f"SELECT[TYPE DATA, MODE BYTES] * FROM '{binary_test_directory}' "
            "WHERE NAME = 'ML.txt' OR NAME = 'Lorem.txt' AND LINENO = 10"
        )

    @staticmethod
    def test_search_conditions_with_conditional_operators(
        binary_test_directory: Path,
    ) -> None:
        """Tests the binary data search query conditions with conditional operators."""

        _handle_query(
            f"select[type data, mode bytes] * from '{binary_test_directory}' where "
            "name like '^(Lorem|ML).txt$' and path like '^.*/test_directory/Text/.*$'"
        )
        _handle_query(
            f"SELECT[TYPE DATA, MODE BYTES] * FROM '{binary_test_directory}' WHERE NAME IN "
            "('Lorem.txt', 'ML.txt') AND LINENO BETWEEN (1, 24) AND DATA LIKE '^Lorem.*$'"
        )

    @staticmethod
    def test_nested_search_conditions(binary_test_directory: Path) -> None:
        """Tests the binary data search query with nested conditions."""

        _handle_query(
            f"select[type data, mode bytes] * from '{binary_test_directory}' where (name = "
            "'M1.txt' or name = 'Lorem.txt') and path like '^.*/Text/.*$' and lineno = 15"
        )
        _handle_query(
            f"SELECT[TYPE DATA, MODE BYTES] * FROM '{binary_test_directory}' WHERE (DATA LIKE "
            "'^Lorem.*$' OR DATA LIKE '^netus.*$') AND NAME = 'Lorem.txt' AND LINENO BETWEEN (1, 50)"
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
    def test_basic_query_syntax(test_directory: Path) -> None:
        """
        Tests basic directory search query syntax with uppercase and lowercase characters.
        """
        _handle_query(f"select[type dir] * from '{test_directory}'")
        _handle_query(f"SELECT[TYPE DIR] * FROM '{test_directory}'")

    @staticmethod
    def test_individual_search_fields(
        test_directory: Path, dir_fields: tuple[str, ...]
    ) -> None:
        """Tests the directory search query with individual fields."""

        for field in dir_fields:
            _handle_query(f"select[type dir] {field} from '{test_directory}'")
            _handle_query(f"select[type dir] {field.upper()} from '{test_directory}'")

    @staticmethod
    def test_multiple_search_field_patterns(
        test_directory: Path, dir_fields: tuple[str, ...]
    ) -> None:
        """Tests the directory search query with multiple field patterns."""

        dir_fields += ("*",)

        for fields in (
            random.choices(dir_fields, k=random.choice(range(1, 5))) for _ in range(5)
        ):
            _handle_query(
                f"select[type dir] {','.join(fields)} from '{test_directory}'"
            )
            _handle_query(
                f"select[type dir] {', '.join(fields)} from '{test_directory}'"
            )

    @staticmethod
    def test_recursive_search(
        test_directory: Path, recursion_options: tuple[str, ...]
    ) -> None:
        """Tests the recursive operator in directory search query."""

        for i in recursion_options:
            _handle_query(f"{i} select * from '{test_directory}'")

    @staticmethod
    def test_search_with_different_path_types(
        test_directory: Path, path_types: tuple[str, ...]
    ) -> None:
        """Tests the directory search query with different path types."""

        for type_ in path_types:
            _handle_query(f"r select[type dir] * from {type_} '{test_directory}'")

    @staticmethod
    def test_export_to_file(
        test_directory: Path, test_export_files: tuple[Path, ...]
    ) -> None:
        """Tests exporting directory search records to different file types."""

        for file in test_export_files:
            _handle_query(f"export '{file}' select[type dir] * from '{test_directory}'")

            # Verifies whether the export was successful.
            assert file.exists()
            file.unlink()

    @staticmethod
    def test_search_conditions_with_comparison_operators(test_directory: Path) -> None:
        """Tests the directory search query conditions with comparison operators."""

        _handle_query(
            f"select[type dir] * from '{test_directory}' where name = 'Software'"
        )
        _handle_query(
            f"SELECT[TYPE DIR] * FROM '{test_directory}' WHERE NAME = "
            "'Media' OR NAME = 'Archive' AND PERMS = 16395"
        )

        if sys.platform != "win32":
            _handle_query(
                f"select[type dir] * from '{test_directory}' where name = "
                "'Documents' and owner = 'none' and group != 'unknown'"
            )

    @staticmethod
    def test_search_conditions_with_conditional_operators(test_directory: Path) -> None:
        """Tests the directory search query conditions with conditional operators."""

        _handle_query(
            f"select[type dir] * from '{test_directory}' where name like "
            "'^(Documents|Software)$' and path like '^.*/test_directory/.*$' "
            "and parent in ('test_directory', 'tests', 'archive')"
        )
        _handle_query(
            f"SELECT[TYPE DIR] * FROM '{test_directory}' WHERE NAME IN ('Software',"
            " 'Documents', 'Archive') AND PARENT LIKE '^.*/test_directory'"
        )

    @staticmethod
    def test_nested_search_conditions(test_directory: Path) -> None:
        """Tests the directory search query with nested conditions."""

        _handle_query(
            f"select[type dir] * from '{test_directory}' where (name ="
            " 'Software' and parent like '^.*/test_directory')"
        )
        _handle_query(
            f"SELECT[TYPE DIR] * FROM '{test_directory}' WHERE (PATH LIKE '^.*/Documents/.*$'"
            " OR PATH LIKE '^.*/Software/.*$') AND NAME IN ('Libraries', 'Meeting_Notes')"
        )

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
