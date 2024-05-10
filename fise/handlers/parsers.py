r"""
Parsers Module
--------------

This modules comprises objects and methods for parsing user
queries extracting relavent data for further processing.
"""

from typing import Literal


class FileQueryParser:
    r"""
    FileQueryParsers defined methods for parsing
    file search/manipulation operation queries.
    """

    __slots__ = "_query", "_operation"

    def __init__(
        self, query: list[str], operation: Literal["select", "remove"]
    ) -> None:
        r"""
        Creates an instance of `FileQueryParser` class.

        #### Params:
        - query (list[str]): query to be parsed.
        - operation ['select' | 'remove']: the operation to be performed upon the query.
        """
        self._query = query
        self._operation = operation
