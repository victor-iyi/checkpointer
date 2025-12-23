"""Configuration management for the checkpointer.

Uses Pydantic settings for environment-based configuration with `.env` file support.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class CheckpointerConfig(BaseSettings):
    """Configuration settings for the checkpointer.

    Loads configuration from environment variables and `.env` files.
    Uses Pydantic's BaseSettings for automatic environment variable binding.
    """

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


@lru_cache
def get_settings() -> CheckpointerConfig:
    """Get the cached checkpointer configuration.

    Returns a singleton instance of `CheckpointerConfig`, cached via `lru_cache`
    to ensure consistent configuration across the application lifetime.

    Returns:
        CheckpointerConfig: The application configuration instance.

    """
    return CheckpointerConfig()  # type: ignore[call-arg]
