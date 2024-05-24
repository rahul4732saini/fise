"""
Notify Module
-------------

This modules comprises class for displaying alerts
and notifications on the command-line interface.
"""

from common import constants


class Message:
    """Prints a success message on the terminal window."""

    def __init__(self, mesg: str) -> None:
        print(constants.COLOR_GREEN % mesg)


class Alert:
    """Prints an alert message on the terminal window."""

    def __init__(self, mesg: str) -> None:
        print(constants.COLOR_YELLOW % mesg)
