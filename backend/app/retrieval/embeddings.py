from __future__ import annotations

import requests

from app.config import settings

OLLAMA_URL = getattr(settings, "ollama_url", "http://localhost:11434")
OLLAMA_MODEL = getattr(settings, "ollama_embedding_model", "nomic-embed-text")


def embed_query(text: str) -> list[float]:
    response = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={
            "model": OLLAMA_MODEL,
            "input": text,
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()
    embeddings = data.get("embeddings")

    if not embeddings or not isinstance(embeddings, list):
        raise ValueError("Invalid response from Ollama")

    embedding = embeddings[0]

    expected_dims = settings.ollama_embedding_dimensions

    if len(embedding) != expected_dims:
        raise ValueError(
            f"Expected embedding dimension {expected_dims}, got {len(embedding)}"
        )

    return embedding
