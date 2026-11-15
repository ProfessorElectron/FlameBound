# Independent Review: Atmospheric Engine

**Review date:** 2026-11-15
**Review scope:** Mathematical correctness, physical assumptions, edge behavior and scientific limits of `modelling/atmospheric.py`, checked against the current tests and documentation. This review independently inspected source code and exercised targeted cases; prior passing-test claims were not treated as proof. No NASA source files were changed.

## Verdict

**B. READY AFTER MINOR CORRECTIONS.** The typed calculations implement the stated equations and units correctly within their declared scope. This review fixed several defects found by edge-case inspection: intermediate overflow for same-unit conversions, underflow silently returning zero, a measured-status provenance bypass, permissive JSON serialization, a falsy empty-unit fallback, a truthy non-Boolean oxygen-conversion gate in the harmonisation helper, and unnecessary pressure coupling in the mass-fraction API. The updated test suite passes 41 tests.

The engine is suitable for a carefully constrained FastAPI integration that uses only typed `calculate_*` functions and server-controlled schemas. It is **not** safe to expose every legacy helper as an AI tool. The backend must not trust client-provided verification flags or source IDs as proof, and it needs a trusted source registry before it can accept measured inputs or verified diluent composition.

## 1. Pressure conversion

The engine normalizes typed atmospheric-condition pressures to kPa using the factor table in `modelling/atmospheric.py`. The factors are internally consistent:

- 1 Pa = 0.001 kPa.
- 1 kPa = 1 kPa.
- 1 bar = 100 kPa.
- 1 atm = 101.325 kPa.
- 1 psi = 6.894757293168361 kPa.
- 1 MPa = 1000 kPa (compatibility unit beyond the required set).

Independent check for psi: using the exact international pound mass, standard gravity and inch definitions, `(0.45359237 kg × 9.80665 m/s²) / (0.0254 m)² = 6894.7572931683613367 Pa/psi`. Decimal arithmetic gives 10.2 psi = 70.3265243903172856 kPa. The implementation gives 70.32652439031727 kPa; the difference is ordinary binary64 rounding. It does not round intermediate or reported values.

The earlier implementation multiplied the pressure by the source factor before dividing by the target factor. That could overflow for a large value converted to the same unit even though the answer was representable (for example `1e308 MPa → MPa`). The reviewed implementation divides the factors first, then multiplies; it returns the original large value for that case. It rejects non-finite results and underflow to zero. Round trips and very small/large cases are tested.

Absolute pressure is explicit in the typed `PressureBasis` input, which currently accepts only `absolute`; gauge and unspecified values are rejected. `convert_pressure` remains a legacy numeric function whose documented contract assumes absolute pressure and cannot detect a caller passing gauge pressure. The backend must use the typed request contract and never infer absolute basis from a unit label.

## 2. Oxygen partial pressure

The calculation implements `pO2 = X_O2 × P_total`. `X_O2` is a mole fraction in [0,1], not a percentage. The typed path requires `gas_basis_verified=True`, an explicit absolute-pressure basis, and a supported pressure unit; it normalizes pressure to kPa and returns normalized inputs and pO2 in kPa. The numeric legacy helper returns pressure in the same unit supplied and has no provenance/basis gate.

Independent reference: `0.30 × 10.2 psi = 3.06 psi` by direct multiplication. Using the independently derived conversion above, this is 21.097957317095185 kPa. The typed function returns approximately 21.097957317095183 kPa. Values 0, 0.21, 0.30 and 1.0 are covered; values such as 30.0 are rejected as outside mole-fraction range. There is no silent percentage conversion in the atmospheric module.

The gas-basis Boolean is a caller assertion, not evidence. The API should make the submitted field itself explicitly `oxygen_mole_fraction` and construct the flag internally for hypothetical inputs; it must never accept an AI-supplied `gas_basis_verified: true`. Source-derived volume percentages require documented normalization metadata and a verified basis before reaching the typed calculation. Real-gas fugacity is outside scope; the result is Dalton-law partial pressure under the stated gas-phase mole-fraction assumption.

