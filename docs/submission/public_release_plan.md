# FlameBound public release plan

**Status:** Conditional release plan; not a legal clearance or a release authorization.
**Repository reviewed:** `codex/flamebound-phase0`
**Review basis:** Current source tree, Python manifests/environment, Git history, and the PSI inventory as inspected on 2026-11-15.

## Release decision at a glance

The current application prototype can operate without the original PSI files. However, the repository contains 54 inventoried PSI source files with unresolved redistribution terms, source-derived audit exports, multiple Git contributors whose authorization under the root MIT license is not documented, and an unpinned Python dependency graph. Do not publish a repository snapshot or source archive containing those unresolved materials until the checklist below is complete.

This plan classifies repository material as:

- **Safe to include:** repository mechanics and factual references that contain no unresolved copied source material. This is a content classification, not blanket permission to distribute the whole repository.
- **Include after confirmation:** project-authored software, documentation, and generated deliverables after contributor and third-party rights, dependency notices, and provenance are confirmed.
- **Exclude until permission is established:** PSI source copies and content extracted or reproduced from them, plus local-only/sensitive material and local environment artifacts.

## PSI source use and release boundary

The inventory `data/metadata/dataset_inventory.csv` contains 54 records: 53 non-placeholder source files are tracked under `data/raw/nasa_psi/`, and one additional BASS workbook is marked local-only and ignored by Git. The inventory format counts are 31 PDFs, 6 XLSX files, 5 CSV files, 5 ZIP files, 2 PPTX files, and 5 DOCX files, including that local-only workbook. The repository also tracks 24 `.gitkeep` placeholders, which are not source documents. Rights for the 53 tracked PSI source files remain unresolved. None of these source files is needed to launch the current ordinary app workflows.

| Area | What source code currently does | Release classification |
|---|---|---|
| Frontend dashboard/scientific views | `frontend/src/App.jsx` uses hardcoded illustrative demo records; it does not load the PSI directory. | Frontend source can be considered after contributor authorization and third-party notice review. Do not describe fixture rows as live PSI data. |
| Atmospheric API/calculations | Calculates from request inputs; it does not require PSI files. | Backend and modelling source can be considered after contributor authorization and dependency review. |
| Experiment and evidence data services | Current backend services/endpoints are placeholders and do not load raw PSI files. | Code may be included after contributor authorization; explain the unavailable behavior accurately. |
| Assistant retrieval at runtime | Retrieval can consult an optional SQLite index when configured. No approved source entries are recorded in `ai/ingestion_approvals.csv`; no operational project evidence corpus is established by the current repository state. | Do not ship an index built from PSI sources unless its source rights, excerpts, metadata, and distribution terms have been reviewed and cleared. |
| Optional PDF ingestion | `ai/document_ingestion/service.py` has an explicit approval, hash, path containment, size, and PDF-only ingestion path under `data/raw/nasa_psi`. It is an optional workflow, not a requirement for ordinary app launch. | Keep source PDFs out until item-level permission is established. Code may be considered after contributor authorization and a review of its documented purpose. |
| PSI audit-generation script | `scripts/build_psi_audit.py` reads the five experimental-table CSVs, `BASS test matrix.xlsx`, and four SAFFIRE image/raw index workbooks. It writes copied row values and workbook summaries to `data/processed/audit/`, a header-only harmonised file, and processing-log entries. | Exclude source inputs and audit exports until permission and derived-content review are complete. The script cannot regenerate its PSI audit outputs without those inputs. |
| Harmonisation and provenance logs | `data/metadata/harmonisation_log.csv` has 75 data rows describing proposed field mappings, source support, and decisions. `data/metadata/processing_log.csv`, the inventory/registry, and `data/processed/audit/source_file_review.csv` include source paths, identifiers, hashes, or file-structure summaries. | Treat as PSI-derived research/provenance material and review for source-derived details, copied wording, sensitive/local paths, and redistribution terms before inclusion. |

### Exact PSI inputs used by the audit script

The script's normal audit path reads these ten files (all under `data/raw/nasa_psi/`):

