"""
Tools module
------------

This module comprises utility functions supporting
other classes and functions throughout the project.
"""

import getpass
from pathlib import Path
from typing import Generator

import numpy as np
import pandas as pd
from sqlalchemy.exc import OperationalError
from sqlalchemy.engine.base import Engine
import sqlalchemy

from . import constants
from errors import OperationError, QueryHandleError
from notify import Alert


def parse_query(query: str) -> list[str]:
    """
    Parses the specified raw string query and converts into
    a list of tokens for further parsing and evaluation.

    #### Params:
    - query (str): Query to be parsed.
    """

    delimiters: dict[str, str] = {"[": "]", "(": ")", "'": "'", '"': '"'}
    conflicting: set[str] = {"'", '"'}
    tokens: list = []

    # Temporarily stores the current token.
    token = ""

    # Stores an array of current starting delimiters in the specified
    # query which are not yet terminated during iteration.
    cur: list = []

    # Adds a whitespace at the end of the query to avoid
    # parsing the last token separately after iteration.
    for char in query + " ":
        # Only executes the conditional block if the character is a starting
        # delimiter and not nested inside or in the conflicting delimiters.
        if char in delimiters and (not cur or char not in conflicting):
            cur.append(char)
            token += char

        # Adds the current character to the list if it is a terminating delimiter
        # and also pops up its corresponding starting delimiter in the `cur` list.
        elif cur and char == delimiters.get(cur[-1]):
            cur.pop()
            token += char

        # Adds to list if the character is a top-level whitespace
        # and `token` is not an nested or empty string.
        elif not cur and char.isspace():
            if token:
                tokens.append(token)
                token = ""

        # For all other characters.
        else:
            token += char

    return tokens


def get_files(directory: Path, recursive: bool) -> Generator[Path, None, None]:
    """
    Returns a `typing.Generator` object of all files present within the specified directory.
    Files present within subdirectories are also extracted if `recursive` is set to `True`.

    #### Params:
    - directory (pathlib.Path): Path to the directory.
    - recursive (bool): Whether to include files from subdirectories.
    """

    try:
        for path in directory.iterdir():
            if path.is_file():
                yield path

            # Extracts files from sub-directories.
            elif recursive and path.is_dir():
                yield from get_files(path, recursive)

    except PermissionError:
        Alert(f"Permission Error: Skipping directory '{directory}'")

        # Yields from a tuple to not disrupt the proper functioning of
        # the function if the `yield from get_files(...)` statement is
        # to be executed in case the function is executed recursively.
        yield from ()


def get_directories(directory: Path, recursive: bool) -> Generator[Path, None, None]:
    """
    Returns a `typing.Generator` object of all subdirectories present within the specified
    directory. Directories present within subdirectories are also extracted if `recursive`
    is set to `True`.

    #### Params:
    - directory (pathlib.Path): Path to the directory.
    - recursive (bool): Whether to include files from subdirectories.
    """

    try:
        for path in directory.iterdir():
            if not path.is_dir():
                continue

            if recursive:
                yield from get_directories(path, recursive)
            
            yield path

    except PermissionError:
        Alert(f"Permission Error: Skipping directory '{directory}'")

        # Yields from a tuple to not disrupt the proper functioning of the
        # function if the `yield from get_directories(...)` statement is
        # to be executed in case the function is executed recursively.
        yield from ()


def export_to_file(data: pd.DataFrame, file: Path) -> None:
    """
    Exports search data to the specified file in a suitable format.

    #### Params:
    - data (pd.DataFrame): pandas DataFrame comprising search records.
    - file (Path): Path to the file.
    """

    kwargs: dict[str, str] = {}

    # String representation of the export method for exporting search records.
    export_method: str = constants.DATA_EXPORT_TYPES_MAP[file.suffix]

    # Converts datetime objects present in datetime columns into
    # string objects for better representation in Excel files.
    if export_method == "to_excel":
        for col in data.dtypes.index[data.dtypes == np.dtype("<M8[ns]")]:
            data[col] = data[col].map(str)

    # Adds parameters for additional formatting if the export is to a json file.
    if export_method == "to_json":
        kwargs["indent"] = 4

    # Exports search records to the specified file with a suitable method.
    getattr(data, export_method)(file, **kwargs)


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
    - database (str): The name of the database to connect.
    """

    # Inputs database credentials.
    user: str = input("Username: ")
    passkey: str = getpass.getpass("Password: ")
    host: str = input("Host [localhost]: ") or "localhost"
    port: str = input("Port: ")
    db: str = input("Database: ")

    if not port:
        raise QueryHandleError(f"Invalid port number: {port!r}")

    return sqlalchemy.create_engine(
        f"{constants.DATABASE_URL_DIALECTS[database]}{user}:{passkey}@{host}:{port}/{db}"
    )


def export_to_sql(data: pd.DataFrame, database: str) -> None:
    """
    Exports search records to the specified database.

    #### Params:
    - data (pd.DataFrame): pandas DataFrame comprising search records.
    - database (str): The name of the database to connect.
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
        raise OperationError(f"Unable to connect to {database!r} database.")

    else:
        # Prompts for replacement if the specified table already exists in the database.
        if table in metadata:
            force: str = input(
                "The specified table already exist, would you like to alter it? (Y/N) "
            )

            if force.lower() != "y":
                print("Export cancelled!")

                # Raises `QueryHandleError` without any message to terminate the current query.
                raise QueryHandleError

        data.to_sql(table, conn, if_exists="replace", index=False)
