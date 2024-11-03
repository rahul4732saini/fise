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
from shared import Condition
from entities import BaseEntity
from fields import BaseField, parse_field


class ConditionParser:
    """
    ConditionParser defined methods for parsing query
    conditions for search and delete operations.
    """

    __slots__ = "_query", "_entity"

    def __init__(self, subquery: list[str], entity: int) -> None:
        """
        Creates an instance of the `ConditionParser` class.

        #### Params:
        - subquery (list[str]): Subquery comprising the query conditions.
        - entity (int): Entity being operated upon.
        """

        self._query = subquery
        self._entity = entity

    def _parse_datetime(self, operand: str) -> datetime | None:
        """
        Parses date/datetime from the specified operand if it
        matches the corresponding pattern, else returns None.
        """

        if not constants.DATETIME_PATTERN.match(operand):
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
                f"Invalid datetime specifications {operand!r} in query conditions."
            )

    def _parse_comparison_operand(self, operand: str) -> Any:
        """
        Parses individual operands defined within a condition
        expression and converts them into appropriate data types.

        #### Params:
        - operand (str): Operand to be parsed.
        """

        if constants.STRING_PATTERN.match(operand):
            # Strips the leading and trailing quotes in the string.
            operand = operand[1:-1]

            # Returns a datetime object if it matches the ISO-8601
            # date & time pattern. Otherwise, returns a string object.
            return self._parse_datetime(operand) or operand

        elif constants.FLOAT_PATTERN.match(operand):
            return float(operand)

        elif operand.isdigit():
            return int(operand)

        elif operand.lower() == "none":
            return None

        # If none of the above conditions match, the operand
        # is assumed to be a query field and parse accordingly.
        return parse_field(operand, self._entity)

    def _parse_collective_operand(self, operand: str, operator: str) -> Any | list[str]:
        """
        Parses the second operand of a query condition as a collective object explicitly
        for an `IN` or `BETWEEN` operation based on the specified operator.
        """

        if not constants.TUPLE_PATTERN.match(operand):

            # In the context of the `IN` operation, the operand might also be a
            # string or a Field object, the following also handles this situation.
            if operator == "in":
                return self._parse_comparison_operand(operand)

            raise QueryParseError(
                f"Invalid query pattern around {' '.join(self._query)!r}"
            )

        # Parses and creates a list of individual operands.
        operands: list[Any] = [
            self._parse_comparison_operand(i.strip()) for i in operand[1:-1].split(",")
        ]

        if operator == "between" and len(operands) != 2:
            raise QueryParseError(
                "The tuple specified for the `BETWEEN` "
                "operation must only comprise two elements."
            )

        return operands

    def _parse_conditional_operand(
        self, operand: str, operator: str
    ) -> Any | list[str] | re.Pattern:
        """
        Parses the second operand specified within a query
        condition for an `IN`, `BETWEEN` or `LIKE` operation.
        """

        # In case of an `IN` or `BETWEEN` operation, the
        # operand is parsed using the following method.
        if operator != "like":
            return self._parse_collective_operand(operand, operator)

        # The operand is parsed using the following
        # mechanism in case of the `LIKE` operation.

        elif not constants.STRING_PATTERN.match(operand):
            raise QueryParseError(
                f"Invalid Regex pattern {operand} specified in query conditions"
            )

        try:
            return re.compile(operand[1:-1])

        except re.error:
            raise QueryParseError(
                f"Invalid regex pattern {operand} specified in query conditions"
            )

    def _extract_condition_elements(self, condition: list[str]) -> list[str]:
        """
        Extracts the individual elements/token present within the specified query condition.
        """

        if len(condition) == 3:

            # The operator is defined at the 1st index and is lowered in
            # case it is a conditional operator and is typed in uppercase.
            condition[1] = condition[1].lower()

            if condition[1] not in (
                constants.COMPARISON_OPERATORS | constants.CONDITIONAL_OPERATORS
            ):
                raise QueryParseError(
                    f"Invalid query syntax around {' '.join(self._query)!r}"
                )

            return condition

        # The condition is parsed using differently if all the
        # tokens are not already separated as individual strings.

        # In such case, the condition is only looked up for comparison operators
        # for partitioning it into individual tokens as conditional operators
        # require whitespaces around them which are already parsed beforehand
        # using the `tools.parse_query` function.
        for i in constants.COMPARISON_OPERATORS:
            if i not in condition[0]:
                continue

            # If the operator is present within the condition, all the
            # individual tokens are partitioned into individual strings.
            condition[:] = condition[0].partition(i)
            break

        else:
            raise QueryParseError(
                f"Invalid query syntax around {' '.join(condition)!r}"
            )

        # Strips out redundant whitespaces around the tokens.
        for index, value in enumerate(condition):
            condition[index] = value.strip()

        return condition

    def _parse_condition(self, condition: list[str]) -> list | Condition:
        """
        Parses individual query conditions.

        #### Params:
        - condition (list[str]): Condition to be parsed.
        """

        if len(condition) == 1 and constants.TUPLE_PATTERN.match(condition[0]):
            return list(
                self._parse_conditions(tools.parse_query(condition[0][1:-1])),
            )

        # All individual strings are combined into a single string to parse them
        # differently if the length of the list is not 3, i.e., the tokens are
        # not already separated into individual strings.
        if len(condition) != 3:
            condition = ["".join(condition)]

        condition[:] = self._extract_condition_elements(condition)

        operator = condition[1]
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
    ) -> Generator[str | list | Condition, None, None]:
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
        yield self._parse_condition(condition)

    def parse_conditions(self) -> Generator[str | list | Condition, None, None]:
        """Parses and returns a generator of the query conditions."""
        return self._parse_conditions(self._query)