## 3. Oxygen mass fraction

The code uses the binary-mixture mass balance:

`Y_O2 = X_O2*M_O2 / (X_O2*M_O2 + (1-X_O2)*M_diluent)`.

Molar masses are both g/mol, so the ratio is dimensionless. Oxygen molar mass defaults to 31.998 g/mol; no diluent is assumed. The low-level function requires an explicit diluent molar mass and `diluent_verified=True`; the typed function requires a named `BinaryDiluent` with MEASURED or DERIVED status and matching provenance. It rejects absent or UNVERIFIED diluent inputs. A one-species diluent is the model's explicit limit; it is not a general multicomponent mixture solver.

Independent decimal reference for X_O2=0.21, M_O2=31.998 g/mol, M_N2=28.014 g/mol is 0.232909217958423106. The implementation agrees within floating-point tolerance. An explicit argon diluent gives a different mass fraction, as expected. Pure-O2 and zero-O2 limits are tested. A mixture containing multiple diluents must not be passed as a fictitious nitrogen balance gas; the API should use a verified gas composition service or refuse the operation.

## 4. Atmospheric comparison

The typed comparison converts both absolute pressures to kPa, reports each oxygen fraction, total pressure and pO2, then reports scenario-minus-reference and relative differences. A relative difference is `(scenario-reference)/reference`; it is `None` when the reference quantity is zero, with a warning. A missing/null required condition is rejected before calculation rather than treated as zero. Zero oxygen is valid and distinct from missing.

The result distinguishes total pressure from pO2 and includes a limitation that equal pO2 does not establish combustion equivalence or fire safety. Example: 0.30 at 10.2 psi and 0.20 at 15.3 psi both give pO2=3.06 psi, while oxygen fraction and total pressure differ. The comparison output makes those differences visible. An AI must not summarize the match as equivalent flame behavior.

The old `compare_atmospheres` returns `None` for relative pO2 when reference pO2 is zero but has no structured warning/provenance. It now rejects an explicitly empty reference unit rather than silently treating it as the scenario unit. Use typed comparison for backend work.

## 5. Missing, invalid and floating-point inputs

The model rejects bools even though Python considers `bool` an `int`; it rejects strings, `None`, NaN, infinity, negative fractions, fractions above 1, and nonpositive total pressures. Required `AtmosphericCondition` fields cannot be marked MISSING while carrying a numeric value; missing/null required API fields should produce a structured validation error. Zero oxygen is a valid numeric input. Conversion overflow/underflow is rejected rather than returned as infinity or plausible zero.

## 6. Changes made during this independent review

See [`phase3_issue_register.md`](phase3_issue_register.md) for full disposition. The code changes were limited to demonstrated edge and provenance defects:

1. Compute pressure conversion factor ratio before multiplying, preventing false overflow for representable same-unit conversions.
2. Reject pressure, pO2 and mass-fraction underflow to zero when the mathematical result is positive.
3. Require measured statuses to have source-record provenance and a locator, and require field-level provenance to match a MEASURED `AtmosphericCondition` field.
4. Make `.to_dict()` reject non-finite numbers, unsupported objects and non-string mapping keys.
5. Reject an explicitly empty `reference_pressure_unit` instead of using truthiness fallback.
6. Require an oxygen volume-percent verification switch to be an actual Boolean; strings such as `"false"` can no longer authorize conversion.
7. Require normalization-method provenance for percent-valued source oxygen and for pressure provenance whose raw unit differs from the normalized unit.
8. Add `OxygenComposition` so binary mass fraction does not require an unrelated pressure value; `AtmosphericCondition` remains accepted for compatibility.

No NASA source, audit output, harmonised row or AI/frontend implementation was changed.
