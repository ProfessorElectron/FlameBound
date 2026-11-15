# API Readiness and Ollama Integration Assessment

## Current state

`modelling/atmospheric.py` now has typed, deterministic operations returning `CalculationResult.to_dict()` JSON-compatible structures. The FastAPI app currently exposes only `GET /health`; there is no `/api/health` or scientific route. This review does not implement routes. The backend must call typed `calculate_*` operations and must not duplicate their equations.

Recommended common response:

```json
{
  "status": "success",
  "calculation": "oxygen_partial_pressure",
  "formula": "pO2 = X_O2 * P_total",
  "inputs": {},
  "outputs": {},
  "units": {},
  "verification": {},
  "conversion_methods": {},
  "provenance": {},
  "assumptions": [],
  "limitations": [],
  "warnings": []
}
```

For errors, return no numeric outputs, for example `{"status":"error","error":{"code":"invalid_unit","field":"pressure_unit","message":"Use an explicit supported absolute-pressure unit."}}`. Use HTTP 422 for missing, malformed, unsupported or scientifically ambiguous inputs. Never return a partial success value after validation fails.

## Proposed endpoints

### `GET /api/health`

- **Request:** none.
- **Response:** `{"status":"ok","components":{"atmospheric_engine":"available"}}`.
- **Rules:** health means the process and deterministic module load; it does not imply verified NASA evidence or model readiness. Existing `GET /health` can remain as a compatibility alias.
- **Provenance/limits:** no experimental claims; report no dataset status from this endpoint unless dynamically read from authoritative metadata.

### `POST /api/atmosphere/oxygen-partial-pressure`

Proposed request schema (Pydantic, `extra="forbid"`):

```json
{
  "oxygen_mole_fraction": 0.30,
  "total_pressure": 10.2,
  "pressure_unit": "psi",
  "pressure_basis": "absolute",
  "input_origin": "user_supplied",
  "provenance": null
}
```

- Required: numeric `oxygen_mole_fraction` [0,1], positive finite `total_pressure`, one of `Pa/kPa/bar/atm/psi`, and literal `pressure_basis="absolute"`.
- Do not accept an oxygen percentage field or a client `gas_basis_verified`/`verification_status` flag. The field name defines that the client supplies a mole fraction. For user inputs, backend sets both input verification statuses to UNVERIFIED and origin to `user_supplied`; it may construct the typed condition with the basis gate satisfied by this schema. For source values, backend resolves a verified record and its raw-unit normalization itself.
- Handler calls `calculate_oxygen_partial_pressure(AtmosphericCondition(...))` and serializes its result; it does not reimplement multiplication or conversion.
- Errors: 422 `missing_field`, `invalid_fraction`, `invalid_pressure`, `invalid_unit`, `non_absolute_pressure`, or `ambiguous_oxygen_basis`.
- Provenance: request provenance is advisory only. A source-derived MEASURED value requires lookup against a server-controlled registry with source ID and locator; never trust a body-supplied `MEASURED` status.
- Limits: result is calculated pO2 under Dalton's law; not combustion equivalence, prediction, or safety.

### `POST /api/atmosphere/oxygen-mass-fraction`

Proposed request schema:

```json
{
  "oxygen_mole_fraction": 0.21,
  "diluent_id": "nitrogen",
  "composition_record_id": "GAS-COMP-001"
}
```

- Required: valid oxygen mole fraction and a `diluent_id` resolving to a server-approved, verified, single-species diluent record with molar mass in g/mol and source provenance. Do not accept an untrusted `diluent_verified: true` or arbitrary molar mass as verified.
- Handler obtains `BinaryDiluent` from the trusted composition registry, constructs `OxygenComposition` (no pressure field is needed for this mass-balance equation), and calls `calculate_oxygen_mass_fraction`.
- If there is no approved composition record, return 422 `unverified_diluent` (or 503 until the registry exists); do not substitute air/N2.
- Response includes mass fraction (dimensionless), exact binary equation, selected diluent, its source/locator, verification, assumptions and limitation to O2 plus that one diluent.
- No general multi-component mixture is supported by this endpoint.

### `POST /api/atmosphere/compare`

Proposed request:

```json
{
  "scenario": {"oxygen_mole_fraction": 0.30, "total_pressure": 10.2,
               "pressure_unit": "psi", "pressure_basis": "absolute"},
  "reference": {"oxygen_mole_fraction": 0.20, "total_pressure": 15.3,
                 "pressure_unit": "psi", "pressure_basis": "absolute"}
}
```

- Both states require complete explicit fields; reject nulls and unsupported units. Treat inputs as user supplied/UNVERIFIED unless source records are server-resolved.
- Handler constructs two conditions and calls `compare_atmospheric_conditions`.
- Response separates scenario/reference mole fraction, total pressure and pO2; returns absolute and relative differences, null relative values and warning where a reference is zero, provenance, assumptions and limitations.
- Explicit limitation: similar/equal pO2 does not establish combustion equivalence, spread, extinction, safety or certification.

## Ollama tool policy

