import sys
from pathlib import Path

ADDITIONAL_PATHS = [
    str(Path(__file__).parents[1]),
    str(Path(__file__).parents[2]),
    str(Path(__file__).parents[2] / "fise"),
]

sys.path.extend(ADDITIONAL_PATHS)
