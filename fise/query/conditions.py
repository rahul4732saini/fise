"""
Conditions Module
-----------------

This module comprises classes for parsing and evaluating query
conditions, and filtering file, data and directory records.
"""

import re
from datetime import datetime
from typing import Generator, Callable, Any

from common import constants, tools
from errors import QueryParseError, OperationError
from shared import File, DataLine, Directory, Field, Condition, Size


class ConditionParser:
    """
    ConditionParser defined methods for parsing query
    conditions for search and delete operations.
    """

    __slots__ = "_query", "_method_map", "_lookup_fields", "_field_aliases"

    # Regular expression patterns for matching fields in query conditions.
    _string_pattern = re.compile("^['\"].*['\"]")
    _tuple_pattern = re.compile(r"^\(.*\)$")
    _float_pattern = re.compile(r"^-?\d+\.\d+$")

    # This regex pattern only matches date and datetime formats, and does
    # not explicitly verify the validity of the date and time values.
    _datetime_pattern = re.compile(
        r"['\"]\d{4}-\d{1,2}-\d{1,2}( \d{1,2}:\d{1,2}:\d{1,2})?['\"]$"
    )

    _fields: dict[str, tuple[str, ...]] = {
        "file": constants.FILE_FIELDS,
        "dir": constants.DIR_FIELDS,
        "data": constants.DATA_FIELDS,
    }

    _aliases: dict[str, dict[str, str]] = {
        "file": constants.FILE_FIELD_ALIASES,
        "dir": constants.DIR_FIELD_ALIASES,
        "data": constants.DATA_FIELD_ALIASES,
    }

    def __init__(self, subquery: list[str], operation_target: str) -> None:
        """
        Creates an instance of the `ConditionParser` class.

        #### Params:
        - subquery (list[str]): Subquery comprising the conditions.
        - operation_target (str): Targeted operand in the operation (file/data/directory).
        """
        self._query = subquery

        self._lookup_fields = set(self._fields[operation_target])
        self._field_aliases = self._aliases[operation_target]

    def _parse_datetime(self, operand: str) -> datetime | None:
        """
        Parses date/datetime from the specified operand if it
        matches the corresponding pattern, else returns None.
        """

        if not self._datetime_pattern.match(operand):
            return None

        try:
            return datetime.strptime(operand, r"%Y-%m-%d %H:%M:%S")

        except ValueError:
            # Passes without raising an error if in
            # case the operand matches the date format.
            ...

        try:
            return datetime.strptime(operand, r"%Y-%m-%d")

        except ValueError:
            raise QueryParseError(
                f"Invalid datetime format around {' '.join(self._query)!r}"
            )

    def _parse_field(self, field: str) -> Field | Size:
        """
        Parses the specified string formatted field.
        """

        low_field: str = field.lower()
        field = self._field_aliases.get(low_field, field)

        if low_field not in self._lookup_fields:
            raise QueryParseError(f"Found an invalid field {field!r} in the query.")

        if field.startswith("size"):
            return Size.from_string(field)

        return Field(field)

    def _parse_comparison_operand(self, operand: str) -> Any:
        """
        Parses individual operands specified within a comparison
        operation expression for appropriate data type conversion.

        #### Params:
        - operand (str): Operand to be parsed.
        """

        if self._string_pattern.match(operand):
            # Strips the leading and trailing quotes in the string.
            operand = operand[1:-1]
            timedate: datetime | None = self._parse_datetime(operand)

            return timedate if timedate else operand

        elif self._float_pattern.match(operand):
            return float(operand)

        elif operand.isdigit():
            return int(operand)

        if operand.lower() == "none":
            return None

        # If none of the above conditions are matched, the operand is assumed
        # to be a query field and returned as `Field` object or explicitly as
        # a `Size` object for size fields.
        return self._parse_field(operand)

    def _parse_conditional_operand(
        self, operand: str, operator: str
    ) -> list[str] | re.Pattern:
        """
        Parses individual operands specified within a conditional operation expression.
        """

        if operator == "like":
            if not self._string_pattern.match(operand):
                raise QueryParseError(
                    f"Invalid query pattern around {' '.join(self._query)!r}"
                )

            return re.compile(operand[1:-1])

        # In case of a `IN` or `BETWEEN` operation, second operand is expected to be
        # a string formatted tuple. The below mechanism parses it and creates a list.
        else:
            if not self._tuple_pattern.match(operand):
                raise QueryParseError(
                    f"Invalid query pattern around {' '.join(self._query)!r}"
                )

            # Parses and creates a list of individual operands.
            operands: list[Any] = [
                self._parse_comparison_operand(i.strip())
                for i in operand[1:-1].split(",")
            ]

            if operator == "between" and len(operands) != 2:
                raise QueryParseError(
                    "The tuple specified for `BETWEEN` conditional "
                    "operation must only comprises two elements."
                )

        return operands

    def _parse_condition(
        self, condition: list[str]
    ) -> Condition | list[str | Condition]:
        """
        Parses individual query conditions.

        #### Params:
        - condition (list[str]): Condition to be parsed.
        """

        # Evaluates and returns a list of conditions if nested.
        if len(condition) == 1 and self._tuple_pattern.match(condition[0]):
            return list(
                self._parse_conditions(tools.parse_query(condition[0][1:-1])),
            )

        elif len(condition) < 3:
            raise QueryParseError(
                f"Invalid query syntax around {' '.join(condition)!r}"
            )

        condition[1] = condition[1].lower()

        for i in constants.COMPARISON_OPERATORS | constants.CONDITIONAL_OPERATORS:
            if i == condition[1]:
                operator: str = i
                break
        else:
            raise QueryParseError(
                f"Invalid query syntax around {' '.join(self._query)!r}"
            )

        operand1: Any = self._parse_comparison_operand(condition[0])

        # Parses the second operand accordingly based on the specified operator.
        operand2: Any = (
            self._parse_comparison_operand(condition[2])
            if operator in constants.COMPARISON_OPERATORS
            else self._parse_conditional_operand(condition[2], operator)
        )

        return Condition(operand1, operator, operand2)

    def _parse_conditions(
        self, subquery: list[str]
    ) -> Generator[Condition | str | list, None, None]:
        """
        Parses the query conditions.

        #### Params:
        - subquery (list): Subquery comprising the query conditions.
        """

        # Stores individual conditions during iteration.
        condition: list[str] = []

        for token in subquery:
            if token.lower() in constants.CONDITION_SEPARATORS:
                yield self._parse_condition(condition)
                yield token.lower()

                condition.clear()

                continue

            condition.append(token)

        # Parses the last condition specified in the query.
        if condition:
            yield self._parse_condition(condition)

    def parse_conditions(self) -> Generator[Condition | str | list, None, None]:
        """
        Parses the query conditions and returns a `typing.Generator` object of the parsed
        conditions as `Condition` objects also including the condition separators `and`
        and `or` as string objects or a list of all of the above if nested.
        """
        return self._parse_conditions(self._query)


