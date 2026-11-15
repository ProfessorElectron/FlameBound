# FlameBound AI Integration Recovery Plan

**Baseline:** `main` at `08e22c9`
**Recovery source reviewed:** `origin/feature/flamebound-ai-rag` at `87dc9ea`
**Status:** Baseline recovery and shared scientific service are complete. Backend AI foundation and assistant API are implemented on `codex/flamebound-phase0`; frontend integration is intentionally out of scope for the current stage.

## Goals and boundaries

Preserve the recovered FlameBound application while developing the scientific backend and AI integration in parallel. The deterministic atmospheric engine remains authoritative for supported calculations. The model may explain a result, but must not calculate or alter authoritative outputs.

The first supported tools, after assistant implementation, are limited to oxygen partial pressure and atmospheric comparison. Mass fraction remains unavailable until the server-side verified diluent registry is restored and populated with reviewed records. There is no supported fire-behavior prediction or safety/certification operation.

## Recovery inventory

Start from `08e22c9`, not the destructive feature tip. Restore the following from that baseline:

- Backend/API: `backend/app/main.py`, `backend/app/api/atmosphere.py`, `backend/app/schemas/atmosphere.py`, `backend/app/services/diluent_registry.py`, and `backend/app/version.py`.
- Scientific code and tests: `modelling/atmospheric.py`, `modelling/data_harmonization.py`, `tests/test_atmospheric.py`, `tests/test_atmospheric_api.py`, `tests/test_data_harmonization.py`, and `scripts/build_psi_audit.py`.
- Project metadata: `README.md`, `pyproject.toml`, `data/metadata/dataset_inventory.csv`, `data/metadata/harmonisation_log.csv`, `data/metadata/processing_log.csv`, and `data/metadata/source_registry.csv`.
- Processed artifacts: `data/processed/audit/bass_audit.csv`, `bass_ii_audit.csv`, `saffire_i_audit.csv`, `saffire_ii_audit.csv`, `saffire_iii_audit.csv`, `source_file_review.csv`, and `data/processed/harmonised/test_points.csv`.
- Research documentation: `docs/MODELLING_KICKOFF.md`, `docs/atmospheric_engine.md`, `docs/data_audit_report.md`, `docs/data_dictionary.md`, `docs/evidence_assessment.md`, `docs/harmonisation_plan.md`, `docs/mathematical_framework.md`, all existing `docs/phase3_review/*.md`, `docs/phase4/fastapi_scientific_interface.md`, all existing `docs/phase5/*.md`, and all existing `docs/scientific_review/*.md`.
- Frontend recovery is planned for its own phase. The affected paths are `frontend/src/App.jsx`, `frontend/src/main.jsx`, `frontend/src/api.js`, `frontend/src/App.css`, `frontend/src/index.css`, `frontend/package.json`, and `frontend/package-lock.json`. Do not modify these during the initial backend stage.

The six teammate modules were selectively restored and refactored: `ai/document_ingestion/pdf_loader.py`, `ai/llm/ollama_client.py`, `ai/rag/pipeline.py`, and `ai/retrieval/{chunker,embeddings,search}.py`. New AI code lives in centralized configuration/providers, controlled ingestion, SQLite indexing, retrieval evaluation, and backend orchestration modules. The feature branch's `ai/**/test_*.py` files remain excluded; normal tests are mocked and assertion-based. Do not retain generated `flamebound_research.egg-info/*` files.

The feature branch also contains a separate `modelling/evidence_coverage.py` implementation and `tests/test_evidence_coverage.py` changes. Review these as a separate scientific change; do not treat them as part of AI integration or as evidence backed by verified data.

## Required architecture decisions

### Deterministic service boundary

Both existing HTTP routes and future assistant tools call the same typed functions in a shared backend atmospheric service. The HTTP API remains an adapter and must preserve its current paths, request schemas, response envelope, error codes, API schema version, and provenance semantics. The assistant must not make internal HTTP self-calls.

