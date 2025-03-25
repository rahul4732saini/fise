"""
Test Projections Module
-----------------------

This module defines functions for testing the classes defined
within the `query/projections.py` module for parsing and handling
search query projections.
"""

from pathlib import Path
import pytest

from fise.common import tools, constants
from fise.shared import QueryQueue
from fise.fields import BaseField, Field, Size
from fise.query.projections import Projection, ProjectionsParser
from fise.entities import File, Directory, BaseEntity


# The following block comprises constants used by the
# functions for testing the associated functionalities.


TEST_DIR = Path(__file__).parents[1] / "test_directory"
FD_TEST_DIR = TEST_DIR / "file_dir"

PROJECTION_TEST_ARGS = [
    ("size", Size.parse("B")),
    ("parent", Field("parent")),
    ("access_time", Field("access_time")),
    ("name", Field("name")),
]

PROJECTION_TEST_ENTITIES = [
    File(FD_TEST_DIR / "TODO"),
    Directory(FD_TEST_DIR),
    File(FD_TEST_DIR / "README.md"),
    Directory(FD_TEST_DIR / "media"),
]

PROJ_PARSER_TEST_ARGS = [
    ("Parent", constants.ENTITY_DIR),
    ("*,line, LineNo, FILENAME", constants.ENTITY_DATA),
    ("name, Atime, Create_time,Parent", constants.ENTITY_DIR),
    ("size[KB], parent", constants.ENTITY_FILE),
    ("type,Mtime, SIZE[Tb], FilePath", constants.ENTITY_FILE),
]


# The following block comprise classes for testing
# the classes defined within the `projections` module.


class TestProjection:
    """Tests the `Projection` class."""

    @pytest.mark.parametrize(
        ("name", "field"),
        PROJECTION_TEST_ARGS,
    )
    def test_obj_init(self, name: str, field: BaseField) -> None:
        """
        Tests the object initialization and verifies the string
        representation of the class ensuring proper display of the
        projection names during runtime.
        """

        projection = Projection(name, field)
        assert str(projection) == name

    @pytest.mark.parametrize(
        ("args", "entity"),
        zip(PROJECTION_TEST_ARGS, PROJECTION_TEST_ENTITIES),
    )
    def test_evaluate_method(
        self, args: tuple[str, BaseField], entity: BaseEntity
    ) -> None:
        """
        Tests the `evaluate` method for evaluating the projection and
        verifies the result by equilating it with the result obtained
        by evaluating the field itself.
        """

        name, field = args

        projection = Projection(name, field)
        projection.evaluate(entity) == field.evaluate(entity)


class TestProjectionsParser:
    """Tests the `ProjectionsParser` class."""

    @pytest.mark.parametrize(("specs", "entity"), PROJ_PARSER_TEST_ARGS)
    def test_class(self, specs: str, entity: str) -> None:
        """
        Tests the class and the only public method defined within it by
        initializing it with a `QueryQueue` object comprising the query
        fields along with the `FROM` keyword for making termination and
        the entity name associated with them, and finally verifying the
        parse method by equilating the names of the parsed projections.
        """

        names = list(tools.tokenize(specs, ","))

        query = QueryQueue.from_string(specs)
        query.add(constants.KEYWORD_FROM)

        parser = ProjectionsParser(query, entity)
        projections: list[Projection] = parser.parse()

        # Keeps track of the current index in the projections
        # list during the verification process.
        ctr = 0

        for field in names:
            if field != constants.KEYWORD_ASTERISK:
                assert str(projections[ctr]) == field
                ctr += 1

                continue

            for name in constants.FIELDS[entity]:
                assert str(projections[ctr]) == name
                ctr += 1

        assert ctr == len(projections)
