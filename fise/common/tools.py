"""
Tools module
------------

This module comprises utility function for assisting
other classes and functions defined within the project.
"""

from typing import Generator

from . import constants
from errors import QueryParseError


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

    return tokens

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

    if constants.QUALIFIED_CLUASE_PATTERN.match(clause) is None:
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
