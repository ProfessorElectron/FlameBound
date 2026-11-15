
"""PDF text extraction for FlameBound research documents."""

from pathlib import Path

from pypdf import PdfReader


def load_pdf(file_path):
    """
    Extract text from a PDF while preserving page-level metadata.

    Returns a list of dictionaries, one per page.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported")

    reader = PdfReader(str(path))

    if reader.is_encrypted:
        raise ValueError(f"Encrypted PDF cannot be processed: {path.name}")

    documents = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if not text.strip():
            continue

        documents.append({
            "text": text.strip(),
            "metadata": {
                "source": path.name,
                "source_path": str(path),
                "page": page_number,
                "total_pages": len(reader.pages),
            },
        })

    return documents
