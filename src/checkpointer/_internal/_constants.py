"""Package-level path constants.

Defines directory paths used throughout the `checkpointer` package.
"""

from pathlib import Path
from typing import Final

PROJECT_DIR: Final[Path] = Path(__file__).parent.parent.parent.parent
"""The top-level project directory."""

CKPT_LIB: Final[Path] = PROJECT_DIR / 'src/checkpointer'
"""The directory containing the `checkpointer` library."""

SQL_DIR: Final[Path] = CKPT_LIB / '_internal/sql'
"""The directory containing the SQL files."""
