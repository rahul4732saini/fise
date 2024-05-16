"""
Errors Module
-------------

This module defines error classes used throughout the
FiSE project to handle various exceptional scenarios.
"""


class QueryHandleError(Exception):
    """
    Exception raised when there is an error handling the query.
    """


class BaseError:
    """
    BaseError class serves as a base class for all error classes.
    """

    _error: str

    def __init__(self, description: str) -> None:
        print(f"\033[91m{self._error}\nDescription: {description}\033[0m")

        # Raises an exception to terminate the process. To be handled
        # by another module to start a new query handling process.
        raise QueryHandleError


class QueryParseError(BaseError):
    """
    Exception raised when there is an error in parsing the query.
    """

    _error = "QueryParseError: There was an error in parsing the query."


class OperationError(BaseError):
    """
    Exception raised when there is an error in processing the query.
    """

    _error = "OperationError: There was an error in processing the query."
