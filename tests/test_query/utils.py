"""
Utils.py
--------

This module comprises utility functions specifically designed
to support test functions and methods defined within the project.
"""

from pathlib import Path

import pandas as pd


def read_hdf(file: Path, path: str) -> pd.DataFrame:
    """
    Reads the test records stored at the specified
    path from the specified HDF5 file.
    """

    with pd.HDFStore(str(file)) as store:
        return store[path]
