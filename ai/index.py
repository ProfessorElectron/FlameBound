"""Persistent SQLite index for approved source documents and page chunks."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


class SQLiteDocumentIndex:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript(
                """
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS documents (
                    source_id TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    title TEXT NOT NULL,
                    uri TEXT NOT NULL,
                    review_status TEXT NOT NULL,
                    publication_date TEXT NOT NULL DEFAULT '',
                    document_type TEXT NOT NULL DEFAULT '',
                    PRIMARY KEY (source_id, content_hash)
                );
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    page_number INTEGER NOT NULL,
                    start_char INTEGER NOT NULL,
                    end_char INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    embedding_model TEXT NOT NULL,
                    embedding_dimension INTEGER NOT NULL,
                    embedding_json TEXT NOT NULL,
                    FOREIGN KEY (source_id, content_hash)
                      REFERENCES documents(source_id, content_hash) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS chunks_source_page ON chunks(source_id, page_number);
                """
            )

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def upsert_document(self, *, source_id: str, content_hash: str, title: str, uri: str,
                        review_status: str, chunks: list[dict[str, Any]],
                        publication_date: str = "", document_type: str = "") -> None:
        if not source_id or not content_hash or not title or not uri.startswith("https://"):
            raise ValueError("Document identity and an HTTPS source URI are required")
        if review_status not in {"unreviewed", "reviewed"}:
            raise ValueError("review_status must be unreviewed or reviewed")
        with self._connect() as db:
            db.execute("DELETE FROM documents WHERE source_id=?", (source_id,))
            db.execute(
                """INSERT INTO documents
                   (source_id, content_hash, title, uri, review_status, publication_date, document_type)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (source_id, content_hash, title, uri, review_status, publication_date, document_type),
            )
            embedding_dimension = None
            for chunk in chunks:
                vector = chunk["embedding"]
                if not vector or (embedding_dimension is not None and len(vector) != embedding_dimension):
                    raise ValueError("Document embeddings must be non-empty and have a stable dimension")
                embedding_dimension = len(vector)
                db.execute(
                    """INSERT INTO chunks
                       (chunk_id, source_id, content_hash, page_number, start_char, end_char, text,
                        embedding_model, embedding_dimension, embedding_json)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (chunk["chunk_id"], source_id, content_hash, int(chunk["page_number"]),
                     int(chunk["start_char"]), int(chunk["end_char"]), chunk["text"],
                     chunk["embedding_model"], len(vector), json.dumps(vector, allow_nan=False)),
                )

    def search_candidates(self, *, embedding_model: str, limit: int = 1000) -> list[dict[str, Any]]:
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 10000:
            raise ValueError("candidate limit must be between 1 and 10000")
        with self._connect() as db:
            rows = db.execute(
                """SELECT c.*, d.title, d.uri, d.review_status, d.publication_date, d.document_type
                   FROM chunks c JOIN documents d USING(source_id, content_hash)
                   WHERE c.embedding_model=? ORDER BY c.source_id, c.page_number LIMIT ?""",
                (embedding_model, limit),
            ).fetchall()
        return [{**dict(row), "embedding": json.loads(row["embedding_json"])} for row in rows]

    def citation_metadata(self, chunk_ids: list[str]) -> dict[str, dict[str, Any]]:
        if not chunk_ids:
            return {}
        if len(chunk_ids) > 100:
            raise ValueError("At most 100 citation IDs may be resolved at once")
        placeholders = ",".join("?" for _ in chunk_ids)
        with self._connect() as db:
            rows = db.execute(
                f"""SELECT c.chunk_id, c.page_number, c.content_hash, d.source_id,
                           d.title, d.uri, d.review_status, d.publication_date, d.document_type
                    FROM chunks c JOIN documents d USING(source_id, content_hash)
                    WHERE c.chunk_id IN ({placeholders})""",
                chunk_ids,
            ).fetchall()
        return {
            row["chunk_id"]: {
                "citation_id": row["chunk_id"], "source_id": row["source_id"],
                "title": row["title"], "source_uri": row["uri"],
                "page": row["page_number"], "content_hash": row["content_hash"],
                "review_status": row["review_status"], "publication_date": row["publication_date"],
                "document_type": row["document_type"],
            }
            for row in rows
        }
