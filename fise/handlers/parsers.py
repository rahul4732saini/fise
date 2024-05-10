r"""
Parsers Module
--------------

This modules comprises objects and methods for parsing user
queries extracting relavent data for further processing.
"""

from typing import Literal
from pathlib import Path

from ..common import constants
from ..shared import DeleteQuery, SelectQuery


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

    def _get_from_keyword_index(self) -> int:
        r"""
        Returns the index of the 'from' keyword in the query.
        """

        match = {"from", "FROM"}

        for i in range(len(self._query)):
            if self._query[i] in match:
                return i

        # TODO: Exception handling

    def _parse_remove_query(self) -> DeleteQuery:
        r"""
        Parses the file deletion query.
        """

        assert self._query[0].lower() == "from"

        if self._query[1] in constants.PATH_TYPES:
            path_type: str = self._query[1]
            path: Path = Path(self._query[2])

        else:
            path_type: str = "relative"
            path: Path = Path(self._query[1])

        assert path.is_dir()

        # TODO: condition parsing.

        return DeleteQuery(path, path_type, lambda metadata: True)
