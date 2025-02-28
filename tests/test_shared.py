"""
Test Shared Module
------------------

This module defines functions for testing the classes
defined within the shared.py module in FiSE.
"""

from pathlib import Path
import pytest
from fise.shared import QueryQueue, FileIterator


BASE_DIR = Path(__file__).parent
TEST_DATA_DIR = BASE_DIR / "test_directory/data/"


# The following block comprises constants
# required by the test functions for operation.


QUERY_QUEUE_ARGS = [
    ("export", "file[./res.xlsx]", "select", "*", "from", "."),
    ("select", "*", "from", ".", "where", "name", "like", r"^.*\.py$"),
    ("Recursive", "delete[type file, skip_err true]", "from", "."),
]

QQ_OBJ_INIT_FROM_STR_ARGS = [" ".join(source) for source in QUERY_QUEUE_ARGS]
QQ_OBJ_INIT_FROM_STR_RESULTS = QUERY_QUEUE_ARGS

# Test arguments for initializing the FileIterator class.
FI_TEST_ARGS = [
    (TEST_DATA_DIR / "complaints.txt", "r"),
    (TEST_DATA_DIR / "reports/report-2020.xlsx", "rb"),
    (TEST_DATA_DIR / "todo.txt", "r"),
]


# The following block comprise classes for testing
# the classes defined within the `shared` module.


class TestQueryQueue:
    """Tests the `QueryQueue` class."""

    @pytest.mark.parametrize("source", QUERY_QUEUE_ARGS)
    def test_obj_init(self, source: tuple[str]) -> None:
        """
        Tests the object initialization and
        validates the operation for success.
        """

        queue = QueryQueue(source)

        for token in source:
            assert queue.pop() == token

    @pytest.mark.parametrize(
        ("source", "result"),
        zip(QQ_OBJ_INIT_FROM_STR_ARGS, QQ_OBJ_INIT_FROM_STR_RESULTS),
    )
    def test_obj_init_from_string(self, source: str, result: tuple[str]) -> None:
        """
        Tests the object initialization from a string
        and validates the operation for success.
        """

        queue = QueryQueue.from_string(source)

        for token in result:
            assert queue.pop() == token

    @pytest.mark.parametrize("source", QUERY_QUEUE_ARGS)
    def test_operator_method(self, source: tuple[str]) -> None:
        """Tests the operator methods (add, pop, peek)."""

        queue = QueryQueue()

        for token in source:
            queue.add(token)

        for token in source:
            assert queue.peek() == token
            queue.pop()

        assert not queue


class TestFileIterator:
    """Tests the `FileIterator` class."""

    @pytest.mark.parametrize(("path", "filemode"), FI_TEST_ARGS)
    def test_iterator(self, path: Path, filemode: str) -> None:
        """
        Tests the iterator and validates the iteration process by
        matching the lines at the corresponding index in the file.
        """

        iterator = FileIterator(Path(path), filemode)
        ctr: int = 0

        lines: list[str]

        with open(path, filemode) as file:
            lines = file.readlines()

        for count, line in iterator:
            ctr += 1

            assert lines[ctr - 1] == line
            assert ctr == count
