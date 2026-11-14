# FlameBound Modelling Kickoff

This note turns the project blueprint into the first modelling work package. The first deliverable is the mathematical and physical framework in [mathematical_framework.md](mathematical_framework.md). After the team reviews its variables, equations, and assumptions, build an auditable map of what NASA has tested and how close a habitat scenario is to those tests. Fit a flammability boundary only after the test rows and outcome labels have been verified.

## What we are trying to answer

For a proposed atmosphere and flow condition, show which NASA solid-fuel combustion tests are relevant, which inputs lie outside tested conditions, and whether the available evidence supports estimating sustained flame spread. This is a research triage tool; it cannot certify a material or declare a habitat safe.

## Modelling sequence

1. **Freeze the row definition and units with the data owner.** One row is one experimental test point, not one paper or one investigation. Store source file, page/table/record, extraction method, and reviewer with each row.
2. **Build the evidence and coverage layer first.** Validate units and categorical vocabularies; show per-investigation ranges and evidence islands. Add a mixed-variable distance only after the feature schema and missing-value policy are agreed.
3. **Audit outcomes.** Count verified sustained-spread and extinction outcomes by investigation. Keep unknown, ambiguous, and unreported distinct from extinction.
4. **Go/no-go for a boundary model.** Use the blueprint's rough screen of at least 10 verified examples of each outcome per fitted predictor as a warning threshold, not a statistical guarantee. If the data fail it, deliver coverage and gaps without probabilities.
5. **Fit and validate a modest baseline if supported.** Start with a regularised logistic model and investigation-level holdout (leave one investigation out). Compare with a simple oxygen-only baseline. Report calibration and uncertainty, not only accuracy.
6. **Expose results to the UI and AI teammate through a stable, provenance-carrying output.** The AI may describe retrieved evidence and model outputs, but must label measured, modelled, and extrapolated results separately.

## First mathematical pieces

Atmosphere bookkeeping:

```text
pO2 = X_O2 * P
```

Here `X_O2` is oxygen mole fraction (0 to 1), `P` is total pressure, and `pO2` has the same pressure unit as `P`. Keep mole fraction, total pressure, and derived oxygen partial pressure as separate fields. They are not independent predictors in a small dataset: `pO2` is exactly their product, so do not put all three into one regression without a specific identifiability plan.

Coverage candidate from the blueprint:

```text
D_G(x, x_i) = sum_k w_k * delta_k(x, x_i)
d_ext(x)    = mean of the 3 smallest distances to eligible tested rows
```

For numeric feature `k`, `delta_k = abs(x_k - x_ik) / (max_k - min_k)` using a documented training/reference range. For categorical features, `delta_k` is 0 for a match and 1 for a mismatch. Missing values must be omitted from both numerator and denominator for that pair; also return the fraction of feature weight actually compared. If a numeric feature has zero range, it cannot distinguish rows and should not be divided by zero. Weights and eligible features must be fixed and reported. Calculate coverage separately by gravity and compatible fuel/geometry scope; a low distance across incompatible experiments is misleading.

Also report a convex-hull flag over the continuous query dimensions (initial candidate: `X_O2`, `ln(P)`, `ln(U)`) only when all required values exist and there are enough non-degenerate points. A hull flag and nearest-neighbour distance are coverage indicators, not probabilities of fire or safety.

Candidate boundary model, only after the data audit:

```text
logit Pr(spread_i = 1) = b0 + b1*X_O2 + b2*ln(U) + b3*ln(U)^2
                         + b4*ln(P) + fuel_class_effect + investigation_effect
```

This is a predictive empirical model, not a first-principles combustion solver. Confirm that velocity `U` is positive, has consistent units, and represents comparable flow direction/configuration before taking its logarithm or pooling rows. Do not interpolate between microgravity and 1 g or make partial-gravity predictions. If there are too few independent investigations, do not claim a reliable random-effects estimate; use investigation-held-out evaluation and report how much evidence supports pooling.

## Data needed from the team

For each test point, provide raw value, canonical value, unit, source/provenance, and confidence where available:

- Investigation ID and test/run ID; gravity category (`microgravity`, `1g`, or `unknown`).
- Outcome: sustained spread, extinction, blow-off, ignition failure, other, or unknown; keep the source's wording too.
- Fuel identity/class, material orientation, dimensions/thickness, and geometry.
- Oxygen mole fraction, total pressure, oxidizer/diluent composition, and temperature where reported.
- Flow speed, unit, direction/configuration (opposed, concurrent, stagnation, other), and measurement location if known.
- Spread rate and extinction threshold as separate measured quantities, each with units and source.
- Source document/page/table/figure or data-file and row index; extraction method; verifier; ambiguity notes.

Please send the challenge's official resource links, the first investigation files or inventory, and any existing extracted spreadsheet/CSV. Prioritise the three solid-fuel investigations the team selects. BASS/BASS-II and SAFFIRE are candidates from the blueprint, but the team must confirm exact scope and available records before treating them as the dataset. Gas-flame studies can give context but must not silently become solid-fuel training rows.

## My work package

1. Agree the schema, units, eligible rows, and missing-value rules with the data owner.
2. Produce a data audit: counts, ranges, missingness, label ambiguity, and investigation overlap.
3. Implement and document coverage distance and the out-of-domain flags.
4. At the data checkpoint, make a written model/no-model recommendation.
5. If supported, implement the baseline, investigation-held-out validation, and uncertainty summaries.
6. Publish a compact interface for the UI/AI teammates: input scenario, evidence grade/coverage diagnostics, supported outputs, limitations, and source IDs.

## Questions to settle before the first model code

- Which three investigations and which gravity folders are in scope for the first pass?
- What exact source label counts as sustained spread, and how are ambiguous outcomes handled?
- Which flow variable is comparable across investigations, and what does “zero/near-zero flow” mean in each apparatus?
- Will the data teammate provide one row per test point with source citations and units?
- Does the team accept a coverage-only result if the outcome data are too sparse?

The repository currently contains only its README, so there is no existing data schema or modelling implementation to preserve. This kickoff is a proposal for team review; the numerical model should follow verified data rather than assumptions in the blueprint.
