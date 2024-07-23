"""
Notify Module
-------------

This module comprises class for displaying alerts
and notifications on the command-line interface.
"""


class Message:
    """Prints a success message on the terminal window."""

    def __init__(self, mesg: str) -> None:
        print(f"\033[32m{mesg}\033[0m")


class Alert:
    """Prints an alert message on the terminal window."""

    def __init__(self, mesg: str) -> None:
        print(f"\033[33m{mesg}\033[0m")
