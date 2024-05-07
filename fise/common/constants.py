r"""
Constants Module
----------------

This module comprises all the constants used throughout utility and
are designed to assist other functionalities present withing it.
"""

from typing import Literal

# Mapping of storage unit string labels mapped with coressponding divisors
# for storage size conversion into specified units.
SIZE_CONVERSION_MAP = {
    "b": 0.125,
    "B": 1,
    "KB": 1e3,
    "KiB": 1024,
    "MB": 1e6,
    "MiB": 1024**2,
    "GB": 1e9,
    "GiB": 1024**3,
    "TB": 1e12,
    "TiB": 1024**4,
}

FILE_MODES = Literal["text", "bytes"]
FILE_MODES_MAP = {"text": "r", "bytes": "rb"}

# Mapping of file suffixes mapped with coressponding
# `pandas.DataFrame`  methods for exporting data.
DATA_EXPORT_TYPES_MAP = {
    ".csv": "to_csv",
    ".json": "to_json",
    ".html": "to_html",
    ".xlsx": "to_excel",
}