- `BASS/experimental_tables/PSI-26_Experimental table_BASS.csv`
- `BASS/experimental_tables/BASS test matrix.xlsx`
- `BASS_II/experimental_tables/PSI-25_Experimental table_BASS-II.csv`
- `SAFFIRE_I/experimental_tables/PSI-98_Experimental table_SAFFIRE-1.csv`
- `SAFFIRE_II/experimental_tables/PSI-99_Experimental table_SAFFIRE-2.csv`
- `SAFFIRE_III/experimental_tables/PSI-100_Experimental table_SAFFIRE-3.csv`
- `SAFFIRE_I/investigation_metadata/SAFFIRE-1_MergeResult-jpeg_Update_Final_v2.xlsx`
- `SAFFIRE_II/investigation_metadata/SAFFIRE-II_MergeResult-jpeg_v5_Final.xlsx`
- `SAFFIRE_III/investigation_metadata/SAFFIRE-III_MergeResult-jpeg_Final.xlsx`
- `SAFFIRE_III/investigation_metadata/SAFFIRE-III_MergeResult-raw_Final.xlsx`

These ten are only the files read by that audit-generation workflow; they are not a complete release exclusion list. The PDFs, ZIPs, office documents, and other raw files may be future research or optional ingestion inputs, but are not required by the normal current application workflow. The source inventory's local-only `BASS Test Matrix 050213.xlsx` is not one of the 54 cleared source records; it is ignored by Git due to a prior credential-like-content flag and must remain excluded from public packages unless separately cleared for both sensitivity and rights. Do not add it to release artifacts.

### Proposed public-release exclusion list

Until item-level rights and content are cleared, exclude:

- `data/raw/nasa_psi/**` — all PSI source copies, not just the ten audit inputs.
- `data/processed/audit/**` — audit CSVs include copied row values and source workbook summaries.
- `data/metadata/harmonisation_log.csv` and any processing or source-review records that reproduce PSI-derived descriptions, decisions, source paths, or content; include only after a row-level metadata/provenance review.
- Any SQLite/vector index, chunk export, embedding cache, extracted PDF text, screenshots, figures, or reports containing PSI source content or derived values, including future files outside the paths above.
- The local-only `data/raw/nasa_psi/BASS/experimental_tables/BASS Test Matrix 050213.xlsx` under all circumstances until its credential-like content concern is independently resolved; do not distribute it as part of this release.
- Any archive or built application bundle that accidentally includes the excluded files above.

At the time of this check, `data/processed/harmonised/test_points.csv` has 45 columns and zero data rows. The harmonisation log is not empty: it contains 75 data rows and needs separate review. Recheck both at packaging time; if verified records or additional derived material appear, assess all values and provenance before release.

### Can references and metadata remain?

Potentially, after manual review. Keep exact bibliographic citations and stable source URLs where they are accurate and useful. Review `data/metadata/source_registry.csv`, `dataset_inventory.csv`, `processing_log.csv`, and source-specific docs for duplicated prose, copied captions, sensitive details, personal/local file paths, and claims about permissions. Hashes and filenames identify files but do not establish redistribution rights. Do not include source extracts or audit-derived values merely because they are in CSV form.

## Contributor authorization

Git records the following identities and identifiable work. Git authorship is evidence of commit attribution, not evidence of a license grant or consent. No contributor authorization/assignment record was found in the repository review. The root `LICENSE` is MIT and names Arkaprava Bishnu; do not change it as part of this plan.

| Identity recorded in Git | Relevant identifiable contributions | Authorization documented? | Confirmation needed |
|---|---|---|---|
| `Arkaprava Bishnu <111085273+ProfessorElectron@users.noreply.github.com>` and `ProfessorElectron <arkapravabishnu@gail.com>` | Initial project/scaffold and PSI-table commits; PSI-26/98/99/100 file commits; audit/backend and evidence-coverage hardening. These identities appear likely related, but confirm they represent the same rights holder. | No. Root MIT notice names Arkaprava, but Git history alone does not prove authorization for all contributions or resolve alias ownership. | Confirm identity aliases, authorship/ownership of copyrightable code and original assets, and agreement to the project's MIT distribution terms. |
| `SHWETARKA BANERJEE <banerjee.sanu167@gmail.com>` | Commit `08e22c9`, frontend UI and package-manifest/lock changes. | No record found. | Confirm the contribution is theirs, identify any third-party assets/snippets, and authorize inclusion under the project's selected license. |
| `umernawazneal-afk <umernawaz.neal@gmail.com>` | PSI-25 files (`6944c98`), evidence-coverage code/tests, and local RAG implementation (`87dc9ea`). | No record found. | Confirm contribution scope, ownership, third-party material, and authorization under the project's selected license. |

