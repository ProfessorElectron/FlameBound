
from ai.document_ingestion.pdf_loader import load_pdf
from ai.retrieval.chunker import chunk_documents
from ai.retrieval.embeddings import embed_documents
from ai.rag.pipeline import answer_question


pdf_path = (
    "data/raw/nasa_psi/BASS/"
    "science_documents/SRD_BASS.pdf"
)

# Step 1: Load NASA research
pages = load_pdf(pdf_path)

# Step 2: Split research into chunks
chunks = chunk_documents(pages)

# Step 3: Generate embeddings
embedded_chunks = embed_documents(chunks)

# Step 4: Ask a scientific question
question = (
    "What is the boiling point of liquid nitrogen "
    "at 1 atmosphere?"
)

# Step 5: Run the complete RAG pipeline
result = answer_question(
    question,
    embedded_chunks,
    top_k=3,
)

print("\n" + "=" * 60)
print("FLAMEBOUND AI RESPONSE")
print("=" * 60)

print("\nQUESTION:")
print(result["question"])

print("\nANSWER:")
print(result["answer"])

print("\nSUPPORTING SOURCES:")

for source in result["sources"]:
    print(
        f"- {source['source']} | "
        f"Page {source['page']} | "
        f"Similarity: {source['similarity']:.4f}"
    )

print("\n" + "=" * 60)
