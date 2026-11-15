
from ai.document_ingestion.pdf_loader import load_pdf
from ai.retrieval.chunker import chunk_documents
from ai.retrieval.embeddings import embed_documents


pdf_path = (
    "data/raw/nasa_psi/BASS/"
    "science_documents/SRD_BASS.pdf"
)

pages = load_pdf(pdf_path)
chunks = chunk_documents(pages)

embedded_chunks = embed_documents(chunks)

print("Chunks embedded:", len(embedded_chunks))
print("Embedding dimensions:", len(embedded_chunks[0]["embedding"]))
print("Source:", embedded_chunks[0]["metadata"]["source"])
print("Page:", embedded_chunks[0]["metadata"]["page"])
