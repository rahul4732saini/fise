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

    def __init__(self, description: str) -> None:
        print(
            "Error: Unable to parse the query.",
            f"Description: {description}",
            sep="\n",
        )
        sys.exit(1)
