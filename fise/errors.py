r"""
Errors Module
-------------

This module defines error classes used throughout the
utility to handle various exceptional scenarios.
"""

import sys


class QueryParseError:
    r"""
    Exception raised when there is an error parsing the query.
    """

    _error = "QueryParseError: There was an error in parsing the query."

    def __init__(self, description: str) -> None:
        print(self._error, f"Description: {description}", sep="\n")
        sys.exit(1)


class OperationError:
    r"""
    Exception raised when there is an error in processing the query.
    """

    _error = "OperationError: There was an error in processing the query."

    def __init__(self, description: str) -> None:
        print(self._error, f"Desctiption: {description}", sep="\n")
        sys.exit(1)
