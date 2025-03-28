"""
Main Module
-----------

This script serves as the entry point for the FiSE (File Search Engine)
application. It provides a command-line interface for users to perform
search and delete queries on file system entities.

Author: rahul4732saini (github.com/rahul4732saini)
License: MIT
"""

import sys
import time

import pandas as pd

from query import handle_query
from version import version
from common import constants
from notify import Message, Alert
from errors import QueryHandleError
from shared import QueryQueue


def enable_readline() -> None:
    """
    Enables readline functionality for enhanced
    input handling in POSIX-based OS terminals.
    """

    import readline

    readline.parse_and_bind("tab: complete")


def evaluate_query() -> None:
    """Inputs and evaluates the user-specified query."""

    query: str = input("FiSE> ")
    start_time: float = time.perf_counter()

    if not query:
        return

    elif query.lower() in constants.CMD_EXIT:
        sys.exit(0)

    elif query.lower() in constants.CMD_CLEAR:
        return print("\033c", end="")

    # If none of the above conditions are matched, the input
    # is assumed to be a query and evaluated accordingly.

    query_queue = QueryQueue.from_string(query)
    result = handle_query(query_queue)

    if result is not None:
        if result.shape[0] > 30:
            Alert(
                "Displaying a compressed output of the dataset. "
                "Export the records to get a more detailed view."
            )

        print(result if not result.empty else "Empty Dataset")

    elapsed: float = time.perf_counter() - start_time
    Message(f"Completed in {elapsed:.2f} seconds")


def main() -> None:
    """Main function for program execution."""

    while True:
        try:
            evaluate_query()

        except KeyboardInterrupt:
            print("^C")

        except EOFError:
            sys.exit(0)

        except QueryHandleError:
            ...

        except Exception as e:
            QueryHandleError(str(e))


if __name__ == "__main__":

    # Sets an upper limit for max rows to be displayed in the dataframe.
    pd.options.display.max_rows = 30

    print(f"Welcome to FiSE(v{version})")
    print(
        r"Type '\c' or 'clear' to clear the terminal"
        r" window. Type 'exit' or 'quit' to quit."
    )

    # Enables readline feature if the OS is a POSIX-based.
    if sys.platform != "win32":
        enable_readline()

    main()
