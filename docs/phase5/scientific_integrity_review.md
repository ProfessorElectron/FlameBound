# Phase 5 Scientific Integrity Review

## Available calculations

The backend exposes deterministic calculations for user-entered atmospheric values:

- Oxygen partial pressure through Dalton's law, `pO2 = X_O2 * P_total`, after conversion of an explicitly absolute pressure to kPa.
- Atmospheric comparison through the typed engine, with scenario/reference values, scenario-minus-reference differences, relative differences where defined, and warnings for zero reference values.
- The binary oxygen mass-fraction endpoint is present in the route contract but cannot return a calculation until a trusted server-side diluent catalogue exists.

Routes call the existing typed functions. They do not reproduce equations or expose legacy numeric helpers.

## Input status and source evidence

All currently calculable values come directly from the HTTP caller. The backend labels inputs `USER_SUPPLIED` and `UNVERIFIED`, keeps units and absolute pressure explicit, and rejects client-provided verification/provenance fields. A result status of `DERIVED` means the engine derived a quantity from submitted inputs; it does not mean those inputs are verified experimental data.

The backend has no NASA source-record resolution flow, no trusted source registry, and no measured-input endpoint. No submitted number can become experimental evidence because it matches an apparent source value. No diluent or mixture composition is inferred from its identifier.

## What the backend cannot establish

- The current harmonized test-point file has zero verified rows. Inventory counts, candidate file rows, and unreviewed values are not experimental test-point counts.
- No verified record search, coverage calculation, similarity analysis, or source-based atmospheric comparison is exposed over HTTP.
- No flame-spread, extinction, ignition, combustion-equivalence, or operational fire-risk prediction is available.
- No lunar or Martian partial-gravity interpolation/extrapolation is implemented.
- No measurement uncertainty or uncertainty propagation is returned. Numeric precision describes floating-point output, not experimental confidence.
- The engine's idealized Dalton-law treatment does not calculate real-gas fugacity or combustion response.
- The mass-fraction operation is limited to O2 plus one explicitly verified named diluent. A multicomponent atmosphere cannot be represented through this route.
- No fire-safety, material qualification, habitat-safety, or certification determination can be made.

Zero verified harmonized rows prevent defensible training or validation of predictive models. The API must remain a deterministic calculator until independently verified source records and a separate model feasibility/validation review justify more.

## Project boundaries retained

Phase 5 did not populate harmonized data, alter experimental outcomes, introduce source records, assume air/nitrogen, fit a model, mix gaseous-fuel outcomes into solid-fuel outcomes, use CFI-G values as solid-fuel fire bounds, or extrapolate to partial gravity. Raw NASA source files were not modified. Equal pO2 does not imply equivalent combustion.
