# FlameBound release-candidate manifest

**Candidate type:** Technical review package with distribution hold.

**Prepared:** 2026-11-15.

**Branch:** `codex/flamebound-phase0`.

**Archive:** `FlameBound-preclearance-candidate-20261115-215000.zip` in the user's Downloads folder.

The candidate snapshot contains 117 files. The path inventory records 120 existing repository paths excluded from it, plus the absent local-only workbook and eight exclusion-policy patterns.

## Release status

This archive is a functional review candidate that omits PSI sources and source-derived research outputs. It is **not cleared for public redistribution or final submission**. Contributor authorization, PSI-source terms, and a subset of Python package license evidence remain unresolved. The candidate manifest does not grant rights or make legal representations.

The complete path-level inventory is [`release_candidate_inventory.csv`](release_candidate_inventory.csv). It records each file included or excluded from the current working tree and the reason. The archive contains its own copy of that inventory.

## Included

- Application source: `ai/`, `backend/`, `frontend/`, and `modelling/`.
- Root setup and project notices: `README.md`, `LICENSE`, `THIRD_PARTY_NOTICES.md`, `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, and `uv.lock`.
- Frontend source manifests and lockfile; no installed npm dependencies or build output.
- Current setup, demo, API, architecture, and limitation documentation, including `docs/submission/` and `docs/phase5/`.
- Python tests and live Ollama compatibility tests.
- Small repository configuration files such as `.gitignore`.

The exact paths and SHA-256 hashes are in the inventory CSV. Project authorship and license authorization still require human confirmation.

## Excluded

- `data/raw/nasa_psi/**`: PSI source files and placeholders; redistribution rights are unresolved. The separate local-only BASS workbook with the credential-like-content flag was not present in the worktree and is explicitly excluded.
- `data/processed/**`, `data/metadata/**`, and `data/index/**`: audit outputs, the 75-row harmonisation log, provenance registries, processing records, and indexes are source-linked or derived; omitted pending review.
- `results/**`, `notebooks/**`, and PSI audit/source-review reports, including `docs/data_audit_report.md`, `docs/data_dictionary.md`, `docs/evidence_assessment.md`, `docs/harmonisation_plan.md`, `docs/NASA_DATA_SOURCES.md`, `docs/phase3_review/**`, and `docs/scientific_review/**`.
- `scripts/build_psi_audit.py`, because it consumes the excluded PSI files and is not needed to run the application.
- `.git`, virtual environments, `node_modules`, `dist`, `build`, caches, `*.egg-info`, local databases, model weights, `.env*`, and secret/credential files.

These exclusions are applied to the candidate archive only. The original repository files remain in place.

## Verification performed

- Clean locked Python 3.13 environment: **101 unittest cases passed**; the two opt-in live Ollama probes were skipped in this default run.
- Live Ollama compatibility tests with `qwen3:4b`: **2 probes passed**. This is a narrow compatibility check, not a reliability claim.
- FastAPI health, direct oxygen partial pressure, direct scenario comparison, assistant calculations/clarifications/unsupported prediction/evidence abstention: passed through real HTTP.
- Vite served the frontend and proxied `/api/health`, assistant calculation, and evidence abstention successfully to FastAPI.
- Controlled Ollama-unavailable test: general-background response returned HTTP 503 with `provider_unavailable`; deterministic calculation still returned 21.27825 kPa.
- Clean temporary frontend copy: `npm ci` and `npm run build` passed. `npm ci` in the working frontend directory could not replace an in-use native Vite binding because the existing Vite server was running; no forced file removal was attempted.
- `uv lock --check`, Python `compileall`, and `git diff --check` passed.
- No browser automation package was available, so browser console/navigation inspection was not performed. The HTTP workflow and production build were verified.

## Known limits and remaining hold items

- No PSI test data, audit export, or evidence index is included.
- Project evidence retrieval is unavailable; no validated flame-spread or lunar prediction is provided.
- Ollama was available during the live probe; general responses require it. The controlled unavailable-provider path was verified separately.
- No browser-console test, hosted deployment, authentication, or production CORS validation was performed.
- Confirm all contributors' authorization, resolve uncommitted authorship, review the 12 Python license metadata gaps and upstream resolver warning, and inspect the live team Project Tab and local-event requirements before any public release.
- See [`project_tab_guide.md`](project_tab_guide.md) and [`submission_checklist.md`](submission_checklist.md) for team-entered submission steps.
