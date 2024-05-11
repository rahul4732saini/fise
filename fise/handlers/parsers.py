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

    @staticmethod
    def _parse_fields(attrs: list[str] | str) -> list[str]:
        r"""
        Parses the select query fields.
        """

        if type(attrs) is list:
            attrs = "".join(attrs)

        # Replaces the `*` field with a string representation of all
        # the fields and splits the string into a list of fields.
        fields: list[str] = attrs.replace("*", ",".join(constants.FILE_FIELDS)).split(
            ","
        )

        # Verifies all the file search fields.
        assert all(
            i in constants.FILE_FIELDS | constants.FILE_FIELD_ALIASES.keys()
            for i in fields
        )

        return fields

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
