"""
Tests the `common/tools.py` module.
"""

from pathlib import Path

import pandas as pd
import pytest

from fise.common import tools

TEST_DIRECTORY = Path(__file__).parent / "test_directory"

# Test parameters defined below.

TEST_GET_FILES_FUNC_PARAMS = [
    (1, TEST_DIRECTORY, True),
    (2, TEST_DIRECTORY / "file_dir", False),
    (3, TEST_DIRECTORY / "file_dir/docs", True),
]

TEST_GET_DIRS_FUNC_PARAMS = [
    (1, TEST_DIRECTORY, True),
    (2, TEST_DIRECTORY / "file_dir", False),
    (3, TEST_DIRECTORY / "file_dir/reports", True),
]


def read_tests_hdf(path: str) -> pd.Series | pd.DataFrame:
    """Reads test data from `test_tools.hdf` file."""

    with pd.HDFStore(Path(__file__).parent / "test_tools.hdf") as store:
        return store[path]


@pytest.mark.parametrize(("ctr", "path", "recur"), TEST_GET_FILES_FUNC_PARAMS)
def test_get_files_function(ctr: int, path: Path, recur: bool) -> None:
    """Tests the `get_files` function."""
    files: pd.Series = pd.Series(str(path) for path in tools.get_files(path, recur))
    assert files.equals(read_tests_hdf(f"/function/get_files/test{ctr}"))


@pytest.mark.parametrize(("ctr", "path", "recur"), TEST_GET_DIRS_FUNC_PARAMS)
def test_get_directories_function(ctr: int, path: Path, recur: bool) -> None:
    """Tests the `get_files` function."""
    files: pd.Series = pd.Series(
        str(path) for path in tools.get_directories(path, recur)
    )
    assert files.equals(read_tests_hdf(f"/function/get_directories/test{ctr}"))
