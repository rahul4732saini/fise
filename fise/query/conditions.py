"""
Conditions Module
-----------------

This module comprises classes and functions
for parsing and evaluating query conditions.
"""

import re
from typing import Callable, Sequence, Optional, Union, TypeAlias

from .. import extractors
from common import constants, tools
from errors import QueryParseError, OperationError
from shared import Condition
from entities import BaseEntity
from fields import BaseField
from entities import BaseEntity
from dataclasses import dataclass


QueryConditionType: TypeAlias = Union[bool, "Condition", "ConditionListNode"]


@dataclass(slots=True, eq=False, frozen=True)
class Condition:
    """
    Condition class encapsulates individual
    query condition specifications.
    """

    operator: str
    left: QueryAttribute
    right: QueryAttribute

    def _evaluate_operand(
        self, operand: QueryAttribute, entity: BaseEntity
    ) -> QueryAttribute:
        """
        Evalutes the specified condition operand
        based on the specified entity object.
        """

        if isinstance(operand, list):
            return [self._evaluate_operand(op, entity) for op in operand]

        elif isinstance(operand, BaseField):
            return operand.evaluate(entity)

        return operand

    def evaluate_operands(
        self, entity: BaseEntity
    ) -> tuple[QueryAttribute, QueryAttribute]:
        """
        Evaluates the encapsulated condition operands
        based on the specified entity object.
        """

        left = self._evaluate_operand(self.left, entity)
        right = self._evaluate_operand(self.right, entity)

        return left, right


@dataclass(slots=True)
class ConditionListNode:
    """
    ConditionListNode class represents an individual
    node in the query conditions linked list.
    """

    condition: QueryConditionType

    # Stores the operator immediately adjacent to the condition.
    operator: str | None = None
    next: Optional["ConditionListNode"] = None


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
            return extractors.parse_datetime(operand) or operand

        elif constants.FLOAT_PATTERN.match(operand):
            return float(operand)

        elif operand.isdigit():
            return int(operand)

        elif operand.lower() == "none":
            return None

        # If none of the above conditions match, the operand
        # is assumed to be a query field and parse accordingly.
        return extractors.parse_field(operand, self._entity)

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
            if token.lower() in constants.LOGICAL_OPEATORS:
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

    __slots__ = "_conditions", "_method_map", "_logical_method_map"

    def __init__(self, subquery: list[str], entity: int) -> None:
        """
        Creates an instance of the `ConditionHandler` class.

        #### Params:
        - subquery (list[str]): Subquery comprising the query conditions.
        - entity (int): Entity being operated upon.
        """

        # Maps logical operators with corresponding evaluation methods.
        self._logical_method_map: dict[str, Callable[[bool, bool], bool]] = {
            "and": self._and,
            "or": self._or,
        }

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

    def _eval_operand(self, operand: Any, entity: BaseEntity) -> Any:
        """
        Evaluates the specified condition operand.

        #### Params:
        - operand (Any): Operand to be processed.
        - entity (BaseEntity): Entity being operated upon.
        """

        if isinstance(operand, BaseField):
            operand = operand.evaluate(entity)

        elif isinstance(operand, list):
            return [self._eval_operand(e, entity) for e in operand]

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
            return self._eval_conditions(condition, entity)

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
        conditions: list[bool | str | list | Condition],
        operator: str,
        entity: BaseEntity,
    ) -> list[bool | str | list | Condition]:
        """
        Evaluates condition segments seperated by the specified operator.

        #### Params:
        - conditions (list): List of query conditions.
        - operator (str): Logical operator which has to be evaluated.
        - entity (BaseEntity): Entity to be operated upon.
        """

        cur: str = ""
        res: list[bool | str | list | Condition] = []

        for token in conditions:
            if isinstance(token, str) and token in constants.LOGICAL_OPEATORS:
                res.append(cur := token)

            elif cur == operator:
                result = self._logical_method_map[res.pop()](
                    res.pop(), self._eval_condition(token, entity)
                )

                res.append(result)
                cur = ""

            else:
                res.append(self._eval_condition(token, entity))

        return res

    def _eval_conditions(
        self,
        conditions: list[str | Condition | list],
        entity: BaseEntity,
    ) -> bool:
        """
        Evaluates all the query conditions.

        #### Params:
        - conditions (list): List comprising the conditions along with their separators.
        - entity (BaseEntity): Entity being operated upon.
        """

        # Evaluates the conditions seperated by the conjunction operator.
        conditions = self._eval_condition_segments(
            conditions, constants.OP_CONJUNCTION, entity
        )

        # Evaluates the conditions seperated by the disjunction operator.
        conditions = self._eval_condition_segments(
            conditions, constants.OP_DISJUNCTION, entity
        )

        return conditions[0]

    def eval_conditions(self, entity: BaseEntity) -> bool:
        """
        Evaluates the query conditions

        #### Params:
        - entity (BaseEntity): Entity being operated upon.
        """
        return self._eval_conditions(self._conditions, entity)

    @staticmethod
    def _and(x: bool, y: bool, /) -> bool:
        return x and y

    @staticmethod
    def _or(x: bool, y: bool, /) -> bool:
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
    def _like(string: str, pattern: re.Pattern) -> bool:
        return bool(pattern.match(string))
