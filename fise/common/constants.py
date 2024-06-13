"""
Constants Module
----------------

This module comprises constants designed to assist various
classes and functions defined within the project.
"""

import sys
from typing import Literal

# Additional fields for Posix-based operating systems.
POSIX_FIELDS = ("owner", "group", "permissions") if sys.platform != "win32" else ()

# Search query fields for various query types.
DIR_FIELDS = (
    "name", "path", "parent", "access_time", "create_time", "modify_time"
) + POSIX_FIELDS

DATA_FIELDS = "name", "path", "lineno", "dataline", "filetype"
FILE_FIELDS = DIR_FIELDS + ("size", "filetype")

OPERATIONS = Literal["search", "remove"]
OPERANDS = Literal["file", "data", "dir"]
SEARCH_QUERY_OPERANDS = {"file", "data", "dir"}
OPERATION_ALIASES = {"select", "delete"}

FILE_MODES = Literal["text", "bytes"]
FILE_MODES_MAP = {"text": "r", "bytes": "rb"}

CONDITION_SEPARATORS = {"and", "or"}
COMPARISON_OPERATORS = {"<", ">", "<=", ">=", "!=", "="}
CONDITIONAL_OPERATORS = {"in", "between", "like"}

SIZE_UNITS = Literal[
    "b", "B", "Kb", "KB", "Kib", "KiB", "Mb", "MB", "Mib",
    "MiB", "Gb", "GB", "Gib", "GiB", "Tb", "TB", "Tib", "TiB"
]

# Mapping of storage unit string labels mapped with corresponding divisors
# for storage size conversion into specified units.
SIZE_CONVERSION_MAP = {
    "b": 0.125, "B": 1, "Kb": 125, "KB": 1e3, "Kib": 128, "KiB": 1024, "Mb": 1.25e5,
    "MB": 1e6, "Mib": 131_072, "MiB": 1024**2, "Gb": 1.25e8, "GB": 1e9, "Gib": 134_217_728,
    "GiB": 1024**3, "Tb": 1.25e11, "TB": 1e12, "Tib": 137_438_953_472, "TiB": 1024**4
}

# Mapping of file suffixes mapped with corresponding
# `pandas.DataFrame`  methods for exporting data.
DATA_EXPORT_TYPES_MAP = {
    ".csv": "to_csv",
    ".json": "to_json",
    ".html": "to_html",
    ".xlsx": "to_excel",
}

# Additional field aliases for Posix-based operating systems.
POSIX_FIELD_ALIASES = {"perms": "permissions"} if sys.platform != "win32" else {}

DIR_FIELD_ALIASES = POSIX_FIELD_ALIASES | {
    "ctime": "create_time",
    "mtime": "modify_time",
    "atime": "access_time",
}

FILE_FIELD_ALIASES = DIR_FIELD_ALIASES | {
    "atime": "access_time",
    "mtime": "modify_time",
    "ctime": "create_time",
    "type": "filetype",
}

DATA_FIELD_ALIASES = {
    "filename": "name",
    "filepath": "path",
    "data": "dataline",
    "line": "dataline",
    "type": "filetype",
}

PATH_TYPES = {"absolute", "relative"}

# Supported databases for data export.
DATABASES = Literal["postgresql", "mysql", "sqlite"]

DATABASE_URL_DIALECTS = {
    "postgresql": "postgresql://",
    "mysql": "mysql+pymysql://",
}
