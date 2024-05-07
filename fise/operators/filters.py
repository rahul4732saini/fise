r"""
Filters Module
--------------

This Module is designed to facilitate objects and methods for filtration
of search data results based on the specified user queries.
"""

import re
import pandas as pd


class BaseFilter:
    r"""
    Base class for all search record filter classes.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        r"""
        Creates an instance of the FileSearchFilter class.

        #### Params:
        - data (pd.DataFrame): pandas DataFrame containing search results.
        """
        self._data = data

    @property
    def data(self) -> pd.DataFrame:
        return self._data


class FileSearchFilter(BaseFilter):
    r"""
    FileSearchFilter class comprises methods for filtering file search results.
    """

    def by_filename(self, name: str):
        r"""
        Filters the search records based on the specified file name.
        """
        self._data = self._data[self._data["name"] == name]
        return self

    def by_filename_pattern(self, pattern: re.Pattern):
        r"""
        Filters the search records based on the specified file name pattern.
        """
        self._data = self._data[
            self._data["name"].apply(lambda name: bool(re.match(pattern, name)))
        ]
        return self
