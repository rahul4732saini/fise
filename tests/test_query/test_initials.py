"""
Test Initials Module
--------------------

This module defines functions for testing the classes
defined within the `query/initials.py` module.
"""

import pytest

from fise.common import constants
from fise.shared import QueryQueue
from fise.query.initials import (
    BaseOperationData,
    FileOperationData,
    DataOperationData,
    DirectoryOperationData,
    FileOperationParser,
    QueryInitialsParser,
)


# The following block comprises constants used by the
# functions for testing the associated functionalities.

# List of all attributes defined within the various operations
# data classes for indirectly comparing the operation data objects
# as direct comparsion is not available.
OP_DATA_ATTRS = ["type_", "skip_err", "mode"]

# Following constants define arguments and results
# for testing File System Operation Parser classes.

FSOP_TEST_ARGS = [
    (constants.OPERATION_SEARCH, {}),
    (constants.OPERATION_DELETE, {"skip_err": "True"}),
    (constants.OPERATION_DELETE, {"skip_err": "FalSE"}),
]

FSOP_TEST_RESULTS = [False, True, False]

# Following constants define arguments and results
# for testing the Query Initials Parser class.

QIP_TEST_ARGS = [
    "select",
    "r select",
    "delete[type file]",
    "r select[type data]",
    "delete[type dir, skip_err true]",
    "recursive select[type file]",
]

QIP_TEST_RESULTS = [
    (FileOperationData(constants.OPERATION_SEARCH), False),
    (FileOperationData(constants.OPERATION_SEARCH), True),
    (FileOperationData(constants.OPERATION_DELETE), False),
    (DataOperationData(constants.OPERATION_SEARCH), True),
    (DirectoryOperationData(constants.OPERATION_DELETE, True), False),
    (FileOperationData(constants.OPERATION_SEARCH), True),
]


# The following block comprise classes for testing
# the classes defined within the `initials` module.


@pytest.mark.parametrize(
    ("source", "skip_err"),
    zip(FOP_TEST_ARGS, FOP_TEST_RESULTS),
)
def test_file_operation_parser(
    source: tuple[str, dict[str, str]], skip_err: bool
) -> None:
    """
    Tests the `FileOperationParser` class and the only public methods defined
    within it by initializing it with the operation type and arguments, and
    verifying the parse method by comparing  the attributes encapsulated in
    the resultant `FileOperationData` object with the specified results.
    """

    parser = FileOperationParser(*source)
    data = parser.parse()

    assert data.skip_err == skip_err


class TestQueryInitialsParser:
    """Tests the `QueryInitialsParser` class."""

    @pytest.mark.parametrize(
        ("source", "result"),
        zip(QIP_TEST_ARGS, QIP_TEST_RESULTS),
    )
    def test_class(self, source: str, result: tuple[BaseOperationData, bool]) -> None:
        """
        Tests the class and the only public method defined within it by
        initializing it with a `QueryQueue` object comprising the query
        initials, and verifying the parse method by comparing the attributes
        encapsulated within the resultant `QueryInitials` object with the
        specified results.
        """

        query = QueryQueue.from_string(source)
        parser = QueryInitialsParser(query)

        initials = parser.parse()
        op_src, op_res = result[0], initials.operation

        assert initials.recursive == result[1]

        # Iterates through the operation data attribute names and compares
        # the values encapsulated within them if it is defined within both
        # the objects.
        for name in OP_DATA_ATTRS:

            # Asserts false in cases where the attribute is defined within
            # one class but not the other, suggesting an inconsistency.
            if hasattr(op_src, name) ^ hasattr(op_res, name):
                assert False

            assert getattr(op_src, name, None) == getattr(op_res, name, None)
