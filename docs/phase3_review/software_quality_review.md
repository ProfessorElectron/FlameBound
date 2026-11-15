# Phase 3 Software Quality Review

## Files inspected

Inspected the actual current contents of:

- `modelling/atmospheric.py`
- `modelling/data_harmonization.py`
- `tests/test_atmospheric.py`
- `tests/test_data_harmonization.py`
- `docs/atmospheric_engine.md`
- `docs/mathematical_framework.md`
- `docs/data_dictionary.md`
- `docs/scientific_review/scientific_api_contract.md`
- `docs/scientific_review/mathematical_development_roadmap.md`
- `README.md`

Also searched every Python file for imports/calls of atmospheric functions. Only `tests/test_atmospheric.py` and internal calls in `modelling/atmospheric.py` use them; no backend service or production Python module currently imports them. The FastAPI app still exposes only `GET /health`.

## Data model and typing

The engine uses `PressureUnit`, `PressureBasis`, `VerificationStatus`, `InputOrigin`, frozen dataclasses `InputProvenance`, `BinaryDiluent`, `AtmosphericCondition`, `OxygenComposition`, and `CalculationResult`. Typed atmospheric conditions explicitly require absolute pressure; unknown/gauge bases are rejected. Oxygen fraction is a real scalar in [0,1]. `BinaryDiluent` requires a positive finite molar mass and matching provenance status. Per-field provenance is retained in calculation results.

The model rejects bools, strings, `None`, nonfinite numbers, unsupported units, invalid ranges, and absent/unverified diluent where the calculation requires it. Missing required calculation inputs fail validation rather than becoming zero. `VerificationStatus.MISSING` is available for provenance metadata, but an `AtmosphericCondition` cannot have a numeric value simultaneously marked MISSING.

`gas_basis_verified` remains a trusted-caller assertion. The Python dataclass cannot prove the truth of an arbitrary Boolean or authenticate a user-supplied source ID. A backend must construct this state from a constrained input schema or a trusted verified source record; it must not accept a caller-provided verification status as evidence.

## Provenance and serialization

`CalculationResult.to_dict()` retains calculation name, formula, input values, normalized outputs, units, verification states, conversion methods, provenance, assumptions, limitations and warnings. `InputProvenance` carries source ID/locator, raw value/unit and normalization method. MEASURED status now requires a source record ID and locator; matching condition fields also require corresponding MEASURED provenance. User-supplied inputs default to UNVERIFIED.

`OxygenComposition` represents composition without requiring a pressure field; `calculate_oxygen_mass_fraction` accepts it directly. This avoids asking an API caller for or inventing pressure for a pressure-independent equation. It also continues accepting an `AtmosphericCondition` for existing typed call sites.

The serializer now recursively rejects NaN/infinity, non-string mapping keys and unsupported objects rather than returning data that would fail strict JSON or serialize as non-standard `NaN`. It does not authenticate source IDs; the backend must validate them against trusted server-side provenance. The source raw value and unit are preserved when supplied, but the engine cannot infer a source's real meaning from those strings.

## Backward compatibility

`convert_pressure`, `oxygen_partial_pressure`, and `compare_atmospheres` keep their existing call signatures and numeric output shapes. They are compatibility-level helpers, not suitable AI/backend operations because they lack explicit provenance and typed verification. They assume absolute pressure by documented contract; only typed inputs carry an explicit pressure-basis value.

`oxygen_mass_fraction` keeps its function name and parameter order, but the former `diluent_molar_mass_g_mol=28.014` default was removed and a keyword-only `diluent_verified=True` is required. Thus these old calls now raise rather than silently assume a nitrogen-like diluent:

```python
oxygen_mass_fraction(0.21)
oxygen_mass_fraction(0.21, 28.014)
```

Update callers to provide a verified composition or use the typed `BinaryDiluent` path. Repository-wide search found no production callers; only tests and internal typed dispatch call the function. This behavioral break is deliberate because an implicit diluent violates the scientific contract. It is documented in `docs/atmospheric_engine.md` and the API contract.

## Defects fixed in this review

- Pressure factor multiplication could overflow before division even when the final same-unit answer was representable; ratio is now computed first.
- Positive conversions and derived quantities could underflow to zero; they now fail explicitly.
- `AtmosphericCondition(oxygen_verification=MEASURED)` could be constructed without measurement provenance; it now requires field-level measured source metadata and a locator.
- Serializer recursion previously passed NaN/infinity through; it now rejects unsupported/nonfinite values and bad object keys.
- An empty reference pressure unit was treated as absent through `or`; only `None` now triggers the documented default.
- `volume_percent_is_mole_fraction="false"` was truthy and could authorize percent conversion; the helper now requires a Boolean.
- Percentage raw oxygen without a normalization method and mismatched raw/normalized pressure units without a normalization method are rejected.

## Tests and runtime

- Interpreter: bundled Python 3.12.14.
- `python -m unittest discover -s tests -v`: **41 tests passed** after review fixes, covering all repository tests.
- `python -m pytest --version`: pytest is not installed in the active environment. No repository virtual environment was found; no package was installed.
- `git diff --check` passed. The harmonised data file remains empty, and the raw source directory is unchanged.

Tests exercise supported pressure conversions and round trips, independently calculated pressure/pO2/mass-fraction references, zero/one boundaries, bad types, underflow/overflow, gas-basis and diluent checks, relative-difference zero references, source provenance, conversion normalization, strict JSON, and legacy helper behavior.

## Remaining quality limits

The legacy numeric helpers can bypass explicit basis/provenance checks; do not expose them directly in FastAPI. The current provenance model can only validate shape and declared status, not authenticate source references. The API must derive verification from server-controlled data, not request flags. There is no schema version/engine version in result objects yet; if responses are persisted or consumed by multiple app versions, add a versioned response contract before launch. Error exceptions must be translated to stable HTTP error codes by the backend rather than leaking stack traces.