The mass-fraction route/tool remains unavailable when the registry has no reviewed `MEASURED` or `DERIVED` diluent. Do not infer air or nitrogen.

### Assistant response can represent multiple bases

One response may combine general scientific background, reviewed evidence, and a deterministic calculation. Represent the basis as a validated collection, not one mutually exclusive enum, for example:

```json
{
  "status": "answered",
  "explanation": "Generated explanatory text.",
  "bases": [
    {"kind": "general_background"},
    {"kind": "reviewed_evidence", "citation_ids": ["..." ]},
    {"kind": "deterministic_calculation", "calculation_id": "..."}
  ],
  "citations": [],
  "calculation": null
}
```

The `calculation` field contains the unmodified server result envelope, or `null`. The LLM supplies explanation text only; the UI displays numeric outputs, units, verification, provenance, assumptions, limitations, and warnings from the calculation envelope itself. General model knowledge must be labeled and must not be described as a project finding. Evidence citations must be constructed from trusted server metadata.

### Strict tool execution boundary

Atmospheric calculation intent and arguments are parsed from the current user question with a narrow deterministic grammar; the model is not asked to select or supply calculation arguments. A server-owned mapping accepts only named tools, validates parsed arguments through the existing strict Pydantic request models, and invokes the shared deterministic service. The calculation explanation is rendered by the server from the result envelope.

Start with a hard maximum of **one tool execution per assistant request**. Reject unknown tool names, extra/missing fields, invalid types, values outside schema constraints, and any second tool request. Missing natural-language parameters must produce a clarification request; do not fill them with defaults. Never expose arbitrary Python, shell, filesystem, network, or dynamically selected URL tools.

Ollama tool-call compatibility probes are informative only and do not authorize model-supplied calculation arguments. Keep deterministic API tests independent of Ollama; separately gated live probes may test provider behavior.

### Stateless, bounded conversation context

The backend does not persist chat state in the first release. The frontend may submit a bounded history with each request. The schema allows only user/assistant roles, a limited number of turns, and capped content length; it rejects system/developer/tool roles and oversized histories. Treat all supplied history as untrusted user-controlled context and never use it to grant tools, provenance, or verification.

### Evidence retrieval and threshold calibration

Do not select a similarity threshold by intuition. First create a small human-labeled query set containing relevant, partially relevant, unrelated, and absent-evidence cases. Record expected source/page matches. Evaluate top-k retrieval, false-support rate, and abstention behavior for each embedding model. Choose and document a threshold from those results; if the evidence is weak or absent, return `insufficient_evidence` rather than prompting the model to guess.

Each stored chunk carries a stable source ID, title, source URI, version/date, content hash, page and offsets, review status, and embedding model/version. Never expose local filesystem paths. The model may only propose citations from retrieved chunk IDs; the server validates membership and builds the displayed citation from trusted metadata. Treat document text as untrusted prompt content and enforce tool policy in code, not only in system instructions.

## Model configuration plan

Use server-side environment settings for the Ollama base URL, generation model, embedding model, timeouts, output limits, and retrieval/index version. Keep generation and embedding settings distinct.

The inspected machine has `qwen3:0.6b`, `qwen3:4b`, `llava:latest`, and `phi3:latest`; the feature code defaults to `llama3.2` and `nomic-embed-text`, which were not listed as installed. Treat `qwen3:4b` as a generation candidate and `qwen3:0.6b` as a smaller comparison candidate, not as verified replacements. No listed model is confirmed as an embedding model. Do not download models in this phase. For later compatibility checks, verify generation, tool call schema adherence, `/api/embed` or the supported embedding endpoint, vector finiteness/dimension stability, retrieval quality, latency, and laptop memory. Store the exact model identifier and vector dimension with the persistent index; changing embedding models requires re-indexing.

## Phases and dependency order

