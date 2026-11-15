
from ai.document_ingestion.pdf_loader import load_pdf
from ai.retrieval.chunker import chunk_documents
from ai.retrieval.embeddings import embed_documents
from ai.retrieval.search import semantic_search


pdf_path = (
    "data/raw/nasa_psi/BASS/"
    "science_documents/SRD_BASS.pdf"
)

# Load and process NASA research
pages = load_pdf(pdf_path)
chunks = chunk_documents(pages)

# Generate document embeddings
embedded_chunks = embed_documents(chunks)

# Ask a scientific question
query = "What affects flame spread in microgravity?"

# Retrieve the three most relevant passages
results = semantic_search(
    query,
    embedded_chunks,
    top_k=3,
)

print("\nSEARCH QUERY:", query)

for index, result in enumerate(results, start=1):
    print(f"\n--- RESULT {index} ---")
    print("Similarity:", round(result["similarity"], 4))
    print("Source:", result["metadata"]["source"])
    print("Page:", result["metadata"]["page"])
    print("Text:", result["text"][:400])
