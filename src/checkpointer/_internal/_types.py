from typing import Any

type MetadataInput = dict[str, Any] | None
"""Optional metadata dictionary for checkpoint filtering in search operations."""

type _Version = int | float | str
"""Version identifier type supporting integer, float, or string representations."""