1. **Completed — Phase 0 and scientific service restoration.** The recovery worktree is based on `08e22c9`; baseline/API regressions and shared service delegation pass.
2. **Completed — selective AI module recovery.** The six approved teammate modules were copied by exact paths and refactored; no destructive frontend/backend replacements were brought over.
3. **Implemented, awaiting data/model prerequisites — provider, ingestion, persistent index, retrieval evaluation.** The SQLite schema stores source metadata, review status, page/chunk identifiers, content hash, embedding model and dimension. Ingestion requires an explicit approval record and validates paths and hashes. The labeled query set exists, but no embedding model is selected and no threshold is calibrated; retrieval abstains.
4. **Implemented — assistant API and deterministic calculations.** Stateless bounded history, citations, multi-basis response, separate calculation envelope, and a one-calculation server allowlist are in place. Calculation questions use deterministic field-bound parsing and do not rely on model tool selection. A live model-driven end-to-end attempt failed to emit a tool call within its output budget; that path is no longer used for calculations. The current endpoint calculation path is covered by mocked HTTP tests.
5. **Later — frontend integration.** Keep the React application unchanged until the team integrates against the stable endpoint contract. Display explanation, citations, and raw calculation envelope separately.
6. **Pending — scientific validation.** Evaluate retrieval and model behavior after an embedding model is selected and approved source documents are indexed. Verify provenance and limitations before claiming retrieval readiness.

## Safe recovery commands (PowerShell; plan only)

Inspect changes separately before restoring or staging:

```powershell
git status --short --branch
git diff --name-status 08e22c9..HEAD       # committed changes
git diff --cached --name-status           # staged changes
git diff --name-status                    # unstaged tracked changes
git ls-files --others --exclude-standard  # untracked files
```

Create a recovery branch from the baseline, then selectively copy only RAG source files later:

```powershell
git switch -c codex/flamebound-ai-recovery 08e22c9
git restore --source=origin/feature/flamebound-ai-rag --worktree -- `
  ai/document_ingestion/pdf_loader.py `
  ai/llm/ollama_client.py `
  ai/rag/pipeline.py `
  ai/retrieval/chunker.py `
  ai/retrieval/embeddings.py `
  ai/retrieval/search.py
```

If operating on a checkout that already contains the destructive commit, restore exact baseline paths with `git restore --source=08e22c9 --worktree -- <file paths>`; enumerate individual files, including the paths listed in the recovery inventory. Do not use `docs`, `data/processed/audit`, or other whole-directory pathspecs because they may erase newly created work. Review each Git state independently: inspect committed history with `git log` and `git diff <base>..HEAD`, staged changes with `git diff --cached`, unstaged tracked changes with `git diff`, and untracked paths with `git status --short --untracked-files=all`. Do not stage until all four are accounted for.

## Current initial-stage status

- The implementation worktree/branch, `codex/flamebound-phase0`, starts directly from baseline commit `08e22c9`; local `main` remains untouched.
- Phase 0 baseline recovery is represented by using the intact baseline as the starting point. No directory-wide restoration was run and no README, metadata, audit output, or historical research document was rewritten.
- `backend/app/services/atmospheric_service.py` is shared by the original atmospheric routes and assistant tools; original API regressions pass.
- Assistant API is registered at `POST /api/assistant/chat`. The generated explanation and authoritative atmospheric calculation are separate response fields. Calculation inputs are parsed only from the current user question; ambiguous or missing absolute pressure basis results in clarification. Calculation explanations are server-rendered from engine output.
- `ai/ingestion_approvals.csv` intentionally has no records; current source metadata has no approval/review status. `pypdf` is an optional, uninstalled dependency. No documents have been ingested, no database has been populated, and retrieval stays disabled until approval plus embedding-model threshold calibration.
- The full Python suite reports 99 tests: 97 passed and 2 opt-in provider compatibility tests skipped. The tightened live model-driven end-to-end calculation attempt was executed and failed to produce a tool call; the assistant now executes explicit calculations deterministically without model-supplied arguments. Retrieval is not calibrated, and expected page matches in the source-level evaluation set await document review. No frontend files were changed.
