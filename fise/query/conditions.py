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
from common import constants, tools
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

    # Stores the operator immediately adjacent
    # on the right side of the query condition.
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

    def _parse_binary_condition(self, operator: str, operands: list[str]) -> Condition:
        """
        Parses the associated binary query condition
        based on the specified operator and operands.

        #### Params:
        - operator (str): Binary operator associated with query condition.
        - operands (list[str]): List comprising the condition operands.
        """

        # Raises a parse error if the operator is lexical and there
        # is no whitespace between it and either of the operands.
        if operator in constants.LEXICAL_OPERATORS and not (
            operands[0].endswith(" ") and operands[1].startswith(" ")
        ):
            raise QueryParseError(f"Invalid query syntax.")

        operands = [operand.strip(" ") for operand in operands]

        evaluator = self._parsers_map[operator]
        condition: Condition = evaluator(*operands)

        return condition

    def _tokenize_condition(self, condition: str) -> tuple[str, list[str]]:
        """
        Tokenizes the specified condition and returns a tuple
        comprising the operator and the associated operands.

        #### Params:
        - condition (str): String comprising the condition specifications.
        """

        # Extracts the starting and ending indices of the operator.
        indices = tools.find_base_string(condition, constants.CONDITION_OPERATORS)

        if indices is None:
            raise QueryParseError(f"{condition!r} is not a valid condition.")

        start, end = indices

        operator = condition[start:end].lower()
        operands = condition[:start], condition[end:]

        return operator, [operand for operand in operands if operand]

    def _parse_condition(self, condition: str) -> Condition | ConditionListNode:
        """
        Parses the specified condition specifications.

        #### Params:
        - condition (str): String comprising the condition specifications.
        """

        if not condition:
            raise QueryParseError("Invalid query syntax!")

        # Recursively parses the condition if nested.
        elif constants.NESTED_CONDITION_PATTERN.match(condition):

            query = QueryQueue.from_string(condition[1:-1])
            return self._parse_conditions(query)

        operator, operands = self._tokenize_condition(condition)
        return self._parse_binary_condition(operator, operands)

    def _parse_conditions(self, query: QueryQueue) -> ConditionListNode:
        """
        Parses the specified query conditions.

        #### Params:
        - query (QueryQueue): `QueryQueue` object comprising the query.
        """

        head = dummy = ConditionListNode(True)
        condition: list[str] = []

        # Stores individual query tokens during iteration.
        token: str

        while query:
            token = query.pop()

            if token.lower() not in constants.LOGICAL_OPERATORS:
                condition.append(token)
                continue

            # Adds the parsed condition at the end of the conditions list.
            head.next = ConditionListNode(
                self._parse_condition(" ".join(condition)),
                operator=token.lower(),
            )

            head = head.next
            condition.clear()

        # Appends the last condition to the conditions.
        head.next = ConditionListNode(self._parse_condition(" ".join(condition)))
        return dummy.next

    def parse(self) -> ConditionListNode:
        """Parses the query conditions."""

        if self._query.peek().lower() != constants.KEYWORD_WHERE:
            raise QueryParseError(
                "Could not find the 'WHERE' keyword in "
                "its anticipated position in the query."
            )

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

        op_left_dtype, op_right_dtype = (
            op_left.dtype if isinstance(op_left, BaseField) else type(op_left),
            op_right.dtype if isinstance(op_right, BaseField) else type(op_right),
        )

        # Relational operations are only allowed for operands with the same
        # datatype with an exception of the operator being Equals (==) or
        # Not Equals (!=) and one of the operand being None. The following
        # condition statement raises a parse error if none of the specified
        # conditions are met.

        if (
            op_left_dtype != op_right_dtype
            and operator in (constants.OP_EQ, constants.OP_NE)
            and not (op_left is None or op_right is None)
        ):
            raise QueryParseError(
                f"{op_left} and {op_right} cannot be "
                "compared with a relational operator."
            )

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

        # Raises a parse error if the right operand
        # is not an iterable query attribute.
        if not (
            isinstance(op_right, Sequence)
            or isinstance(op_right, BaseField)
            and issubclass(op_right.dtype, Sequence)
        ):
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
        if not (isinstance(op_right, Sequence) and len(op_right) == 2):
            raise QueryParseError(
                f"{right!r} is not a valid operand for "
                f"the {constants.OP_BETWEEN!r} operation."
            )

        return Condition(constants.OP_BETWEEN, op_left, op_right)

    def _like(self, left: str, right: str) -> Condition:
        """Parses the condition for the like operation."""

        op_left, op_right = self._parse_operands(left, right)
        op_left_dtype = (
            op_left.dtype if isinstance(op_left, BaseField) else type(op_left)
        )

        if not (issubclass(op_left_dtype, str) and isinstance(op_right, str)):
            raise QueryParseError("Invalid condition operands for the 'like' operator.")

        return Condition(constants.OP_LIKE, op_left, op_right)


