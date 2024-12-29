"""
Conditions Module
-----------------

This module comprises classes and functions
for parsing and evaluating query conditions.
"""

import re
from typing import Callable, Sequence, Optional, Union, TypeAlias

import parsers
from parsers import QueryAttribute
from common import constants
from errors import QueryParseError
from shared import QueryQueue
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
    ConditionParser class defines methods for
    parsing the user-specified query conditions.
    """

    __slots__ = "_query", "_entity", "_parsers_map"

    def __init__(self, query: QueryQueue, entity: str) -> None:
        """
        Creates an instance of the ConditionParser class.

        #### Params:
        - query (QueryQueue): `QueryQueue` object comprising the query.
        - entity (str): Name of the entity being operated upon.
        """

        self._query = query
        self._entity = entity

        # Maps operators with their corresponding condition parser methods.
        self._parsers_map: dict[str, Callable[[str, str], Condition]] = {
            constants.OP_EQ: self._eq,
            constants.OP_NE: self._ne,
            constants.OP_GT: self._gt,
            constants.OP_GE: self._ge,
            constants.OP_LT: self._lt,
            constants.OP_LE: self._le,
            constants.OP_CONTAINS: self._contains,
            constants.OP_BETWEEN: self._between,
            constants.OP_LIKE: self._like,
        }

    def _parse_binary_condition(
        self, condition: str, operator: str
    ) -> tuple[str, list[str]]:
        """
        Parses the specified binary condition based on the specified operator.

        #### Params:
        - condition (str): String comprising the condition specifications.
        - operator (str): Binary operator present in the specified condition.
        """

        operands: list[str] = condition.split(operator, maxsplit=1)

        # Raises a parse error if the operator is lexical and there
        # is no whitespace between it and either of the operands.
        if operator in constants.LEXICAL_OPERATORS and not (
            operands[0].startswith(" ") and operands[1].endswith(" ")
        ):
            raise QueryParseError(f"{condition!r} is not a valid condition.")

        operands = [operand.strip(" ") for operand in operands]

        evaluator = self._parsers_map[operator]
        condition: Condition = evaluator(*operands)

        return condition

    def _parse_condition(self, condition: str) -> Condition | ConditionListNode:
        """
        Parses the specified condition specifications.

        #### Params:
        - condition (str): String comprising the condition specifications.
        """

        if not condition:
            raise QueryParseError("Invalid query syntax!")

        elif constants.NESTED_CONDITION_PATTERN.match(condition):

            # Recursively parses the condition if nested.
            query = QueryQueue.from_string(condition[1:-1])
            return self._parse_conditions(query)

        # Looks up for the operator and parses the condition accordingly.
        for op in constants.CONDITION_OPERATORS:
            if op not in condition:
                continue

            return self._parse_binary_condition(condition, op)

        raise QueryParseError(f"{condition!r} is not a valid query condition.")

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
        self._query.pop()

        return self._parse_conditions(self._query)

    def _parse_operands(
        self, left: str, right: str
    ) -> tuple[QueryAttribute, QueryAttribute]:
        """
        Parses the specified condition operands
        and returns a tuple comprising the same.
        """

        op_left = parsers.parse_attribute(left, self._entity)
        op_right = parsers.parse_attribute(right, self._entity)

        return op_left, op_right

    def _parse_relational(self, operator: str, left: str, right: str) -> Condition:
        """Parses the query condition comprising a relational operator."""

        op_left, op_right = self._parse_operands(left, right)
        return Condition(operator, op_left, op_right)

    def _eq(self, left: str, right: str) -> Condition:
        """Parses the query conditions for the equals operation."""
        return self._parse_relational(constants.OP_EQ, left, right)

    def _ne(self, left: str, right: str) -> Condition:
        """Parses the condition for the not equals operation."""
        return self._parse_relational(constants.OP_NE, left, right)

    def _gt(self, left: str, right: str) -> Condition:
        """Parses the condition for the greater than operation."""
        return self._parse_relational(constants.OP_GT, left, right)

    def _ge(self, left: str, right: str) -> Condition:
        """Parses the condition for the greater than or equals operation"""
        return self._parse_relational(constants.OP_GE, left, right)

    def _lt(self, left: str, right: str) -> Condition:
        """Parses the condition for the lower than operation."""
        return self._parse_relational(constants.OP_LT, left, right)

    def _le(self, left: str, right: str) -> Condition:
        """Parses the condition for the lower than or equals operation."""
        return self._parse_relational(constants.OP_LE, left, right)

    def _contains(self, left: str, right: str) -> Condition:
        """Parses the condition for the contains operation."""

        op_left, op_right = self._parse_operands(left, right)

        if not isinstance(op_right, Sequence):
            raise QueryParseError(
                f"{right!r} is not a valid operand for "
                f"the {constants.OP_CONTAINS!r} operation."
            )

        return Condition(constants.OP_CONTAINS, op_left, op_right)

    def _between(self, left: str, right: str) -> Condition:
        """Parses the condition for the between operation."""

        op_left, op_right = self._parse_operands(left, right)

        # Raises an error if the right operand
        # is not an array with a length of 2.
        if not isinstance(op_right, Sequence) or len(op_right) != 2:

            raise QueryParseError(
                f"{right!r} is not a valid operand for "
                f"the {constants.OP_BETWEEN!r} operation."
            )

        return Condition(constants.OP_BETWEEN, op_left, op_right)

    def _like(self, left: str, right: str) -> Condition:
        """Parses the condition for the like operation."""

        op_left, op_right = self._parse_operands(left, right)

        if not (isinstance(op_left, str | BaseField) and isinstance(op_right, str)):
            raise QueryParseError("Invalid query conditions syntax.")

        return Condition(constants.OP_LIKE, op_left, op_right)


class ConditionHandler:
    """
    ConditionHandler class defines methods for
    handling user-specified query conditions.
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
