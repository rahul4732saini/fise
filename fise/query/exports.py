"""
Exports Module
--------------

This module defines classes and functions for parsing
and handling exports to DBMS and external file formats.
"""

from abc import ABC, abstractmethod
from typing import Callable, ClassVar
from pathlib import Path
from dataclasses import dataclass
from getpass import getpass

import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.engine import URL, Engine, Connection, Inspector
from sqlalchemy.exc import OperationalError

from common import tools, constants
from errors import QueryParseError, OperationError
from notify import Message
from shared import QueryQueue


class BaseExportData:
    """
    ExportData serves as the base class for all classes
    responsible for storing export data specifications.
    """

    __slots__ = ()

    type_: ClassVar[str]


@dataclass(slots=True, frozen=True, eq=False)
class FileExportData(BaseExportData):
    """
    FileExportData class encapsulates
    file export data specifications.
    """

    type_ = constants.EXPORT_FILE
    file: Path


@dataclass(slots=True, frozen=True, eq=False)
class DBMSExportData(BaseExportData):
    """
    DBMSExportData class encapsulates
    DBMS export data specifications.
    """

    type_ = constants.EXPORT_DBMS
    dbms: str


class ExportParser:
    """
    ExportParse class defines methods for parsing export
    specifications defined in the user-specified query.
    """

    __slots__ = "_query", "_method_map"

    def __init__(self, query: QueryQueue):
        """
        Creates an instance of the ExportParser class.

        #### Params:
        - query (QueryQueue): `QueryQueue` object comprising the query.
        """

        self._query = query

        # Maps export types with their corresponding parser methods.
        self._method_map: dict[str, Callable[[str], BaseExportData]] = {
            constants.EXPORT_FILE: self._parse_file_export,
            constants.EXPORT_DBMS: self._parse_dbms_export,
        }

    @staticmethod
    def _parse_file_export(args: str) -> FileExportData:
        """
        Parse file export specifications
        based on the specified arguments.

        #### Params:
        - args (str): String comprising the file export arguments.
        """

        # Currently, the only argument accepted for file exports is the path to
        # the external file. Hence, it is directly converted into a Path object.

        file: Path = Path(args)

        if file.exists():
            raise OperationError(
                f"The specified path {file.as_posix()!r} for file export"
                " is already reserved by another file system entity."
            )

        elif not file.parent.exists():
            raise OperationError(
                "The specified directory for file export does not exist."
            )

        elif file.suffix not in constants.EXPORT_FILE_FORMATS:
            raise QueryParseError(
                f"{file.suffix!r} is not a supported format for file exports."
            )

        return FileExportData(file)

    @staticmethod
    def _parse_dbms_export(args: str) -> DBMSExportData:
        """
        Parses DBMS export specifications
        based on the specified arguments.

        #### Params:
        - args (str): String comprising the DBMS export arguments.
        """

        # Currently, the only argument accepted for DBMS exports
        # is the name of the DBMS. Hence, it is directly validated
        # against an array of valid DBMS.

        args = args.lower()

        if args not in constants.DBMS:
            raise QueryParseError(f"The specified DBMS {args!r} is not supported!")

        return DBMSExportData(args)

    def parse(self) -> BaseExportData:
        """Parses the export specifications defined within the query."""

        if self._query.seek().lower() != constants.KEYWORD_EXPORT:
            raise QueryParseError(
                "Expected the first clause of the query to"
                f" be {constants.KEYWORD_EXPORT.upper()!r}."
            )

        # Pops out the `EXPORT` keyword from the query.
        self._query.pop()

        # Tokenizes the export specifications and extracts
        # the export type along with the associated arguments.
        type_, args = tools.tokenize_qualified_clause(
            self._query.pop(), mandate_args=True
        )

        if type_ not in constants.EXPORT_TYPES:
            raise QueryParseError(f"{type_!r} is not a valid export type!")

        return self._method_map[type_](args)


class BaseExportHandler(ABC):
    """
    BaseExportHandler serves as the base
    class for all export handler classes.
    """

    @abstractmethod
    def __init__(self, specs: BaseExportData, data: pd.DataFrame) -> None: ...

    @abstractmethod
    def export(self) -> None: ...


