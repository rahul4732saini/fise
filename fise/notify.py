"""
Notify Module
-------------

This module comprises class for displaying alerts
and notifications on the Command Line Interface.
"""


class Message:
    """Prints a success message on the Command Line Interface."""

    def __init__(self, mesg: str) -> None:
        print(f"\033[32m{mesg}\033[0m", flush=True)


class Alert:
    """Prints an alert message on the Command Line Interface."""

    def __init__(self, mesg: str) -> None:
        print(f"\033[33m{mesg}\033[0m", flush=True)
