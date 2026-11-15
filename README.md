# FlameBound

FlameBound is a research project for organizing and analysing NASA solid-fuel combustion investigations, including BASS, BASS-II, and SAFFIRE. It aims to compare documented test conditions, map where evidence exists, and make the limits of any analysis visible. It is not a material certification or habitat safety assessment.

## Purpose and current status

FlameBound is a research workspace for organizing NASA's BASS, BASS-II, and SAFFIRE solid-fuel combustion investigations and making the limits of experimental evidence visible. The motivating problem is that fire-safety decisions for spacecraft environments must not be inferred from sparse experiments without tracking conditions, provenance, and uncertainty. FlameBound is not a fire-safety certification or operational decision system.

The current usable scientific engine calculates oxygen partial pressure and compares two atmospheric conditions. Its equation is `p(O₂) = X(O₂) × P`; pressure must be absolute, units are converted deterministically, and API inputs are marked user-supplied and unverified. It does not predict ignition or flame spread. The mass-fraction operation remains unavailable without a reviewed diluent record. The development working tree contains PSI source files, but redistribution rights remain unresolved and the public-release candidate excludes them. No reviewed harmonised test-point rows are available. Dashboard records and visualizations are illustrative fixtures, not NASA statistics.

The React assistant calls the FastAPI `/api/assistant/chat` endpoint. Explicit atmospheric calculation requests are parsed and executed by the deterministic server-side calculation service; the LLM does not supply or rewrite calculation inputs or results. Ollama generation is used only for non-calculation responses. Project evidence retrieval is currently unavailable: there are no approved ingested documents or calibrated retrieval configuration, so the assistant abstains on project-evidence questions and does not claim general model knowledge as retrieved evidence. Do not interpret this prototype as a validated lunar flame-spread model.

**Technology stack:** Python, FastAPI, and Pydantic for the API and calculation boundary; React 19 and Vite for the browser interface; Ollama as an optional local language-model provider for non-calculation questions. SQLite and embedding support exist as retrieval infrastructure, but project retrieval is not operational.

See `docs/atmospheric_engine.md`, `docs/mathematical_framework.md`, `docs/phase4/fastapi_scientific_interface.md`, and `docs/phase5/` for scientific contracts and historical implementation reviews. The locked startup guide and API walkthrough are in [the demo script](docs/submission/demo_script.md) and [AI setup guide](docs/phase5/ai_setup.md). The Phase 5 handover and audit documents are historical snapshots; see [the Phase 5 index](docs/phase5/README.md).

Before publicly distributing the project, review [third-party notices and source provenance](THIRD_PARTY_NOTICES.md). PSI document redistribution terms and authorization for all project contributors have not yet been confirmed.

## Setup

Use Python 3.10 or newer and Node.js 20.19+ or 22.12+. For a locked Python environment, install `uv` once and sync from the repository root:

```powershell
python -m pip install uv
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
```

`uv.lock` fixes the Python runtime dependency graph for Python `>=3.10`. The core install contains the API/runtime dependencies. Install optional groups only when needed: `uv sync --locked --extra ai` adds PDF ingestion support, `--extra audit` adds the PSI audit script's XLSX reader, and `--extra dev` adds pytest. The normal suite uses standard-library `unittest`. `python -m pip install -r requirements.txt` remains available as an unlocked pip alternative.

Run the API with `uv run --locked python -m uvicorn backend.app.main:app --reload` after syncing. The API is available at `http://127.0.0.1:8000`; health is at `/api/health` and interactive OpenAPI docs are at `/docs`.

For current run instructions and limitations, see [the reproducible demo script](docs/submission/demo_script.md) and [the assistant API contract](docs/phase5/assistant_api.md). Earlier Phase 5 backend handover documents are retained as historical snapshots.

In a second terminal, start the frontend:

```powershell
cd frontend
npm ci
npm run dev
```

Vite proxies `/api` calls to `http://127.0.0.1:8000` during local development. Set `FLAMEBOUND_API_PROXY_TARGET` if the backend listens elsewhere. For a separately hosted frontend, set `VITE_API_BASE_URL` to the API origin and configure an appropriately restricted backend CORS policy for that known origin. Do not expose Ollama directly to the browser.

## Short demonstration

1. Start the API and Vite frontend using the commands above.
2. Open **Scenario Analysis**, enter oxygen fraction `0.21` and absolute pressure `101.325 kPa`, then calculate. The displayed result and expandable calculation envelope come from the backend.
3. Open **AI Assistant** and ask: “Calculate oxygen partial pressure for 21% oxygen at 101.325 kPa absolute.” The response should include the deterministic result and calculation details.
4. Ask: “What experimental evidence exists for flame spread in reduced gravity?” The assistant should report that project evidence retrieval is unavailable, without fabricating citations.
5. Ask it to predict lunar flame spread; it should decline because no validated predictive model is available.

General AI answers require Ollama installed and running at `http://localhost:11434`, with the configured generation model available. The default model is `qwen3:4b`; on a fresh Ollama installation, fetch it with `ollama pull qwen3:4b` and start Ollama (for example, `ollama serve` if it is not already running). Override the endpoint or model with `FLAMEBOUND_OLLAMA_BASE_URL` and `FLAMEBOUND_OLLAMA_GENERATION_MODEL`. Deterministic calculations, unsupported-request handling, and evidence abstention do not require Ollama.

For a complete staged walkthrough, including comparison, clarification, and fallback cases, see [the reproducible demo script](docs/submission/demo_script.md). Submission preparation is tracked in [the checklist](docs/submission/submission_checklist.md); runtime and packaging details are in [the release manifest](docs/submission/release_manifest.md).

## Repository map

- `data/raw/nasa_psi/`: PSI sources in the development working tree; omitted from the pre-clearance public candidate.
- `data/processed/`: audit and harmonisation outputs in the working tree; source-derived outputs are omitted from the pre-clearance candidate.
- `data/metadata/`: source inventory and processing records; review these before any public release.
- `data/template/`: blank test-point CSV template.
- `docs/`: mathematical framework, data dictionary, source notes, and limitations.
- `modelling/`: deterministic scientific calculations and analysis modules.
- `backend/`: FastAPI atmospheric calculation and assistant endpoints; project evidence and experiment query routes remain unavailable.
- `frontend/`: React/Vite dashboard and local API integration; evidence views use clearly labeled demo fixtures.
- `ai/`: Ollama provider and retrieval infrastructure; project retrieval is disabled pending document approval and model calibration.
- `notebooks/`: exploratory analysis only; reusable calculations belong in `modelling/`.
- `results/`: generated figures, reports, and model evaluations.
- `tests/`: Python tests for the modelling code.

See [the mathematical framework](docs/mathematical_framework.md) for the calculation assumptions, and the [submission demo guide](docs/submission/demo_script.md) for a walkthrough. PSI experimental rows are not included in the release candidate.
