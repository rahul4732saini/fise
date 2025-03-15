"""
Tests Paths Module
------------------

This module defines classes and methods for testing the classes defined
within the `qeury/paths.py` module for parsing and handling file system
paths.
"""

from pathlib import Path
import pytest

from fise.common import constants
from fise.shared import QueryQueue
from fise.query.paths import QueryPathParser


# Treats the 'test' directory as the base directory for all operations.
BASE_DIR = Path(__file__).parents[1]

# The following constants store absolute and relative paths to the
# file_dir and data test directories to effectively test the query
# path parser class with different path types.

FD_TEST_DIR_ABS = BASE_DIR / "test_directory/file_dir"
FD_TEST_DIR_REL = FD_TEST_DIR_ABS.relative_to(BASE_DIR)

DATA_TEST_DIR_ABS = BASE_DIR / "test_directory/data"
DATA_TEST_DIR_REL = DATA_TEST_DIR_ABS.relative_to(BASE_DIR)

# The following constants store arguments and results
# for testing the functionalities associated with them.

QPP_VALID_TEST_ARGS = [
    (f"absolute {FD_TEST_DIR_REL / 'project'}", constants.ENTITY_FILE),
    (f"{FD_TEST_DIR_REL / 'media'}", constants.ENTITY_DIR),
    (f"relative {FD_TEST_DIR_ABS / 'docs'}", constants.ENTITY_FILE),
    (f"absolute {DATA_TEST_DIR_REL / 'todo.txt'}", constants.ENTITY_DATA),
]

QPP_VALID_TEST_RESULTS = [
    FD_TEST_DIR_ABS / "project",
    FD_TEST_DIR_ABS / "media",
    FD_TEST_DIR_ABS / "docs",
    DATA_TEST_DIR_ABS / "todo.txt",
]

QPP_INVALID_TEST_ARGS = [
    (f"absl {FD_TEST_DIR_REL}", constants.ENTITY_FILE),
    (f"relative {DATA_TEST_DIR_REL / 'specs.xlsx'}", constants.ENTITY_DATA),
    (f"{FD_TEST_DIR_ABS / 'todo.txt'}", constants.ENTITY_DATA),
    (f"rel {FD_TEST_DIR_REL}", constants.ENTITY_DIR),
]


class TestQueryPathParser:
    """Tests the `QueryPathParser` class."""

    @staticmethod
    def init_parser(query: str, entity: str) -> QueryPathParser:
        """
        Initializes the QueryPathParser class
        with the specified arguments.
        """

        queue = QueryQueue.from_string(query)
        parser = QueryPathParser(queue, entity)

        return parser

    @pytest.mark.parametrize(
        ("args", "result"),
        zip(QPP_VALID_TEST_ARGS, QPP_VALID_TEST_RESULTS),
    )
    def test_with_valid_query(self, args: tuple[str, str], result: Path) -> None:
        """Tests the parser with valid query path specifications."""

        parser = self.init_parser(*args)
        path_obj = parser.parse()

        path = path_obj.path

        if not path.is_absolute():
            path = BASE_DIR / path

        # Compares the absolute paths of the file/directory for validation.
        assert path == result

    @pytest.mark.parametrize("args", QPP_INVALID_TEST_ARGS)
    def test_with_invalid_query(self, args: tuple[str, str]) -> None:
        """Tests the parser with invalid query path specifications."""

        parser = self.init_parser(*args)

        # Unable to pass 'QueryParserError' as the error class as it is
        # local to the project. Referencing it from both inside and outside
        # the project directory causes a mismatch, leading to a failure.
        with pytest.raises(Exception):
            parser.parse()
