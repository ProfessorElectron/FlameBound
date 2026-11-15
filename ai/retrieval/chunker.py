
"""Text chunking utilities for FlameBound RAG."""

def chunk_documents(documents, chunk_size=1000, overlap=200):
    """Split extracted document pages into overlapping chunks."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")

    chunks = []

    for document in documents:
        text = document["text"]
        metadata = document["metadata"]

        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        **metadata,
                        "chunk_index": len(chunks),
                        "start_char": start,
                        "end_char": end,
                    },
                })

            if end == len(text):
                break

            start = end - overlap

    return chunks
