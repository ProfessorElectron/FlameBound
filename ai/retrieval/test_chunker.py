
from ai.document_ingestion.pdf_loader import load_pdf
from ai.retrieval.chunker import chunk_documents


pdf_path = (
    "data/raw/nasa_psi/BASS/"
    "science_documents/SRD_BASS.pdf"
)

# Extract PDF pages
pages = load_pdf(pdf_path)

# Convert pages into overlapping chunks
chunks = chunk_documents(
    pages,
    chunk_size=1000,
    overlap=200,
)

print(f"Pages extracted: {len(pages)}")
print(f"Chunks generated: {len(chunks)}")

for index, chunk in enumerate(chunks[:3], start=1):
    print(f"\n--- CHUNK {index} ---")
    print("Source:", chunk["metadata"]["source"])
    print("Page:", chunk["metadata"]["page"])
    print("Characters:", len(chunk["text"]))
    print("Preview:", chunk["text"][:200])
