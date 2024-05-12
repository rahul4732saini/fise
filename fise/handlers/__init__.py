r"""
Handlers Package
----------------

This package provides a collection of objects and methods designed for
parsing and processing user-specified search and manipulation queries.
"""

import re
from pathlib import Path

import pandas as pd

from ..common import constants
from ..errors import QueryParseError
from ..shared import QueryInitials, ExportData
from .parsers import FileQueryParser, FileDataQueryParser, DirectoryQueryParser
from .operators import FileQueryOperator, FileDataQueryOperator, DirectoryQueryOperator


class QueryHandler:
    r"""
    QueryHandler defines methods for handling, parsing and
    processing user-specified search and manipulation queries.
    """

    __slots__ = ("_query",)

    def __init__(self, query: list[str]) -> None:
        r"""
        Creates an instance of the `QueryHandler` class.
        """
        self._query = query

    @staticmethod
    def _parse_export_data(query: list[str]) -> ExportData | None:
        r"""
        Parses export data from the query if specified else returns `None`.
        """

        if query[0].lower() != "export":
            return
        
        if query[1].lower().startswith("sql"):
            if not re.match(rf"^SQL\[({"|".join(constants.DATABASES)})\]$", query[1]):
                QueryParseError(
                    "Unable to parse SQL database name."
                )

            return ExportData("database", query[1][4:-1])
        
        else:
            path: Path = Path(query[1])

            if not path.is_file():
                QueryParseError(
                    "The path specified for exporting search records must be an existing file."
                )

            return ExportData("file", path)
