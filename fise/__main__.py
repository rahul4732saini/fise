"""
FiSE (File Search Engine)
"""

import sys
import time

import pandas as pd

from version import version
from common import constants
from handlers import QueryHandler
from errors import QueryHandleError


def enable_readline() -> None:
    """
    Enables readline functionality for enhanced input handling in Linux terminal.
    """
    import readline

    readline.parse_and_bind("tab: complete")


def evaluate_query() -> None:
    """
    Inputs the evaluates the used specified query.
    """

    query: str = input("FiSE>")
    start_time: float = time.perf_counter()

    if not query:
        return

    elif query.lower() in ("exit", "quit"):
        sys.exit(0)

    elif query.lower() in (r"\c", "clear"):
        return print("\033c", end="")

    else:
        handler = QueryHandler(query)
        data: pd.DataFrame | None = handler.handle()

        if data is not None:
            print(data if not data.empty else "Empty Dataset")

    elapsed: float = time.perf_counter() - start_time
    print(constants.COLOR_GREEN % f"Completed in {elapsed:.2f} seconds")


def main() -> None:
    while True:
        try:
            evaluate_query()

        except KeyboardInterrupt:
            print("^C")

        except EOFError:
            sys.exit(0)

        except QueryHandleError:
            ...


if __name__ == "__main__":

    print(
        f"Welcome to FiSE(v{version})",
        r"Type '\c' or 'clear' to clear the terminal window. Type 'exit' or 'quit' to quit.",
        sep="\n",
    )

    # Enables readline feature if the current operating system is not windows.
    if sys.platform != "win32":
        enable_readline()

    main()
