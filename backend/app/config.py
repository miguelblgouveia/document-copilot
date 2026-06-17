from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import AnyHttpUrl, PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    _backend_env_file = Path(__file__).resolve().parent.parent / ".env"

    model_config = SettingsConfigDict(
        env_file=str(_backend_env_file),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Document Copilot API"
    app_env: str = "development"
    log_level: str = "INFO"

    supabase_url: AnyHttpUrl
    supabase_anon_key: SecretStr
    supabase_service_role_key: SecretStr

    database_url: PostgresDsn

    genai_api_key: SecretStr
    genai_embedding_model: str
    genai_embedding_dimensions: int

    allowed_origins: Annotated[list[str], NoDecode]

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: object) -> list[str]:
        """Support comma-separated origins in ALLOWED_ORIGINS."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        if isinstance(value, list):
            return [str(origin).strip() for origin in value if str(origin).strip()]
        raise ValueError("ALLOWED_ORIGINS must be a comma-separated string or a list")


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Import-time initialization makes missing/invalid required env vars fail fast.
settings = get_settings()