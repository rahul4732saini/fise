"""
Tools module
------------

This module comprises functions and tools supporting other
objects and functions throughout the FiSE project.
"""

import sys
import getpass
from pathlib import Path
from typing import Generator

import pandas as pd
from sqlalchemy.exc import OperationalError
from sqlalchemy.engine.base import Engine
import sqlalchemy

from . import constants


def parse_query(query: str) -> list[str]:
    """
    Parses the specified raw string query and converts
    into a list of tokens for further parsing.

    ####
    - query (str): Query to be parsed.
    """

    delimiters: dict[str, str] = {"[": "]", "(": ")", "'": "'", '"': '"'}
    conflicting: set[str] = {"'", '"'}
    tokens: list = []

    # `token` temporarily stores the current token and `cur` stores the current delimiter.
    token = cur = ""

    # Level indicates the level of nesting of the current character during iteration.
    level: int = 0

    for char in query:
        # Only executes the conditional block if the character is a starting
        # delimiter and not nested inside or in the conflicting delimiters.
        if char == cur and (not level or char not in conflicting):
            level += 1
            cur = char
            token += char

        # Adds the token to list if the current character is
        # not nested inside  and is a terminating delimiter.
        elif level and char == delimiters.get(cur):
            level -= 1

            if not level:
                tokens.append(token + char)
                token = ""
                continue

            token += char

        # Adds to list if the character is a whitespace
        # and `token` is not an empty or enclosed string.
        elif not level and char.isspace():
            if token:
                tokens.append(token)
                token = ""

        # For all other characters.
        else:
            token += char

    # Adds the ending token of the query to `tokens` list.
    if token:
        tokens.append(token)

    return tokens


def get_files(directory: Path, recursive: bool) -> Generator[Path, None, None]:
    """
    Returns a `typing.Generator` object of all files present within the specified
    directory. Also extracts the files present within the subdirectories if
    `recursive` is set to `True`.

    #### Params:
    - directory (pathlib.Path): Path of the directory to be processed.
    - recursive (bool): Boolean value to specify whether to include the files
    present within the subdirectories.
    """

    try:
        for path in directory.iterdir():
            if path.is_file():
                yield path

            # Extracts files from sub-directories.
            elif recursive and path.is_dir():
                yield from get_files(path, recursive)

    except PermissionError:
        print(
            constants.COLOR_YELLOW % f"Permission Error: Skipping directory {directory}"
        )

        # Returns a tuple to not disrupt the proper functioning of
        # the function if the  `yield from` statement is to be
        # executed in case the function is executed recursively.
        yield from ()


def get_directories(directory: Path, recursive: bool) -> Generator[Path, None, None]:
    """
    Returns a `typing.Generator` object of all subdirectories present within
    the specified directory. Also extracts the directories present within the
    subdirectories if `recursive` is set to `True`.

    #### Params:
    - directory (pathlib.Path): Path of the directory to be processed.
    - recursive (bool): Boolean value to specify whether to include the files
    present within the subdirectories.
    """

    try:
        for path in directory.iterdir():
            if path.is_file():
                continue

            if recursive:
                yield from get_directories(path, recursive)

            yield path

    except PermissionError:
        print(
            constants.COLOR_YELLOW % f"Permission Error: Skipping directory {directory}"
        )

        # Returns a tuple to not disrupt the proper functioning of
        # the function if the  `yield from` statement is to be
        # executed in case the function is executed recursively.
        yield from ()


def export_to_file(data: pd.DataFrame, path: str) -> None:
    """
    Exports search data to the specified file in a suitable format.

    #### Params:
    - data (pd.DataFrame): pandas DataFrame comprising search records.
    - path (str): string representation of the file path.
    """

    file: Path = Path(path)

    if file.is_file():
        print(
            "Error: The specified path for exporting search"
            "records must not direct to an existing file."
        )
        sys.exit(1)

    elif not file.parent.exists():
        print(
            f"Error: The specified directory '{file.parent}'"
            "for exporting search records cannot be found."
        )
        sys.exit(1)

    # String representation of the export method used for exporting
    # the pandas DataFrame comprising the search data records.
    export_method: str | None = constants.DATA_EXPORT_TYPES_MAP.get(file.suffix)

    if not export_method:
        print(
            f"Error: {file.suffix!r} file type is not"
            "supported for search records export."
        )
        sys.exit(1)

    # Exporting the search data to the specified file with a suitable method.
    getattr(data, export_method)(file)


def _connect_sqlite() -> Engine:
    """
    Connects to a SQLite database file.
    """
    database: Path = Path(input("Enter the path to database file: "))
    return sqlalchemy.create_engine(f"sqlite:///{database}")


def _connect_database(database: str) -> Engine:
    """
    Connects to the specified SQL database server.

    #### Params:
    - database (str): database name to export data.
    """

    # Inputs database credentials.
    user: str = input("Username: ")
    passkey: str = getpass.getpass("Password: ")
    host: str = input("Host[localhost]: ") or "localhost"
    port: str = input("Port: ")
    db: str = input("Database: ")

    return sqlalchemy.create_engine(
        f"{constants.DATABASE_URL_DIALECTS[database]}{user}:{passkey}@{host}:{port}/{db}"
    )


def export_to_sql(data: pd.DataFrame, database: constants.DATABASES) -> None:
    """
    Exports search records data to the specified database.

    #### Params:
    - data (pd.DataFrame): pandas DataFrame comprising search records.
    - database (str): database name to export data.
    """

    # Creates an `sqlalchemy.Engine` object of the specified SQL database.
    conn: Engine = (
        _connect_sqlite() if database == "sqlite" else _connect_database(database)
    )

    table: str = input("Table name: ")
    metadata = sqlalchemy.MetaData()

    try:
        metadata.reflect(bind=conn)
        conn.connect()

    except OperationalError:
        print(f"Unable to connect to {database} database.")
        sys.exit(1)

    else:
        # Prompts for data replacement if the specified table already exists in the database.
        if table in metadata:
            force: str = input(
                "The specified table already exist, would you like to alter it? (Y/N) "
            )

            if force.lower() != "y":
                print("Export cancelled!")
                return

        data.to_sql(table, conn, if_exists="replace", index=False)
