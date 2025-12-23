"""Package-level path constants.

Defines directory paths used throughout the `checkpointer` package.
"""

from importlib.resources import files
from pathlib import Path
from typing import Final

SQL_DIR: Final[Path] = Path(str(files('checkpointer._internal') / 'sql'))
"""The directory containing the SQL files."""
