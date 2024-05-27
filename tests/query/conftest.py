import sys
from pathlib import Path

import pytest

# Adds the project directories to sys.path at runtime.
sys.path.append(str(Path(__file__).parents[2]))
sys.path.append(str(Path(__file__).parents[2] / "fise"))


@pytest.fixture
def test_directory() -> Path:
    return Path(__file__).parents[1] / "test_directory"


@pytest.fixture
def file_fields() -> tuple[str, ...]:
    posix_fields: tuple = ("owner", "group") if sys.platform != "win32" else ()

    return (
        ("name", "path", "parent", "permissions")
        + posix_fields
        + ("size", "filetype", "access_time", "create_time", "modify_time")
    )


@pytest.fixture
def data_fields() -> tuple[str, ...]:
    return "name", "path", "lineno", "data"


@pytest.fixture
def dir_fields() -> tuple[str, ...]:
    posix_fields: tuple = ("owner", "group") if sys.platform != "win32" else ()
    return ("name", "path", "parent", "permissions") + posix_fields
