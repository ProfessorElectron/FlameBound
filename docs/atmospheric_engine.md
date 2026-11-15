# Deterministic Atmospheric Engine

**Status:** Implemented deterministic calculations; no NASA row is loaded, normalized, or predicted by this module. The engine is independent of FastAPI, the frontend, and Ollama.

## Scientific quantities and units

### Pressure conversion

Pressure inputs are **absolute**. Supported canonical units are Pa, kPa, bar, atm, and psi. MPa and common spelled-out aliases remain accepted for compatibility. Conversion factors to the internal kPa representation are:

| Unit | kPa per unit |
|---|---:|
| Pa | 0.001 |
| kPa | 1 |
| bar | 100 |
| atm | 101.325 |
| psi | 6.894757293168361 |
| MPa (compatibility) | 1000 |

Factors are applied with IEEE-754 binary64 floating point, without intermediate rounding. The output is a `float`; small representation/rounding differences are expected. Gauge pressures are not supported and must not be treated as absolute.

### Oxygen partial pressure

\[
p_{O_2}=X_{O_2}P
\]

`X_O2` is the gas-phase oxygen mole fraction in [0,1], `P` is positive total absolute pressure, and `p_O2` is returned in the same pressure unit (legacy function) or kPa (typed calculation). This is the gas-mixture partial-pressure relation, `p_i = x_i p`, defined in the [IUPAC Gold Book entry for pressure](https://goldbook.iupac.org/terms/view/P04819). It assumes the supplied fraction represents the appropriate gas-phase mole fraction. A volume-percent value is not automatically accepted as a mole fraction. Under an ideal-gas mixture assumption, volume fraction and mole fraction are numerically equivalent at the same state; the caller must document and verify the basis before using that equivalence. This engine does not calculate non-ideal fugacity.

### Oxygen mass fraction

\[
Y_{O_2}=\frac{X_{O_2}M_{O_2}}{X_{O_2}M_{O_2}+(1-X_{O_2})M_{dil}}
\]

`M_O2` and `M_dil` are molar masses in g/mol. The relationship follows from the IUPAC definitions of [amount fraction](https://goldbook.iupac.org/terms/view/A00296) and [mass fraction](https://goldbook.iupac.org/terms/view/M03722) applied to a binary mixture. This equation is limited to a binary O2 plus one-diluent mixture. The diluent name, molar mass, composition status, and provenance must be explicit and verified. There is no default air or nitrogen assumption. It does not model multi-species balance gas unless the user supplies a justified effective mean molar mass and documents that approximation; the current typed interface deliberately represents one named diluent.

### Atmospheric comparison

For each state, the engine reports `X_O2`, `P` in kPa absolute, and `p_O2` in kPa; it reports scenario-minus-reference differences and relative differences when the reference is nonzero. A zero reference yields `null` for that relative difference. Similar oxygen partial pressure does **not** establish combustion equivalence, and no comparison implies safety or certification.

## Typed input and provenance model

Implemented in `modelling/atmospheric.py`:

- `PressureUnit`: Pa, kPa, bar, atm, psi, and compatibility MPa; `PressureBasis` currently permits only absolute pressure.
- `VerificationStatus`: `MEASURED`, `DERIVED`, `MODELLED`, `INFERRED`, `UNVERIFIED`, `MISSING`.
- `InputOrigin`: `user_supplied`, `source_record`, `derived`, `other`.
- `InputProvenance`: origin, verification status, optional source ID/locator, raw value/unit, normalization method and note. `MEASURED` requires source-record origin, source ID and locator. User-supplied values default to `UNVERIFIED`.
- `BinaryDiluent`: explicit named diluent, molar mass, verification status and provenance.
- `OxygenComposition`: oxygen mole fraction and verified basis with an optional binary diluent; mass-fraction calculations use this type and do not require an irrelevant pressure value.
- `AtmosphericCondition`: oxygen mole fraction, total pressure, explicit pressure unit and absolute pressure basis, `gas_basis_verified`, oxygen/pressure verification statuses, optional binary diluent and per-field provenance. A field marked `MEASURED` must have matching source provenance. A numeric value cannot be labeled `MISSING`; missing/null required values are rejected.
- `CalculationResult`: JSON-compatible envelope with formula, inputs, outputs, units, verification, conversion methods, provenance, assumptions, limitations and warnings; call `.to_dict()` before API serialization. The serializer rejects non-finite values and non-string object keys.

The `gas_basis_verified` flag is a caller assertion, not an evidence record; an API must not accept an arbitrary AI-supplied verification flag. For source measurements, populate field provenance with a source identifier and locator. If oxygen raw provenance is in percent units, provide its explicit normalization method. A manually entered condition remains user-supplied and unverified unless independently supported and identified as a source record.

## Function signatures

Existing numeric APIs remain available for backward compatibility where safe:

```python
convert_pressure(value, from_unit, to_unit) -> float
oxygen_partial_pressure(oxygen_fraction, total_pressure) -> float
oxygen_mass_fraction(oxygen_fraction, diluent_molar_mass_g_mol=None,
                    oxygen_molar_mass_g_mol=31.998, *, diluent_verified=False) -> float
compare_atmospheres(oxygen_fraction, total_pressure,
                    reference_oxygen_fraction, reference_pressure,
                    pressure_unit="kPa", reference_pressure_unit=None) -> dict
```

The `oxygen_mass_fraction` signature preserves the callable name and parameter names, but its former implicit nitrogen-like default is intentionally removed for scientific safety. It now requires an explicit diluent molar mass and `diluent_verified=True`. New integrations should use the typed functions:

```python
calculate_pressure_conversion(value, from_unit, to_unit=PressureUnit.KPA,
                              *, pressure_basis, provenance=None) -> CalculationResult
calculate_oxygen_partial_pressure(condition: AtmosphericCondition) -> CalculationResult
calculate_oxygen_mass_fraction(composition: OxygenComposition | AtmosphericCondition) -> CalculationResult
compare_atmospheric_conditions(scenario, reference) -> CalculationResult
```

## Validation behavior

- Reject booleans and non-numeric values where real numbers are required; reject NaN/infinity, conversion overflow, and conversion underflow to zero.
- Oxygen mole fraction must be in [0,1]. Percent values such as 21 or 30 are not accepted by the atmospheric calculation model.
- Absolute pressure must be positive; zero/negative pressure is rejected. Only listed pressure units are accepted.
- Typed pO2 and atmospheric comparison require `gas_basis_verified=True`; this flag must be backed by caller evidence before source data are labeled verified.
- Pressure basis is a required typed input and only `absolute` is accepted. The low-level numeric conversion functions retain their legacy interface and assume absolute pressure.
- Binary mass fraction requires a `BinaryDiluent`, with `MEASURED` or `DERIVED` status and matching provenance status. Missing/unverified composition is rejected.
- Errors raise `TypeError` for invalid types or `ValueError` for invalid values/units/basis. The calculation functions return no result after validation failure.
- Raw input values, source units, verification statuses, normalized inputs and conversion methods are retained in structured result fields when supplied.

## Examples

### pO2 with a user-supplied hypothetical state

```python
from modelling.atmospheric import (
    AtmosphericCondition,
    PressureUnit,
    calculate_oxygen_partial_pressure,
)

state = AtmosphericCondition(
    oxygen_mole_fraction=0.30,
    total_pressure=10.2,
    pressure_unit=PressureUnit.PSI,
    pressure_basis="absolute",
    gas_basis_verified=True,  # caller must have established this basis
)
result = calculate_oxygen_partial_pressure(state).to_dict()
# pO2 = 0.30 * 10.2 = 3.06 psi = about 21.098 kPa
```

With no source provenance, both inputs remain `UNVERIFIED`; the numeric calculation is deterministic but is not a measured NASA result.

### JSON shape

```json
{
  "status": "success",
  "calculation": "oxygen_partial_pressure",
  "formula": "pO2 = X_O2 * P_total",
  "inputs": {
    "oxygen_mole_fraction": 0.3,
    "total_pressure": 10.2,
    "pressure_unit": "psi",
    "pressure_basis": "absolute",
    "gas_basis_verified": true,
    "oxygen_verification": "UNVERIFIED",
    "pressure_verification": "UNVERIFIED",
    "diluent": null
  },
  "outputs": {
    "oxygen_mole_fraction": 0.3,
    "total_pressure_kpa": 70.32652439031727,
    "oxygen_partial_pressure_kpa": 21.097957317095183
  },
  "units": {
    "oxygen_mole_fraction": "1",
    "total_pressure_kpa": "kPa absolute",
    "oxygen_partial_pressure_kpa": "kPa"
  },
  "verification": {
    "oxygen": "UNVERIFIED",
    "total_pressure": "UNVERIFIED",
    "result": "DERIVED"
  },
  "conversion_methods": {
    "total_pressure_kpa": "psi to kPa"
  },
  "provenance": {},
  "assumptions": ["Dalton's law is applied to the supplied gas-phase oxygen mole fraction."],
  "limitations": [
    "This calculation does not establish combustion equivalence or fire safety.",
    "Non-ideal mixture fugacity is not calculated."
  ],
  "warnings": []
}
```

The values shown are from the hypothetical numerical example above; no NASA values are used.

## Scientific limitations

- These are deterministic calculations, not a combustion model and not NASA data interpretation.
- Correct arithmetic does not verify the supplied measurement, gas basis, pressure basis, or provenance.
- Volume/mole equivalence requires a justified gas-mixture assumption; the module does not infer that from a header.
- A two-species mass fraction is not a general arbitrary-atmosphere composition solver.
- Equal `pO2` does not show equal flame behavior across fuels, apparatuses, flows, or gravity conditions.
- No lunar-gravity extrapolation, flame-spread prediction, extinction boundary, habitat safety, or certification is supported.

## Test coverage

`tests/test_atmospheric.py` covers supported pressure conversions, round trips, pressure aliases, overflow/underflow, invalid types/ranges/units, pO2 hand-calculation (including 0.30 × 10.2 psi = 3.06 psi), binary mass fraction using explicitly supplied diluents, missing/unverified composition, atmospheric differences, provenance preservation, verification status, strict JSON serialization and legacy numeric pressure/pO2/comparison APIs. `tests/test_data_harmonization.py` also checks that its volume-percent verification switch must be a Boolean. All tolerances use `unittest.TestCase.assertAlmostEqual`; no NASA values are used as reference cases.
