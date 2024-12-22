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

    export_methods: dict[str, Callable[[pd.DataFrame, Path], None]] = {
        ".json": _export_to_json,
        ".xlsx": _export_to_xlsx,
        ".csv": _export_to_csv,
        ".html": _export_to_html,
    }

    # Exports data using a method suitable for the associated file type.
    export_methods[file.suffix](data, file)


def _parse_port(port: str) -> int:
    """
    Validates the specified port and converts
    it into an integer for further usage.
    """

    if not port.isnumeric():
        raise QueryHandleError(f"Invalid port number: {port!r}")

    port_num = int(port)

    if port_num not in range(65536):
        raise QueryHandleError("The specified port number is out of range!")

    return port_num


def _connect_sqlite() -> Engine:
    """Connects to a SQLite database file."""

    database: str = input("Enter the path to the database file: ")
    return sqlalchemy.create_engine(f"sqlite:///{database}")


def _connect_database(dbms: str) -> Engine:
    """
    Connects to the specified SQL Database Management System.

    #### Params:
    - dbms (str): The name of the Database Management System.
    """

    # Inputs database credentials.
    user: str = input("Username: ")
    passkey: str = getpass.getpass("Password: ")
    host: str = input("Host [localhost]: ") or "localhost"
    port: str = input("Port: ")
    database: str = input("Database: ")

    port_num: int = _parse_port(port)

    url = URL.create(
        constants.DATABASE_URL_DIALECTS[dbms],
        user,
        passkey,
        host,
        port_num,
        database,
    )

    return sqlalchemy.create_engine(url)


def export_to_sql(data: pd.DataFrame, dbms: str) -> None:
    """
    Exports search records to the specified Database Management System.

    #### Params:
    - data (pd.DataFrame): pandas DataFrame comprising search records.
    - dbms (str): The name of the Database Management System.
    """

    # Creates an `sqlalchemy.Engine` object of the specified SQL database.
    engine: Engine = _connect_sqlite() if dbms == "sqlite" else _connect_database(dbms)

    table: str = input("Table name: ")
    metadata = sqlalchemy.MetaData()

    try:
        metadata.reflect(bind=engine)
        conn: Connection = engine.connect()

    except OperationalError:
        raise OperationError(f"Unable to connect to the specified {dbms!r} database.")

    else:
        # Prompts for replacement if the specified table already exists in the database.
        if table in metadata:
            force: str = input(
                "The specified table already exists, would you like to alter it? (y/n) "
            )

            if force.lower() != "y":
                print("Export cancelled!")

                # Raises an error without any message to terminate
                # the current query.
                raise QueryHandleError

        data.to_sql(table, conn, if_exists="replace", index=False)

    finally:
        conn.close()
        engine.dispose(close=True)
