import sys
from pathlib import Path

import pytest

# Adds the project directories to sys.path at runtime.
sys.path.append(str(Path(__file__).parents[2]))
sys.path.append(str(Path(__file__).parents[2] / "fise"))


@pytest.fixture
def test_directory() -> Path:
    return Path(__file__).parents[1] / "test_directory"
