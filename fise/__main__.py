"""
FiSE (File Search Engine)
"""

import sys
import time

import pandas as pd

from version import version
from common import constants
from handlers import QueryHandler
from errors import QueryHandleError, Alert


EXIT = {"exit", "quit"}
CLEAR = {r"\c", "clear"}


def enable_readline() -> None:
    """
    Enables readline functionality for enhanced input handling in Linux/Mac terminal.
    """
    import readline

    readline.parse_and_bind("tab: complete")


def evaluate_query() -> None:
    """
    Inputs the evaluates the user specified query.
    """
    global EXIT, CLEAR

    query: str = input("FiSE> ")
    start_time: float = time.perf_counter()

    if not query:
        return

    elif query.lower() in EXIT:
        sys.exit(0)

    elif query.lower() in CLEAR:
        return print("\033c", end="")

    # If none of the above are matched, the input is
    # assumed to be a query and evaluated accordingly.

    handler = QueryHandler(query)
    data: pd.DataFrame | None = handler.handle()

    if data is not None:

        if data.shape[0] > 30:
            Alert(
                "Displaying a compressed output of the dataset. "
                "Export the records for a more detailed view."
            )

        print(data if not data.empty else "Empty Dataset")

    elapsed: float = time.perf_counter() - start_time
    print(constants.COLOR_GREEN % f"Completed in {elapsed:.2f} seconds")


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
            print(e)
            # TODO: Unexpected exceptions handling.


if __name__ == "__main__":

    # Sets an upper limit for max rows to be displayed in the dataframe.
    pd.options.display.max_rows = 30

    print(
        f"Welcome to FiSE(v{version})",
        r"Type '\c' or 'clear' to clear the terminal window. Type 'exit' or 'quit' to quit.",
        sep="\n",
    )

    # Enables readline feature if the current operating system is not windows.
    if sys.platform != "win32":
        enable_readline()

    main()
