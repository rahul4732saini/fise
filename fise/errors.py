"""
Errors Module
-------------

This module defines error classes for handling the
various exceptional scenarios within the project.
"""

import sys


class QueryHandleError(Exception):
    """
    This exception is raised when there
    is an error while handling the query.
    """

    _error: str = "QueryHandleError: There is an error in handling the query."

    def __init__(self, description: str = "") -> None:

        # Only prints the error description if specified explicitly.
        if description:
            description = "\nDescription: " + description

        print(
            f"\033[31m{self._error}{description}\033[0m",
            flush=True,
            file=sys.stderr,
        )

        super().__init__()


class QueryParseError(QueryHandleError):
    """
    This exception is raised when there
    is an error while parsing the query.
    """

    _error = "QueryParseError: An error occured while parsing the query."


class OperationError(QueryHandleError):
    """
    This exception is raised when there
    is an error while processing the query.
    """

    _error = "OperationError: An error occured while processing the query."
