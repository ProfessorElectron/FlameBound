# Model Readiness Assessment

**Assessment date:** 2026-11-15. No predictive or inferential model was fit.

## Evidence state

The harmonised table contains **zero verified records** and therefore zero verified independent experiments. Source CSVs contain 263 candidate rows by current row-role rules; the BASS primary matrix adds nine unmatched keyed rows. These counts are not the number of independent experiments. There are no verified outcome labels or class counts, so class imbalance cannot be calculated. The 22/3,116 blank-cell count is only raw syntactic CSV missingness; it is not missingness over a harmonised feature set. Whole payload classes (SAFFIRE sensor/image data) are missing, and source tables use non-equivalent variables and grains. See `docs/data_audit_report.md` and `independent_audit_review.md` for source-specific findings.

## Analysis status

| Analysis | Status | Basis and safe boundary |
|---|---|---|
| Descriptive statistics | **READY WITH RESTRICTIONS** | Can describe source-table fields, missing tokens, and table-level nominal settings if labeled as source descriptions and stratified by investigation/source. No pooled physical summary or outcome rate is valid until row grain, units, repeated views, and definitions are verified. |
| Experimental coverage | **READY WITH RESTRICTIONS** | Repository/file availability and candidate-field presence can be mapped now. Coverage of the physical experiment domain is **NOT READY** because there are zero verified points and no validated common feature space. |
| Evidence similarity / Gower distance | **NOT READY** | Requires verified point-level variables, predeclared comparability strata, feature weights/ranges, missingness handling, and minimum compared-weight reporting. A distance is representation similarity, not prediction confidence. |
| Dimensionless parameter analysis | **NOT READY for experimental records; READY WITH RESTRICTIONS for formula/module design** | No verified row-level inputs or consistent gas/material properties. Definitions and input validation can be implemented with synthetic hand-checks, but no PSI point can be assigned a defensible Re/Gr/Da/etc. now. |
| Spread/extinction boundary estimation | **NOT SUPPORTED BY AVAILABLE DATA** | No verified outcome labels, independent point count, label counts, or common condition definitions. Do not estimate a boundary from candidate rows or qualitative study summaries. |
| Logistic regression or other predictive classification | **NOT READY** | Zero verified observations/outcomes, no estimable class balance, investigation confounding, no predictor overlap assessment, and no scientifically possible grouped validation. Python fit capability is irrelevant to evidence sufficiency. |
| Cross-investigation inference | **NOT READY** | Different apparatuses, sample geometry, flow conventions, oxygen representation, gravity labels, and outcome definitions. No five-investigation pooled inference is justified. |
| Lunar/partial-gravity prediction | **NOT SUPPORTED BY AVAILABLE DATA** | No relevant partial-gravity measurements. Microgravity and 1 g are distinct regimes, not endpoints for interpolation. No safety/certification claim is supported. |

## Statistical validity barriers

1. Independent experiment count is unknown; candidate rows may represent sample, condition, repeat, or summary records.
2. BASS has repeated year/matrix views; BASS-II has a 126-versus-129 count conflict and incomplete appendix crosswalk.
3. SAFFIRE outcomes and sensor readings are missing locally; current fields are mostly nominal setup, summary, or image references.
4. No verified outcome classes means event counts, imbalance, sensitivity, calibration, and discrimination are undefined.
5. Investigation and PI are likely confounders with fuel, apparatus, protocol, and measurement definitions. Random row splits would leak source-specific structure and cannot validate transportability.
6. Oxygen mole fraction and pO2 are algebraically dependent when total pressure is also included. Do not count them as independent predictors without a predeclared estimand and identifiability analysis.
7. Missingness is structured by investigation/file type, not a random uniform omission; complete-case analysis could select a different apparatus/substudy.

## Gate before any model

First establish row grain and test IDs; resolve the BASS crosswalk and BASS-II count; retrieve the missing payloads needed for outcome and sensor validation; define outcome labels using apparatus-specific source evidence; preserve gravity as categories; collect field-level provenance; double-review records. Then report per-investigation counts, duplicate/repeat structure, feature availability, outcome counts, and overlap before selecting an analysis. If entire investigations are held out, the number of groups may still be too small for reliable generalization estimates; document that limitation rather than substitute random row-level cross-validation.
