# FlameBound Backend Handover

**Contract version:** `1.0`

**Status:** Ready for constrained frontend and AI integration of atmospheric calculations; not an evidence or prediction service.

## Architecture

The backend has three layers:

1. `backend/app/main.py` creates the FastAPI app, health routes, and structured error handlers.
2. `backend/app/schemas/atmosphere.py` validates strict Pydantic v2 request models. `backend/app/api/atmosphere.py` constructs server-controlled typed inputs, calls the existing engine, and serializes full results.
3. `modelling/atmospheric.py` owns the deterministic scientific calculations and `CalculationResult.to_dict()` output. The backend does not duplicate the equations.

The mass-fraction route uses the `DiluentRegistry` interface in `backend/app/services/diluent_registry.py`. Its default implementation contains no records and never assumes nitrogen or air. Evidence, experiment, and general analysis route modules remain placeholders.

## Python and dependencies

- Python: **3.10 or newer** (`pyproject.toml`); the audit runtime was Python 3.13.0.
- API runtime dependencies: FastAPI `>=0.110`, Pydantic `>=2.6`, and Uvicorn `>=0.27` with standard extras.
- API test client dependency: HTTPX `>=0.27` is now included in the `all` optional dependency set because `tests/test_atmospheric_api.py` uses FastAPI `TestClient`.
- `requirements.txt` installs `.[all]`, including other research/data packages and pytest; it is broader than the minimum API runtime.
- Audited versions: FastAPI 0.163.0, Pydantic 2.14.3, Starlette 1.10.0, Uvicorn 0.54.0, HTTPX 0.28.1.

## Setup and run

Run these commands from the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload
```

The last command was started successfully during Phase 5.1 and served on `http://127.0.0.1:8000`. Interactive API docs are available at `/docs` while the local server is running. Stop the development server with Ctrl+C.

Run tests from the repository root:

```powershell
python -m unittest tests.test_atmospheric_api -v
python -m unittest discover -s tests -v
```

## Endpoints

| Method/path | Request | Behavior |
|---|---|---|
| `GET /api/health` | None | 200; backend and atmospheric engine availability plus schema version. It does not report data readiness. |
| `GET /health` | None | Compatibility 200 `{"status":"ok"}`; intentionally no schema version. |
| `POST /api/atmosphere/oxygen-partial-pressure` | One atmosphere object | Typed Dalton-law calculation; 200 or structured 422/500. |
| `POST /api/atmosphere/compare` | `scenario` and `reference` atmosphere objects | Typed comparison; 200 or structured 422/500. |
| `POST /api/atmosphere/oxygen-mass-fraction` | Oxygen mole fraction and `diluent_id` | Currently 503 `unverified_diluent`; no trusted diluent catalogue exists. |

An atmosphere object requires all four fields:

```json
{
  "oxygen_mole_fraction": 0.30,
  "total_pressure": 10.2,
  "pressure_unit": "psi",
  "pressure_basis": "absolute"
}
```

The comparison body uses two such objects:

```json
{
  "scenario": {
    "oxygen_mole_fraction": 0.30,
    "total_pressure": 10.2,
    "pressure_unit": "psi",
    "pressure_basis": "absolute"
  },
  "reference": {
    "oxygen_mole_fraction": 0.20,
    "total_pressure": 15.3,
    "pressure_unit": "psi",
    "pressure_basis": "absolute"
  }
}
```

The mass-fraction request is:

```json
{"oxygen_mole_fraction": 0.21, "diluent_id": "catalogue-id"}
```

That identifier is only a schema example; no identifier currently resolves. Requests reject extras, missing/null fields, booleans, numeric strings, non-finite values, nonzero JSON decimals that underflow binary64, oxygen fractions outside [0,1], nonpositive pressure, unsupported units, gauge/unspecified basis, and blank/padded diluent IDs. Units are `Pa`, `kPa`, `bar`, `atm`, and `psi`. Mole fractions are not percentages.

## Success and error format

Schema version is **`1.0`**, defined in `backend/app/version.py`. Successful calculation responses preserve the complete engine envelope:

