r"""
Handlers Package
----------------

This package provides a collection of objects and methods designed for
parsing and processing user-specified search and manipulation queries.
"""

from .parsers import FileQueryParser, FileDataQueryParser, DirectoryQueryParser
from .operators import FileQueryOperator, FileDataQueryOperator, DirectoryQueryOperator


class QueryHandler:
    r"""
    QueryHandler defines methods for handling, parsing and
    processing user-specified search and manipulation queries.
    """