Uncommitted/untracked work has no Git author metadata. Identify each author before distribution, including the AI integration, tests, and recent documentation. Do not contact anyone as part of this plan; the team must obtain and retain confirmations.

## Python dependency reproducibility and notices

`pyproject.toml` declares Python `>=3.10`. Core runtime dependencies are FastAPI, HTTPX, Pydantic, and Uvicorn. Optional groups add `openpyxl` for the PSI audit script, `pypdf` for PDF ingestion, and pytest for optional test-running convenience. Source import inspection found no current Python imports of NumPy, SciPy, pandas, Plotly, or Matplotlib, so those packages were removed from install groups. `requirements.txt` remains an unlocked pip alternative; `uv.lock` pins runtime and optional package resolution. The build-system versions are pinned in `pyproject.toml` but are outside the application dependency lock graph.

The lock was generated with uv 0.13.8, resolving 37 unique dependency name/version pairs (38 package entries including the project and Python/platform marker variants). A clean Python 3.13.0 environment installed core runtime plus the `dev` extra and passed the full unittest discovery run. Only Python 3.13 on Windows was executed; the lock declares support for Python `>=3.10` but that does not replace CI testing on other supported versions/platforms.

Exact package versions and PyPI license metadata are recorded in [`python_dependency_inventory.csv`](python_dependency_inventory.csv). Twelve package/version rows did not provide an SPDX expression in exact-version PyPI metadata; raw license fields are preserved or left blank rather than inferred. The generated [CycloneDX SBOM](python_sbom.cdx.json) contains dependency edges and artifact hashes but no license fields, so it complements rather than replaces the inventory. Review package license files and bundled binary components before shipping executable environments.

### Minimal reproducibility recommendation

Use `uv sync --locked` for the reproducible core install; add `--extra ai`, `--extra audit`, or `--extra dev` only when that functionality is needed. The `all` extra is a convenience aggregate of the optional groups. The alternative `pip install -r requirements.txt` still resolves against lower bounds and is not reproducible. The project build backend is pinned to the versions recorded in `pyproject.toml`; the uv lock does not independently lock build isolation tooling. Additional Python/platform matrix tests remain recommended before a wider software release.

## Release manifest

### Safe to include based on current evidence

These items have no identified PSI source payload in their current function, but review the exact release snapshot for stray generated or copied content:

- `.gitignore` and ordinary repository build/developer configuration after checking it contains no local secrets or private paths.
- `frontend/package.json`, `frontend/package-lock.json`, `frontend/index.html`, and frontend source as a software candidate, subject to contributor authorization, third-party notice requirements, and an accurate demonstration-data label.
- Current deterministic atmospheric source and API code as a software candidate, subject to contributor authorization and dependency/license review.
- Factual project setup and architecture documentation after checking for unreviewed PSI quotations, figures, copied passages, and claims.
- Bibliographic URLs/titles only after metadata review; the citation itself is not a redistribution license.

“Safe” here applies to the identified file type/content only, and does not override unresolved authorship, package, font, or event requirements. The repository as a whole is not currently cleared for public distribution.

### Include after confirmation

- `README.md`, project source (`ai/`, `backend/`, `frontend/`, `modelling/`, scripts, and tests), docs, and `pyproject.toml` after all contributors with included copyrightable work authorize distribution under the chosen project license and copied/adapted code is reviewed.
- Root `LICENSE` after confirming all included contributors authorize the MIT terms and the copyright notice is accurate. This plan does not edit the file.
- `THIRD_PARTY_NOTICES.md`, frontend lockfile, and any build/runtime bundle after validating dependency versions, full transitive licenses/notices, fonts, and applicable disclosure obligations.
- `data/metadata/` registries and inventory only after source-derived content, sensitive/local path fields, and attribution have been reviewed. Keep references even if raw source is excluded only where their text and metadata are suitable for redistribution.
- `docs/submission/` materials after checking their claims and any source-derived wording against the final distribution.
- A reproducibility lock/SBOM and verified setup instructions after the project chooses a Python target and dependency scope.

