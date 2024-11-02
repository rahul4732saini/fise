"""
Constants Module
----------------

This module comprises constants designed for assisting operations
within the various classes and functions defined in the project.
"""

import re
import sys
from typing import Literal

# Additional query fields and aliases for POSIX-based operating systems.
if sys.platform != "win32":
    POSIX_FIELDS = "owner", "group", "permissions"
    POSIX_FIELD_ALIASES = {"perms": "permissions"}

else:
    POSIX_FIELDS = ()
    POSIX_FIELD_ALIASES = {}

DIR_FIELDS = (
    "name", "path", "parent", "access_time", "create_time", "modify_time"
) + POSIX_FIELDS

DATA_FIELDS = "name", "path", "lineno", "dataline", "filetype"
FILE_FIELDS = DIR_FIELDS + ("size", "filetype")

DIR_FIELD_ALIASES = POSIX_FIELD_ALIASES | {
    "ctime": "create_time",
    "mtime": "modify_time",
    "atime": "access_time",
}

FILE_FIELD_ALIASES = DIR_FIELD_ALIASES | {
    "filepath": "path",
    "filename": "name",
    "type": "filetype",
}

DATA_FIELD_ALIASES = {
    "filename": "name",
    "filepath": "path",
    "data": "dataline",
    "line": "dataline",
    "type": "filetype",
}

ENTITY_FILE = 0
ENTITY_DIR = 1
ENTITY_DATA = 2

FIELDS = {
    ENTITY_FILE: set(FILE_FIELDS),
    ENTITY_DIR: set(DIR_FIELDS),
    ENTITY_DATA: set(DATA_FIELDS),
}

ALIASES = {
    ENTITY_FILE: FILE_FIELD_ALIASES,
    ENTITY_DIR: DIR_FIELD_ALIASES,
    ENTITY_DATA: DATA_FIELD_ALIASES,
}

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

FIELD_PATTERN = re.compile(r"^[a-zA-Z]+(\[.+])?$")
STRING_PATTERN = re.compile(r"^['\"].*['\"]$")

# Maps storage unit string lables with their corresponding
# divisors relative to 1 Byte for storage size conversions.
SIZE_CONVERSION_MAP = {
    "b": 0.125, "B": 1, "Kb": 125, "KB": 1e3, "Kib": 128, "KiB": 1024, "Mb": 1.25e5,
    "MB": 1e6, "Mib": 131_072, "MiB": 1024**2, "Gb": 1.25e8, "GB": 1e9, "Gib": 134_217_728,
    "GiB": 1024**3, "Tb": 1.25e11, "TB": 1e12, "Tib": 137_438_953_472, "TiB": 1024**4
}

PATH_ABSOLUTE = "absolute"
PATH_RELATIVE = "relative"

PATH_TYPES = {
    PATH_ABSOLUTE,
    PATH_RELATIVE,
}

# Supported databases for exporting search records.
DATABASES = {"postgresql", "mysql", "sqlite"}

DATABASE_URL_DIALECTS = {
    "postgresql": "postgresql://",
    "mysql": "mysql+pymysql://",
}
