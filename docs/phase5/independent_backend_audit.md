# Phase 5: Independent Backend Audit

**Review date:** 2026-11-15

**Scope:** Phase 4 FastAPI atmospheric interface, integration boundary, engine calls, and evidence limits. This review inspected the current source and exercised the API; Phase 4's prior test report was not treated as proof.

## Verdict

**B: READY AFTER MINOR CORRECTIONS**, for the constrained atmospheric calculation API only. The request validation, typed engine delegation, provenance labels, error categories, strict response serialization, and versioned error schema are now verified by tests. Frontend and AI integration remain conditional on transport setup and respecting the narrow tool contract. The API does not provide the project's planned evidence query or prediction features.

No Critical or High severity defects were found. Three Medium findings were corrected; two Medium integration limitations remain explicitly open (cross-origin transport configuration and absence of evidence/uncertainty services).

## Repository and execution path inspected

- Root structure and Git status; existing uncommitted work was present before this audit and has been preserved.
- All source modules under `backend/app/` (excluding generated `__pycache__` artifacts), including main app, API modules, schemas, services, and placeholders; backend tests directory.
- `modelling/atmospheric.py`, `modelling/data_harmonization.py`, all test modules under `tests/`, dependency declarations, README, Phase 3 review material, Phase 4 docs, and the scientific API contract.
- Frontend scaffold/package and AI directory contents; search found no current frontend or AI API consumer.

Request path: FastAPI parses the request → Pydantic v2 strict models reject coercion, extras, invalid units/bases/ranges → the route creates the typed engine dataclass and server-controlled provenance → a typed `calculate_*` function returns `CalculationResult` → `.to_dict()` retains metadata → the route validates JSON with `allow_nan=False`, adds schema version, and returns the result. The mass-fraction route resolves the server registry before constructing a composition; the default registry has no records and returns 503.

The production Python application exposes `/health`, `/api/health`, and exactly three atmospheric POST operations. Legacy numeric helpers are not routed or registered as tools. The evidence, experiment, and analysis route files remain placeholders.

## Findings

### P5-01 — Unexpected engine exceptions were mislabeled as client errors

- **Severity:** Medium
- **Affected:** `backend/app/main.py`, global `ValueError` and `TypeError` handlers.
- **Finding:** Every `ValueError` or `TypeError`, including an internal invariant/programming failure, was returned as HTTP 422. This blurred invalid input with backend failure and could make a defect appear to be user error.
- **Consequence:** Clients could retry or alter scientifically valid inputs instead of surfacing a server failure; monitoring would lose the 500 signal.
- **Correction:** Removed broad 422 handlers. Schema errors remain 422; recognized finite-range errors map explicitly to `calculation_out_of_range`/422; unexpected exceptions return generic `internal_error`/500 without details.
- **Fixed:** Yes. Regression test injects `RuntimeError`, `TypeError`, and unexpected `ValueError` and checks generic 500 responses.

### P5-02 — Non-finite result values could be normalized to JSON null

- **Severity:** Medium
- **Affected:** `backend/app/api/atmosphere.py::_serialized_result`.
- **Finding:** FastAPI's response encoder converted a mocked NaN result to JSON `null` with HTTP 200, silently changing the result rather than rejecting it.
- **Consequence:** A malformed calculation response could look like a successful missing value, obscuring a numerical/software failure.
- **Correction:** The route now validates the full engine payload with standard JSON serialization and `allow_nan=False` before returning it. Failure is handled as a generic 500 without partial output.
- **Fixed:** Yes. Adversarial response-serialization regression test passes.

### P5-03 — Blank diluent identifiers were treated as unavailable catalogue records

- **Severity:** Low
- **Affected:** `backend/app/schemas/atmosphere.py::OxygenMassFractionRequest`.
- **Finding:** A whitespace-only `diluent_id` passed the original minimum-length constraint and received 503 instead of an input-validation error.
- **Consequence:** Invalid request data was conflated with unavailable trusted scientific information.
- **Correction:** Blank IDs and IDs with surrounding whitespace are rejected by schema validation.
- **Fixed:** Yes. Empty, whitespace, padded, and null IDs return 422.

### P5-04 — OpenAPI advertised a different validation-error shape

- **Severity:** Medium
- **Affected:** `backend/app/api/atmosphere.py` route metadata and `backend/app/schemas/atmosphere.py`.
- **Finding:** Runtime validation returned FlameBound's versioned error envelope, but generated OpenAPI defaulted to FastAPI's validation-error schema.
- **Consequence:** Generated clients and frontend/AI implementers could code against a body the API does not return.
- **Correction:** Added strict `APIErrorResponse` schemas to route responses for 422, 500, and mass-registry 503; a regression test checks generated OpenAPI.
- **Fixed:** Yes.

### P5-05 — The API contract document did not match runtime payloads

- **Severity:** Medium
- **Affected:** `docs/scientific_review/scientific_api_contract.md`, Phase 4 API documentation.
- **Finding:** Earlier proposal text described fields such as `result` and `inputs_used`, and sample request properties that the current strict HTTP API does not accept.
- **Consequence:** Teammates could send rejected requests or depend on absent response fields.
- **Correction:** Replaced the current contract with verified routes, request/response structures, error codes, provenance semantics, and a captured actual successful response. Historical Phase 3 review documents remain unchanged as historical snapshots.
- **Fixed:** Yes.

### P5-06 — Cross-origin frontend transport is not configured

