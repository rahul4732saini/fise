import sys
from pathlib import Path

# Adds the directories comprising the software into the
# system path for testing the associated functionalities.

ADDITIONAL_PATHS = [
    Path(__file__).parents[1].as_posix(),
    (Path(__file__).parents[1] / "fise").as_posix(),
]

sys.path.extend(ADDITIONAL_PATHS)
