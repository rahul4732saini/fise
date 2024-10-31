"""
Fields Module
-------------

This module comprises comprises classes and functions
for storing and handling file system metadata fields.
"""

from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Self, Any


@dataclass(slots=True, frozen=True, eq=False)
class BaseField(ABC):
    """BaseField serves as the base class for all field class."""

    @classmethod
    @abstractmethod
    def parse(cls, descriptor: str) -> Self: ...

    @abstractmethod
    def evaluate(self, field) -> Any: ...
