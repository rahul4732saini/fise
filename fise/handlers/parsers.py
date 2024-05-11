r"""
Parsers Module
--------------

This modules comprises objects and methods for parsing user
queries extracting relavent data for further processing.
"""

import re
from typing import Literal
from pathlib import Path

from ..common import constants
from ..shared import DeleteQuery, FileSearchQuery


class FileQueryParser:
    r"""
    FileQueryParser defines methods for parsing
    file search/manipulation operation queries.
    """

    __slots__ = "_query", "_operation", "_size_unit"

    _size_pattern = re.compile(
        rf"^size(\[({'|'.join(constants.SIZE_CONVERSION_MAP)})\]|)$"
    )

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

        self._size_unit = "B"

    def _parse_fields(self, attrs: list[str] | str) -> list[str]:
        r"""
        Parses the search query fields.
        """

        if type(attrs) is list:
            attrs = "".join(attrs)

        fields = []

        file_fields: set[str] = (
            constants.FILE_FIELDS | constants.FILE_FIELD_ALIASES.keys()
        )

        for field in attrs.split(","):
            if field == "*":
                fields.extend(constants.FILE_FIELDS)

            elif field.startswith("size"):
                assert self._size_pattern.match(field)

                if field[5:-1]:
                    self._size_unit = field[5:-1]

                fields.append("size")

            else:
                assert field in file_fields
                fields.append(field)

        # TODO: Custom exceptional handling

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

        for i, kw in enumerate(self._query):
            if kw in match:
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

    def _parse_search_query(self) -> FileSearchQuery:
        r"""
        Parses the file search query.
        """

        from_index: int = self._get_from_keyword_index()

        fields: list[str] = self._parse_fields(self._query[:from_index])
        directory, path_type = self._parse_directory(self._query[from_index + 1 :])

        # TODO: condition parsing

        return FileSearchQuery(
            directory, path_type, lambda metadata: True, fields, self._size_unit
        )

    def parse_query(self) -> FileSearchQuery | DeleteQuery:
        r"""
        Parses the file search/deletion query.
        """
        return (
            self._parse_search_query()
            if self._operation == "search"
            else self._parse_remove_query()
        )


class FileDataQueryParser:
    r"""
    FileDataQueryParser defines methods for
    parsing file data search operation queries.
    """
