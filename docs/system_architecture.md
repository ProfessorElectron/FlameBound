# FlameBound System Architecture

## Data flow

```text
NASA PSI files and pages
        │
        ▼
Raw source archive ──► extraction and provenance records
                              │
                              ▼
                   harmonised test-point table
                       │                  │
                       ▼                  ▼
              modelling functions     document index
                       │                  │
                       └────────┬─────────┘
                                ▼
                 backend API and evidence outputs
                       │                  │
                       ▼                  ▼
                frontend dashboard    AI assistant
```

## Component boundaries

- `data/raw/` preserves source files. Processing must not overwrite those files.
- `data/processed/` contains extracted and harmonised tables, with provenance back to source rows or document locations.
- `modelling/` contains deterministic calculations and analysis logic. It should not depend on the UI or language model.
- `backend/` exposes selected data and modelling functions through API schemas and services.
- `frontend/` collects user inputs and displays outputs, units, evidence grades, and limitations.
- `ai/` retrieves cited source passages and may call approved backend tools. It must not invent measured values or calculations.
- `results/` stores generated analysis outputs and evaluation artifacts.

The folders are scaffolds for team work. API contracts and cross-team interfaces should be agreed before feature implementations are coupled.
