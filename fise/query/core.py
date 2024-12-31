"""
Core Module
-----------

This module implements the core mechanism for
parsing and handling the user-specified query.
"""

from typing import Callable, Type
from dataclasses import dataclass

import pandas as pd

from common import constants
from shared import QueryQueue
from errors import QueryParseError
from .initials import QueryInitials, QueryInitialsParser
from .conditions import ConditionListNode, ConditionParser, ConditionHandler
from .projections import Projection, ProjectionsParser
from .paths import BaseQueryPath, QueryPathParser

from .exports import (
    BaseExportData,
    ExportParser,
    BaseExportHandler,
    FileExportHandler,
    DBMSExportHandler,
)

from .operators import (
    BaseOperator,
    FileQueryOperator,
    DataQueryOperator,
    DirectoryQueryOperator,
)


@dataclass
class SearchQuery:
    """
    SearchQuery class encapsulates the search query specifications.
    """

    export: BaseExportData | None
    initials: QueryInitials
    projections: list[Projection]
    path: BaseQueryPath
    conditions: ConditionListNode | None


class DeleteQuery:
    """
    DeleteQuery class encapsulates the delete query specifications.
    """

    initials: QueryInitials
    path: BaseQueryPath
    conditions: ConditionListNode | None
