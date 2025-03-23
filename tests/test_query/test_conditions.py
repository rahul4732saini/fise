"""
Test Conditions Module
----------------------

This module defined classes and methods for testing the classes defined
within the `query/conditions.py` module for parsing and handling query
conditions.
"""

from datetime import datetime

import pytest

from fise import Field, Size
from fise.common import constants
from fise.shared import QueryQueue
from fise.query.conditions import Condition, ConditionListNode, ConditionParser

# The following constants store arguments and results
# for testing the functionalities associated with them.

CONDITION_PARSER_VALID_ARGS = [
    (
        "where Name = 'main.py' and (ATIME < 2022-01-01 OR mtime < 2022-01-01)",
        constants.ENTITY_DIR,
    ),
    (
        "WherE sizE[KiB] < 10.0 AND Filetype In ['.txt', '.md', '.docx']",
        constants.ENTITY_FILE,
    ),
    (
        "WHERE Dataline like '^A.*celebration$' And ((lineno Between [10, 78]))",
        constants.ENTITY_DATA,
    ),
    (
        "Where ('.py' in name Or ('.c' in NAME)) and Size[KB] >= 25",
        constants.ENTITY_FILE,
    ),
]

CONDITION_PARSER_RESULTS = [
    ConditionListNode(
        Condition("=", Field("name"), "main.py"),
        constants.OP_CONJUNCTION,
        ConditionListNode(
            ConditionListNode(
                Condition("<", Field("access_time"), datetime(2022, 1, 1)),
                constants.OP_DISJUNCTION,
                ConditionListNode(
                    Condition("<", Field("modify_time"), datetime(2022, 1, 1)),
                ),
            )
        ),
    ),
    ConditionListNode(
        Condition("<", Size.parse("KiB"), 10.0),
        constants.OP_CONJUNCTION,
        ConditionListNode(
            Condition("in", Field("filetype"), [".txt", ".md", ".docx"]),
        ),
    ),
    ConditionListNode(
        Condition(constants.OP_LIKE, Field("dataline"), "^A.*celebration$"),
        constants.OP_CONJUNCTION,
        ConditionListNode(
            ConditionListNode(
                ConditionListNode(
                    Condition(constants.OP_BETWEEN, Field("lineno"), [10, 78])
                )
            ),
        ),
    ),
    ConditionListNode(
        ConditionListNode(
            Condition(constants.OP_CONTAINS, ".py", Field("name")),
            constants.OP_DISJUNCTION,
            ConditionListNode(
                ConditionListNode(
                    Condition(constants.OP_CONTAINS, ".c", Field("name")),
                ),
            ),
        ),
        constants.OP_CONJUNCTION,
        ConditionListNode(
            Condition(constants.OP_GE, Size.parse("KB"), 25),
        ),
    ),
]


class TestConditionParser:
    """Tests the `ConditionParser` class."""

    @staticmethod
    def init_parser(query: str, entity: str) -> ConditionParser:
        """
        Initializes the ConditionParser class
        with the specified arguments.
        """

        queue = QueryQueue.from_string(query)
        parser = ConditionParser(queue, entity)

        return parser

    @pytest.mark.parametrize(
        ("args", "result"),
        zip(CONDITION_PARSER_VALID_ARGS, CONDITION_PARSER_RESULTS),
    )
    def test_parse_with_valid_conditions(
        self, args: tuple[str, str], result: ConditionListNode
    ) -> None:
        """
        Tests the parser with valid condition specifications
        and verifies it with the specified result.
        """

        parser = self.init_parser(*args)
        conditions = parser.parse()

        assert conditions == result
