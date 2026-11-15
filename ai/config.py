"""Environment-backed, bounded configuration for the AI subsystem."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _bounded_int(name: str, default: int, minimum: int, maximum: int) -> int:
    raw = os.getenv(name)
    value = default if raw is None else int(raw)
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


@dataclass(frozen=True)
class AISettings:
    ollama_base_url: str
    generation_model: str
    embedding_model: str | None
    database_path: Path
    request_timeout_seconds: float
    max_question_chars: int
    max_history_messages: int
    max_message_chars: int
    max_history_chars: int
    retrieval_top_k: int
    max_pdf_bytes: int
    max_pdf_pages: int
    max_chunks_per_document: int
    max_output_tokens: int

    @classmethod
    def from_env(cls) -> "AISettings":
        base_url = os.getenv("FLAMEBOUND_OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("FLAMEBOUND_OLLAMA_BASE_URL must be an HTTP(S) URL")
        embedding_model = os.getenv("FLAMEBOUND_OLLAMA_EMBEDDING_MODEL", "").strip() or None
        generation_model = os.getenv("FLAMEBOUND_OLLAMA_GENERATION_MODEL", "qwen3:4b").strip()
        if not generation_model:
            raise ValueError("FLAMEBOUND_OLLAMA_GENERATION_MODEL must not be blank")
        timeout = float(os.getenv("FLAMEBOUND_AI_TIMEOUT_SECONDS", "120"))
        if not 0 < timeout <= 300:
            raise ValueError("FLAMEBOUND_AI_TIMEOUT_SECONDS must be greater than 0 and at most 300")
        return cls(
            ollama_base_url=base_url,
            generation_model=generation_model,
            embedding_model=embedding_model,
            database_path=Path(os.getenv("FLAMEBOUND_AI_DB", "data/index/flamebound.sqlite3")),
            request_timeout_seconds=timeout,
            max_question_chars=_bounded_int("FLAMEBOUND_AI_MAX_QUESTION_CHARS", 2000, 64, 10000),
            max_history_messages=_bounded_int("FLAMEBOUND_AI_MAX_HISTORY_MESSAGES", 8, 0, 20),
            max_message_chars=_bounded_int("FLAMEBOUND_AI_MAX_MESSAGE_CHARS", 2000, 16, 10000),
            max_history_chars=_bounded_int("FLAMEBOUND_AI_MAX_HISTORY_CHARS", 8000, 0, 20000),
            retrieval_top_k=_bounded_int("FLAMEBOUND_AI_RETRIEVAL_TOP_K", 4, 1, 10),
            max_pdf_bytes=_bounded_int("FLAMEBOUND_AI_MAX_PDF_BYTES", 20_000_000, 1024, 100_000_000),
            max_pdf_pages=_bounded_int("FLAMEBOUND_AI_MAX_PDF_PAGES", 500, 1, 5000),
            max_chunks_per_document=_bounded_int("FLAMEBOUND_AI_MAX_CHUNKS", 5000, 1, 20000),
            max_output_tokens=_bounded_int("FLAMEBOUND_AI_MAX_OUTPUT_TOKENS", 1024, 32, 4096),
        )


class ProviderError(RuntimeError):
    """Safe provider failure with a stable code suitable for API mapping."""

    def __init__(self, code: str, message: str, *, retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.retryable = retryable
