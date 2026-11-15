# FlameBound

FlameBound is a research project for organizing and analysing NASA solid-fuel combustion investigations, including BASS, BASS-II, and SAFFIRE. It aims to compare documented test conditions, map where evidence exists, and make the limits of any analysis visible. It is not a material certification or habitat safety assessment.

## Project status

The repository contains raw PSI tables and supporting files for BASS, BASS-II, and SAFFIRE-I/II/III, plus an initial conservative source audit. The audit has not verified any test-point records, and `data/processed/harmonised/test_points.csv` remains header-only. A typed deterministic atmospheric engine and its strict FastAPI interface are implemented; evidence coverage and statistical models remain unimplemented, while the frontend and AI retrieval are scaffolds. The mass-fraction API remains unavailable until a trusted diluent catalogue exists. See `docs/atmospheric_engine.md`, `docs/phase4/fastapi_scientific_interface.md`, `docs/data_audit_report.md`, and `docs/scientific_review/` for current findings and limits.

## Setup

Use Python 3.10 or newer and Node.js 20.19+ or 22.12+ for the optional frontend.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Run the API with `python -m uvicorn backend.app.main:app --reload` after installing `requirements.txt`.

For the backend setup, endpoint contract, and integration limits, see [the backend handover](docs/phase5/backend_handover.md).

The frontend scaffold is in `frontend/`; run `npm install` and `npm run dev` from that directory when working on it.

## Repository map

- `data/raw/nasa_psi/`: source files, arranged by investigation and source type.
- `data/processed/`: harmonised, cleaned, and derived datasets.
- `data/metadata/`: dataset inventory, source registry, and processing log templates.
- `data/template/`: blank test-point CSV template.
- `docs/`: mathematical framework, data dictionary, source notes, and limitations.
- `modelling/`: deterministic scientific calculations and analysis modules.
- `backend/`: FastAPI atmospheric calculation interface; evidence and experiment routes remain unimplemented.
- `frontend/`: React/Vite interface scaffold.
- `ai/`: future document ingestion, retrieval, prompts, and evaluation.
- `notebooks/`: exploratory analysis only; reusable calculations belong in `modelling/`.
- `results/`: generated figures, reports, and model evaluations.
- `tests/`: Python tests for the modelling code.

See [the mathematical framework](docs/mathematical_framework.md) and [the data dictionary](docs/data_dictionary.md) before adding or interpreting experimental rows.
