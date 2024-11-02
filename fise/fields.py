"""
Fields Module
-------------

This module comprises classes and functions
for storing and handling query fields.
"""

from typing import Self, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass

from common import constants
from entities import BaseEntity, File
from errors import QueryParseError


@dataclass(slots=True, frozen=True, eq=False)
class BaseField(ABC):
    """BaseField serves as the base class for all field class."""

    @classmethod
    @abstractmethod
    def parse(cls, descriptor: str) -> Self: ...

    @abstractmethod
    def evaluate(self, entity) -> Any: ...


@dataclass(slots=True, frozen=True, eq=False)
class Field(BaseField):
    """
    Field class stores individual query fields and
    defines methods for parsing and evaluating them.
    """

    field: str

    @classmethod
    def parse(cls, field: str):
        """
        Parses the specified field and returns
        an instance of the `Field` class.
        """
        return cls(field)

    def evaluate(self, entity: BaseEntity) -> Any:
        """
        Evaluates the stored field object based on associated
        attributes within the specified entity object.
        """
        return getattr(entity, self.field)


@dataclass(slots=True, frozen=True, eq=False)
class Size(BaseField):
    """
    Size class stores the size conversion divisor for converting
    file sizes and defines methods for parsing and evaluating them.
    """

    divisor: int | float

    @classmethod
    def parse(cls, unit: str):
        """
        Parses the specified size unit specifications
        and creates an instance of the `Size` class.
        """

        # Assigns "B" -> bytes unit is not explicitly specified.
        unit = unit or "B"
        divisor: int | float | None = constants.SIZE_CONVERSION_MAP.get(unit)

        if divisor is None:
            raise QueryParseError(f"{unit!r} is not valid unit for the 'size' field.")

        return cls(divisor)

    def evaluate(self, file: File) -> float | None:
        """
        Extracts the size from the specified `File` object and
        converts it in accordance with the stored size divisor.
        """

        if file.size is None:
            return None

        return round(file.size / self.divisor, 5)


# Maps field names with their corresponding storage and evaluator classes.
_fields_map: dict[str, BaseField] = {
    "size": Size,
}


def parse_field(
    field: str, entity: str, fields_map: dict[str, BaseField] = _fields_map
) -> BaseField:
    """Parses the specified field specifications."""

    label = args = ""

    for i in range(len(field)):
        if field[i] != "[":
            continue

        label, args = field[:i].lower(), field[i + 1 : -1]
        break

    else:
        label = field.lower()

    label = constants.ALIASES[entity].get(label, label)

    if label not in constants.FIELDS[entity]:
        raise QueryParseError(f"{field!r} is not a valid field!")

    return fields_map[label].parse(args) if label in fields_map else Field.parse(label)
