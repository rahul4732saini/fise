"""
Errors Module
-------------

This module defines error classes used throughout the
FiSE project to handle various exceptional scenarios.
"""

import sys


class QueryHandleError(Exception):
    """
    Exception raised when there is an error handling the query.
    """

    _error: str

    def __init__(self, description: str = "") -> None:

        # Only prints the error description if specified
        # explicitly else prints any empty string.
        if description:
            description = "\nDescription: " + description

        print(
            f"\033[31m{self._error}{description}\033[0m",
            file=sys.stderr,
        )
        super().__init__()


class QueryParseError(QueryHandleError):
    """
    Exception raised when there is an error in parsing the query.
    """

    _error = "QueryParseError: There was an error in parsing the query."


class OperationError(QueryHandleError):
    """
    Exception raised when there is an error in processing the query.
    """

    _error = "OperationError: There was an error in processing the query."
