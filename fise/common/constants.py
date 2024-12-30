"""
Constants Module
----------------

This module comprises constants designed for assisting operations
within the various classes and functions defined in the project.
"""

import re
import sys

# CLI commands available to the user.
CMD_EXIT = {"exit", "quit"}
CMD_CLEAR = {"\c", "clear"}

# Keywords reserved for different query operations.
KEYWORD_EXPORT = "export"
KEYWORD_RECURSIVE = "recursive"
KEYWORD_RECURSIVE_SHORT = "r"
KEYWORD_FROM = "from"
KEYWORD_WHERE = "where"
KEYWORD_NONE = "none"
KEYWORD_ASTERISK = "*"

# Boolean types available for usage in query operation.

BOOLEAN_TRUE = "true"
BOOLEAN_FALSE = "false"

BOOLEANS = {BOOLEAN_TRUE, BOOLEAN_FALSE}

# Constants associated with the export operation.

EXPORT_FILE = "file"
EXPORT_DBMS = "dbms"

EXPORT_TYPES = {EXPORT_FILE, EXPORT_DBMS}

# Available DBMS for search record exports.
DBMS_MYSQL = "mysql"
DBMS_POSTGRESQL = "postgresql"
DBMS_SQLITE = "sqlite"

DBMS_DRIVERNAMES = {
    DBMS_MYSQL: "mysql+pymysql",
    DBMS_POSTGRESQL: "postgresql+psycopg2",
    DBMS_SQLITE: "sqlite",
}

DBMS = {DBMS_MYSQL, DBMS_POSTGRESQL, DBMS_SQLITE}
EXPORT_FILE_FORMATS = {".csv", ".json", ".html", ".xlsx"}

# Entities available for usage in query operation.

ENTITY_FILE = "file"
ENTITY_DIR = "dir"
ENTITY_DATA = "data"

DEFAULT_OPERATION_ENTITY = ENTITY_FILE

ENTITIES = {ENTITY_FILE, ENTITY_DIR, ENTITY_DATA}

# Available modes for reading file contents.

READ_MODE_TEXT = "text"
READ_MODE_BYTES = "bytes"

READ_MODES_MAP = {READ_MODE_TEXT: "r", READ_MODE_BYTES: "rb"}

# Available query operations.

OPERATION_SEARCH = "select"
OPERATION_DELETE = "delete"

OPERATIONS = {OPERATION_SEARCH, OPERATION_DELETE}

# Constants associated with query fields and projections.

# Additional query fields and aliases for POSIX-based operating systems.
if sys.platform != "win32":
    POSIX_FIELDS = "owner", "group", "permissions"
    POSIX_FIELD_ALIASES = {"perms": "permissions"}

else:
    POSIX_FIELDS = ()
    POSIX_FIELD_ALIASES = {}

DIR_FIELDS = (
    "name",
    "path",
    "parent",
    "access_time",
    "create_time",
    "modify_time",
) + POSIX_FIELDS

DATA_FIELDS = "name", "path", "lineno", "dataline", "filetype"
FILE_FIELDS = DIR_FIELDS + ("size", "filetype")

# Aliases associated with file, directory and data query fields.

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

# The following constant map entity names with
# their corresponding query fields and aliases.

FIELDS = {
    ENTITY_FILE: FILE_FIELDS,
    ENTITY_DIR: DIR_FIELDS,
    ENTITY_DATA: DATA_FIELDS,
}

ALIASES: dict[str, dict[str, str]] = {
    ENTITY_FILE: FILE_FIELD_ALIASES,
    ENTITY_DIR: DIR_FIELD_ALIASES,
    ENTITY_DATA: DATA_FIELD_ALIASES,
}

# Path types available for usage in query operation.

PATH_ABSOLUTE = "absolute"
PATH_RELATIVE = "relative"

PATH_TYPES = {PATH_ABSOLUTE, PATH_RELATIVE}

# Date and datetime formats used with the associated query fields.
DATE_FORMAT = r"%Y-%m-%d"
DATETIME_FORMAT = r"%Y-%m-%d %H:%M:%S"

# The following constants comprise patterns for matching
# associated query clauses, tokens, fields, and much more.

QUALIFIED_CLAUSE_PATTERN = re.compile(r"^[a-zA-Z_]+(\[.*])?$")
STRING_PATTERN = re.compile(r"^['\"].*['\"]$")
TUPLE_PATTERN = re.compile(r"^\[.*]$")
NESTED_CONDITION_PATTERN = re.compile(r"^\(.*\)$")
FLOAT_PATTERN = re.compile(r"^-?\d+(\.\d+)?$")
DATETIME_PATTERN = re.compile(r"^\d{4}-\d{1,2}-\d{1,2}( \d{1,2}:\d{1,2}:\d{1,2})?$")

# Logical operators for separating query condition segments.
OP_CONJUNCTION = "and"
OP_DISJUNCTION = "or"

# Binary symbolic condition operators
OP_GT = ">"
OP_GE = ">="
OP_LT = "<"
OP_LE = "<="
OP_EQ = "="
OP_NE = "!="

# Binary lexical condition operators
OP_CONTAINS = "in"
OP_BETWEEN = "between"
OP_LIKE = "like"

# The symbolic operators have been arranged in descending order of
# their length to avoid misinterpretation while parsing conditional
# clauses in the query.
SYMBOLIC_OPERATORS = OP_GE, OP_LE, OP_NE, OP_GT, OP_LT, OP_EQ
LEXICAL_OPERATORS = OP_CONTAINS, OP_BETWEEN, OP_LIKE

CONDITION_OPERATORS = LEXICAL_OPERATORS + SYMBOLIC_OPERATORS
LOGICAL_OPERATORS = OP_CONJUNCTION, OP_DISJUNCTION

# Maps storage unit string labels with their corresponding
# divisors relative to 1 Byte for storage size conversions.
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
