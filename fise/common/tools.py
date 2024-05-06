r"""
Tools module
------------

This module comprises functions and tools supporting other
objects and functionalities throughout the utility.
"""

from pathlib import Path
from typing import Generator


def get_files(directory: Path, recursive: bool) -> Generator[Path, None, None]:
    r"""
    Returns a `typing.Generator` object of all files present within the specified
    directory. Also extracts the files present within the subdirectories if
    `recursive` is set to `True`.

    #### Params:
    - directory (pathlib.Path): Path of the directory to be processed.
    - recursive (bool): Boolean value to specify whether to include the files
    present in the subdirectories.
    """

    for path in directory.glob('*'):
        if path.is_file():
            yield path

        # Extracts files from sub-directories.
        elif recursive and path.is_dir():
            yield from get_files(path, recursive)