### Exclude until permission is established

- Entire `data/raw/nasa_psi/` tree (53 tracked non-placeholder source files plus 24 `.gitkeep` placeholders); the inventory also lists one additional local-only sensitive workbook that is not tracked and must remain excluded.
- `data/processed/audit/` and any other tables or exports reproducing raw source rows, source values, workbook contents, or document text.
- `data/metadata/harmonisation_log.csv` until its 75 source-derived decision/mapping records receive a row-level redistribution and content review. Review `processing_log.csv`, `dataset_inventory.csv`, and `source_registry.csv` before including them because they contain source-linked metadata.
- Any RAG/vector database, extracted text, embeddings, or packaged evidence index derived from PSI documents.
- The local-only credential-like workbook described above.
- Local secrets/configuration (`.env`, `.env.*` except a reviewed `.env.example`), credentials/tokens, `.venv/`, `venv/`, `node_modules/`, `dist/`, Python caches, local databases, and model weights. The `.gitignore` excludes several of these already; inspect the final archive rather than relying only on ignore rules.
- Any content whose author, license, or source cannot be established.

## Third-party notices and attribution

Keep `THIRD_PARTY_NOTICES.md` as an audit aid, then reconcile it with the exact release contents and resolved package versions. For source distributions and built bundles, retain required license text, copyright notices, and third-party component notices. Preserve the `frontend/package-lock.json`; do not bundle `node_modules/`. If font binaries, model weights, datasets, or generated indexes are later included, inventory their exact versions, source, license, and notices separately. Cite NASA PSI records and scientific sources used by the project; citations do not replace permission where permission is required.

## Build and setup instructions for a source-only local prototype

These commands describe the current development setup, not a reproducible/pinned release environment. They do not require PSI source files for ordinary app startup. The Python requirements currently include the full `all` extra.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload
```

In a second terminal:

```powershell
Set-Location frontend
npm ci
npm run dev
```

Install the optional PDF ingestion dependency with `uv sync --locked --extra ai`, the XLSX audit dependency with `--extra audit`, and pytest with `--extra dev`. Optional local AI operation may require Ollama and a configured model; it is not required for deterministic atmospheric calculations. Do not claim operational project evidence retrieval or validated fire-spread prediction. Verify current app configuration and README instructions against the chosen release snapshot before publishing.

## Final public-release checklist

- [ ] Decide whether PSI source files may be redistributed, based on item-level source terms and required attribution; otherwise exclude `data/raw/nasa_psi/**` from the public artifact.
- [ ] Review and exclude or clear all PSI-derived audit exports, indexes, extracted text, figures, reports, and other reproductions.
- [ ] Preserve the local-only sensitive workbook exclusion; check archives and Git history for accidental inclusion or secrets.
- [ ] Obtain and retain authorization from all contributors whose original code/assets are included; resolve Git aliases and identify authors of uncommitted work.
- [ ] Confirm root MIT copyright holder and final license wording; do not infer authorization from the current `LICENSE` or commit history.
- [ ] Complete Python direct/transitive dependency, version, license, bundled-binary, and reproducibility inventory for the release target.
- [ ] Retain/verify third-party notices for Python, npm, fonts, AI/model assets, and any other distributed components.
- [ ] Verify exact Project Tab fields, attachments, word/upload limits, submission access, and deadline in the team's live account.
- [ ] Verify local-event requirements, forms, judging cutoff, timezone, and live-demo requirements with the registered event.
- [ ] Rebuild and inspect the final release archive; confirm it omits raw/derived restricted content, secrets, environments, caches, indexes, and model files.
- [ ] Confirm README/setup/demo claims match actual behavior and label illustrative records clearly.
- [ ] Obtain final team approval for the public artifact only after the above evidence is recorded.
