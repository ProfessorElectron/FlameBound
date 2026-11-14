# FlameBound

FlameBound is a research project for organizing and analysing NASA solid-fuel combustion investigations, including BASS, BASS-II, and SAFFIRE. It aims to compare documented test conditions, map where evidence exists, and make the limits of any analysis visible. It is not a material certification or habitat safety assessment.

## Project status

The repository currently contains the mathematical framework, atmospheric calculation functions, a proposed data schema, and their initial tests. NASA experiment records, coverage analysis, statistical models, the API, the frontend, and AI retrieval are not implemented yet.

## Setup

Use Python 3.10 or newer and Node.js 20.19+ or 22.12+ for the optional frontend.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

The frontend scaffold is in `frontend/`; run `npm install` and `npm run dev` from that directory when working on it.

## Repository map

- `data/raw/nasa_psi/`: source files, arranged by investigation and source type.
- `data/processed/`: harmonised, cleaned, and derived datasets.
- `data/metadata/`: dataset inventory, source registry, and processing log templates.
- `data/template/`: blank test-point CSV template.
- `docs/`: mathematical framework, data dictionary, source notes, and limitations.
- `modelling/`: deterministic scientific calculations and analysis modules.
- `backend/`: API scaffold for serving modelling and evidence results.
- `frontend/`: React/Vite interface scaffold.
- `ai/`: future document ingestion, retrieval, prompts, and evaluation.
- `notebooks/`: exploratory analysis only; reusable calculations belong in `modelling/`.
- `results/`: generated figures, reports, and model evaluations.
- `tests/`: Python tests for the modelling code.

See [the mathematical framework](docs/mathematical_framework.md) and [the data dictionary](docs/data_dictionary.md) before adding or interpreting experimental rows.
