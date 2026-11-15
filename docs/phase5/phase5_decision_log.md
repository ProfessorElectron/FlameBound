# Phase 5 Decision Log

**Date:** 2026-11-15

## Audit decisions

1. Treat the live source code and fresh HTTP tests as authority; historical Phase 3 and Phase 4 review documents are not evidence of current runtime behavior.
2. Preserve typed engine operations and its equations. Do not add prediction, evidence scoring, uncertainty propagation, or client-selectable trust states.
3. Keep the current mass-fraction route unavailable because the server has no trusted diluent catalogue. A schema/registry interface is not a trusted record.
4. Classify malformed requests as 422, recognized unrepresentable calculations as 422, unavailable verified diluent data as 503, and unexpected application failures as generic 500.
5. Reject non-finite response values instead of normalizing them to null.
6. Preserve JSON decimal tokens until schema validation so a tiny nonzero input cannot silently become exact zero.
7. Keep `/health`'s historical minimal response; use `/api/health` for the versioned API health contract.
8. Document that `gas_basis_verified` in the engine echo is an internal calculation gate, while provenance remains `user_supplied` and verification remains `UNVERIFIED`.
9. Do not invent frontend origins, allow CORS wildcard, add frontend code, or implement Ollama. Browser origin/proxy configuration must be agreed with the UI developer.
10. Do not modify raw NASA files or populate the harmonized dataset. Do not commit or push.

## Defects corrected

- Removed global 422 handling for arbitrary `ValueError`/`TypeError`; unexpected backend failures now return generic 500.
- Added explicit mapping for known numeric finite-range failures to 422 `calculation_out_of_range`.
- Enforced strict JSON serialization with `allow_nan=False` at the API boundary.
- Rejected whitespace-only/padded `diluent_id` as an invalid request.
- Added OpenAPI error response models consistent with runtime error envelopes.
- Rewrote the current scientific API contract to remove proposal-only fields and request shapes.
- Added a Phase 4 documentation note on missing uncertainty estimates and the API 422/500/503 categories.
- Preserved JSON decimals through validation and rejected nonzero values that underflow binary64.
- Updated README's backend description to reflect the implemented API and unimplemented evidence/experiment routes.

## Tests added or expanded

`tests/test_atmospheric_api.py` now covers strict/extra/nested input validation, forged provenance, numeric and pressure boundaries, decimal underflow, finite-range errors, unit normalization, zero-reference comparisons, malformed JSON/content type, registry unavailability, typed-engine call routing, OpenAPI consistency, API version consistency, JSON serialization failure, and internal 500 behavior.

## Remaining risks and decisions

- There is no CORS middleware or Vite proxy; configure a narrow allowlist or same-origin proxy once the UI origin is agreed.
- No authentication, rate limiting, or deployment policy is defined; keep the service on a trusted development network until deployment controls are chosen.
- No source-record service, diluent catalogue, verified harmonized points, or uncertainty model exists.
- FastAPI/Pydantic were verified on the active Python 3.13 environment only; the full declared version range was not tested as a matrix.
- Frontend and AI routes/tools remain separate-team work. No frontend source, AI source, or dependency integration was changed.
