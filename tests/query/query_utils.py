"""
Query Utilities Module
----------------------

This module comprises utility functions supporting
classes and functions for testing queries.
"""

import sys
from pathlib import Path

import pandas as pd

# Adds the project directories to sys.path at runtime.
sys.path.append(str(Path(__file__).parents[2]))
sys.path.append(str(Path(__file__).parents[2] / "fise"))

from fise.query import QueryHandler


def eval_search_query(
    path: Path,
    fields: str = "*",
    ucase: bool = False,
    path_type: str | None = None,
    export: str | None = None,
    recur: str | None = None,
    oparams: str | None = None,
    conditions: str | None = None,
) -> pd.DataFrame | None:
    """
    Evaluates the search query.
    """

    export = f"export {export}" if export else ""
    recur = recur or ""
    operation: str = "select" + (f"[{oparams}]" if oparams else "")
    path_type = path_type or ""
    fields = fields or ""
    from_ = "FROM" if ucase else "from"
    conditions = "where " + conditions if conditions else ""

    if ucase:
        export, recur, operation, path_type = (
            export.upper(),
            recur.upper(),
            operation.upper(),
            path_type.upper(),
        )

    # Joins the query segments into a single string.
    query: str = " ".join(
        [export, recur, operation, fields, from_, path_type, f"'{path}'", conditions]
    )

    # Handles the specified query.
    return QueryHandler(query).handle()


def eval_delete_query(
    path: str,
    ucase: bool = False,
    path_type: str | None = None,
    recur: str | None = None,
    oparams: str | None = None,
    conditions: str | None = None,
) -> pd.DataFrame | None:
    """
    Evaluates the delete query.
    """

    recur = recur or ""
    operation: str = "delete" + (f"[{oparams}]" if oparams else "")
    path_type = path_type or ""
    from_ = "FROM" if ucase else "from"
    conditions = "where" + conditions if conditions else ""

    if ucase:
        recur, operation, path_type = (
            recur.upper(),
            operation.upper(),
            path_type.upper(),
        )

    # Joins the query segments into a single string.
    query: str = " ".join([recur, operation, from_, path_type, f"'{path}'", conditions])

    # Handles the specified query.
    return QueryHandler(query).handle()
