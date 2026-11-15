# Scientific API Contract for Frontend and Ollama Integration

This file describes the current HTTP API. It supersedes the earlier proposal in this document. Engine-only helpers and future evidence operations are not public routes. Phase 4 implementation details and limits are in [`docs/phase4/fastapi_scientific_interface.md`](../phase4/fastapi_scientific_interface.md).

## Version and supported operations

The versioned response contract is `api_schema_version: "1.0"` on `/api/health`, successful calculations, and structured API errors. The legacy `/health` endpoint retains `{"status":"ok"}` without a version field.

| Method | Path | Status and engine operation |
|---|---|---|
| GET | `/api/health` | 200; app and atmospheric module availability only. |
| POST | `/api/atmosphere/oxygen-partial-pressure` | 200 or 422; `calculate_oxygen_partial_pressure`. |
| POST | `/api/atmosphere/compare` | 200 or 422; `compare_atmospheric_conditions`. |
| POST | `/api/atmosphere/oxygen-mass-fraction` | 503 until a trusted diluent registry can resolve a verified record; then typed calculation. |
| GET | `/health` | 200; compatibility response only. |

No pressure-conversion route, source-record route, evidence route, prediction route, or legacy numeric helper is public.

## Request bodies

Partial-pressure and each nested comparison condition require this exact shape; extra keys are rejected:

```json
{
  "oxygen_mole_fraction": 0.30,
  "total_pressure": 10.2,
  "pressure_unit": "psi",
  "pressure_basis": "absolute"
}
```

- `oxygen_mole_fraction`: finite JSON number in [0,1]. It is a mole fraction; percent scales are not inferred.
- `total_pressure`: finite JSON number greater than zero.
- `pressure_unit`: one of `Pa`, `kPa`, `bar`, `atm`, `psi`.
- `pressure_basis`: literal `absolute`.
- Booleans, strings containing numbers, nulls, missing fields, and additional fields are rejected.

Comparison body:

```json
{"scenario": {"oxygen_mole_fraction": 0.30, "total_pressure": 10.2, "pressure_unit": "psi", "pressure_basis": "absolute"},
 "reference": {"oxygen_mole_fraction": 0.20, "total_pressure": 15.3, "pressure_unit": "psi", "pressure_basis": "absolute"}}
```

Mass-fraction body:

```json
{"oxygen_mole_fraction": 0.21, "diluent_id": "catalogue-id"}
```

`diluent_id` must be nonblank and have no surrounding whitespace. Molar mass, source metadata, and trust flags are never accepted from the client. Today every ID returns 503 `unverified_diluent`; the example is a schema illustration, not a currently resolvable record.

## Success response

The following is the actual response shape from the partial-pressure route for the example request above, captured against the current implementation. Numeric precision is not rounded by the API.

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
    "oxygen_mole_fraction": "Input supplied as mole fraction; no scale conversion recorded.",
    "total_pressure_kpa": "psi to kPa"
  },
  "provenance": {
    "oxygen_mole_fraction": {
      "origin": "user_supplied",
      "verification_status": "UNVERIFIED",
      "source_id": null,
      "source_locator": null,
      "raw_value": null,
      "raw_unit": null,
      "normalization_method": null,
      "note": "Submitted by API client; no source record was asserted or verified."
    },
    "total_pressure": {
      "origin": "user_supplied",
      "verification_status": "UNVERIFIED",
      "source_id": null,
      "source_locator": null,
      "raw_value": null,
      "raw_unit": null,
      "normalization_method": null,
      "note": "Submitted by API client; no source record was asserted or verified."
    }
  },
  "assumptions": ["Dalton's law is applied to the supplied gas-phase oxygen mole fraction."],
  "limitations": [
    "This calculation does not establish combustion equivalence or fire safety.",
    "Non-ideal mixture fugacity is not calculated."
  ],
  "warnings": [],
  "api_schema_version": "1.0"
}
```

The engine currently echoes `gas_basis_verified: true` because the endpoint's constrained field contract accepts an explicitly declared mole fraction. This field is not experimental verification: the `verification` and `provenance` sections remain `UNVERIFIED` and `user_supplied`. A UI must not display that boolean as evidence provenance.

Comparison results preserve `outputs.scenario`, `outputs.reference`, `outputs.differences_scenario_minus_reference`, and `outputs.relative_differences`. Relative values are `null` with a warning when the reference is zero. Equal pO2 is not combustion equivalence.

## Error contract

Errors contain no calculation outputs:

```json
{"status":"error","api_schema_version":"1.0","error":{"code":"invalid_request","field":"pressure_basis","message":"Request fields must use finite JSON numbers, supported values, and the documented schema."}}
```

| HTTP | Code | Meaning |
|---:|---|---|
| 422 | `invalid_request` | Missing, malformed, extra, incorrectly typed, non-finite, unsupported, or scientifically invalid request. |
| 422 | `calculation_out_of_range` | Inputs pass schema checks, but a recognized numerical operation cannot be represented as a finite result. |
| 503 | `unverified_diluent` | No trusted diluent record is available. |
| 500 | `internal_error` | Unexpected backend failure; details are suppressed. |

Unknown paths or methods use framework 404/405 handling and are not part of the supported contract. The current app-level HTTP exception wrapper may produce generic `request_unavailable` errors for these framework responses.

## Provenance semantics

HTTP clients may supply only hypothetical numeric conditions. The server creates `USER_SUPPLIED` provenance and `UNVERIFIED` status. It does not accept or resolve source IDs, locators, raw source values, normalization metadata, or client assertions of `MEASURED`/`DERIVED`. Similarity between a submitted value and a source value does not change this status.

There is no trusted source registry, no verified experimental API, and no diluent catalogue. No successful measured-data flow is available. The atmospheric engine currently returns no measurement-uncertainty estimate; none should be inferred from its deterministic numeric output.

## AI tool allowlist

An eventual Ollama tool layer may call only:

1. `POST /api/atmosphere/oxygen-partial-pressure`
2. `POST /api/atmosphere/compare`
3. `POST /api/atmosphere/oxygen-mass-fraction` only after a trusted diluent registry exists
4. Optional `GET /api/health` for availability diagnostics

The AI must pass validated user-provided values through the API, preserve exact results/provenance/limitations, and must not use unrestricted Python execution. It must not claim experimental evidence, predict spread/extinction, extrapolate partial gravity, or assess safety/certification. It cannot set trust flags or invent a diluent composition.

## Integration limits

The API is suitable for a UI that exposes only the listed deterministic calculations and labels inputs/results as unverified. It does not currently expose NASA evidence search, evidence coverage, harmonized records, uncertainty propagation, prediction, or operational safety functions. The harmonized dataset has zero verified test-point rows. See [`docs/phase5/api_integration_readiness.md`](../phase5/api_integration_readiness.md) for current integration decisions.
