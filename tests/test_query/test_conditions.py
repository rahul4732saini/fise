"""
Test Conditions Module
----------------------

This module defined classes and methods for testing the classes defined
within the `query/conditions.py` module for parsing and handling query
conditions.
"""

from pathlib import Path
from datetime import datetime

import pytest

from fise import Field, Size, QueryParseError
from fise.common import constants
from fise.entities import BaseEntity, File, Directory, DataLine
from fise.shared import QueryQueue

from fise.query.conditions import (
    Condition,
    ConditionListNode,
    ConditionParser,
    ConditionHandler,
)

BASE_DIR = Path(__file__).parents[1]
TEST_DIR = BASE_DIR / "test_directory"

FD_TEST_DIR = TEST_DIR / "file_dir"
DATA_TEST_DIR = TEST_DIR / "data"

# The following constants store arguments and results
# for testing the functionalities associated with them.

VALID_PARSER_ARGS = [
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

VALID_PARSER_RESULTS = [
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

INVALID_PARSER_ARGS = [
    (
        "Where Name Like size[KiB] Or name = 'main.py'",
        constants.ENTITY_FILE,
    ),
    (
        "filetype in ['.txt', '.md', '.docx']",
        constants.ENTITY_DATA,
    ),
    (
        "where (lineno between [1, 100] or lineno between (200, 201))",
        constants.ENTITY_DATA,
    ),
    (
        "WHERE atime >= 2022-01-01 and lineno in [1, 10, 100]",
        constants.ENTITY_FILE,
    ),
]

HANDLER_CONDITIONS = [
    (
        "where filetype in [None, '.txt', '.md'] and (ctime > 1990-01-01) and size[KB] = 0",
        constants.ENTITY_FILE,
    ),
    (
        r"where ('test_directory' in parent) and name like '^(docs|report-\d{4})$'",
        constants.ENTITY_DIR,
    ),
    (
        "where dataline like '^.*!$' and ((lineno between [1, 100] or lineno > 200))",
        constants.ENTITY_DATA,
    ),
]

TRUTHY_HANDLER_ENTITIES = [
    (
        File(FD_TEST_DIR / "TODO"),
        File(FD_TEST_DIR / "roadmap.txt"),
        File(FD_TEST_DIR / "docs/config/getting-started.md"),
    ),
    (
        Directory(FD_TEST_DIR / "reports/report-2021"),
        Directory(FD_TEST_DIR / "docs"),
        Directory(FD_TEST_DIR / "reports/report-2024"),
    ),
    (
        # The arguments specified to the following DataLine objects are not
        # associated with any actual file but serve as test placeholders as
        # the object itself and its associated mechanism do not verify their
        # validity during operation.
        DataLine(DATA_TEST_DIR / "todo.txt", b"Hello there!", 49),
        DataLine(DATA_TEST_DIR / "specs.txt", "This is an open source software!", 343),
        DataLine(DATA_TEST_DIR / "todo.txt", "You can use it!", 1),
    ),
]

FALSY_HANDLER_ENTITIES = [
    (
        File(FD_TEST_DIR / "media/birthday.avi"),
        File(FD_TEST_DIR / "project/setup.py"),
        File(FD_TEST_DIR / "media/galaxy.mp3"),
    ),
    (
        Directory(FD_TEST_DIR),
        Directory(FD_TEST_DIR / "project"),
        Directory(FD_TEST_DIR / "media"),
    ),
    (
        # The arguments specified to the following DataLine objects are not
        # associated with any actual file but serve as test placeholders as
        # the object itself and its associated mechanism do not verify their
        # validity during operation.
        DataLine(DATA_TEST_DIR / "todo.txt", "Who're you?", 10),
        DataLine(DATA_TEST_DIR / ".py", "Morning!", 200),
        DataLine(DATA_TEST_DIR / ".txt", "Shut up...", 101),
    ),
]


def init_parser(query: str, entity: str) -> ConditionParser:
    """
    Initializes the ConditionParser class
    with the specified arguments.
    """

    queue = QueryQueue.from_string(query)
    parser = ConditionParser(queue, entity)

    return parser


def init_handler(query: str, entity: str) -> ConditionHandler:
    """
    Initializes the ConditionHandler class by parsing the
    specified condition specifications based on the specified
    entity name.
    """

    parser = init_parser(query, entity)
    conditions = parser.parse()

    return ConditionHandler(conditions)


class TestConditionParser:
    """Tests the `ConditionParser` class."""

    @pytest.mark.parametrize(
        ("args", "result"),
        zip(VALID_PARSER_ARGS, VALID_PARSER_RESULTS),
    )
    def test_parse_with_valid_conditions(
        self, args: tuple[str, str], result: ConditionListNode
    ) -> None:
        """
        Tests the parse method with valid conditions specifications
        and verifies it with the specified result.
        """

        parser = init_parser(*args)
        conditions = parser.parse()

        assert conditions == result

    @pytest.mark.parametrize("args", INVALID_PARSER_ARGS)
    def test_parse_with_invalid_conditions(self, args: tuple[str, str]) -> None:
        """
        Tests the parse method with invalid condition
        specifications expecting a query parser error.
        """

        parser = init_parser(*args)

        with pytest.raises(QueryParseError):
            parser.parse()


class TestConditionHandler:
    """Tests the `ConditionHandler` class."""

    @pytest.mark.parametrize(
        ("condition", "entities"),
        zip(HANDLER_CONDITIONS, TRUTHY_HANDLER_ENTITIES),
    )
    def test_for_truthiness(
        self, condition: tuple[str, str], entities: tuple[BaseEntity]
    ) -> None:
        """
        Tests the handler and its evaluator method with entities
        that hold true with the specified condition specifications.
        """

        handler = init_handler(*condition)
        assert all(handler(entity) for entity in entities)

    @pytest.mark.parametrize(
        ("condition", "entities"),
        zip(HANDLER_CONDITIONS, FALSY_HANDLER_ENTITIES),
    )
    def test_for_fasliness(
        self, condition: tuple[str, str], entities: tuple[BaseEntity]
    ) -> None:
        """
        Tests the handler and its evaluator method with entities
        that hold false with the specified condition specifications.
        """

        handler = init_handler(*condition)
        assert all(not handler(entity) for entity in entities)
