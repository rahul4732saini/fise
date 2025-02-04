import sys
from pathlib import Path

# Adds the directories comprising the software into the
# system path for testing the associated functionalities.

BASE_DIR = Path(__file__).parents[1]

ADDITIONAL_PATHS = [
    BASE_DIR.as_posix(),
    BASE_DIR.joinpath("fise").as_posix(),
]

sys.path.extend(ADDITIONAL_PATHS)
