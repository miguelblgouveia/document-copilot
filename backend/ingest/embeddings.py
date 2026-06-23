import requests

from app.config import settings

OLLAMA_URL = getattr(settings, "ollama_url", "http://localhost:11434")
OLLAMA_MODEL = getattr(settings, "ollama_embedding_model", "nomic-embed-text")

EMBED_BATCH_SIZE = 32  # baixar ajuda estabilidade local


def embed_texts(
    texts: list[str],
    *,
    batch_size: int = EMBED_BATCH_SIZE,
) -> list[list[float]]:
    if not texts:
        return []

    vectors: list[list[float]] = []

    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]

        response = requests.post(
            f"{OLLAMA_URL}/api/embed",
            json={
                "model": OLLAMA_MODEL,
                "input": batch,
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        batch_embeddings = data.get("embeddings")
        if not batch_embeddings:
            raise ValueError("No embeddings returned from Ollama")

        vectors.extend(batch_embeddings)

    return vectors