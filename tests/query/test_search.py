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
        Tests the the validity of query syntax with uppercase and lowercase characters.
        """
        _handle_query(f"select * from '{test_directory}'")
        _handle_query(f"SELECT * FROM '{test_directory}'")

        # Explicitly mentions the file search operation and tests once for all fields.
        _handle_query(f"select[type file] * from '{test_directory}'")
        _handle_query(f"SELECT[TYPE FILE] * FROM '{test_directory}'")

    @staticmethod
    def test_recursive_search(test_directory: Path) -> None:
        """Tests the recursive operator in file search query."""

        for i in ("r", "recursive", "R", "RECURSIVE"):
            _handle_query(f"{i} select * from '{test_directory}'")

    @staticmethod
    def test_search_with_different_path_types(test_directory: Path) -> None:
        """Tests the file search query with different path types."""

        for type_ in ("absolute", "relative", "ABSOLUTE", "RELATIVE"):
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
            rf"R SELECT * FROM '{test_directory}' WHERE PATH LIKE '^.*/Sofware/.*$' AND "
            r"(NAME IN ('main.py', 'array.py', 'random.py') OR NAME LIKE '^.*\.js$') AND "
            "MTIME BETWEEN ('2022-12-07', '2024-07-03')"
        )


class TestDirSearchQuery:
    """
    Tests the data search query with different test cases.
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
    def test_recursive_search(test_directory: Path) -> None:
        """Tests the recursive operator in directory search query."""

        for i in ("r", "recursive", "R", "RECURSIVE"):
            _handle_query(f"{i} select * from '{test_directory}'")

    @staticmethod
    def test_search_with_different_path_types(test_directory: Path) -> None:
        """Tests the directory search query with different path types."""

        for type_ in ("absolute", "relative", "ABSOLUTE", "RELATIVE"):
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
        """Tests the directroy search query conditions with conditional operators."""

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
                f"EXPORT '{file}' r SELECT * from ABSOLUTE '{test_directory}' WHERE name IN "
                "('Sofware', 'Libraries', 'Documents', 'Music') OR path like '^.*(Media|Archive)'"
            )

            # Verifies whether the export was successful.
            assert file.exists()
            file.unlink()
