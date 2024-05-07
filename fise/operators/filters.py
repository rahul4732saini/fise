r"""
Filters Module
--------------

This Module is designed to facilitate objects and methods for filtration
of search data results based on the specified user queries.
"""

import pandas as pd


class FileSearchFilter:
    r"""
    FileSearchFilter class comprises methods for filtering file search results.
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

    def by_filename(self, name: str) -> None:
        r"""
        Filters the search records based on the specified file name.
        """
        self._data = self._data[self._data["name"] == name]
        return self