class ConditionHandler:
    """
    ConditionHandler class defines methods for
    handling user-specified query conditions.
    """

    __slots__ = "_conditions", "_evaluator_map", "_logical_map"

    def __init__(self, conditions: ConditionListNode | None) -> None:
        """
        Creates an instance of the ConditionHandler class.

        #### Params:
        - conditions (ConditionListNode | None): List comprising the
        query conditions or None if no conditions are to be applied.
        """

        self._conditions = conditions

        # Maps logical operators with their corresponding
        # condition segment evaluator methods.
        self._logical_map: dict[str, Callable[[bool, bool], bool]] = {
            constants.OP_CONJUNCTION: self._and,
            constants.OP_DISJUNCTION: self._or,
        }

        # Maps operators with their corresponding condition evaluator methods.
        self._evaluator_map: dict[str, Callable[[Condition], bool]] = {
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

    def __call__(self, entity: BaseEntity) -> bool:
        """
        Evaluates the query conditions and returns
        a boolean value for filtering query records.

        #### Params:
        - entity (BaseEntity): Entity object for evaluating the query fields.
        """

        # Returns ture if no conditions were specified at
        # initialization, to include all the query records.
        if self._conditions is None:
            return True

        return self._evaluate_conditions(self._conditions, entity)

    def _evaluate_condition(
        self, condition: QueryConditionType, entity: BaseEntity
    ) -> bool:
        """
        Evaluates the specified condition or conditions if nested.

        #### Params:
        - condition (QueryConditionType): Condition to be evaluated.
        - entity (BaseEntity): Entity object being operated upon.
        """

        if isinstance(condition, ConditionListNode):

            # Recursively evaluates if the specified condition
            # holds reference to a nested query conditions list.
            return self._evaluate_conditions(condition, entity)

        elif isinstance(condition, bool):
            return condition

        left, right = condition.evaluate_operands(entity)

        evaluator = self._evaluator_map[condition.operator]
        result: bool = evaluator(left, right)

        return result

    def _evaluate_condition_segment(
        self, node: ConditionListNode, operator: str, entity: BaseEntity
    ) -> ConditionListNode:
        """
        Evaluates the condition segment present in the begining of the
        specified conditions list based on the specified entity object.

        #### Params:
        - node (ConditionListNode): Conditions list comprising the segment
        to be evaluated.
        - operator (str): Operator to operate on.
        - entity (BaseEntity): Entity object being operated upon.
        """

        left = self._evaluate_condition(node.condition, entity)
        right = self._evaluate_condition(node.next.condition, entity)

        evaluator = self._logical_map[operator]

        # Stores the evaluated condition in the current node, copies
        # the operator of the next node and removes it from the list.
        node.condition = evaluator(left, right)
        node.operator = node.next.operator
        node.next = node.next.next

        return node

    def _evaluate_condition_segments(
        self, node: ConditionListNode, operator: str, entity: BaseEntity
    ) -> ConditionListNode:
        """
        Evaluates individual condition segments present in the specified
        conditions list seperated by the specified logical operator based
        on the specified entity object.

        #### Params:
        - node (ConditionListNode): Condition segments to be evaluated.
        - operator (str): Operator to operate on.
        - entity (BaseEntity): Entity object being operated upon.
        """

        # Adds a truthy preceding node for the conjunction operator
        # or a falsy preceding node for the disjunction operator to
        # ensure consistency in case of a single query condition.
        root = head = ConditionListNode(
            operator == constants.OP_CONJUNCTION, operator, node
        )

        while head and head.next:
            if head.operator != operator:
                head = head.next
                continue

            self._evaluate_condition_segment(head, operator, entity)

        return root

    def _evaluate_conditions(self, node: ConditionListNode, entity: BaseEntity) -> bool:
        """
        Evaluates the specified query conditions based on
        the specified entity object and returns a boolean
        value for filtering the query records.

        #### Params:
        - node (ConditionListNode): Conditions to be evaluated.
        - entity (BaseEntity): Entity object being operated on.
        """

        node = self._evaluate_condition_segments(node, constants.OP_CONJUNCTION, entity)
        node = self._evaluate_condition_segments(node, constants.OP_DISJUNCTION, entity)

        return node.condition

    @staticmethod
    def _and(left: bool, right: bool) -> bool:
        return left and right

    @staticmethod
    def _or(left: bool, right: bool) -> bool:
        return left or right

    @staticmethod
    def _eq(left: QueryAttribute, right: QueryAttribute) -> bool:
        return left == right

    @staticmethod
    def _ne(left: QueryAttribute, right: QueryAttribute) -> bool:
        return left != right

    @staticmethod
    def _gt(left: QueryAttribute, right: QueryAttribute) -> bool:
        return left > right

    @staticmethod
    def _ge(left: QueryAttribute, right: QueryAttribute) -> bool:
        return left >= right

    @staticmethod
    def _lt(left: QueryAttribute, right: QueryAttribute) -> bool:
        return left < right

    @staticmethod
    def _le(left: QueryAttribute, right: QueryAttribute) -> bool:
        return left <= right

    @staticmethod
    def _contains(left: QueryAttribute, right: QueryAttribute) -> bool:
        return left in right

    @staticmethod
    def _between(left: QueryAttribute, right: QueryAttribute) -> bool:
        return right[0] <= left <= right[1]

    @staticmethod
    def _like(left: QueryAttribute, right: QueryAttribute) -> bool:

        pattern: re.Pattern = re.compile(right)
        return bool(pattern.match(left))
