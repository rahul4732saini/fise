"""
This module comprises test functions for verifying the
classes defined within the shared.py module in FiSE.
"""

import pytest
from fise.shared import QueryQueue


# The following block comprises constants
# required by the test functions for operation.


QUERY_QUEUE_ARGS = [
    ("export", "file[./res.xlsx]", "select", "*", "from", "."),
    ("select", "*", "from", ".", "where", "name", "like", r"^.*\.py$"),
    ("Recursive", "delete[type file, skip_err true]", "from", "."),
]

QQ_OBJ_INIT_FROM_STR_ARGS = [" ".join(source) for source in QUERY_QUEUE_ARGS]
QQ_OBJ_INIT_FROM_STR_RESULTS = QUERY_QUEUE_ARGS


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