class FileExportHandler(BaseExportHandler):
    """
    FileExportHandler class defines methods for
    handling exports to external file formats.
    """

    __slots__ = "_specs", "_data", "_method_map"

    def __init__(self, specs: FileExportData, data: pd.DataFrame) -> None:
        """
        Creates an instance of the FileExportHandler class.

        #### Params:
        - specs (FileExportData): File export data specifications.
        - data (pd.DataFrame): pandas Dataframe comprising the search records.
        """

        self._specs = specs
        self._data = data

        # Maps file formats with their corresponding export methods.
        self._method_map: dict[str, Callable[[], None]] = {
            ".csv": self._to_csv,
            ".json": self._to_json,
            ".xlsx": self._to_xlsx,
            ".html": self._to_html,
        }

    def _to_json(self) -> None:
        """Exports search data to a JSON file."""
        self._data.to_json(self._specs.file, indent=4)

    def _to_html(self) -> None:
        """Exports search data to an HTML file."""
        self._data.to_html(self._specs.file)

    def _to_csv(self) -> None:
        """Exports search data to a CSV file."""
        self._data.to_csv(self._specs.file)

    def _to_xlsx(self) -> None:
        """Exports search data to a XLSX file."""

        # Converts 'datetime.datetime' objects into strings in
        # the dataframe for proper representation in Excel files.
        for col in self._data.columns[self._data.dtypes == np.dtype("<M8[ns]")]:
            self._data[col] = self._data[col].astype(str)

        self._data.to_excel(self._specs.file)

    def export(self) -> None:
        """
        Exports data using a method suitable for the format associated
        with the file defined in the export data specifications.
        """

        # Calls the export method associated with the file format.
        self._method_map[self._specs.file.suffix]()


class DBMSExportHandler(BaseExportHandler):
    """
    DBMSExportHandler class defines methods for
    handling exports to Database Management Systems.
    """

    __slots__ = "_specs", "_data", "_method_map"

    def __init__(self, specs: DBMSExportData, data: pd.DataFrame) -> None:
        """
        Creates an instance of the DBMSExportHandler class.

        #### Params:
        - specs (DatabaseExportData): DBMS export data specifications.
        - data (pd.DataFrame): pandas Dataframe comprising the search records.
        """

        self._specs = specs
        self._data = data

        # Maps DBMS names with their corresponding connector methods.
        self._method_map: dict[str, Callable[[], Engine]] = {
            constants.DBMS_MYSQL: self._connect_mysql,
            constants.DBMS_POSTGRESQL: self._connect_postgresql,
            constants.DBMS_SQLITE: self._connect_sqlite,
        }

    @staticmethod
    def _parse_port(port: str) -> int:
        """
        Validates the specified port and converts
        it into an integer for further usage.

        #### Params:
        - port (str): String formatted port number.
        """

        if not port.isdigit():
            raise QueryParseError(f"{port!r} is not a valid port number!")

        port_num = int(port)

        if port_num not in range(65536):
            raise QueryParseError("The specified port number is out of range!")

        return port_num

    @staticmethod
    def _table_exists(engine: Engine, table: str) -> bool:
        """
        Returns a boolean value signifying the presence of
        the specified table in the specified DBMS connection.

        #### Params:
        - engine (Engine): SQLAlchemy Engine instance.
        - table (str): Name of the table to check for existence.
        """

        try:
            inspector = Inspector(engine)
            tables: list[str] = inspector.get_table_names()

        except OperationalError:
            engine.dispose(close=True)
            raise OperationalError("Unable to establish a connection with the DBMS!")

        else:
            return table in tables

    def _connect_sql_server(self) -> Engine:
        """Connects to a SQL server."""

        # Inputs database credentials.
        user: str = input("Username: ")
        passkey: str = getpass("Password: ")
        host: str = input("Host [localhost]: ") or "localhost"
        port: str = input("Port: ")
        database: str = input("Database: ")

        port_num: int = self._parse_port(port)

        # Creates a URL for initializing a SQLAlchemy Engine.
        url = URL.create(
            constants.DBMS_DRIVERNAMES[self._specs.dbms],
            user,
            passkey,
            host,
            port_num,
            database,
        )

        return sqlalchemy.create_engine(url)

    def _connect_sqlite(self) -> Engine:
        """Connects to a SQLite database file."""

        database: str = input("Enter the path to the database file: ")

        # Creates a URL for initializing a SQLAlchemy Engine.
        url = URL.create(
            constants.DBMS_DRIVERNAMES[self._specs.dbms],
            database=database,
        )

        return sqlalchemy.create_engine(url)

    def _connect_mysql(self) -> Engine:
        """Connects to a MySQL Server."""
        return self._connect_sql_server()

    def _connect_postgresql(self) -> Engine:
        """Connects to a PostgreSQL Server."""
        return self._connect_sql_server()

    def export(self) -> None:
        """
        Exports search records to the DBMS specified
        within the DBMS export data specifications.
        """

        # Connects with the DBMS with a suitable connector method.
        engine: Engine = self._method_map[self._specs.dbms]()
        table: str = input("Table name: ")

        # Prompts for replacement if the specified
        # table already exists in the database.
        if self._table_exists(engine, table):
            force: str = input(
                "The specified table already exists, "
                "would you like to alter it? (y/n): "
            )

            if force.lower() != "y":
                Message("Export cancelled!")
                return None

        try:
            conn: Connection = engine.connect()

        except OperationalError:
            raise OperationError(
                f"Unable to connect to the specified {self._specs.dbms!r} database."
            )

        else:
            self._data.to_sql(table, conn, if_exists="replace", index=False)

        finally:
            engine.dispose(close=True)
