"""
Tools module
------------

This module comprises utility function for assisting
other classes and functions defined within the project.
"""

import typing

from types import UnionType
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


def find_base_string(source: str, strings: tuple[str]) -> tuple[int, int] | None:
    """
    Searches for the specified substrings in the specified source string
    at the base level and returns the starting and ending indices of the
    found substring.

    #### Params:
    - source (str): Source string to search within.
    - strings (tuple[str]): Tuple of strings to search for.
    """

    paired_delimiters = {"[": "]", "(": ")", "'": "'", '"': '"'}
    conflicting = {"'", '"'}

    # Stores opening paired delimiters in the source string during iteration.
    cur: list[str] = []

    for i in range(len(source)):
        token = source[i]

        # Avoids recognizing nested conflicting delimiters in the
        # source string to maintain consistency in the operation.
        if token in paired_delimiters and (not cur or token not in conflicting):
            cur.append(token)

        elif cur and token == paired_delimiters.get(cur[-1]):
            cur.pop()

        elif cur:
            continue

        # Looks for the specified strings at each index if at the base level.
        for string in strings:
            if string != source[i : i + len(string)].lower():
                continue

            return i, i + len(string)


def dtype_equals(x: type | UnionType, y: type | UnionType, /) -> bool:
    """
    Compares the specified types or union of data types for eqality
    and returns a boolean value signifying whether the two are equal.
    """

    t1 = typing.get_args(x) if isinstance(x, UnionType) else (x,)
    t2 = typing.get_args(y) if isinstance(y, UnionType) else (y,)

    return any(type_ in t2 for type_ in t1)


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

    # Yields from an empty tuple in case of an exception to
    # not disrupt the proper functioning of the operation.

    except PermissionError:
        Alert(f"Permission Error: Skipping directory {directory.as_posix()!r}")
        yield from ()

    except FileNotFoundError:
        Alert(f"Path Not Found: Skipping directory {directory.as_posix()!r}")
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

    # Yields from an empty tuple in case of an exception to
    # not disrupt the proper functioning of the operation.

    except PermissionError:
        Alert(f"Permission Error: Skipping directory {directory.as_posix()!r}")
        yield from ()

    except FileNotFoundError:
        Alert(f"Path Not Found: Skipping directory {directory.as_posix()!r}")
        yield from ()
