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

    @staticmethod
    def _parse_directory(subquery: list[str]) -> tuple[Path, str]:
        r"""
        Parses the directory path and its type from the specified sub-query.
        """

        if subquery[0].lower() in constants.PATH_TYPES:
            path_type: str = subquery[0].lower()
            path: Path = Path(subquery[1])

        else:
            path_type: str = "relative"
            path: Path = Path(subquery[0])

        # Asserts if the path is a directory.
        assert path.is_dir()

        return path, path_type

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

        # TODO: condition parsing.

        return DeleteQuery(
            *self._parse_directory(self._query[1:]), lambda metadata: True
        )
