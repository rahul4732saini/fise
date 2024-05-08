r"""
Constants Module
----------------

This module comprises all the constants used throughout utility and
are designed to assist other functionalities present withing it.
"""

from typing import Literal

# Mapping of storage unit string labels mapped with corresponding divisors
# for storage size conversion into specified units.
SIZE_CONVERSION_MAP = {
    "b": 0.125,
    "B": 1,
    "Kb": 125,
    "KB": 1e3,
    "Kib": 128,
    "KiB": 1024,
    "Mb": 1.25e5,
    "MB": 1e6,
    "Mib": 131_072,
    "MiB": 1024**2,
    "Gb": 1.25e8,
    "GB": 1e9,
    "Gib": 134_217_728,
    "GiB": 1024**3,
    "Tb": 1.25e11,
    "TB": 1e12,
    "Tib": 137_438_953_472,
    "TiB": 1024**4,
}

FILE_MODES = Literal["text", "bytes"]
FILE_MODES_MAP = {"text": "r", "bytes": "rb"}

# Mapping of file suffixes mapped with corresponding
# `pandas.DataFrame`  methods for exporting data.
DATA_EXPORT_TYPES_MAP = {
    ".csv": "to_csv",
    ".json": "to_json",
    ".html": "to_html",
    ".xlsx": "to_excel",
}

# Dictionary mapping alias names to actual field names for file search queries.
FILE_QUERY_FIELD_ALIAS = {
    "atime": "access_time",
    "mtime": "modify_time",
    "ctime": "create_time",
    "perms": "permissions",
}
