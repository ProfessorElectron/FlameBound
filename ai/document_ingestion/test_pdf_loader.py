
from ai.document_ingestion.pdf_loader import load_pdf


pdf_path = (
    "data/raw/nasa_psi/BASS/"
    "science_documents/SRD_BASS.pdf"
)

pages = load_pdf(pdf_path)

print(f"Extracted {len(pages)} pages")

for page in pages[:2]:
    print("\nSOURCE:", page["metadata"]["source"])
    print("PAGE:", page["metadata"]["page"])
    print("TEXT PREVIEW:", page["text"][:300])
