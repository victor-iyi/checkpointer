from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class CheckpointerConfig(BaseSettings):
    """Configuration for the checkpointer."""

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


@lru_cache
def get_settings() -> CheckpointerConfig:
    """Get the settings for the checkpointer."""
    return CheckpointerConfig()  # type: ignore[call-arg]
