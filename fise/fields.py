"""
Fields Module
-------------

This module comprises classes and functions
for storing and handling query fields.
"""

import re
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Self, ClassVar, Any

from entities import BaseEntity, File
from common import constants
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

    # Regex pattern for matching size field specifications.
    _size_field_pattern: ClassVar[re.Pattern] = re.compile(r"^size(\[.*])?$")

    divisor: int | float

    @classmethod
    def parse(cls, field: str):
        """
        Parses the specified field specifications
        and creates an instance of the `Size` class.
        """

        if not cls._size_field_pattern.match(field.lower()):
            raise QueryParseError(f"Found an invalid field {field!r} in the query.")

        # Assigns "B" -> bytes unit is not explicitly specified.
        unit: str = field[5:-1] or "B"
        divisor: int | float | None = constants.SIZE_CONVERSION_MAP.get(unit)

        if divisor is None:
            raise QueryParseError(
                f"Invalid unit {unit!r} specified for the 'size' field."
            )

        return cls(divisor)

    def evaluate(self, file: File) -> float | None:
        """
        Extracts the size from the specified `File` object and
        converts it in accordance with the stored size divisor.
        """

        if file.size is None:
            return None

        return round(file.size / self.divisor, 5)
