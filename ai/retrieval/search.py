"""Cosine ranking and abstaining retrieval over the persistent index."""

from __future__ import annotations

import math


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    if len(vector_a) != len(vector_b) or not vector_a:
        raise ValueError("Embedding dimensions must match and be non-empty")
    a = [float(value) for value in vector_a]
    b = [float(value) for value in vector_b]
    if any(not math.isfinite(value) for value in a + b):
        raise ValueError("Embeddings must contain finite numbers")
    scale_a = max(abs(value) for value in a)
    scale_b = max(abs(value) for value in b)
    if scale_a == 0 or scale_b == 0:
        return 0.0
    a = [value / scale_a for value in a]
    b = [value / scale_b for value in b]
    norm_a = math.sqrt(sum(value * value for value in a))
    norm_b = math.sqrt(sum(value * value for value in b))
    cosine = sum(x * y for x, y in zip(a, b)) / (norm_a * norm_b)
    return max(-1.0, min(1.0, cosine))


def rank_candidates(query_embedding: list[float], candidates: list[dict], *, top_k: int) -> list[dict]:
    if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= 10:
        raise ValueError("top_k must be between 1 and 10")
    results = []
    for candidate in candidates:
        score = cosine_similarity(query_embedding, candidate["embedding"])
        results.append({**candidate, "similarity": score})
    return sorted(results, key=lambda item: (-item["similarity"], item["chunk_id"]))[:top_k]


def apply_calibrated_threshold(results: list[dict], threshold: float | None) -> list[dict]:
    if threshold is None:
        return []
    if not math.isfinite(threshold) or not -1 <= threshold <= 1:
        raise ValueError("calibrated threshold must be finite and between -1 and 1")
    return [result for result in results if result["similarity"] >= threshold]
