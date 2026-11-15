# Harmonisation and Software Validation Report

**Review date:** 2026-11-15. No raw PSI source was changed and no candidate row was promoted.

## 1. Conversion review

### Pressure

`modelling.data_harmonization.pressure_kpa` uses kPa factors Pa 0.001, kPa 1, bar 100, atm 101.325, psi 6.894757293168361. These factors are mathematically correct for the named units. It rejects nonpositive values and requires `basis == "absolute"`; this is appropriate because the conversion is not a gauge-to-absolute conversion. It does not document uncertainty/rounding, and the string `basis` is a caller assertion, not source evidence. The BASS matrix's `atm` field cannot currently use this helper because its pressure basis is **UNVERIFIED**.

`modelling.atmospheric.convert_pressure` similarly converts positive absolute pressures; Pa/kPa/MPa/bar/atm/psi factors are internally coherent. It does not accept a basis argument: the API must make the absolute-pressure contract explicit and validate/record the source basis before invoking it.

### Oxygen and partial pressure

`oxygen_fraction` correctly accepts mole-fraction forms in [0,1]. Volume-percent forms are rejected unless `volume_percent_is_mole_fraction=True`, then range checked [0,100] and divided by 100. The factor of 1/100 is mathematically correct for percent to fraction; the gate properly prevents automatic reinterpretation. However, the Boolean is not evidence itself: the caller must retain the source citation and the ideal-gas / gas-composition basis establishing that volume fraction is an acceptable mole-fraction representation. The ambiguous BASS `0.221` must not be passed as either 0.221% or 22.1% until its scale is resolved. Bare `"percent"` is intentionally rejected as underspecified.

`oxygen_partial_pressure_kpa` implements `pO2 = xO2 * P`, with xO2 range [0,1] and positive absolute P. It is correct for a gas mixture under the conventional mole-fraction definition; it returns `None` if either value is missing. Inputs must be same-row, same-state values with consistent kPa pressure. pO2 is mathematically dependent on xO2 and total pressure, not an independent measurement.

`modelling.atmospheric.oxygen_partial_pressure` implements the same product, returning the pressure unit supplied. `compare_atmospheres` normalizes pressure to kPa and computes the relative difference against the reference, returning `None` for zero reference pO2. These functions are suitable deterministic calculations when the caller supplies verified composition and absolute pressure.

`oxygen_mass_fraction` implements the correct two-species mass fraction formula. Its default diluent molar mass (28.014 g/mol) silently encodes a nitrogen-like balance gas. Although documented, API callers should supply an explicit gas composition/assumption or a justified mixture-average molar mass rather than relying on that default for arbitrary atmospheres.

### Speed and outcome helpers

`speed_m_s` uses correct cm/s→m/s (0.01) and mm/s→m/s (0.001) factors; it rejects negative values but permits zero, which is meaningful for quiescent flow. It accepts a scalar only; do not pass fan settings or sequences. `classify_outcome` only applies an exact caller-supplied mapping when its definition is verified; it returns `unknown` for missing/unverified definitions and `ambiguous` for unmatched evidence. This is appropriately conservative but has no built-in provenance record or confidence output. `flag_duplicate_records` flags, but does not merge, rows; duplicate meaning depends on the caller's chosen key.

## 2. Validation behavior and limitations

The module distinguishes explicit missing tokens/`None` from numeric zero, rejects booleans and non-finite numbers, rejects unsupported units, and range-checks normalized O2 and positive absolute pressure. Raw preservation is not performed by the conversion functions themselves; it depends on caller/storage behavior. Conversion provenance (source field, source unit, rule/version, source locator, verification evidence, reviewer) is also external to the functions and should be carried in API responses/records.

Minimal robustness issues to address before public API exposure: public unit/basis arguments call `.strip()` without first checking their type, so malformed JSON types can raise `AttributeError` rather than the documented `ValueError`/`TypeError`; the backend must validate types or the helpers should normalize errors. The O2 Boolean gate is acceptable internally but should not be exposed as an unaudited client switch. No current test exercises invalid argument types, all conversion boundaries, alias cases, or atmospheric-module interoperability. These are API hardening and test gaps, not evidence that current numeric factors are wrong. No conversion code was changed in this review.

## 3. Test and runtime results

- Active interpreter: bundled Python **3.12.14** at `C:\Program Files\WindowsApps\OpenAI.CodexPrimaryRuntime.v26-1112-737-0_26.1112.737.0_x64__3k8sg7r9htsxt\dependencies\python\python.exe`.
- `python -m unittest discover -s tests -v`: **17 tests passed**, including the existing atmospheric tests and new harmonisation tests.
- `python -m pytest --version`: unavailable; this interpreter reports `No module named pytest`.
- No repository `.venv` or `venv` was present. No dependency was installed into an unrelated environment.
- All tests are `unittest`-compatible; the README setup lists the project dependency set including pytest. The full suite's unittest execution is valid, but pytest-specific behavior was not exercised.

## 4. Schema review

`data/template/test_points_template.csv` has a useful record-level source title/path/locator, raw fields, units, outcome, missingness notes, and derived-pO2 slot. It cannot fully meet the Phase 2 needs without loss or overloaded notes:

- Provenance, raw value, normalized value, unit, conversion method, and verification status are record-level or absent, not **per-field**. Add a separate long-form measurement/provenance table (one row per measurement) rather than many one-off columns.
- There is one `run_id_raw`, but no distinct raw test ID, sample ID, repeat/condition ID, or source-defined grain. Preserve each identifier separately.
- No structured `duplicate_flag` / duplicate group, gravity evidence locator, gravity confidence, fuel classification evidence, outcome confidence/reviewer, or row-level outcome decision reason is available.
- `oxygen_fraction_raw` and `total_pressure_raw` do not support separate initial/final sensor readings or multiple time points. SAFFIRE and BASS-II sensor data need a time-series sidecar keyed by source file, channel, timestamp, unit, and calibration/provenance.
- `missingness_notes` has useful statuses, but it is free text and cannot distinguish uncollected payload from unextractable instrument data robustly.

Keep the existing CSV header as an empty/simple analytical view. Before promoting rows, agree on a normalized core plus long-form `measurements` and `source_assertions`/provenance table. Do not place unresolved values into the current template to make it appear complete. Current `test_points.csv` is correctly header-only.

## 5. Audit script review

`scripts/build_psi_audit.py` captures original headers/values and row locators, classifies annotations/candidates, adds duplicate flags, writes a header-only harmonised table, and refreshes its process-ID entries in `processing_log.csv`. It does not mutate `data/raw/`. A safety defect existed: rerunning it silently replaced all per-investigation audit files and `test_points.csv`, which could erase manual verification or future harmonised rows. This review made a minimal correction: it now refuses to replace existing generated outputs unless the operator explicitly supplies `--overwrite-generated`. The message lists target files to be replaced. The files are generated from scratch when that explicit flag is chosen; keep reviewer adjudications in a separate durable file before using it.

The prior audit run successfully generated all five investigation audits; this review did not rerun the builder over existing review outputs. The guard was checked against the current existing outputs and refused before writing. Source hashes/inventory paths were also checked without altering raw data.

## 6. Compatibility and follow-up

`modelling/atmospheric.py` is standalone, unit-explicit and covered by current tests; `data_harmonization.py` does not alter or import it. No compatibility break was introduced. Add later tests for cross-checking harmonization pressure/O2 results against atmospheric calculations, invalid unit/basis types, input boundaries, and provenance serialization. Keep the current conversion functions internal until backend schemas enforce those contracts.
