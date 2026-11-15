# Phase 5 Frontend and AI Integration Readiness

This contract is verified against the current FastAPI app. Schema version: **1.0**. The API is suitable for a constrained atmospheric-calculation UI or tool caller. It is not a NASA evidence or prediction API.

## Available operations

| Method/path | Request | Normal responses |
|---|---|---|
| `GET /api/health` | None | 200 with backend/module availability and `api_schema_version`. |
| `GET /health` | None | Compatibility 200 `{"status":"ok"}`; no version field. |
| `POST /api/atmosphere/oxygen-partial-pressure` | One atmosphere object | 200 calculation; 422 invalid request/range; 500 internal error. |
| `POST /api/atmosphere/compare` | `scenario` and `reference`, each an atmosphere object | 200 comparison; 422 invalid request/range; 500 internal error. |
| `POST /api/atmosphere/oxygen-mass-fraction` | `oxygen_mole_fraction`, `diluent_id` | 422 invalid request; 503 `unverified_diluent`; 500 internal error. Current registry always returns 503 for valid IDs. |

Atmosphere object fields are all required: `oxygen_mole_fraction` (finite JSON number 0 through 1), `total_pressure` (finite JSON number greater than zero), `pressure_unit` (`Pa`, `kPa`, `bar`, `atm`, or `psi`), and `pressure_basis` (literal `absolute`). Booleans, numeric strings, null/missing fields, unsupported values, extra keys, and decimal inputs that underflow binary64 to zero are rejected. Mole fraction is not percent; the service does not infer scale. Compare conditions use precisely this nested shape. Mass-fraction `diluent_id` must be nonblank, without surrounding whitespace; client molar masses, verification flags, and provenance are forbidden.

## Error codes

| Status | Code | Client handling |
|---:|---|---|
| 422 | `invalid_request` | Correct request fields/types/values. No calculation outputs are present. |
| 422 | `calculation_out_of_range` | Inputs were schema-valid but the numerical result cannot be represented finitely. Do not retry by rounding automatically. |
| 503 | `unverified_diluent` | Mass fraction is unavailable until a trusted server registry is supplied. Do not substitute nitrogen or air. |
| 500 | `internal_error` | Show a generic failure and report through the app's operational channel; response contains no internal details. |

All structured errors contain `status: "error"`, `api_schema_version: "1.0"`, and `error: {code, field, message}`. `field` may be null. Errors contain no partial numeric output. OpenAPI documents the same error model. Unknown routes/methods are not supported operations.

## Successful response structure

The API preserves every field returned by `CalculationResult.to_dict()`: `status`, `calculation`, `formula`, `inputs`, `outputs`, `units`, `verification`, `conversion_methods`, `provenance`, `assumptions`, `limitations`, and `warnings`; it adds `api_schema_version`. See the complete captured pO2 response in [`scientific_api_contract.md`](../scientific_review/scientific_api_contract.md#success-response).

An actual comparison response's `outputs` for scenario `0.3`, `10 psi` and reference `0.0`, `15 psi` was:

```json
{
  "scenario": {
    "oxygen_mole_fraction": 0.3,
    "total_pressure_kpa": 68.94757293168361,
    "oxygen_partial_pressure_kpa": 20.684271879505083
  },
  "reference": {
    "oxygen_mole_fraction": 0.0,
    "total_pressure_kpa": 103.4213593975254,
    "oxygen_partial_pressure_kpa": 0.0
  },
  "differences_scenario_minus_reference": {
    "oxygen_mole_fraction": 0.3,
    "total_pressure_kpa": -34.4737864658418,
    "oxygen_partial_pressure_kpa": 20.684271879505083
  },
  "relative_differences": {
    "oxygen_mole_fraction": null,
    "total_pressure_kpa": -0.3333333333333333,
    "oxygen_partial_pressure_kpa": null
  }
}
```

The actual response includes `warnings` explaining each zero-reference null and `limitations` stating equal pO2 does not establish combustion equivalence. Inputs remain user supplied and unverified.

## Provenance and missing data

Valid client calculations are hypothetical: server origin is `USER_SUPPLIED`, and oxygen and pressure verification are `UNVERIFIED`. The engine input echo includes `gas_basis_verified: true` due to its internal contract gate; do not interpret this as NASA evidence. Use response `verification` and `provenance` fields. A value resembling a NASA observation remains user supplied.

No source-record lookup, evidence endpoint, verified experimental test-point row, or diluent catalogue is available. The harmonized dataset has zero verified rows. No measurement uncertainty or prediction is returned. Relative comparison values may be null when the reference quantity is zero.

## Frontend guidance

- Send only the documented JSON fields and preserve unit/basis selections explicitly.
- Label submissions/results as user supplied and unverified; display formula, units, limitations, and warnings.
- Treat mass fraction as unavailable; do not hard-code nitrogen/air.
- Do not label equal pO2 as combustion equivalent or safe.
- The current frontend scaffold has no API proxy; the backend has no CORS middleware. Before a browser on a separate origin calls the API, agree a development origin and configure either a narrow CORS allowlist or same-origin proxy. No wildcard CORS policy is preconfigured.
- `/health` is legacy/minimal; use `/api/health` for a versioned app availability check.

## AI tool allowlist

Permit only:

1. `POST /api/atmosphere/oxygen-partial-pressure`
2. `POST /api/atmosphere/compare`
3. `POST /api/atmosphere/oxygen-mass-fraction` only when a trusted diluent registry is deployed
4. Optional `GET /api/health` for service availability

Do not expose unrestricted Python, legacy numerical helpers, source verification controls, or a direct data write tool. The AI must pass values to deterministic endpoints, preserve numeric outputs and metadata, and must not invent evidence, composition, uncertainty, flame spread, extinction, partial-gravity behavior, safety, or certification conclusions.

## Readiness decision

- **Frontend:** **B — Ready after minor integration setup** for pO2/comparison forms; CORS or proxy configuration remains. Evidence dashboards, verified records, and mass-fraction success are unavailable.
- **AI:** **B — Ready for a constrained caller** of pO2/comparison only. There is no Ollama integration in this repo; the AI teammate must implement tool calling outside this backend and maintain the allowlist. Mass fraction remains disabled.
- **Deployment:** Local/trusted-network development only until deployment origin, access policy, and operational controls are agreed. The app does not define authentication or rate limiting.
