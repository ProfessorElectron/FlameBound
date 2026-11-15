# Phase 4: FastAPI Scientific Interface

## Scope and version

The API exposes the existing deterministic atmospheric calculations. It does not predict flame spread or extinction, infer partial-gravity behaviour, assess safety, or certify materials. Successful result bodies preserve the complete `CalculationResult.to_dict()` envelope and add `api_schema_version: "1.0"`. The schema version is an API contract constant, not a claim about a separately versioned engine release.

## Endpoints

| Method and path | Purpose |
|---|---|
| `GET /api/health` | Reports backend and atmospheric module availability only. |
| `GET /health` | Compatibility health endpoint retained from the original app. |
| `POST /api/atmosphere/oxygen-partial-pressure` | Calls `calculate_oxygen_partial_pressure`. |
| `POST /api/atmosphere/compare` | Calls `compare_atmospheric_conditions`. |
| `POST /api/atmosphere/oxygen-mass-fraction` | Calls `calculate_oxygen_mass_fraction` only after server registry resolution. |

Atmosphere requests require `oxygen_mole_fraction` in [0,1], positive `total_pressure`, `pressure_unit`, and `pressure_basis: "absolute"`. Supported API units are `Pa`, `kPa`, `bar`, `atm`, and `psi`. Numeric JSON values must be finite; booleans and numeric strings are rejected. Percent values such as `21` are not converted to `0.21`. Unknown fields are rejected, including gauge/unspecified bases and client verification/provenance flags. Comparisons take complete `scenario` and `reference` objects of the same schema.

The mass-fraction request takes `oxygen_mole_fraction` and `diluent_id`. It does not accept a molar mass or a trust flag. The route uses `OxygenComposition` and a `BinaryDiluent` returned by the server-side `DiluentRegistry` abstraction; total pressure is not requested because the calculation does not need it.

## Trust and provenance

For atmospheric hypothetical calculations, the backend marks each input `USER_SUPPLIED` and `UNVERIFIED`, then constructs the typed engine object. The API's public field name and strict numeric range define the requested gas-phase mole-fraction contract; this does not promote the value to experimental evidence. The backend currently has no trusted source-record registry. No source-derived measured flow is available and clients cannot submit source IDs, locators, `MEASURED`, or verification flags as authoritative data.

The diluent registry currently resolves no trusted records. Consequently, mass-fraction requests return HTTP 503 with code `unverified_diluent`, including for identifiers such as `nitrogen`; no nitrogen/air record or assumed composition is bundled. To activate this calculation, implement a reviewed server-side catalogue with stable IDs, named composition, molar mass, source ID and locator, field identity, units, normalization/derivation method, and a verified `MEASURED` or justified `DERIVED` status. The registry must return a validated `BinaryDiluent` whose provenance status agrees with its verification status.

## Responses and errors

Successful calculation bodies retain engine fields: `status`, `calculation`, `formula`, `inputs`, `outputs`, `units`, `verification`, `conversion_methods`, `provenance`, `assumptions`, `limitations`, and `warnings`, plus `api_schema_version`. Engine precision is preserved; presentation rounding belongs in a separate UI layer. Results are returned as strict JSON and non-finite serialized values are not allowed.

Errors have the form `{"status":"error","api_schema_version":"1.0","error":{"code":"...","field":null,"message":"..."}}`. Current error identifiers and statuses are `invalid_request` (422), `calculation_out_of_range` (422 for recognized representability failures), `unverified_diluent` (503), and `internal_error` (500). Unexpected backend exceptions are not reclassified as invalid requests; internal messages and stack traces are not exposed. A non-finite result is rejected before it can be normalized to JSON `null`.

FastAPI OpenAPI documents the same `APIErrorResponse` envelope for the calculation routes' 422/500 errors and the mass-fraction route's 503 error. Runtime request validation is strict Pydantic v2; the app-level validation handler returns the contract envelope instead of FastAPI's default validation body.

`GET /api/health` includes schema version `1.0`. The compatibility `GET /health` intentionally keeps its original minimal `{"status":"ok"}` shape and has no version field. It reports process availability only.

## Scientific boundary and AI tool whitelist

Only these typed operations are allowed for tool integration:

1. `calculate_oxygen_partial_pressure`
2. `compare_atmospheric_conditions`
3. `calculate_oxygen_mass_fraction` only after a trusted diluent record is available

Optional health diagnostics may report service availability. Legacy numeric helpers (`convert_pressure`, `oxygen_partial_pressure`, `oxygen_mass_fraction`, `compare_atmospheres`) are not API or AI tools. An AI caller cannot set verification flags or invent provenance. Equal oxygen partial pressures do not establish combustion equivalence. These atmospheric tools cannot answer flame-spread, extinction, lunar/Martian extrapolation, fire-safety, or certification questions.

## Run and test

From the repository root, install the declared project dependencies in the project's environment and start the API:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload
```

Run API tests with:

```powershell
python -m unittest tests.test_atmospheric_api -v
```

Run the complete unit test suite with:

```powershell
python -m unittest discover -s tests -v
```

## Known limitations and future work

- There is no verified experimental test-point registry and no trusted diluent catalogue.
- Results do not currently include measurement-uncertainty estimates; no uncertainty model is implemented for these user-supplied calculations.
- Atmospheric calculations are deterministic transformations of submitted values, not combustion outcome models.
- Source-backed requests require a future registry that resolves and validates source ID, locator, field, units, and normalization on the server.
- Add cross-version API contract tests and review catalogue provenance before enabling measured inputs or mass-fraction success responses.
