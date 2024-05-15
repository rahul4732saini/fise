"""
Constants Module
----------------

This module comprises constants designed to assist various
objects and functions present within the FiSE project.
"""

from typing import Literal

DIR_FIELDS = {"path", "parent", "name", "owner", "group", "permissions"}
DATA_FIELDS = {"name", "path", "dataline", "lineno"}
FILE_FIELDS = DIR_FIELDS | {"size", "access_time", "create_time", "modify_time"}

OPERATIONS = Literal["search", "remove"]
OPERANDS = Literal["file", "data", "dir"]
SEARCH_QUERY_OPERANDS = ("file", "data", "dir")
DELETE_QUERY_OPERANDS = ("file", "dir")
OPERATION_ALIASES = {"select": "search", "delete": "remove"}

FILE_MODES = Literal["text", "bytes"]
FILE_MODES_MAP = {"text": "r", "bytes": "rb"}

CONDITION_SEPERATORS = {"and", "or"}

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

# Mapping of file suffixes mapped with corresponding
# `pandas.DataFrame`  methods for exporting data.
DATA_EXPORT_TYPES_MAP = {
    ".csv": "to_csv",
    ".json": "to_json",
    ".html": "to_html",
    ".xlsx": "to_excel",
}

FILE_FIELD_ALIASES = {
    "atime": "access_time",
    "mtime": "modify_time",
    "ctime": "create_time",
    "perms": "permissions",
}

DATA_FIELD_ALIASES = {
    "filename": "name",
    "filepath": "path",
    "data": "dataline",
    "line": "dataline",
}

DIR_FIELD_ALIASES = {"perms": "permissions"}

PATH_TYPES = {"absolute", "relative"}

# Supported databases for data export.
DATABASES = "postgresql", "mysql", "sqlite"

DATABASE_URL_DIALECTS = {
    "postgresql": "postgresql://",
    "mysql": "mysql+pymysql://",
}
