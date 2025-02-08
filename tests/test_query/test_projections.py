"""
Test Projections Module
-----------------------

This module defines functions for testing the classes
defined within the `query/projections.py` for parsing
and handling search query projections. 
"""

from pathlib import Path
import pytest

from fise.query.projections import Projection
from fise.fields import BaseField, Field, Size
from fise.entities import File, Directory, BaseEntity


# The following block comprises constants
# required by the test functions for operation.


TEST_DIR = Path(__file__).parents[1] / "test_directory"
FILE_DIR_TEST_DIR = TEST_DIR / "file_dir"

PROJECTION_TEST_ARGS = [
    ("size", Size.parse("B")),
    ("parent", Field("parent")),
    ("access_time", Field("access_time")),
    ("name", Field("name")),
]

PROJECTION_TEST_ENTITIES = [
    File(FILE_DIR_TEST_DIR / "TODO"),
    Directory(FILE_DIR_TEST_DIR),
    File(FILE_DIR_TEST_DIR / "README.md"),
    Directory(FILE_DIR_TEST_DIR / "media"),
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
        """"""

        projection = Projection(name, field)
        assert str(projection) == name

    @pytest.mark.parametrize(
        ("args", "entity"),
        zip(PROJECTION_TEST_ARGS, PROJECTION_TEST_ENTITIES),
    )
    def test_evaluate_method(
        self, args: tuple[str, BaseField], entity: BaseEntity
    ) -> None:
        """"""

        name, field = args

        projection = Projection(name, field)
        projection.evaluate(entity) == field.evaluate(entity)
