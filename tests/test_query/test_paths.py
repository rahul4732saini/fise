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

# The following constants store absolute paths to the file_dir and
# data test directories to effectively test the query path classes.

FD_TEST_DIR = BASE_DIR / "test_directory/file_dir"
DATA_TEST_DIR = BASE_DIR / "test_directory/data"

# The following constants store arguments and results
# for testing the functionalities associated with them.

QPP_VALID_TEST_ARGS = [
    (f"absolute {FD_TEST_DIR / 'project'}", constants.ENTITY_FILE),
    (f"{FD_TEST_DIR / 'media'}", constants.ENTITY_DIR),
    (f"relative {FD_TEST_DIR / 'docs'}", constants.ENTITY_FILE),
    (f"absolute {DATA_TEST_DIR / 'todo.txt'}", constants.ENTITY_DATA),
]

QPP_VALID_TEST_RESULTS = [
    FD_TEST_DIR / "project",
    FD_TEST_DIR / "media",
    FD_TEST_DIR / "docs",
    DATA_TEST_DIR / "todo.txt",
]

QPP_INVALID_TEST_ARGS = [
    (f"absl {FD_TEST_DIR}", constants.ENTITY_FILE),
    (f"relative {DATA_TEST_DIR / 'specs.xlsx'}", constants.ENTITY_DATA),
    (f"{FD_TEST_DIR / 'todo.txt'}", constants.ENTITY_DATA),
    (f"rel {FD_TEST_DIR}", constants.ENTITY_DIR),
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

        # Compares the absolute paths of the file/directory for validation.
        assert path_obj.path == result

    @pytest.mark.parametrize("args", QPP_INVALID_TEST_ARGS)
    def test_with_invalid_query(self, args: tuple[str, str]) -> None:
        """Tests the parser with invalid query path specifications."""

        parser = self.init_parser(*args)

        # Unable to pass 'QueryParserError' as the error class as it is
        # local to the project. Referencing it from both inside and outside
        # the project directory causes a mismatch, leading to a failure.
        with pytest.raises(Exception):
            parser.parse()
