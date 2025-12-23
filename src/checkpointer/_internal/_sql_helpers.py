"""SQL file loading utilities.

Provides cached loading of SQL query files from the package's SQL directory.
"""

from functools import lru_cache
from pathlib import Path

from checkpointer._internal._constants import SQL_DIR


@lru_cache
def get_sql_file(file_name: str | Path) -> str:
    """Load the SQL query content from the SQL Path.

    Args:
        file_name(str | Path): The relative path (from the SQL directory) of the SQL file to load.

    Returns:
        str: The SQL query content.

    """
    return (SQL_DIR / file_name).read_text()
