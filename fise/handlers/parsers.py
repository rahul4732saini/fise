"""
Parsers Module
--------------

This module comprises objects and methods for parsing user
queries extracting relevant data for further processing.
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Generator, Callable, override, Any

from errors import QueryParseError, OperationError
from common import constants
from shared import (
    FileSearchQuery,
    DeleteQuery,
    SearchQuery,
    Directory,
    Condition,
    DataLine,
    Field,
    File,
)


def _parse_path(subquery: list[str]) -> tuple[bool, Path]:
    """
    Parses the file/directory path and its type from the specified sub-query.
    """

    if subquery[0].lower() in constants.PATH_TYPES:
        is_absolute: bool = subquery[0].lower() == "absolute"

        return is_absolute, Path(subquery[1])

    # Returns `False` for a relative path type if not specified in query.
    return False, Path(subquery[0])


def _get_from_keyword_index(query: list[str]) -> int:
    """
    Returns the index of the 'from' keyword in the file query.
    """

    match: str[str] = {"from", "FROM"}

    for i, kw in enumerate(query):
        if kw in match:
            return i
    else:
        QueryParseError("Cannot find 'FROM' keyword in the query.")


class ConditionParser:
    """
    ConditionParser defines methods for parsing
    query conditions for search/delete operations.
    """

    __slots__ = "_query", "_operand", "_conditions", "_method_map", "_aliases"

    # Regular expression patterns for matching fields in query conditions.
    _string_pattern = re.compile(r"^('|\").*('|\")$")
    _float_pattern = re.compile(r"^-?\d+(\.)\d+$")
    _tuple_pattern = re.compile(r"^\(.*\)$")

    def __init__(self, subquery: list[str], operand: constants.OPERANDS) -> None:
        """
        Creates an instance of the `ConditionParser` class.

        #### Params:
        - subquery (list[str]): subquery to be parsed.
        """
        self._query = subquery
        self._operand = operand

        self._aliases = (
            constants.FILE_FIELD_ALIASES
            | constants.DATA_FIELD_ALIASES
            | constants.DIR_FIELD_ALIASES
        )

        # Maps operator names with coresponding evaluation methods.
        self._method_map: dict[str, Callable[[Any, Any], bool]] = {
            ">=": self._ge,
            "<=": self._le,
            "<": self._lt,
            ">": self._gt,
            "=": self._eq,
            "!=": self._ne,
            "like": self._like,
            "in": self._contains,
            "between": self._between,
        }

        self._conditions = list(self._parse_conditions())

    def _parse_comparison_operand(self, field: str) -> Field | str | float | int:
        """
        Parses individual operands specified within a comparison
        expression for appropriate data type conversion.
        """

        if self._string_pattern.match(field):
            # Strips the leading and trailing quotes and returns the string.
            return field[1:-1]

        elif self._float_pattern.match(field):
            return float(field)

        elif field.isdigit():
            return int(field)

        # If none of the above conditions are matched, the field is
        # assumed to be a query field and returns as a `Field` object.
        return Field(field)

    def _parse_conditional_operand(
        self, field: str, operator: str
    ) -> tuple | re.Pattern:
        """
        Parses individual operands specified within a conditional expression.
        """

        if operator == "like":
            return re.compile(field[1:-1])

        # In case of a `IN` or `BETWEEN` operation, tuples are defined as
        # second operands. The below mechanism parses and creates a list
        # out of the string formatted tuple.
        else:
            if not self._tuple_pattern.match(field):
                QueryParseError(
                    f"Invalid query pattern around {" ".join(self._query)!r}"
                )

            # Parses and creates a list of individual
            # operands present within specified tuple.
            field: list[str] = [
                self._parse_comparison_operand(i) for i in field[1:-1].split(",")
            ]

            if operator == "between" and len(field) != 2:
                QueryParseError(
                    "The tuple specified for `BETWEEN` conditional "
                    "operation must only comprises two elements."
                )

        return field

    def _parse_condition(self, condition: list[str]) -> Condition:
        """
        Parses individual query conditions.
        """

        if len(condition) < 3:
            QueryParseError(f"Invalid query syntax around {" ".join(condition)}")

        for i in constants.COMPARISON_OPERATORS | constants.CONDITIONAL_OPERATORS:
            if condition[1] == i:
                operator: str = i
                break
        else:
            QueryParseError(f"Invalid query syntax around {" ".join(self._query)!r}")

        field1 = self._parse_comparison_operand(condition[0])
        field2 = (
            self._parse_comparison_operand(condition[2])
            if operator in constants.COMPARISON_OPERATORS
            else self._parse_conditional_operand("".join(condition[2:]), operator)
        )

        return Condition(field1, operator, field2)

    def _parse_conditions(self) -> Generator[Condition | str, None, None]:
        """
        Parses the query conditions and returns a `typing.Generator` object of the
        parsed conditions as `Condition` objects also including the condition
        seperators `and` and `or` as string objects.
        """

        # Stores individual conditions during iteration.
        condition = []

        for token in self._query:
            if token in constants.CONDITION_SEPERATORS:
                yield self._parse_condition(condition)
                yield token

                condition.clear()

                continue

            condition.append(token)

        # Parses the last condition specified in the query.
        if condition:
            yield self._parse_condition(condition)

    def _evaluate_operand(self, operand: Any, obj: File | DataLine | Directory) -> Any:
        r"""
        Evaluates the specified condition operand.

        #### Params:
        - operand (Any): operand to be processed.
        - obj (File | DataLine | Directory): Metadata object for extracting field values.
        """

        if isinstance(operand, Field):
            try:
                field: str = operand.field
                operand = getattr(obj, self._aliases.get(field, field))

            except AttributeError:
                QueryParseError(
                    f"Invalid field {operand.field!r} specified in query conditions."
                )

            if isinstance(operand, Path):
                operand = str(operand)

        return operand

    def _evaluate_condition(
        self, condition: Condition, obj: File | DataLine | Directory
    ) -> bool:
        r"""
        Evaluates the specified condition.

        #### Params:
        - condition (Condition): condition to be processed.
        - obj (File | DataLine | Directory): Metadata object for extracting field values.
        """

        # Evaluates the condition operands.
        operand1, operand2 = self._evaluate_operand(
            condition.operand1, obj
        ), self._evaluate_operand(condition.operand2, obj)

        try:
            # Process the operation with a method coressponding to the name
            # of the operator in the `_method_map` instance attribute.
            response: bool = self._method_map[condition.operator](operand1, operand2)
        except (TypeError, ValueError):
            OperationError("Unable to process the query conditions.")

        return response

    def _eval_condition_segments(
        self, segment: list[Condition | str], obj: File | DataLine | Directory
    ) -> bool:
        r"""
        Evaluates the specified condition segment.

        #### Params:
        - segment (list): query condition segment to be evaluated.
        - obj (File | DataLine | Directory): Metadata object for extracting field values.
        """

        # Evalautes individual conditions if not done yet.
        if isinstance(segment[0], Condition):
            segment[0] = self._evaluate_condition(segment[0], obj)

        if isinstance(segment[2], Condition):
            segment[2] = self._evaluate_condition(segment[2], obj)

        return (
            segment[0] and segment[2]
            if segment[1] == "and"
            else segment[0] or segment[2]
        )

    @staticmethod
    def _evaluate_and(x: bool, y: bool, /) -> bool:
        return x and y

    @staticmethod
    def _evaluate_or(x: bool, y: bool, /) -> bool:
        return x or y

    @staticmethod
    def _gt(x: Any, y: Any, /) -> bool:
        return x > y

    @staticmethod
    def _ge(x: Any, y: Any, /) -> bool:
        return x >= y

    @staticmethod
    def _lt(x: Any, y: Any, /) -> bool:
        return x < y

    @staticmethod
    def _le(x: Any, y: Any, /) -> bool:
        return x <= y

    @staticmethod
    def _eq(x: Any, y: Any, /) -> bool:
        return x == y

    @staticmethod
    def _ne(x: Any, y: Any, /) -> bool:
        return x != y

    @staticmethod
    def _contains(x: Any, y: list[Any], /) -> bool:
        return x in y

    @staticmethod
    def _between(x: Any, y: tuple[Any, Any], /) -> bool:
        return y[0] <= x <= y[1]

    @staticmethod
    def _like(pattern: re.Pattern, string: str) -> bool:
        return pattern.match(string)


class FileQueryParser:
    """
    FileQueryParser defines methods for parsing
    file search/delete operation queries.
    """

    __slots__ = "_query", "_operation", "_size_unit"

    _size_field_pattern = re.compile(
        rf"^size(\[({'|'.join(constants.SIZE_CONVERSION_MAP)})\]|)$"
    )

    def __init__(self, subquery: list[str], operation: constants.OPERATIONS) -> None:
        """
        Creates an instance of `FileQueryParser` class.

        #### Params:
        - subquery (list[str]): subquery to be parsed.
        - operation (constants.OPERATIONS): the operation to be performed upon the query.
        """

        # This parser object accepts the subquery and parses only the fields, directory/file
        # and conditions defined within the query. The initials are parsed before-hand and
        # the remaining is handed and parsed here.

        self._query = subquery
        self._operation = operation

        # Default size unit for file search queries.
        self._size_unit = "B"

    def _parse_fields(self, attrs: list[str] | str) -> list[str]:
        """
        Parses the search query fields.
        """

        if type(attrs) is list:
            attrs = "".join(attrs)

        fields = []

        file_fields: set[str] = (
            constants.FILE_FIELDS | constants.FILE_FIELD_ALIASES.keys()
        )

        # Iteratres through the specified tokens, parses and stores them in the `fields` list.
        for field in attrs.split(","):
            if field == "*":
                fields.extend(constants.FILE_FIELDS)

            elif field.startswith("size"):
                if not self._size_field_pattern.match(field):
                    QueryParseError(
                        f"Found an invalid field {field} in the search query."
                    )

                # Parses the size unit.
                if field[5:-1]:
                    self._size_unit = field[5:-1]

                fields.append("size")

            elif field in file_fields:
                fields.append(field)

            else:
                QueryParseError(
                    f"Found an invalid field {field!r} in the search query."
                )

        return fields

    @staticmethod
    def _parse_directory(subquery: list[str]) -> tuple[Path, str]:
        """
        Parses the directory path and its type from the specified sub-query.
        """
        type_, path = _parse_path(subquery)

        if not path.is_dir():
            QueryParseError("The specified path for lookup must be a directory.")

        return path, type_

    def _parse_remove_query(self) -> DeleteQuery:
        """
        Parses the file deletion query.
        """

        if self._query[0].lower() != "from":
            QueryParseError("Cannot find 'FROM' keyword in the query.")

        # TODO: condition parsing.

        return DeleteQuery(
            *self._parse_directory(self._query[1:]), lambda metadata: True
        )

    def _parse_search_query(self) -> FileSearchQuery:
        """
        Parses the file search query.
        """

        from_index: int = _get_from_keyword_index(self._query)

        fields: list[str] = self._parse_fields(self._query[:from_index])
        directory, path_type = self._parse_directory(self._query[from_index + 1 :])

        # TODO: condition parsing

        return FileSearchQuery(
            directory, path_type, lambda metadata: True, fields, self._size_unit
        )

    def parse_query(self) -> FileSearchQuery | DeleteQuery:
        """
        Parses the file search/deletion query.
        """
        return (
            self._parse_search_query()
            if self._operation == "search"
            else self._parse_remove_query()
        )


class FileDataQueryParser:
    """
    FileDataQueryParser defines methods for
    parsing file data search operation queries.
    """

    __slots__ = ("_query",)

    def __init__(self, subquery: list[str]) -> None:
        """
        Creates an instance of the `FileDataQueryParser` class.

        #### Params:
        - subquery (list[str]): query to be parsed.
        """

        # This parser object accepts the subquery and parses only the fields, directory/file
        # and conditions defined within the query. The initials are parsed before-hand and
        # the remaining is handed and parsed here.

        self._query = subquery

    @staticmethod
    def _parse_fields(attrs: list[str] | str) -> list[str]:
        """
        Parses the data search query fields.
        """

        if type(attrs) is list:
            attrs = "".join(attrs)

        fields = []

        data_fields: set[str] = (
            constants.DATA_FIELDS | constants.DATA_FIELD_ALIASES.keys()
        )

        # Iteratres through the specified tokens, parses and stores them in the `fields` list.
        for field in attrs.split(","):
            if field == "*":
                fields.extend(constants.DATA_FIELDS)

            elif field in data_fields:
                fields.append(field)

            else:
                QueryParseError(
                    f"Found an invalid field {field!r} in the search query."
                )

        return fields

    @staticmethod
    def _parse_path(subquery: list[str]) -> tuple[Path, str]:
        """
        Parses the file/directory path and its type from the specified sub-query.
        """
        type_, path = _parse_path(subquery)

        if (path.is_dir() or path.is_file()) is False:
            QueryParseError(
                "The specified path for lookup must be a file or directory."
            )

        return path, type_

    def parse_query(self) -> SearchQuery:
        """
        Parses the file data search query.
        """

        from_index: int = _get_from_keyword_index(self._query)

        fields: list[str] = self._parse_fields(self._query[:from_index])
        path, path_type = self._parse_path(self._query[from_index + 1 :])

        # TODO: condition parsing

        return SearchQuery(path, path_type, lambda metadata: True, fields)


class DirectoryQueryParser(FileQueryParser):
    """
    DirectoryQueryParser defines methods for parsing
    directory search/manipulation operation queries.
    """

    __slots__ = "_query", "_operation"

    @override
    def __init__(
        self, subquery: str | list[str], operation: constants.OPERATIONS
    ) -> None:
        """
        Creates an instance of the `DirectoryQueryParser` class.

        #### Params:
        - subquery (list[str]): query to be parsed.
        - operation (constants.OPERATIONS): the operation to be performed upon the query.
        """

        # This parser object accepts the subquery and parses only the fields, directory/file
        # and conditions defined within the query. The initials are parsed before-hand and
        # the remaining is handed and parsed here.

        self._query = subquery
        self._operation = operation

    @override
    def _parse_fields(self, attrs: list[str] | str) -> list[str]:
        """
        Parses the directory search query fields.
        """

        if type(attrs) is list:
            attrs = "".join(attrs)

        fields = []

        dir_fields: set[str] = constants.DIR_FIELDS | constants.DIR_FIELD_ALIASES.keys()

        # Iteratres through the specified tokens, parses and stores them in the `fields` list.
        for field in attrs.split(","):
            if field == "*":
                fields.extend(constants.FILE_FIELDS)

            elif field in dir_fields:
                fields.append(field)

            else:
                QueryParseError(
                    f"Found an invalid field {field!r} in the search query."
                )

        return fields

    @override
    def _parse_search_query(self) -> SearchQuery:
        """
        Parses the file search query.
        """

        from_index: int = _get_from_keyword_index(self._query)

        fields: list[str] = self._parse_fields(self._query[:from_index])
        directory, path_type = self._parse_directory(self._query[from_index + 1 :])

        # TODO: condition parsing

        return SearchQuery(directory, path_type, lambda metadata: True, fields)
