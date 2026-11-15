# Scientific Review Decision Log

**Date:** 2026-11-15

## Decisions made

1. **Keep zero verified harmonised rows.** The current table `data/processed/harmonised/test_points.csv` is correctly header-only; candidate source rows do not pass independent run, variable, outcome, and locator review.
2. **Keep source counts separate.** Retain BASS 121 CSV candidates plus nine unmatched primary-matrix keys; retain BASS-II's 129 distinct CSV labels alongside the NASA/TM 126 claim. Neither count is promoted to independent test count.
3. **Do not convert unresolved BASS O2 or pressure.** `O2 % by volume` contains 0.221-scale values and `pressure, atm` has no stated basis. The existing helper must not be used to force either into a canonical value.
4. **Do not classify SAFFIRE `?-g` as microgravity.** Preserve explicit 1-g comparator data separately.
5. **Treat SAFFIRE MergeResult workbooks as indexes.** Their file IDs/timestamps/sizes/status are not image or sensor measurements. Original payloads are missing locally per the DoD documents.
6. **No model fit or extrapolation.** There are zero verified observations/outcomes; partial-gravity and safety claims are unsupported.
7. **Keep source data untouched.** No external files were downloaded and no `data/raw/` source was edited in this review.

## Issues resolved by this review

- README and mathematical-framework status text that said there was no completed audit/no NASA rows was stale after the initial audit. Both now link to the current audit and accurately state that raw rows exist but zero are verified.
- `scripts/build_psi_audit.py` previously replaced audit exports and `test_points.csv` silently. It now refuses when generated targets exist unless `--overwrite-generated` is provided. This guards future manual review/harmonised rows. No overwrite regeneration was performed during this review.
- Existing numeric unit conversions were checked: pressure factors, percent-to-fraction factor under explicit gas-basis gate, speed factors, pO2 product, and binary-mixture mass-fraction equation are mathematically consistent with their documented domains.

## Unresolved issues

- BASS oxygen scale; pressure basis; run ID grain; nine unmatched matrix keys; calibrated flow-display interpretation; row-level outcome crosswalk.
- BASS-II 126 vs 129 and five-vs-six PI discrepancy; no documented explanation for whether counts differ by convention, repeats, exclusion, missing records, or version.
- Missing SAFFIRE sensor spreadsheets and image/video payloads; Saffire dimension label conflicts; `?-g` gravity meaning; outcome definitions.
- Current schema lacks robust variable-level provenance, distinct test/sample/repeat IDs, structured duplicate/gravity evidence/outcome adjudication, and time-series sidecar representation.
- Backend scientific routes are not implemented. The API contract is proposal only.
- Unit helpers need malformed-type validation at API boundary and stronger cross-module/boundary tests.

## Changes made

- Added `docs/scientific_review/independent_audit_review.md`.
- Added `docs/scientific_review/harmonisation_validation_report.md`.
- Added `docs/scientific_review/model_readiness_assessment.md`.
- Added `docs/scientific_review/mathematical_development_roadmap.md`.
- Added `docs/scientific_review/scientific_api_contract.md`.
- Added this decision log.
- Updated stale project status in `README.md` and `docs/mathematical_framework.md`.
- Added explicit overwrite protection to `scripts/build_psi_audit.py`.
- No raw data, harmonised rows, conversion formulas, or outcome labels were changed.

## Validation performed

- Bundled Python 3.12.14 `unittest` discovery: 17 tests passed.
- pytest is not installed in the active interpreter; no repository virtual environment was found; no packages were installed.
- Existing-output guard on audit builder was invoked without overwrite option; it refused before writing.
- Dataset inventory has 54 file entries and every `local_path` resolves. Source registry has 54 source entries; it does not use a local-path column. Raw tree was not modified.
- No commits or pushes were made.

## Outstanding actions

1. Resolve investigation-specific crosswalks and obtain missing PSI payloads before promoting any row.
2. Agree on a normalized core plus long-form measurement/provenance and time-series schema.
3. Add API input validation and cross-module tests before giving the AI teammate tools.
4. Reassess modelling readiness only after verified row and outcome counts are documented.
