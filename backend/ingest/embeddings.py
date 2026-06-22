"""Google Gen AI embedding generation for document chunks."""

from __future__ import annotations

from google import genai

from app.config import settings

EMBED_BATCH_SIZE = 100


def _client() -> genai.Client:
    return genai.Client(api_key=settings.google_api_key)


def embed_texts(
    texts: list[str],
    *,
    batch_size: int = EMBED_BATCH_SIZE,
) -> list[list[float]]:
    if not texts:
        return []

    expected_dims = settings.google_embedding_dimensions
    vectors: list[list[float]] = []

    client = _client()

    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]

        response = client.models.embed_content(
            model=settings.google_embedding_model,
            contents=batch,
            config={
                "output_dimensionality": expected_dims,
            },
        )

        for embedding in response.embeddings:
            vector = embedding.values

            if len(vector) != expected_dims:
                raise ValueError(
                    f"Expected embedding dimension {expected_dims}, got {len(vector)}"
                )

            vectors.append(vector)

    return vectors