- **Severity:** Medium
- **Affected:** `backend/app/main.py`, `frontend/vite.config.js`.
- **Finding:** The frontend and backend run as separate development servers; there is no backend CORS allowlist or Vite API proxy in the current scaffold.
- **Consequence:** Browser requests from a separate origin may fail even when the API contract and server are correct.
- **Recommendation:** Before browser integration, agree a development origin and add either a narrowly configured backend CORS allowlist or a same-origin development proxy. Do not use wildcard origins with credentials. CORS is not authentication.
- **Fixed:** No. This needs an agreed frontend/deployment origin; no origin was invented during this audit.

### P5-07 — No evidence API, uncertainty output, or predictive capability exists

- **Severity:** Medium (scope limitation)
- **Affected:** evidence/analysis placeholders, `modelling/atmospheric.py::CalculationResult`, verified harmonized table.
- **Finding:** The API exposes atmospheric transformations only. It has no source-backed evidence query, uncertainty estimate, or predictive model. The harmonized table contains zero verified rows.
- **Consequence:** It cannot support experimental coverage comparisons, evidence similarity, or outcome predictions. Deterministic outputs must not be presented as measured or uncertainty-qualified findings.
- **Recommendation:** Keep these as explicitly unavailable until source registration/review, verified data, and a separately validated model exist.
- **Fixed:** Not applicable; intentionally not implemented in Phase 5.

### P5-08 — Verification metadata has a semantic field to explain to clients

- **Severity:** Low
- **Affected:** `backend/app/api/atmosphere.py::_condition`, engine echo of `gas_basis_verified`.
- **Finding:** The response inputs echo `gas_basis_verified: true` because the route satisfies the engine's gas-phase mole-fraction gate from the constrained API field contract; the same result reports oxygen verification `UNVERIFIED` and user-supplied provenance.
- **Consequence:** A consumer that reads the Boolean alone could mistake a declared input convention for experimental verification.
- **Correction:** Documented this distinction prominently in API integration docs. No source trust is conferred; clients cannot submit the flag.
- **Fixed:** Partly by documentation. Client display must use `verification` and `provenance`, not this engine gate alone.

### P5-09 — Public deployment controls are outside the current scaffold

- **Severity:** Low
- **Affected:** FastAPI app configuration.
- **Finding:** No authentication, rate limiting, or deployment policy is defined. Current routes are read-only calculations, but no public-hosting controls are included.
- **Consequence:** The app should not be treated as a production public service based only on API correctness.
- **Recommendation:** Keep development service on a trusted network; establish deployment-specific access, origin, and resource controls before public hosting.
- **Fixed:** No. Operational hosting was outside scope.

### P5-10 — JSON decimal underflow could masquerade as exact zero

- **Severity:** Medium
- **Affected:** FastAPI JSON parsing and `backend/app/schemas/atmosphere.py::_finite_json_float`.
- **Finding:** The default JSON float parser can convert a literal such as `1e-999` to `0.0` before Pydantic validation. An oxygen input that is small but nonzero could then be reported as exact zero.
- **Consequence:** The API could silently change a scientifically meaningful input at parse time.
- **Correction:** Atmospheric routes now parse JSON decimal tokens as `Decimal` until schema validation and reject nonzero values that underflow binary64.
- **Fixed:** Yes. A raw JSON exponent adversarial test confirms 422 with no result.

## Scientific and provenance assessment

- pO2 and comparison use only the typed engine functions. Pressure is required to be positive and explicitly absolute; only Pa, kPa, bar, atm, and psi are accepted by the API.
- Mole fractions are constrained to [0,1]; zero and one are valid. The engine normalizes pressure to kPa without route-level equations.
- Comparisons preserve scenario/reference fields, scenario-minus-reference differences, relative values, zero-reference nulls/warnings, and limitations against combustion-equivalence claims.
- Mass fraction cannot succeed because the registry returns no trusted records. No nitrogen/air record is invented and no client molar mass is accepted.
- Every API-supplied hypothetical input is assigned `USER_SUPPLIED` and `UNVERIFIED`. No NASA source lookup or measured-data flow exists.
- Calculation output carries formula, units, conversion methods, provenance, assumptions, limitations, and warnings. It carries no measurement-uncertainty estimates.
- The API reports no flame spread, extinction, partial-gravity extrapolation, safety, or certification output.

## Health and response assessment

`/api/health` reports process/module availability and schema version only; it does not claim datasets or prediction readiness. `/health` remains the minimal compatibility response and is intentionally unversioned. Successful calculation responses preserve engine fields and use `api_schema_version: "1.0"`. Structured errors have no output values. Unexpected errors are generic 500; error text and stack traces are suppressed.

## Integration assessment

- **Frontend:** The request/response contract is stable for the two available calculations, after origin/proxy setup. The UI must label values as user-supplied and unverified, display limitations, and handle mass fraction as unavailable. It cannot yet display NASA evidence search, coverage, uncertainty, or prediction results.
- **AI:** A constrained caller can use only pO2 and comparison today; mass fraction is excluded until a trusted registry exists. No Ollama integration is present. The AI must not compute results itself, set trust flags, invent source records/composition, use unrestricted Python, or make safety/prediction claims.

## Verification summary

The focused API suite passes 21 tests; the full `unittest` suite passes 62 tests. `git diff --check` passes with Git line-ending conversion warnings only. Raw NASA files and the zero-row harmonized table remain unchanged. No frontend or AI source was changed, and no commit or push was made. See `adversarial_test_report.md` for detailed cases and exact commands.
