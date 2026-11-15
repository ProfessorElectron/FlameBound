
"""Semantic search utilities for FlameBound."""

import numpy as np

from ai.retrieval.embeddings import generate_embedding


def cosine_similarity(vector_a, vector_b):
    """Calculate cosine similarity between two vectors."""

    vector_a = np.array(vector_a, dtype=float)
    vector_b = np.array(vector_b, dtype=float)

    if vector_a.shape != vector_b.shape:
        raise ValueError("Embedding dimensions must match")

    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(
        np.dot(vector_a, vector_b) / (norm_a * norm_b)
    )


def semantic_search(query, embedded_chunks, top_k=3):
    """Retrieve the most relevant chunks for a query."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must be a non-empty string")

    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
        raise ValueError("top_k must be a positive integer")

    if not embedded_chunks:
        return []

    query_embedding = generate_embedding(query)

    results = []

    for chunk in embedded_chunks:
        similarity = cosine_similarity(
            query_embedding,
            chunk["embedding"],
        )

        results.append({
            "text": chunk["text"],
            "metadata": chunk["metadata"],
            "similarity": similarity,
        })

    results.sort(
        key=lambda item: item["similarity"],
        reverse=True,
    )

    return results[:top_k]
