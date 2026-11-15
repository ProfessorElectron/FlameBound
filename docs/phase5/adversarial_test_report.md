# Phase 5 Adversarial Test Report

**Runtime:** Python 3.13.0, FastAPI 0.163.0, Pydantic 2.14.3, Starlette TestClient.

**Commands:** `python -m unittest tests.test_atmospheric_api -v`; `python -m unittest discover -s tests -v`.

## Results

- Focused API suite: **21 tests passed, 0 failed**.
- Complete test suite: **62 tests passed, 0 failed**.
- `git diff --check`: passed; Git printed line-ending conversion warnings only.
- TestClient printed a Starlette deprecation warning about `httpx` and future `httpx2` support. It did not affect results. No extra package was installed for that warning.

## Cases exercised and observed behavior

| Area | Inputs/actions | Expected | Observed |
|---|---|---|---|
| Required fields/types | Missing values, nulls, booleans, numeric strings, strings in unit slots | Structured 422, no outputs | 422 `invalid_request`, no outputs |
| Extra/trust fields | `gas_basis_verified`, measured status, source ID/locator, origin, provenance, diluent flags/molar mass; extra nested comparison fields | Reject extras; no trust promotion | 422 `invalid_request`; successful user inputs in valid calls remain `USER_SUPPLIED`/`UNVERIFIED` |
| Numeric edge cases | NaN, ±infinity, huge integer `10**1000`, zero/negative pressure, fractions below 0/above 1 | Reject with 422, no outputs | 422; huge integer conversion is caught as request validation, not 500 |
| JSON decimal parse underflow | Raw JSON `oxygen_mole_fraction: 1e-999` | Reject nonzero decimal that would underflow to binary64 zero | 422; not silently treated as exact zero |
| Boundaries | `X_O2=0`, `X_O2=1`, very small finite nonzero fraction | Accept finite outputs | 200; zero remains zero, one and low nonzero values calculate successfully |
| Units/basis | Pa/kPa/atm/psi examples, gauge/unknown basis, unsupported MPa | Supported units normalize; invalid basis/unit rejected | Supported examples calculate through typed engine; unsupported values return 422 |
| Representability | `1e308 psi`, `5e-324 kPa` with nonzero fraction | 422 range error without partial results | 422 `calculation_out_of_range`; no outputs |
| Comparison | Identical physical pressure represented as 1 atm and 101.325 kPa; zero-reference quantities | Correct normalized differences; null relative value at zero | Differences approximately zero for equivalent values; zero-reference relative values are null and warnings retained |
| Parsing/media | Malformed JSON; correct JSON body with `text/plain` content type | Structured 422, no result | 422 `invalid_request`, no outputs |
| Diluent | Missing catalogue record, arbitrary molar mass/trust flags, blank/null/padded IDs | No assumed nitrogen/air; 503 only for valid ID with unavailable record, 422 malformed ID | Valid-shaped ID returns 503 `unverified_diluent`; malformed IDs and client assertions return 422 |
| Error semantics | Mocked internal `RuntimeError`, `TypeError`, and unexpected `ValueError` | Generic 500, no internal details | 500 `internal_error`; no stack/message/output in body |
| Response JSON | NaN in mocked engine result | Fail closed, not success/null | 500 `internal_error`; no `NaN` or partial output. Engine `.to_dict()` also has independent non-finite tests. |
| API contract | Versions, route operation delegation, OpenAPI error schema | Match runtime contract; typed functions only | Version `1.0` consistent on API success/error/health; pO2 and comparison typed calls verified; mass calc not called without registry; OpenAPI error schema checked |

## Defects found and corrected

1. Global `ValueError`/`TypeError` handlers categorized implementation failures as 422. They were removed; recognized range errors map explicitly to 422 and unexpected failures to 500.
2. FastAPI could convert a non-finite mocked response to JSON `null` while returning 200. Strict `json.dumps(..., allow_nan=False)` is now applied before returning a result.
3. Whitespace-only `diluent_id` was incorrectly classified as an unavailable registry entry. The schema now rejects blank and padded IDs.
4. Generated OpenAPI described the default FastAPI 422 body while runtime used a different body. The declared 422/500/503 response models now match the versioned error envelope.
5. The prior API contract file documented proposal-only fields (`result`, `inputs_used`, client provenance) that were not supported by runtime. It has been rewritten to match actual request/response structures.
6. Default JSON parsing could erase tiny nonzero decimal values before schema validation. Atmospheric request bodies now preserve decimal tokens through validation and reject binary64 underflow.

## Limits of these tests

These are local in-process tests, not load, deployment, browser CORS, authentication, or network-security tests. They do not validate a trusted source registry, because none exists. Mass-fraction success cannot be tested without fabricating the very trusted record the API correctly lacks. API behavior was exercised on the installed runtime versions; the full declared dependency-version range was not matrix-tested.
