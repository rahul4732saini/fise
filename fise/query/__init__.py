"""
Query Package
-------------

This package implements the mechanism for parsing and handling user-specified
queries. If offers a robust suite of classes and functions designed for the same.
"""

import pandas as pd

from .core import QueryParser, QueryHandler
from shared import QueryQueue


__all__ = "handle_query", "QueryHandler", "QueryParser"


def handle_query(query: QueryQueue) -> pd.DataFrame | None:
    """
    Parses and evaluates the query encapsulated
    in the specified query queue object.
    """

    parser = QueryParser(query)
    query_specs = parser.parse()

    handler = QueryHandler(query_specs)
    return handler.evaluate()
