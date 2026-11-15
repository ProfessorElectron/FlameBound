"""Registry-gated PDF ingestion with path containment and size limits."""

from __future__ import annotations

import hashlib
import csv
import re
from pathlib import Path
from typing import Any

from ai.config import AISettings
from ai.document_ingestion.pdf_loader import load_pdf
from ai.index import SQLiteDocumentIndex
from ai.providers import OllamaProvider
from ai.retrieval.chunker import chunk_documents


def load_approved_registry_entries(repo_root: str | Path) -> list[dict[str, Any]]:
    """Join project source/inventory registries with explicit AI ingestion approvals."""
    root = Path(repo_root)
    source_path = root / "data" / "metadata" / "source_registry.csv"
    inventory_path = root / "data" / "metadata" / "dataset_inventory.csv"
    approvals_path = root / "ai" / "ingestion_approvals.csv"
    if not all(path.is_file() for path in (source_path, inventory_path, approvals_path)):
        return []
    with source_path.open(encoding="utf-8-sig", newline="") as handle:
        sources = {row["source_id"]: row for row in csv.DictReader(handle)}
    with inventory_path.open(encoding="utf-8-sig", newline="") as handle:
        inventory = {row["dataset_id"]: row for row in csv.DictReader(handle)}
    approved = []
    with approvals_path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            source_id = row.get("source_id", "")
            if row.get("ingestion_approved", "").lower() != "true":
                continue
            source, asset = sources.get(source_id), inventory.get(source_id)
            if not source or not asset:
                raise ValueError("AI ingestion approval references an unknown source registry entry")
            approval_hash = (row.get("content_hash") or "").strip().casefold()
            inventory_hash = (asset.get("checksum_sha256") or "").strip().casefold()
            if not re.fullmatch(r"[0-9a-f]{64}", approval_hash):
                raise ValueError("AI ingestion approval must bind to a SHA-256 content hash")
            if not re.fullmatch(r"[0-9a-f]{64}", inventory_hash) or approval_hash != inventory_hash:
                raise ValueError("AI approval content hash does not match the source inventory")
            review_status = (row.get("review_status") or "").strip()
            if review_status not in {"unreviewed", "reviewed"}:
                raise ValueError("AI ingestion approval has an invalid review status")
            if not row.get("approved_by", "").strip() or not row.get("approved_utc", "").strip():
                raise ValueError("AI ingestion approval must record approver and approval time")
            approved.append({
                "source_id": source_id, "title": source["title"], "uri": source["uri"],
                "local_path": asset["local_path"], "ingestion_approved": True,
                "review_status": review_status,
                "expected_sha256": inventory_hash,
                "approval_content_hash": approval_hash,
                "publication_date": source.get("publication_date", ""),
                "document_type": source.get("document_type", ""),
                "approved_by": row.get("approved_by", ""),
                "approved_utc": row.get("approved_utc", ""),
            })
    return approved


def ingest_approved_source(source_id: str, *, repo_root: str | Path,
                           index: SQLiteDocumentIndex, provider: OllamaProvider,
                           settings: AISettings | None = None) -> int:
    root = Path(repo_root)
    entries = load_approved_registry_entries(root)
    entry = next((item for item in entries if item["source_id"] == source_id), None)
    if entry is None:
        raise ValueError("Source has no explicit AI ingestion approval")
    if not entry["approved_by"] or not entry["approved_utc"]:
        raise ValueError("AI ingestion approval must record approver and approval time")
    return _ingest_registered_pdf(entry, repo_root=root, index=index, provider=provider, settings=settings)


def _ingest_registered_pdf(entry: dict[str, Any], *, repo_root: str | Path,
                           index: SQLiteDocumentIndex, provider: OllamaProvider,
                           settings: AISettings | None = None) -> int:
    """Ingest only an explicitly approved registry entry under data/raw/nasa_psi."""
    settings = settings or provider.settings
    if entry.get("ingestion_approved") is not True:
        raise ValueError("Source registry entry is not approved for ingestion")
    if entry.get("review_status") not in {"unreviewed", "reviewed"}:
        raise ValueError("Source registry entry has an invalid review status")
    if not entry.get("approved_by") or not entry.get("approved_utc"):
        raise ValueError("Source approval must record approver and approval time")
    for key in ("source_id", "title", "uri", "local_path"):
        if not isinstance(entry.get(key), str) or not entry[key].strip():
            raise ValueError(f"Source registry entry requires {key}")
    if not entry["uri"].startswith("https://"):
        raise ValueError("Source registry URI must use HTTPS")

    root = Path(repo_root).resolve()
    allowed_root = (root / "data" / "raw" / "nasa_psi").resolve()
    path = (root / entry["local_path"]).resolve()
    if not path.is_relative_to(allowed_root) or path.suffix.lower() != ".pdf":
        raise ValueError("Registered document must be a PDF inside data/raw/nasa_psi")
    raw = path.read_bytes()
    if len(raw) > settings.max_pdf_bytes:
        raise ValueError("PDF exceeds the configured size limit")
    content_hash = hashlib.sha256(raw).hexdigest()
    expected_hash = entry.get("expected_sha256")
    approval_hash = entry.get("approval_content_hash")
    if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash.casefold()):
        raise ValueError("Source inventory must provide a valid SHA-256 content hash")
    if not isinstance(approval_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", approval_hash.casefold()):
        raise ValueError("Source approval must bind to a SHA-256 content hash")
    if expected_hash.casefold() != content_hash or approval_hash.casefold() != content_hash:
        raise ValueError("PDF content hash does not match the source inventory and approval record")
    pages = load_pdf(path, max_bytes=settings.max_pdf_bytes, max_pages=settings.max_pdf_pages)
    chunks = chunk_documents(
        pages, source_id=entry["source_id"], content_hash=content_hash,
        max_chunks=settings.max_chunks_per_document,
    )
    embedded = []
    for offset in range(0, len(chunks), 32):
        embedded.extend(provider.embed([chunk["text"] for chunk in chunks[offset:offset + 32]]))
    if len(embedded) != len(chunks):
        raise ValueError("Embedding provider returned an incomplete batch")
    model_name = settings.embedding_model
    if chunks and not model_name:
        raise ValueError("An embedding model must be selected before PDF ingestion")
    stored = [
        {**chunk, "embedding": vector, "embedding_model": model_name}
        for chunk, vector in zip(chunks, embedded)
    ]
    index.upsert_document(
        source_id=entry["source_id"], content_hash=content_hash,
        title=entry["title"], uri=entry["uri"],
        review_status=entry["review_status"], chunks=stored,
        publication_date=entry.get("publication_date", ""),
        document_type=entry.get("document_type", ""),
    )
    return len(stored)
