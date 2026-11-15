"""Configured embedding calls; an embedding model must be selected explicitly."""

from ai.config import AISettings
from ai.providers import OllamaProvider


def generate_embeddings(texts: list[str], *, provider: OllamaProvider | None = None) -> list[list[float]]:
    if not texts or any(not isinstance(text, str) or not text.strip() for text in texts):
        raise ValueError("texts must contain non-empty strings")
    client = provider or OllamaProvider(AISettings.from_env())
    return client.embed(texts)


def generate_embedding(text: str, *, provider: OllamaProvider | None = None) -> list[float]:
    return generate_embeddings([text], provider=provider)[0]


def embed_documents(chunks: list[dict], *, provider: OllamaProvider | None = None) -> list[dict]:
    vectors = generate_embeddings([chunk["text"] for chunk in chunks], provider=provider)
    model = (provider.settings.embedding_model if provider else AISettings.from_env().embedding_model)
    if model is None:
        raise ValueError("An embedding model has not been selected")
    return [{**chunk, "embedding": vector, "embedding_model": model} for chunk, vector in zip(chunks, vectors)]
