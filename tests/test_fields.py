"""
Test Fields Module
------------------

This module defines functions for testing the classes
defined within the fields.py module in FiSE.
"""

from pathlib import Path
from typing import Any

import pytest

from fise.common import constants
from fise.entities import BaseEntity, File, DataLine, Directory
from fise.fields import Field, Size


BASE_DIR = Path(__file__).parent
TEST_DIR = BASE_DIR / "test_directory"

DATA_TEST_DIR = TEST_DIR / "data"
FD_TEST_DIR = TEST_DIR / "file_dir"


# The following block comprises constants used by the test functions as
# a necessary requirement for testing the associated functionalities.


GENERIC_FIELD_TEST_ARGS = [
    ("create_time", File(FD_TEST_DIR / "TODO")),
    ("name", Directory(FD_TEST_DIR)),
    ("parent", File(FD_TEST_DIR / "media/galaxy.mp3")),
    ("path", DataLine(FD_TEST_DIR / "project/LICENSE", "", 0)),
    ("access_time", Directory(FD_TEST_DIR / "media")),
    ("dataline", DataLine(FD_TEST_DIR / "README.md", "", 0)),
]

GENERIC_FIELD_TEST_RESULTS = [
    getattr(entity, field) for field, entity in GENERIC_FIELD_TEST_ARGS
]

SIZE_FIELD_TEST_ARGS = [
    ("B", DATA_TEST_DIR / "todo.txt"),
    ("Gb", DATA_TEST_DIR / "reports/report-2020.xlsx"),
    ("KiB", DATA_TEST_DIR / "complaints.txt"),
    ("MB", DATA_TEST_DIR / "specs.txt"),
    ("TiB", DATA_TEST_DIR / "reports/report-2024.xlsx"),
    ("Mib", DATA_TEST_DIR / "roadmap.txt"),
]


SIZE_FIELD_TEST_RESULTS = [
    round(path.stat().st_size / constants.SIZE_CONVERSION_MAP[unit], 5)
    for unit, path in SIZE_FIELD_TEST_ARGS
]


# The following block comprises functions for testing
# the class defined within the `fields` module.


@pytest.mark.parametrize(
    ("args", "result"), zip(GENERIC_FIELD_TEST_ARGS, GENERIC_FIELD_TEST_RESULTS)
)
def test_field_class(args: tuple[str, BaseEntity], result: Any) -> None:
    """
    Tests the `Field` class and the methods defined within it
    by parsing various generic fields and evaluating them for
    verification.
    """

    field, entity = args

    obj = Field.parse(field)
    assert obj.evaluate(entity) == result


@pytest.mark.parametrize(
    ("args", "result"), zip(SIZE_FIELD_TEST_ARGS, SIZE_FIELD_TEST_RESULTS)
)
def test_size_class(args: tuple[str, Path], result: float) -> None:
    """
    Tests the `Size` class and the methods defined within
    it by parsing various size fields and evaluating them
    for verification.
    """

    unit, path = args
    entity = File(path)

    obj = Size.parse(unit)
    assert obj.evaluate(entity) == result
