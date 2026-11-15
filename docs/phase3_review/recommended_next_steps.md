# Recommended Next Steps After Phase 3 Review

## 1. Agree the trust boundary with the backend owner

Build request schemas that accept an explicit `oxygen_mole_fraction`, positive pressure, supported pressure unit and literal absolute basis. For hypothetical user inputs, the backend sets origin/verification to user-supplied/UNVERIFIED. Do not accept client-provided `gas_basis_verified`, `MEASURED`, or `diluent_verified` as facts. Resolve experimental provenance on the server.

## 2. Implement API wrappers without copying equations

Add `/api/health`, `/api/atmosphere/oxygen-partial-pressure`, `/api/atmosphere/oxygen-mass-fraction`, and `/api/atmosphere/compare` routes that call the typed `calculate_*` functions. Map `ValueError`/`TypeError` to stable 422 errors with field names and no partial numeric result. Keep the legacy numeric functions out of Ollama's tool list.

Do not expose the mass-fraction route as successful until a server-controlled verified diluent catalog or verified composition record exists. Never default to nitrogen or air.

## 3. Add API-level tests

Test omitted fields, extra fields, invalid booleans/numbers, gauge pressure, unsupported/ambiguous units, zero/negative pressure, xO2 boundaries, untrusted verification flags, source lookup failures, exact response shape, warnings for zero-reference comparison, and serialization with `allow_nan=False`. Include request-level tests proving a client cannot promote a value to MEASURED by setting JSON fields.

## 4. Version and operationalize provenance

Before persisting API output, add a response schema/engine version and define a trusted source-record lookup contract. Keep source raw values, raw units, normalization method, source locator, review status, formula and assumptions in stored output. User-supplied hypothetical inputs must remain distinct from measured NASA rows.

## 5. Keep physics development within evidence limits

No atmospheric function predicts flame spread or extinction. Do not add lunar-gravity extrapolation or safety claims. Leave `data/processed/harmonised/test_points.csv` empty until the PSI rows and outcomes are verified. A later evidence-coverage API can report data presence/status without calling it model confidence.

## Validation status

At this review, 41 tests pass under bundled Python 3.12.14 with `unittest`; pytest is unavailable and no repository virtual environment was found. No external packages were installed. Raw NASA files and the empty harmonised dataset remain untouched. No commit or push was made.