class ConditionHandler:
    """
    ConditionHandler defines methods for handling and evaluating
    query conditions for search and delete operations.
    """

    __slots__ = "_conditions", "_method_map"

    def __init__(self, subquery: list[str], entity: int) -> None:
        """
        Creates an instance of the `ConditionHandler` class.

        #### Params:
        - subquery (list[str]): Subquery comprising the query conditions.
        - entity (int): Entity being operated upon.
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
        self._conditions = list(ConditionParser(subquery, entity).parse_conditions())

    def _eval_operand(self, operand: Any, obj: BaseEntity) -> Any:
        """
        Evaluates the specified condition operand.

        #### Params:
        - operand (Any): Operand to be processed.
        - obj (BaseEntity): Metadata object for extracting field values.
        """

        if isinstance(operand, BaseField):
            operand = operand.evaluate(obj)

        elif isinstance(operand, list):
            return [self._eval_operand(e, obj) for e in operand]

        return operand

    def _eval_condition(
        self, condition: bool | list | Condition, entity: BaseEntity
    ) -> bool:
        """
        Evaluates the specified condition.

        #### Params:
        - condition (list | Condition): Condition(s) to be evaluated.
        - entity (BaseEntity): Entity being operated upon.
        """

        if isinstance(condition, bool):
            return condition

        # Recursively evaluates if the condition is nested.
        if isinstance(condition, list):
            return self._eval_all_conditions(condition, entity)

        # Evaluates the condition operands.
        operand1, operand2 = self._eval_operand(
            condition.operand1, entity
        ), self._eval_operand(condition.operand2, entity)

        try:
            # Evaluates the operation with a method corresponding to the name
            # of the operator defined in the '_method_map' instance attribute.
            response: bool = self._method_map[condition.operator](operand1, operand2)

        except Exception:
            raise OperationError("Unable to process the query conditions.")

        else:
            return response

    def _eval_condition_segments(
        self,
        segment: list[bool | str | Condition | list],
        obj: BaseEntity,
    ) -> bool:
        """
        Evaluates the specified condition segment comprising
        two conditions along with a seperator.

        #### Params:
        - segment (list): Query condition segment to be evaluated.
        - obj (BaseEntity): Metadata object for extracting field values.
        """

        # Evaluates individual conditions present at the
        # 0th and 2nd position in the list if not done yet.
        for i in (0, 2):
            if not isinstance(segment[i], bool):
                segment[i] = self._eval_condition(segment[i], obj)

        return (
            segment[0] and segment[2]
            if segment[1] == constants.OP_CONJUNCTION
            else segment[0] or segment[2]
        )

    def _eval_all_conditions(
        self,
        conditions: list[str | Condition | list],
        obj: BaseEntity,
    ) -> bool:
        """
        Evaluates all the query conditions.

        #### Params:
        - conditions (list): List comprising the conditions along with their separators.
        - obj (BaseEntity): Metadata object for extracting field values.
        """

        # Adds a `True and` condition at the beginning of the list to avoid
        # explicit definition of a mechanism for evaluating a single condition.
        segments: list[Any] = [True, constants.OP_CONJUNCTION] + conditions
        ctr: int = 0

        # Evaluates conditions separated by `and` operator.
        for _ in range(len(segments) // 2):
            if segments[ctr + 1] == constants.OP_DISJUNCTION:
                # Increments the counter by 1 to skip the
                # conditions separated by the `or` operator.
                ctr += 2
                continue

            segments[ctr : ctr + 3] = [
                self._eval_condition(segments[ctr], obj)
                and self._eval_condition(segments[ctr + 2], obj)
            ]

        # Evaluates conditions separated by `or` operator.
        for _ in range(len(segments) // 2):
            # Replaces the conditions with the evaluated boolean value.
            segments[:3] = [
                self._eval_condition(segments[0], obj)
                or self._eval_condition(segments[2], obj)
            ]

            if segments[0]:
                return True

        # Extracts the singe-most boolean value from the list.
        result: bool = segments[0]

        return result

    def eval_conditions(self, obj: BaseEntity) -> bool:
        """
        Evaluates the query conditions

        #### Params:
        - obj (BaseEntity): Metadata object for extracting field values.
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
