"""
Entities Module
---------------

This module comprises classes and functions for
storing and handling file system metadata fields.
"""

from typing import Callable, Any
from notify import Alert


def safe_extract_field(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator function for safely executes the specified field
    extraction method. Returns None in case of an exception during
    the field extraction process.
    """

    alert: bool = True

    def wrapper(self) -> Any:
        nonlocal alert

        try:
            return func(self)

        except Exception:
            if not alert:
                return

            Alert(
                "Warning: Unable to access specific metadata fields of the"
                "recorded files/directories. The fileds are being assigned"
                "explicitly as 'None'."
            )

            # Sets alert to False to avoid redundant alerts.
            alert = False

    return wrapper
