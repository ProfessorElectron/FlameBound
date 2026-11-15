"""Stable, page-preserving chunking for ingested source documents."""

from __future__ import annotations

import hashlib
from typing import Any


def chunk_documents(documents: list[dict[str, Any]], *, source_id: str,
                    content_hash: str, chunk_size: int = 1000,
                    overlap: int = 150, max_chunks: int = 5000) -> list[dict[str, Any]]:
    if not isinstance(chunk_size, int) or isinstance(chunk_size, bool) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")
    if not isinstance(overlap, int) or isinstance(overlap, bool) or not 0 <= overlap < chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")
    chunks: list[dict[str, Any]] = []
    for document in documents:
        text = document.get("text")
        page = document.get("page_number")
        if not isinstance(text, str) or not isinstance(page, int) or page < 1:
            raise ValueError("Each page requires text and a positive page_number")
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            piece = text[start:end].strip()
            if piece:
                identity = f"{source_id}:{content_hash}:{page}:{start}:{end}:{piece}"
                chunks.append({
                    "chunk_id": hashlib.sha256(identity.encode("utf-8")).hexdigest(),
                    "source_id": source_id,
                    "content_hash": content_hash,
                    "page_number": page,
                    "start_char": start,
                    "end_char": end,
                    "text": piece,
                })
                if isinstance(document.get("location_label"), str):
                    chunks[-1]["location_label"] = document["location_label"]
                if len(chunks) > max_chunks:
                    raise ValueError("Document exceeds the configured chunk limit")
            if end == len(text):
                break
            start = end - overlap
    return chunks
