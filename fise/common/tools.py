"""
Tools module
------------

This module comprises utility function for assisting
other classes and functions defined within the project.
"""

from typing import Generator
from pathlib import Path

from . import constants
from errors import QueryParseError
from notify import Alert


def tokenize(
    source: str, delimiter: str = " ", skip_empty: bool = False
) -> Generator[str, None, None]:
    """
    Tokenizes the specified source string
    based on the specified delimiter.

    #### Params:
    - source (str): String to be tokenized.
    - delimiter (str): Character for seperating individual
    tokens in the source string.
    - skip_empty (bool): Whether to skip empty tokens.
    """

    paired_delimiters: dict[str, str] = {"[": "]", "(": ")", "'": "'", '"': '"'}
    conflicting: set[str] = {"'", '"'}

    # Stores the current token as a list of strings.
    token: list[str] = []

    # Stores opening paired delimiters in the source string during iteration.
    cur: list[str] = []

    # Adds an instance of the delimiter at the end of the source
    # to avoid parsing the last token separately after iteration.
    for char in source + delimiter:

        # Adds the current token to the tokens list if
        # the current character is a top-level delimiter.
        if not cur and char == delimiter:
            if skip_empty and not token:
                continue

            yield "".join(token).strip(" ")

            token.clear()
            continue

        token.append(char)

        # Avoids recognizing nested conflicting delimiters in the
        # source string to maintain consistency in the operation.
        if char in paired_delimiters and (not cur or char not in conflicting):
            cur.append(char)

        elif cur and char == paired_delimiters.get(cur[-1]):
            cur.pop()

    # Raises an error if delimiters are mismatched in the
    # source string such that a token is left unparsed.
    if token:
        raise QueryParseError(f"Invalid syntax around {''.join(token[:-1])!r}")


def tokenize_qualified_clause(
    clause: str, mandate_args: bool = False
) -> tuple[str, str]:
    """
    Tokenizes the specified qualified cluase and returns
    a tuple comprising the label along with the arguments.

    #### Params:
    - clause (str): String comprising the qualified clause.
    - mandate_args (bool): Whether to mandate the presence
    of arguments in the clause. Defaults to False.
    """

    if constants.QUALIFIED_CLAUSE_PATTERN.match(clause) is None:
        raise QueryParseError(f"{clause!r} is not a valid clause!")

    label = args = ""

    # Iterates through the clause and extracts the label and arguments.
    for i in range(len(clause)):
        if clause[i] != "[":
            continue

        label, args = clause[:i], clause[i + 1 : -1]
        break

    else:
        label = clause

    if mandate_args and not args:
        raise QueryParseError(f"Arguments required for the {clause!r} clause.")

    return label.lower(), args.strip(" ")


def enumerate_files(directory: Path, recursive: bool) -> Generator[Path, None, None]:
    """
    Enumerates over the files in the specified directory. Files within
    sub-directories are also included if `recursive` is set to True.

    #### Params:
    - directory (Path): Path to the directory.
    - recursive (bool): Whether to include files from sub-directories.
    """

    try:
        for path in directory.iterdir():
            if path.is_file():
                yield path

            elif recursive and path.is_dir():
                yield from enumerate_files(path, recursive)

    except PermissionError:
        Alert(f"Permission Error: Skipping directory {directory.as_posix()!r}")

        # Yields from an empty tuple to not disrupt
        # the proper functioning of the function.
        yield from ()


def enumerate_directories(
    directory: Path, recursive: bool
) -> Generator[Path, None, None]:
    """
    Enumerates over the sub-directories in the specified directory. Directories
    within sub-directories are also included if `recursive` is set to True.

    #### Params:
    - directory (Path): Path to the directory.
    - recursive (bool): Whether to include directories within sub-directories.
    """

    # Yields sub-directories prior to the base directory during iteration to
    # maintain compatibility with the delete operation, deleting sub-directories
    # prior the parent directory to avoid lookup errors.

    try:
        for path in directory.iterdir():
            if not path.is_dir():
                continue

            elif recursive:
                yield from enumerate_directories(path, recursive)

            yield path

    except PermissionError:
        Alert(f"Permission Error: Skipping directory {directory.as_posix()!r}")

        # Yields from an empty tuple to not disrupt
        # the proper functioning of the function.
        yield from ()
