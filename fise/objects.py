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
    File class serves as a unified class for accessing all methods and attributes
    related to the file `pathlib.Path` and `os.stat_result` object.
    """

    __slots__ = "_file", "_stats"

    def __init__(self, file: Path) -> None:
        r"""
        Creates an instance of the `File` class.

        #### Params:
        file (pathlib.Path): path of the file. 
        """

        self._file = file
        self._stats = file.stat()

    @property
    def file(self) -> None:
        return self._file
    
    @property
    def parent(self) -> None:
        return self._file.parent
    
    @property
    def name(self) -> None:
        return self._file.name
    
    @property
    def owner(self) -> None:
        return self._file.owner()
    
    @property
    def group(self) -> None:
        return self._file.group()

    @property
    def size(self) -> None:
        return self._stats.st_size
    
    @property
    def creation_time(self) -> None:
        return datetime.fromtimestamp(self._stats.st_birthtime).replace(microsecond=0)
    
    @property
    def modify_time(self) -> None:
        return datetime.fromtimestamp(self._stats.st_mtime).replace(microsecond=0)

    @property
    def access_time(self) -> None:
        return datetime.fromtimestamp(self._stats.st_atime).replace(microsecond=0)