Expose only three whitelisted tools corresponding to the calculation endpoints, plus optional health for system diagnostics. Do not expose low-level legacy numeric helpers. The backend should construct typed objects and verification statuses; the model may not set trust flags, invent provenance or choose a diluent by plausibility.

1. If a required parameter is omitted, reject the tool call with a structured missing-field error. Ask the user for the missing value; do not use a default.
2. If pressure unit/basis or oxygen scale is ambiguous, return an error and ask for clarification. Do not infer from context or convert bare `30` to `0.30`.
3. If a calculation is invalid, return no result; the AI should state which field failed and request corrected input.
4. The AI must show input verification status, units, formula, assumptions and limitations with every numeric result. It must call comparisons “atmospheric comparisons,” never “combustion equivalent.”
5. Do not provide flame-spread/extinction predictions or safety claims. Tool schemas return only the deterministic operation's outputs; unsupported questions receive `not_supported_by_engine`.
6. For measured NASA data, require server-side source resolution and row status. The AI cannot turn search snippets, raw table strings or its own inference into MEASURED inputs.

## Example tool interactions

### A. Valid pO2 calculation

Tool request:

```json
{"oxygen_mole_fraction":0.30,"total_pressure":10.2,"pressure_unit":"psi","pressure_basis":"absolute","input_origin":"user_supplied"}
```

Expected response (illustrative rounding for readability; engine retains full float precision):

```json
{
  "status":"success",
  "calculation":"oxygen_partial_pressure",
  "formula":"pO2 = X_O2 * P_total",
  "inputs":{"oxygen_mole_fraction":0.30,"total_pressure":10.2,"pressure_unit":"psi","pressure_basis":"absolute","oxygen_verification":"UNVERIFIED","pressure_verification":"UNVERIFIED"},
  "outputs":{"oxygen_mole_fraction":0.30,"total_pressure_kpa":70.326524,"oxygen_partial_pressure_kpa":21.097957},
  "units":{"oxygen_mole_fraction":"1","total_pressure_kpa":"kPa absolute","oxygen_partial_pressure_kpa":"kPa"},
  "verification":{"oxygen":"UNVERIFIED","total_pressure":"UNVERIFIED","result":"DERIVED"},
  "conversion_methods":{"oxygen_mole_fraction":"Input supplied as mole fraction; no scale conversion recorded.","total_pressure_kpa":"psi to kPa"},
  "provenance":{},
  "assumptions":["Dalton's law is applied to the supplied gas-phase oxygen mole fraction."],
  "limitations":["This calculation does not establish combustion equivalence or fire safety.","Non-ideal mixture fugacity is not calculated."],
  "warnings":[]
}
```

AI wording: “For the user-supplied 0.30 mole fraction and 10.2 psi absolute, calculated pO2 is about 21.098 kPa. Inputs are unverified; this is not a fire-spread or safety prediction.”

### B. Ambiguous percentage / omitted basis

Tool request:

```json
{"oxygen_percent":30,"total_pressure":10.2,"pressure_unit":"psi"}
```

Expected HTTP 422 response:

```json
{"status":"error","error":{"code":"ambiguous_oxygen_basis","field":"oxygen_percent","message":"Provide oxygen as a verified mole fraction between 0 and 1. A bare percentage is not converted automatically."}}
```

AI wording: “I need the oxygen basis clarified. Is 30 reported as mole percent, volume percent under a verified ideal-gas basis, or another scale? I have not calculated pO2.”

### C. Same pO2 comparison with scientific limitation

Tool request: scenario xO2=0.30, P=10.2 psi absolute; reference xO2=0.20, P=15.3 psi absolute.

Expected key result:

```json
{
  "status":"success",
  "calculation":"compare_atmospheric_conditions",
  "outputs":{
    "scenario":{"oxygen_mole_fraction":0.30,"total_pressure_kpa":70.326524,"oxygen_partial_pressure_kpa":21.097957},
    "reference":{"oxygen_mole_fraction":0.20,"total_pressure_kpa":105.489787,"oxygen_partial_pressure_kpa":21.097957},
    "differences_scenario_minus_reference":{"oxygen_mole_fraction":0.10,"total_pressure_kpa":-35.163262,"oxygen_partial_pressure_kpa":0.0},
    "relative_differences":{"oxygen_mole_fraction":0.5,"total_pressure_kpa":-0.333333,"oxygen_partial_pressure_kpa":0.0}
  },
  "limitations":["Equal oxygen partial pressures do not establish combustion equivalence.","This comparison does not infer fire safety or certification."]
}
```

AI wording: “The two supplied states have equal calculated pO2 but different oxygen fractions and total pressures. That does not show equivalent flame behavior; the engine makes no spread, extinction or safety prediction.”

## Readiness decision

The typed engine can be wrapped by FastAPI without duplicating scientific calculations. The endpoints should not be exposed to Ollama until Pydantic models forbid extra fields, source verification is server-controlled, and the mass-fraction endpoint has a trusted diluent catalog. `/api/health` can be added independently. The current routes do not yet exist.