`status`, `calculation`, `formula`, `inputs`, `outputs`, `units`, `verification`, `conversion_methods`, `provenance`, `assumptions`, `limitations`, `warnings`, plus `api_schema_version`.

Actual example: the pO2 request above returned HTTP 200 with `calculation: "oxygen_partial_pressure"`, formula `pO2 = X_O2 * P_total`, and outputs `total_pressure_kpa: 70.32652439031727` and `oxygen_partial_pressure_kpa: 21.097957317095183`. Its verification fields were `UNVERIFIED` for oxygen and pressure. The complete captured response is in [`scientific_api_contract.md`](../scientific_review/scientific_api_contract.md#success-response).

Structured errors have this shape and contain no calculation outputs:

```json
{
  "status": "error",
  "api_schema_version": "1.0",
  "error": {
    "code": "unverified_diluent",
    "field": "diluent_id",
    "message": "No trusted diluent record is available for this identifier."
  }
}
```

Current codes:

- HTTP 422 `invalid_request`: invalid request schema/value.
- HTTP 422 `calculation_out_of_range`: finite numeric result cannot be represented.
- HTTP 503 `unverified_diluent`: no trusted diluent record is available.
- HTTP 500 `internal_error`: unexpected server failure; details are suppressed.

The `APIErrorResponse` model is also included in generated OpenAPI for route errors.

## Provenance semantics

Atmospheric request inputs are hypothetical user values. The server creates `USER_SUPPLIED` provenance and marks oxygen/pressure verification `UNVERIFIED`. A value that happens to match a NASA result remains unverified. Clients cannot submit source IDs, source locators, verification statuses, raw-source normalization, or gas/diluent trust flags.

The engine result echoes `gas_basis_verified: true` because the route's constrained schema requires the caller to declare a mole fraction. That internal engine gate is **not** experimental verification; use the response `verification` and `provenance` fields. The derived result status means calculated from supplied inputs, not measured.

## Known unavailable operations and scientific limits

- Mass-fraction success is disabled until a reviewed server-side diluent catalogue exists. The API will not assume air or nitrogen.
- No source-record lookup, NASA evidence search, evidence-coverage endpoint, verified experimental query, or data-write route exists.
- The harmonized dataset contains zero verified test-point rows.
- No measurement-uncertainty estimate, flame-spread/extinction model, partial-gravity extrapolation, safety determination, or certification is available.
- No legacy numerical helper is an API or AI tool.

## Frontend prerequisites

- Use only the documented request fields and handle all listed status/error codes.
- Display units, formula, limitations, warnings, and user-supplied/unverified status. Do not call equal pO2 combustion-equivalent or safe.
- The current Vite scaffold has no backend proxy and the API has no CORS middleware. Before cross-origin browser calls, the frontend/backend owners must confirm the development origin, then configure a narrow CORS allowlist or a same-origin proxy. CORS was intentionally not implemented during this handover.
- Do not expose evidence dashboards or mass-fraction success states until their server capabilities exist.

## AI integration restrictions

An eventual Ollama tool layer may call only:

1. `POST /api/atmosphere/oxygen-partial-pressure`
2. `POST /api/atmosphere/compare`
3. `POST /api/atmosphere/oxygen-mass-fraction` only after a trusted diluent registry exists
4. Optional `GET /api/health` for service status

Do not expose unrestricted Python execution, legacy numeric helpers, source-verification controls, or fabricated composition. The AI must not independently recalculate returned values or claim verified NASA evidence, predictions, partial-gravity behavior, safety, or certification. No Ollama integration is implemented here.

## Verification snapshot

Phase 5.1 started the exact command documented above and verified over HTTP:

- `/api/health`: 200 with atmospheric engine availability and version 1.0.
- `/health`: 200 compatibility response.
- pO2: 200 with full engine result and unverified provenance.
- comparison: 200 with scenario/reference outputs and differences.
- mass fraction: 503 `unverified_diluent` as expected.

Phase 5.1 verification: **62 tests passed, 0 failed** with `python -m unittest discover -s tests -v`. `git diff --check` passed with line-ending warnings only. TestClient emitted a Starlette deprecation warning for HTTPX compatibility, but the tests passed. Re-run the commands above after changes.
