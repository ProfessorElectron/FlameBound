# Local assistant and PSI retrieval

The FastAPI assistant uses Ollama for general natural-language responses and reads local PSI sources through a hash-verified lexical retriever. The frontend sends chat requests to FastAPI; the browser never calls Ollama directly.

## Ask the assistant

The assistant can answer general scientific questions, explain FlameBound's supported atmospheric concepts, run deterministic oxygen partial-pressure calculations, compare atmospheres, and search local PSI source files. For a calculation, include oxygen fractions, pressure values and units, and explicitly say the pressure is absolute. It does not predict flame spread or provide fire-safety decisions.

Example project questions:

- `What experiment identifiers are listed in the PSI-26 BASS experimental table?`
- `What preparation procedure is documented for BASS-II?`
- `What operations document is available for SAFFIRE-I?`
- `What else can I ask you?`

## Local file retrieval

The first retrieval request checks file hashes against `data/metadata/dataset_inventory.csv`, extracts text from supported PDF, CSV, XLSX, DOCX, PPTX, TXT, and ZIP files, and builds a local cache at `data/index/local_psi_corpus.json`. The cache is ignored by Git and must not be redistributed. Rebuilding after source changes happens when the backend restarts and the inventory hashes no longer match the cache.

Retrieval is lexical rather than embedding-based. The threshold is calibrated against the small labeled dataset in `ai/evaluation/retrieval_cases.json`; its current calibration has zero false positives and full expected-source recall on four negative and four positive cases. That result does not guarantee relevance for other questions. Query hits are excerpts, not proof that the source supports a broader scientific conclusion.

All PSI excerpts are marked **unreviewed**, and citations are constructed from the inventory registry. Do not describe these as peer-reviewed, verified experimental outcomes. The local-only BASS workbook flagged as credential-like/sensitive is explicitly excluded. Sixteen PDF sources currently yield no extractable text and therefore are not searchable; scanned documents would need a separately reviewed OCR workflow.

## Setup

Install the project dependencies, including `pypdf` for PDF text extraction:

```powershell
python -m pip install -e .
```

Then start Ollama with the configured generation model available, start FastAPI with the project command in the root README, and run Vite in a separate terminal. Search is local and does not require a separate embedding model. Ollama is required for general model-generated explanations; fixed greetings, capability guidance, common oxygen partial-pressure definitions, and deterministic calculations can be answered by the backend.

If raw PSI files are absent, excluded, or hash-mismatched, the assistant abstains from project-specific evidence answers. Public release materials continue to exclude PSI sources and the generated local index until their distribution status is resolved.
