"""
Test Operators Module
---------------------

This module defines classes and methods for testing the classes defined
within the `query/operators.py` module for handling file system and data
search and delete operations.

NOTE:
This module is dependent upon a HDF5 file with the same name located in
the hdf/test_query/ directory comprising file and directory search and
delete records for testing the associated methods in the query operator
class, and stores the following at the below specified paths:

- /file_search/t<x>: Stores file search records for testing
the search method in the `FileQueryOperator` class.

- /dir_search/t<x>: Stores directory search records for testing
the search method in the `DirectoryQueryOperator` class.

where `<x>` denotes the 1-indexed positon of the test case in the associated
constant comprising the results for testing the function below in the module.
"""

from pathlib import Path

import pytest
import pandas as pd

from fise.shared import QueryQueue
from fise.common import constants
from fise.query.paths import FileQueryPath, DirectoryQueryPath
from fise.query.projections import ProjectionsParser
from fise.query.operators import BaseOperator, FileQueryOperator, DirectoryQueryOperator
from fise.query.conditions import ConditionParser, ConditionHandler


BASE_DIR = Path(__file__).parents[1]
HDF_DIR = BASE_DIR / "hdf"

TEST_DIR = BASE_DIR / "test_directory"
DATA_TEST_DIR = TEST_DIR / "data"
FD_TEST_DIR = TEST_DIR / "file_dir"

TEST_DIRECTORY_HDF_FILE = HDF_DIR / "test_directory.hdf"
TEST_OPERATORS_HDF_FILE = HDF_DIR / "test_query/test_operators.hdf"

# The following constants store arguments and results
# for testing the functionalities associated with them.

FILE_OPERATOR_SEARCH_ARGS = [
    (
        (FD_TEST_DIR, False),
        ("name, filetype, size[Kb]", "where type in [None, '.md'] and size = 0"),
        "file_search/t1",
    ),
    (
        (FD_TEST_DIR / "project", True),
        ("filename, type", r"where name like '^.*\.py$'"),
        "file_search/t2",
    ),
    (
        (FD_TEST_DIR, True),
        ("name, size[b]", "where filetype in ['.md', '.txt', None]"),
        "file_search/t3",
    ),
]

DIR_OPERATOR_SEARCH_ARGS = [
    (
        (FD_TEST_DIR, False),
        ("name", "where name in ['docs', 'orders', 'project']"),
        "dir_search/t1",
    ),
    (
        (FD_TEST_DIR, True),
        ("name", r"where name like '^report-20\d{2}$'"),
        "dir_search/t2",
    ),
]


def get_condition_handler(condition_specs: str, entity: str) -> None:
    """
    Initializes a ConditionHandler object based on the
    specified condition specifications and entity name.
    """

    queue = QueryQueue.from_string(condition_specs)

    parser = ConditionParser(queue, entity)
    conditions = parser.parse()

    return ConditionHandler(conditions)


def get_search_results(
    operator: BaseOperator, proj_specs: str, condition_specs: str, entity: str
) -> pd.DataFrame:
    """
    Extracts the search results dataframe object based on the specified
    query operator, projection specifications, condition specifications
    and entity name.
    """

    queue = QueryQueue.from_string(proj_specs)
    queue.add(constants.KEYWORD_FROM)

    projections = ProjectionsParser(queue, entity).parse()
    condition_handler = get_condition_handler(condition_specs, entity)

    return operator.search(projections, condition_handler)


class TestFileQueryOperator:
    """Tests the FileQueryOperator class."""

    @staticmethod
    def init_operator(path: Path, recursive: bool) -> FileQueryOperator:
        """Initializes a FileQueryOperator object."""

        path_obj = FileQueryPath(path)
        operator = FileQueryOperator(path_obj, recursive)

        return operator

    @pytest.mark.parametrize(
        ("init_args", "func_args", "result_loc"), FILE_OPERATOR_SEARCH_ARGS
    )
    def test_search(
        self, init_args: tuple[Path, bool], func_args: tuple[str, str], result_loc: str
    ) -> None:
        """
        Tests the search method with the query specifications specified as
        arguments and verifies the result by comparing it with the data stored
        in the associated HDF file.
        """

        global TEST_OPERATORS_HDF_FILE

        operator = self.init_operator(*init_args)
        dataframe = get_search_results(operator, *func_args, constants.ENTITY_FILE)

        result_dataframe = pd.read_hdf(TEST_OPERATORS_HDF_FILE, result_loc)
        assert dataframe.equals(result_dataframe)


class TestDirectoryQueryOperator:
    """Tests the DirectoryQueryOperator class."""

    @staticmethod
    def init_operator(path: Path, recursive: bool) -> DirectoryQueryOperator:
        """Initializes a DirectoryQueryOperator object."""

        path_obj = DirectoryQueryPath(path)
        operator = DirectoryQueryOperator(path_obj, recursive)

        return operator

    @pytest.mark.parametrize(
        ("init_args", "func_args", "result_loc"), DIR_OPERATOR_SEARCH_ARGS
    )
    def test_search(
        self, init_args: tuple[Path, bool], func_args: tuple[str, str], result_loc: str
    ) -> None:
        """
        Tests the search method with the query specifications specified as
        arguments and verifies the result by comparing it with the data stored
        in the associated HDF file.
        """

        global TEST_OPERATORS_HDF_FILE

        operator = self.init_operator(*init_args)
        dataframe = get_search_results(operator, *func_args, constants.ENTITY_DIR)

        result_dataframe = pd.read_hdf(TEST_OPERATORS_HDF_FILE, result_loc)
        assert dataframe.equals(result_dataframe)
