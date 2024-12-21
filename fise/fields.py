"""
Fields Module
-------------

This module defines classes and functions
for storing and handling query fields.
"""

from typing import Any
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
    def parse(cls, descriptor: str) -> "BaseField": ...

    @abstractmethod
    def evaluate(self, entity) -> Any: ...


@dataclass(slots=True, frozen=True, eq=False)
class Field(BaseField):
    """
    Field class implements mechanism for storing,
    parsing and evaluating generic query fields.
    """

    field: str

    @classmethod
    def parse(cls, field: str) -> "Field":
        """
        Initializes the `Field` class based on the specified field name.
        """
        return cls(field)

    def evaluate(self, entity: BaseEntity) -> Any:
        """
        Extracts the data associated with the field
        from the specified entity object.
        """
        return getattr(entity, self.field)


@dataclass(slots=True, frozen=True, eq=False)
class Size(BaseField):
    """
    Size class implements mechanism for parsing and evaluating
    the size field and stores the size unit conversion divisor.
    """

    divisor: int | float

    @classmethod
    def parse(cls, unit: str) -> "Size":
        """
        Initializes the `Size` class based on the specified size unit.
        """

        # Assigns "B" -> bytes unit if no unit is not explicitly specified.
        unit = unit or "B"
        divisor: int | float | None = constants.SIZE_CONVERSION_MAP.get(unit)

        if divisor is None:
            raise QueryParseError(f"{unit!r} is not valid unit for the 'size' field.")

        return cls(divisor)

    def evaluate(self, file: File) -> float | None:
        """
        Extracts the size from the specified `File` entity object
        and converts it it accordance with the stored size divisor.
        """

        if file.size is None:
            return None

        return round(file.size / self.divisor, 5)
