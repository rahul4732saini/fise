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
import sqlalchemy

from . import constants


def parse_query(query: str) -> list[str]:
    """
    Parses the specified raw string query and converts
    into a list of tokens for further parsing.

    ####
    - query (str): Query to be parsed.
    """

    start_brackets, end_brackets = {"[", "("}, {"]", ")"}

    tokens: list = []

    token: str = ""
    in_brackets: bool = False

    for char in query:
        if char in start_brackets:
            in_brackets = True
            token += char

        # Adds the token to list at the ending brackets.
        elif char in end_brackets:
            in_brackets = False
            tokens.append(token + char)
            token = ""

        # Adds to list if the character is a whitespace and not
        # inside brackets  and `token` is not an empty string.
        elif char.isspace() and not in_brackets:
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

    for path in directory.iterdir():
        if path.is_file():
            yield path

        # Extracts files from sub-directories.
        elif recursive and path.is_dir():
            yield from get_files(path, recursive)


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

    for path in directory.iterdir():
        if path.is_dir():
            if recursive:
                yield from get_directories(path, recursive)

            yield path


def export_to_file(data: pd.DataFrame, path: str) -> None:
    """
    Exports search data to the specified file in a suitable format.

    #### Params:
    - data (pd.DataFrame): pandas DataFrame comprising search records.
    - path (str): string representation of the file path.
    """

    file: Path = Path(path)

    # Verifies the path's parent directory for existence.
    # Also verifies if the file is non-existent.
    if not (file.parent.exists() and not file.is_file()):
        print(
            "Error: The specified path for exporting search"
            "records must not direct to an existing file."
        )
        sys.exit(1)

    # String representation of the export method used for exporting
    # the pandas DataFrame comprising the search data records.
    export_method: str | None = constants.DATA_EXPORT_TYPES_MAP.get(file.suffix)

    if not export_method:
        print(
            f"Error: {file.suffix} file type is not"
            "supported for search records export."
        )
        sys.exit(1)

    # Exporting the search data to the specified file with a suitable method.
    getattr(data, export_method)(file)


def _connect_sqlite() -> sqlalchemy.Engine:
    """
    Connects to a SQLite database file.
    """
    database: Path = Path(input("Enter the path to database file: "))
    return sqlalchemy.create_engine(f"sqlite:///{database}")


def _connect_database(database: str) -> sqlalchemy.Engine:
    """
    Connects to specified SQL database server.

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
    Exports search data to the specified database.

    #### Params:
    - data (pd.DataFrame): pandas DataFrame comprising search records.
    - database (str): database name to export data.
    """

    conn: sqlalchemy.Engine = (
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
        if table in metadata:
            force: str = input(
                "The specified table already exist, would you like to alter it? (Y/N) "
            )

            if force != "Y":
                print("Export cancelled!")
                return

        data.to_sql(table, conn, if_exists="replace", index=False)
