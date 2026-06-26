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
    ollama_llm_model: str
    ollama_agent_request_limit: int = 20
    ollama_agent_temperature: float = 0.0

    # openai_api_key: str
    # openai_embedding_model: str = "text-embedding-3-small"
    # openai_embedding_dimensions: int = 1536
    # openai_chat_model: str = "gpt-5.5"
    # openai_grounding_model: str = "gpt-4.1-mini"
    # openai_agent_request_limit: int = 20
    # openai_agent_temperature: float = 0.0

    # Number of candidate chunks fetched from each search arm (semantic + FTS) before
    # Reciprocal Rank Fusion. Higher → broader recall but slower DB queries.
    retrieval_candidate_k: int = 10  # production default: 50

    # Final number of top-ranked passages sent to the LLM as context after fusion.
    # Higher → richer context for complex questions but more tokens consumed per call.
    retrieval_top_k: int = 2  # production default: 10

    # Damping constant in the RRF formula: score = 1 / (k + rank).
    # Higher → rank differences matter less (smoother blending of semantic + FTS scores).
    # Lower → rank-1 results are weighted much more heavily than rank-2+.
    # 60 is the value from the original RRF paper and is rarely worth changing.
    retrieval_rrf_k: int = 60

    # How many adjacent chunks (before and after) to attach to each top-ranked hit.
    # 0 = return only the matched chunk; 1 = add 1 chunk before + 1 after, etc.
    # Higher → more surrounding context for the LLM but proportionally more tokens.
    retrieval_neighbor_radius: int = 0  # production default: 1

    # PostgreSQL text-search dictionary used for stemming and stop-word removal.
    # Controls how both the query and stored documents are normalised for FTS.
    # Change to a language-specific config (e.g. "portuguese") for non-English corpora.
    retrieval_fts_config: str = "english"

    # Ollama model used to distil the user query into precise FTS keywords.
    # Only called when the query exceeds `retrieval_fts_keyword_fast_path_tokens`.
    # Larger/better models produce more precise keywords at the cost of extra latency.
    retrieval_fts_keyword_model: str = "qwen3"

    # Minimum number of keywords the LLM must return; fewer triggers the deterministic fallback.
    retrieval_fts_keyword_min: int = 3

    # Maximum individual words used in the final FTS query (word-budget cap applied after extraction).
    # More words → broader FTS match surface but higher risk of irrelevant hits.
    retrieval_fts_keyword_max: int = 5

    # Queries whose token count is ≤ this threshold skip the LLM extraction and use the
    # raw query text directly for FTS. At 999 the LLM is effectively never called (fast,
    # zero extra latency). Lower values (e.g. 5) make the LLM refine longer queries only.
    retrieval_fts_keyword_fast_path_tokens: int = 999  # production default: 5

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
