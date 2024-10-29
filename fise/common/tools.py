"""
Tools module
------------

This module comprises utility functions desgined for assigned
other classes and functions defined within the project.
"""

import getpass
from pathlib import Path
from typing import Generator, Any

import numpy as np
import pandas as pd
from sqlalchemy.exc import OperationalError
from sqlalchemy.engine import Engine, URL, Connection
import sqlalchemy

from . import constants
from errors import QueryParseError, OperationError, QueryHandleError
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

    tokens: list[str] = []
    token: list[str] = []

    # Stores starting delimiters in the query during iteration.
    cur: list[str] = []

    # Adds a whitespace at the end of the query to avoid
    # parsing the last token separately after iteration.
    for char in query + " ":

        # Adds current token to the tokens list if the current character
        # is a top-level whitespace and the token is not an empty string.
        if not cur and char.isspace():
            if token:
                tokens.append("".join(token))
                token.clear()
            continue

        token.append(char)

        # Only adds top-level conflicting delimiters into the list.
        if char in delimiters and (not cur or char not in conflicting):
            cur.append(char)

        elif cur and char == delimiters.get(cur[-1]):
            cur.pop()

    # Raises an error is delimiters are mismatched in the query
    # and a token is left unparsed indicating invalid syntax.
    if token:
        raise QueryParseError(f"Invalid query syntax around {"".join(token[:-1])!r}")

    return tokens


def get_files(directory: Path, recursive: bool) -> Generator[Path, None, None]:
    """
    Returns a generator of all files present within the specified directory.
    Files present within subdirectories are also extracted if `recursive` is
    set to `True`.

    #### Params:
    - directory (pathlib.Path): Path to the directory.
    - recurisve (bool): Whether to include files from subdirectories.
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

        # Yields from an empty tuple to not disrupt
        # the proper functioning of the function.
        yield from ()


def get_directories(directory: Path, recursive: bool) -> Generator[Path, None, None]:
    """
    Returns a generator of all subdirectories present within the specified
    directory. Directories peresent within subdirectories are also extracted
    if `recursive` is set to True.

    #### Params:
    - directory (pathlib.Path): Path to the directory.
    - recursive (bool): Whether to include files from subdirectories.
    """

    # Extracts subdirectories first to ensure compatibility in the delete
    # operation, deleting them before their parents to avoid lookup errors.

    try:
        for path in directory.iterdir():
            if not path.is_dir():
                continue

            if recursive:
                yield from get_directories(path, recursive)

            yield path

    except PermissionError:
        Alert(f"Permission Error: Skipping directory '{directory}'")

        # Yields from an empty tuple to not disrupt
        # the proper functioning of the function.
        yield from ()


def _export_to_json(data: pd.DataFrame, file: Path) -> None:
    """Exports search data to the specified JSON file."""
    data.to_json(file, indent=4)


def _export_to_html(data: pd.DataFrame, file: Path) -> None:
    """Exports search data to the specified HTML file."""
    data.to_html(file)


def _export_to_csv(data: pd.DataFrame, file: Path) -> None:
    """Exports search data to the specified CSV file."""
    data.to_csv(file)


def _export_to_xlsx(data: pd.DataFrame, file: Path) -> None:
    """Exports search data to the specified XLSX file."""

    for col in data.columns[data.dtypes == np.dtype("<M8[ns]")]:
        data[col] = data[col].astype(str)

    data.to_excel(file)


def export_to_file(data: pd.DataFrame, file: Path) -> None:
    """
    Exports search data to the specified file in the format associated
    with the type of the file.

    #### Params:
    - data (pd.DataFrame): pandas DataFrame comprising search records.
    - file (Path): Path to the file.
    """

    kwargs: dict[str, Any] = {}

    # String representation of the export method for exporting search records.
    export_method: str = constants.DATA_EXPORT_TYPES_MAP[file.suffix]

    # Converts datetime objects present in datetime columns into
    # string objects for better representation in Excel files.
    if export_method == "to_excel":
        for col in data.columns[data.dtypes == np.dtype("<M8[ns]")]:
            data[col] = data[col].map(str)

    # Adds parameters for additional formatting if the export is to a JSON file.
    elif export_method == "to_json":
        kwargs["indent"] = 4

    # Exports search records to the specified file with the specified method.
    getattr(data, export_method)(file, **kwargs)


def _connect_sqlite() -> Engine:
    """
    Connects to a SQLite database file.
    """
    database: Path = Path(input("Enter the path to the database file: "))
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
    database: str = input("Database: ")

    if not port:
        raise QueryHandleError(f"Invalid port number: {port!r}")

    url = URL.create(
        constants.DATABASE_URL_DIALECTS[database], user, passkey, host, port, database
    )

    return sqlalchemy.create_engine(url)


def export_to_sql(data: pd.DataFrame, database: str) -> None:
    """
    Exports search records to the specified database.

    #### Params:
    - data (pd.DataFrame): pandas DataFrame comprising search records.
    - database (str): The name of the database to connect.
    """

    # Creates an `sqlalchemy.Engine` object of the specified SQL database.
    engine: Engine = (
        _connect_sqlite() if database == "sqlite" else _connect_database(database)
    )

    table: str = input("Table name: ")
    metadata = sqlalchemy.MetaData()

    try:
        metadata.reflect(bind=engine)
        conn: Connection = engine.connect()

    except OperationalError:
        raise OperationError(f"Unable to connect to {database!r} database.")

    else:
        # Prompts for replacement if the specified table already exists in the database.
        if table in metadata:
            force: str = input(
                "The specified table already exists, would you like to alter it? (Y/N) "
            )

            if force.lower() != "y":
                print("Export cancelled!")

                # Raises `QueryHandleError` without any message to terminate the current query.
                raise QueryHandleError

        data.to_sql(table, conn, if_exists="replace", index=False)

    finally:
        conn.close()
        engine.dispose(close=True)
