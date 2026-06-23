from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    database_url: str

    # genai_api_key: str
    # genai_embedding_model: str
    # genai_embedding_dimensions: int

    ollama_url: str
    ollama_embedding_model: str
    ollama_embedding_dimensions: int

    # openai_api_key: str
    # openai_embedding_model: str = "text-embedding-3-small"
    # openai_embedding_dimensions: int = 1536
    # openai_chat_model: str = "gpt-5.5"
    # openai_grounding_model: str = "gpt-4.1-mini"
    # openai_agent_request_limit: int = 20
    # openai_agent_temperature: float = 0.0

    retrieval_candidate_k: int = 50
    retrieval_top_k: int = 10
    retrieval_rrf_k: int = 60
    retrieval_neighbor_radius: int = 1
    retrieval_fts_config: str = "english"
    retrieval_fts_keyword_model: str = "gpt-4.1-mini"
    retrieval_fts_keyword_min: int = 3
    retrieval_fts_keyword_max: int = 5
    retrieval_fts_keyword_fast_path_tokens: int = 5

    # Comma-separated in .env; use `cors_origins` for the parsed list.
    allowed_origins: str = "http://localhost:5173, http://localhost:8000/"

    @computed_field
    @property
    def sqlalchemy_database_url(self) -> str:
        """Normalize Supabase-style URLs for SQLAlchemy + psycopg v3."""
        url = self.database_url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+psycopg://", 1)
        return url

    @computed_field
    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.allowed_origins.split(",")
            if origin.strip()
        ]


settings = Settings()


# from __future__ import annotations

# from functools import lru_cache
# from pathlib import Path
# from typing import Annotated

# from pydantic import AnyHttpUrl, PostgresDsn, SecretStr, field_validator
# from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


# class Settings(BaseSettings):
#     """Application settings loaded from environment variables."""

#     _backend_env_file = Path(__file__).resolve().parent.parent / ".env"

#     model_config = SettingsConfigDict(
#         env_file=str(_backend_env_file),
#         env_file_encoding="utf-8",
#         extra="ignore",
#     )

#     app_name: str = "Document Copilot API"
#     app_env: str = "development"
#     log_level: str = "INFO"

#     supabase_url: AnyHttpUrl
#     supabase_anon_key: SecretStr
#     supabase_service_role_key: SecretStr

#     database_url: PostgresDsn

#     genai_api_key: SecretStr
#     genai_embedding_model: str
#     genai_embedding_dimensions: int

#     allowed_origins: Annotated[list[str], NoDecode]

#     @field_validator("allowed_origins", mode="before")
#     @classmethod
#     def parse_allowed_origins(cls, value: object) -> list[str]:
#         """Support comma-separated origins in ALLOWED_ORIGINS."""
#         if isinstance(value, str):
#             return [origin.strip() for origin in value.split(",") if origin.strip()]
#         if isinstance(value, list):
#             return [str(origin).strip() for origin in value if str(origin).strip()]
#         raise ValueError("ALLOWED_ORIGINS must be a comma-separated string or a list")


# @lru_cache
# def get_settings() -> Settings:
#     return Settings()


# # Import-time initialization makes missing/invalid required env vars fail fast.
# settings = get_settings()