
"""Bounded page-level PDF text extraction without exposing local paths."""

from pathlib import Path

def load_pdf(file_path, *, max_bytes=20_000_000, max_pages=500):
    """Extract non-empty pages; return page number and text only."""

    path = Path(file_path)

    if not path.exists() or not path.is_file():
        raise FileNotFoundError("PDF source file is unavailable")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported")

    if path.stat().st_size > max_bytes:
        raise ValueError("PDF exceeds the configured size limit")

    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("PDF ingestion requires the optional pypdf dependency") from exc

    reader = PdfReader(str(path))

    if reader.is_encrypted:
        raise ValueError("Encrypted PDF cannot be processed")

    if len(reader.pages) > max_pages:
        raise ValueError("PDF exceeds the configured page limit")

    documents = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if not text.strip():
            continue

        documents.append({"text": text.strip(), "page_number": page_number})

    return documents
