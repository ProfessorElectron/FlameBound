# AI backend setup

The AI backend uses the existing FastAPI environment and a local Ollama server for non-calculation assistant responses. `qwen3:4b` is the generation default. Deterministic atmospheric requests are parsed and executed server-side without asking Ollama to choose calculation inputs. Generation and embedding configuration are separate; no embedding model is selected by default.

Optional PDF ingestion dependency:

```powershell
python -m pip install -e ".[ai]"
```

This command is documentation only; the dependency was not installed as part of this change. Set configuration before launching the backend:

```powershell
$env:FLAMEBOUND_OLLAMA_BASE_URL = "http://localhost:11434"
$env:FLAMEBOUND_OLLAMA_GENERATION_MODEL = "qwen3:4b"
$env:FLAMEBOUND_OLLAMA_EMBEDDING_MODEL = ""
$env:FLAMEBOUND_AI_DB = "data/index/flamebound.sqlite3"
$env:FLAMEBOUND_AI_TIMEOUT_SECONDS = "120"
python -m uvicorn backend.app.main:app --reload
```

The embedding model setting must remain unset until a candidate is chosen and evaluated. SQLite is created only by explicit ingestion or retrieval-index use. Database and WAL files under `data/index/` are ignored by Git.

Assistant output is bounded with `FLAMEBOUND_AI_MAX_OUTPUT_TOKENS` (default 1,024; maximum 4,096). Provider timeouts default to 120 seconds and cannot exceed 300. Other bounds are also environment-configurable through `ai/config.py`.

## Source ingestion gate

`ai/document_ingestion/service.py` joins `data/metadata/source_registry.csv` with `data/metadata/dataset_inventory.csv`, then requires a matching row in `ai/ingestion_approvals.csv` with `ingestion_approved=true`, an exact `content_hash`, a review status of `unreviewed` or `reviewed`, an approver, and an approval timestamp. The approval hash must match both the inventory SHA-256 and the actual PDF bytes. The approval file currently contains only its header. The resolved PDF must remain beneath `data/raw/nasa_psi/`. This records ingestion permission separately from scientific review status; unreviewed source passages are explicitly identified in assistant response bases and citations.

The source registry currently has no review or approval columns, the approval file has no records, and `pypdf` is not installed in the inspected environment. Consequently, document ingestion is implemented but cannot process project documents yet. The persistent index, retrieval behavior, deterministic calculation path, and provider error handling have mocked tests that do not require Ollama. Live general assistant responses do require the local Ollama service and configured generation model.
