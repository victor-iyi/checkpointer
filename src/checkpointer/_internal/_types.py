from typing import Any

from sqlalchemy.engine import Connection, Engine

type Conn = Connection | Engine
"""A SQLAlchemy Connection or Engine instance."""

type MetadataInput = dict[str, Any] | None
"""Optional metadata dictionary for checkpoint filtering in search operations."""

type _Version = int | float | str
"""Version identifier type supporting integer, float, or string representations."""
