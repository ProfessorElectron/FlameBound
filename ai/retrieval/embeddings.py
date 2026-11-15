
"""Embedding generation using Ollama."""

import httpx


OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBEDDING_MODEL = "nomic-embed-text"


def generate_embedding(text):
    """Convert text into a numerical embedding."""

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text must be a non-empty string")

    response = httpx.post(
        OLLAMA_URL,
        json={
            "model": EMBEDDING_MODEL,
            "prompt": text,
        },
        timeout=120.0,
    )

    response.raise_for_status()

    data = response.json()

    return data["embedding"]


def embed_documents(chunks):
    """Generate embeddings for a collection of text chunks."""

    embedded_chunks = []

    for chunk in chunks:
        vector = generate_embedding(chunk["text"])

        embedded_chunks.append({
            "text": chunk["text"],
            "metadata": chunk["metadata"],
            "embedding": vector,
        })

    return embedded_chunks
