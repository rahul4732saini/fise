"""
Fields Module
-------------

This module defines classes for storing and handling
query fields.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Self, Type

from common import constants
from entities import BaseEntity, File
from errors import QueryParseError


class BaseField(ABC):
    """BaseField serves as the base class for all field class."""

    @property
    @abstractmethod
    def dtype(self) -> Type: ...

    @abstractmethod
    def __str__(self) -> str: ...

    @classmethod
    @abstractmethod
    def parse(cls, descriptor: str) -> Self: ...

    @abstractmethod
    def evaluate(self, entity) -> Any: ...


@dataclass(slots=True, frozen=True)
class Field(BaseField):
    """
    Field class implements mechanism for storing,
    parsing and evaluating generic query fields.
    """

    field: str

    @property
    def dtype(self) -> Type:
        return constants.FIELD_TYPES[self.field]

    def __str__(self) -> str:
        return self.field

    @classmethod
    def parse(cls, descriptor: str) -> Self:
        """
        Initializes the Field class based on the specified field name.

        #### Params:
        - descriptor (str): Name of the query field.
        """

        return cls(descriptor)

    def evaluate(self, entity: BaseEntity) -> Any:
        """
        Extracts the data associated with the field
        from the specified entity object.
        """
        return getattr(entity, self.field)


@dataclass(slots=True, frozen=True)
class Size(BaseField):
    """
    Size class implements mechanism for parsing and evaluating
    the size field and stores the size unit conversion divisor.
    """

    divisor: int | float

    @property
    def dtype(self) -> Type:
        return constants.FIELD_TYPES["size"]

    def __str__(self) -> str:
        return "size"

    @classmethod
    def parse(cls, descriptor: str) -> Self:
        """
        Initializes the Size class based on the specified size unit.

        #### Params:
        - descriptor (str): Size unit to be used for evaluations.
        """

        # Assigns "B" -> bytes unit if no unit is not explicitly specified.
        unit = descriptor or "B"
        divisor: int | float | None = constants.SIZE_CONVERSION_MAP.get(unit)

        if divisor is None:
            raise QueryParseError(f"{unit!r} is not valid unit for the 'size' field.")

        return cls(divisor)

    def evaluate(self, entity: File) -> float | None:
        """
        Extracts the size from the specified `File` entity object
        and transforms it based on the stored size unit.
        """

        if entity.size is None:
            return None

        return round(entity.size / self.divisor, 5)