class ConditionHandler:
    """
    ConditionHandler defines methods for handling and evaluating
    query conditions for search and delete operations.
    """

    # Aliases for query fields.
    _aliases = (
        constants.FILE_FIELD_ALIASES
        | constants.DATA_FIELD_ALIASES
        | constants.DIR_FIELD_ALIASES
    )

    __slots__ = "_conditions", "_method_map"

    def __init__(self, subquery: str, operation_target: str) -> None:
        """
        Creates an instance of the `ConditionHandler` class.

        #### Params:
        - conditions (list): List of parsed query conditions.
        - operation_target (str): Targeted operand in the operation (file/data/directory).
        """

        # Maps operator notations with corresponding evaluation methods.
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

        # Parses the conditions and stores them in a list.
        self._conditions = list(
            ConditionParser(subquery, operation_target).parse_conditions()
        )

    def _eval_operand(self, operand: Any, obj: File | DataLine | Directory) -> Any:
        """
        Evaluates the specified condition operand.

        #### Params:
        - operand (Any): Operand to be processed.
        - obj (File | DataLine | Directory): Metadata object for extracting field values.
        """

        if isinstance(operand, Field):
            try:
                operand = getattr(obj, self._aliases.get(operand.field, operand.field))

            except AttributeError:
                raise QueryParseError(
                    f"Invalid field {operand.field!r} specified in query conditions."
                )

            # Converts `bytes` object into a string for
            # better compatibility in condition evaluation.
            if isinstance(operand, bytes):
                operand = str(operand)[2:-1]

        elif isinstance(operand, Size):
            size = getattr(obj, "size")

            # Converts the size into the specified unit.
            operand = size / constants.SIZE_CONVERSION_MAP[operand.unit]

        return operand

    def _eval_condition(
        self,
        condition: Condition | list[str | Condition],
        obj: File | DataLine | Directory,
    ) -> bool:
        """
        Evaluates the specified condition.

        #### Params:
        - condition (Condition): Condition to be evaluated.
        - obj (File | DataLine | Directory): Metadata object for extracting field values.
        """

        # Recursively evaluates if the condition is nested.
        if isinstance(condition, list):
            return self._eval_all_conditions(condition, obj)

        # Evaluates the condition operands.
        operand1, operand2 = self._eval_operand(
            condition.operand1, obj
        ), self._eval_operand(condition.operand2, obj)

        try:
            # Evaluates the operation with a method corresponding to the name
            # of the operator defined in the `_method_map` instance attribute.
            response: bool = self._method_map[condition.operator](operand1, operand2)
        except (TypeError, ValueError):
            raise OperationError("Unable to process the query conditions.")

        else:
            return response

    def _eval_condition_segments(
        self,
        segment: list[bool | Condition | str | list[str | Condition]],
        obj: File | DataLine | Directory,
    ) -> bool:
        """
        Evaluates the specified condition segment comprising
        two conditions along with a seperator.

        #### Params:
        - segment (list): Query condition segment to be evaluated.
        - obj (File | DataLine | Directory): Metadata object for extracting field values.
        """

        # Evaluates individual conditions if not done yet.
        if isinstance(segment[0], list | Condition):
            segment[0] = self._eval_condition(segment[0], obj)

        if isinstance(segment[2], list | Condition):
            segment[2] = self._eval_condition(segment[2], obj)

        return (
            segment[0] and segment[2]
            if segment[1] == "and"
            else segment[0] or segment[2]
        )

    def _eval_all_conditions(
        self,
        conditions: list[str | Condition | list[str | Condition]],
        obj: File | DataLine | Directory,
    ) -> bool:
        """
        Evaluates all the query conditions.

        #### Params:
        - conditions (list): List comprising the conditions along with their separators.
        - obj (File | DataLine | Directory): Metadata object for extracting field values.
        """

        # Adds a `True and` condition at the beginning of the list to avoid
        # explicit definition of a mechanism for evaluating a single condition.
        segments: list[Any] = [True, "and"] + conditions
        ctr: int = 0

        # Evaluates conditions separated by `and` operator.
        for _ in range(len(segments) // 2):
            segment: list[Any] = segments[ctr : ctr + 3]

            if segment[1] == "or":
                # Increments the counter by 1 to skip the
                # conditions separated by the `or` operator.
                ctr += 2

            else:
                segments[ctr : ctr + 3] = [self._eval_condition_segments(segment, obj)]

        # Evaluates conditions separated by `or` operator.
        for _ in range(len(segments) // 2):
            # Replaces the conditions with the evaluated boolean value.
            segments[:3] = [self._eval_condition_segments(segments[:3], obj)]

            if segments[0]:
                return True

        # Extracts the singe-most boolean value from the list.
        result: bool = segments[0]

        return result

    def eval_conditions(self, obj: File | DataLine | Directory) -> bool:
        """
        Evaluates the query conditions.

        #### Params:
        - obj (File | DataLine | Directory): Metadata object for extracting field values.
        """
        return self._eval_all_conditions(self._conditions, obj)

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
    def _like(string: str, pattern: re.Pattern) -> bool:
        return bool(pattern.match(string))
