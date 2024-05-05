r"""
Objects Module
--------------

This module comprises classes that serve as foundational components
for various objects and functionalities within the project.
"""

from datetime import datetime
from pathlib import Path


class File:
    r"""
    File class serves as a unified class for accessing all methods related to the
    file `pathlib.Path` and `os.stat_result` object methods and attributes.
    """

    def __init__(self, file: Path) -> None:
        r"""
        Creates an instance of the `File` class.

        file (pathlib.Path): path of the file. 
        """

        # Verifies if the specified path is a file.
        assert file.is_file()

        self._file = file
        self._stats = file.stat()