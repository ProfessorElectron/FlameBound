"""Calibrated retrieval and server-owned citation construction."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai.config import AISettings, ProviderError
from ai.index import SQLiteDocumentIndex
from ai.providers import OllamaProvider
from ai.retrieval.search import apply_calibrated_threshold, rank_candidates


def load_calibrated_threshold(path: str | Path, *, embedding_model: str) -> float | None:
    try:
        calibration = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if calibration.get("status") != "calibrated" or calibration.get("embedding_model") != embedding_model:
        return None
    threshold = calibration.get("threshold")
    return threshold if isinstance(threshold, (float, int)) and not isinstance(threshold, bool) else None


class RetrievalService:
    def __init__(self, *, settings: AISettings, index: SQLiteDocumentIndex,
                 provider: OllamaProvider, threshold: float | None):
        self.settings = settings
        self.index = index
        self.provider = provider
        self.threshold = threshold

    def retrieve(self, query: str) -> list[dict[str, Any]]:
        if self.threshold is None or not self.settings.embedding_model:
            return []
        vector = self.provider.embed([query])[0]
        candidates = self.index.search_candidates(embedding_model=self.settings.embedding_model, limit=1000)
        ranked = rank_candidates(vector, candidates, top_k=self.settings.retrieval_top_k)
        accepted = apply_calibrated_threshold(ranked, self.threshold)
        return [
            {
                "citation_id": item["chunk_id"], "text": item["text"],
                "similarity": item["similarity"], "page": item["page_number"],
                "source_id": item["source_id"], "title": item["title"],
                "source_uri": item["uri"], "review_status": item["review_status"],
                "content_hash": item["content_hash"], "publication_date": item["publication_date"],
                "document_type": item["document_type"],
            }
            for item in accepted
        ]


def validate_citations(candidate_ids: list[str], retrieved: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Reject any model citation not present in the current retrieval result."""
    by_id = {item["citation_id"]: item for item in retrieved}
    if any(not isinstance(cid, str) or cid not in by_id for cid in candidate_ids):
        raise ValueError("Model cited an ID outside the retrieved evidence set")
    citations = []
    for citation_id in dict.fromkeys(candidate_ids):
        item = by_id[citation_id]
        citations.append({key: item[key] for key in (
            "citation_id", "source_id", "title", "source_uri", "page",
            "content_hash", "review_status",
            "publication_date", "document_type",
        )})
    return citations
