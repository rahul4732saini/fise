"""
Test Exports Module
-------------------

This module defines classes and methods for testing the classes defined
within the `query/exports.py` module for parsing and handling data exports.
"""

from pathlib import Path

import pytest
import pandas as pd

from fise.common import constants
from fise.shared import QueryQueue

from fise.query.exports import (
    BaseExportData,
    FileExportData,
    DBMSExportData,
    ExportParser,
    FileExportHandler,
)

# The following constants store arguments and results
# for testing the functionalities associated with them.

FILE_EXPORT_PARSER_ARGS = [
    "export file[export.xlsx]",
    "Export FilE[data.csv]",
    "EXPORT FILE[index.html]",
    "exporT File[result.json]",
]
FILE_EXPORT_PARSER_RESULTS = [
    "export.xlsx",
    "data.csv",
    "index.html",
    "result.json",
]

DBMS_EXPORT_PARSER_ARGS = [
    "export dbms[mysql]",
    "Export Dbms[postgresql]",
    "ExporT DBMS[sqlite]",
]
DBMS_EXPORT_PARSER_RESULTS = [
    "mysql",
    "postgresql",
    "sqlite",
]

FILE_EXPORT_HANDLER_ARGS = FILE_EXPORT_PARSER_RESULTS
FILE_EXPORT_HANDLER_DATA = pd.DataFrame(
    [["1", "0", "1"], [6, 1, 85], [-0.25, None, 67.3454]],
)


class TestExportParser:
    """Tests the `ExportParser` class."""

    @staticmethod
    def parse_query(query: str) -> BaseExportData:
        """
        Parses the export specifications from the specified query
        and returns the export data object for further testing.
        """

        queue = QueryQueue.from_string(query)
        parser = ExportParser(queue)

        return parser.parse()

    @pytest.mark.parametrize(
        ("query", "file"),
        zip(FILE_EXPORT_PARSER_ARGS, FILE_EXPORT_PARSER_RESULTS),
    )
    def test_with_file_specs(self, query: str, file: str) -> None:
        """Tests the parser with File export specifications."""

        result: FileExportData = self.parse_query(query)

        assert result.type_ == constants.EXPORT_FILE
        assert result.file.as_posix() == file

    @pytest.mark.parametrize(
        ("query", "dbms"),
        zip(DBMS_EXPORT_PARSER_ARGS, DBMS_EXPORT_PARSER_RESULTS),
    )
    def test_with_dbms_specs(self, query: str, dbms: str) -> None:
        """Tests the parser with DBMS export specifiactions."""

        result: DBMSExportData = self.parse_query(query)

        assert result.type_ == constants.EXPORT_DBMS
        assert result.dbms == dbms


@pytest.mark.parametrize("path", FILE_EXPORT_HANDLER_ARGS)
def test_file_export_handler(path: str) -> None:
    """
    Tests the `FileExportHandler` class and the only public method
    defined within it by initializing it  and verifying the export
    method by verifying the existence of the export file.
    """

    global FILE_EXPORT_HANDLER_DATA

    specs = FileExportData(Path(path))
    handler = FileExportHandler(specs, FILE_EXPORT_HANDLER_DATA)

    try:
        handler.export()
        assert specs.file.exists()

    # Ensures proper deletion of the export file even if an exception occurs.
    finally:
        if specs.file.exists():
            specs.file.unlink()
