# Evidence Assessment

**As of 2026-11-15. No predictive fitting was done.** Counts distinguish source-table rows from verified experimental test points.

## 1. Verified test points by investigation

| Investigation | Verified test points |
|---|---:|
| BASS (PSI-26) | 0 |
| BASS-II (PSI-25) | 0 |
| SAFFIRE-I (PSI-98) | 0 |
| SAFFIRE-II (PSI-99) | 0 |
| SAFFIRE-III (PSI-100) | 0 |

A zero here means no row has yet passed the project rule: independently identified test/run, traceable conditions, interpretable outcome evidence, units, and source locator reviewed. It does **not** mean NASA performed zero tests.

## 2. Unresolved candidates

The five primary experimental CSVs contain 263 candidate rows: BASS 121, BASS-II 129, SAFFIRE-I 2, SAFFIRE-II 9, SAFFIRE-III 2. The BASS primary as-run matrix has 130 keyed rows; 121 crosswalk to the PSI CSV and nine do not. Therefore **272 candidate source rows remain unresolved** when the extra BASS matrix rows are included. BASS year sheets are alternate views and are not added to this count. SAFFIRE F1/F2 and explanatory-note rows are not candidate test rows.

NASA/TM-20210011385 reports 126 BASS-II tests while the PSI CSV has 129 rows and 129 distinct Test # values. Reconcile this discrepancy before calling those rows verified tests.

## 3. Physical variables available

- **Identifiers/material:** Raw identifiers and material names are available in every experimental CSV. They do not always establish a run-level unit or comparable fuel class.
- **Sample properties:** BASS and BASS-II often encode dimensions/configuration in material strings or matrix notes. SAFFIRE tables expose dimensions, but SAFFIRE-I and SAFFIRE-III length/width labels conflict with narrative descriptions; SAFFIRE-II has missing and malformed entries.
- **Oxygen:** BASS-II has calibrated initial/final O2 in vol%. SAFFIRE-I/II have approximate percent values. BASS's as-run matrix header says `% by volume`, but values include 0.221, leaving scale unresolved. SAFFIRE-III's table lacks O2 values; PSI metadata says sensor measurements exist in separate files that are not downloaded.
- **Pressure:** BASS matrix has pressure in atm but does not establish the basis. Other tables lack row-level pressure values. SAFFIRE metadata describes pressure sensors, but payloads are absent.
- **Flow:** BASS and BASS-II matrix displays often contain sequences rather than a single speed. BASS-II documentation defines its airspeed display in cm/s. SAFFIRE tables give nominal flow settings (20 cm/s for SAFFIRE-I/II entries and 30 cm/s for SAFFIRE-III) but not the full run-resolved flow series.
- **Direction/configuration:** Present in the SAFFIRE CSVs, but the direction reference is not fully defined in the collected documents. BASS-II's NASA report contains flow type in PI-specific matrices but it is not in the PSI CSV. BASS's primary CSV lacks a structured row-level direction.
- **Outcomes/spread:** BASS and BASS-II include narrative test observations in richer source matrices/reports, but those have not been row-crosswalked and reviewed against controlled label definitions. SAFFIRE-II has mixed burn/spread fields, including unresolved `?-g` variables. SAFFIRE-I/III local tables do not provide outcomes or spread-rate time series.
- **Temperature, acceleration, and sensor signals:** Sources describe thermocouples, gas sensors, and acceleration measurements, but the corresponding run-level data payloads are not in the local `raw_data/` folders.

## 4. Consistency of definitions and units

Some source-level units are explicit: BASS-II O2/CO2 volume percent and CO ppm, BASS-II airspeed display in cm/s, and SAFFIRE air-flow settings in cm/s. However, no single core physical variable is both consistently defined **and** present as a verified scalar across all five investigations. BASS oxygen scale and pressure basis are unresolved; SAFFIRE dimension labels and `?-g` meaning are unresolved; BASS/BASS-II flow fields can be sequences; outcomes are not consistently coded.

## 5. Missingness

Among the 263 candidate rows in the five primary CSVs, 22 of 3,116 source cells are blank (0.706%): BASS-II 19, SAFFIRE-II 3, and the other CSV candidate rows 0. This is a raw blank-cell rate only. It excludes semantic missing tokens, ambiguous strings, absent columns, missing run-level payloads, and the BASS workbook. It cannot be interpreted as missingness of a harmonized physical field set. In particular, a field absent from an entire table is not counted as a blank cell.

## 6. Scientific comparability

- BASS and BASS-II can only be compared within matched fuel, geometry, flow direction, atmosphere, and apparatus definitions. Both investigations contain heterogeneous substudies.
- SAFFIRE-I and SAFFIRE-III have a potentially useful protocol-level SIBAL comparison (nominal 20 versus 30 cm/s), but currently lack verified outcome/sensor series and need dimension-label reconciliation.
- SAFFIRE-II's nine-material sample card and unresolved gravity fields should remain separate from the large SIBAL SAFFIRE-I/III configuration.
- No pooled five-investigation analysis is currently justified.

## 7. Statistical modelling readiness

**Not ready.** There are zero verified harmonized points, no consistent outcome label, unresolved BASS-II count/crosswalk discrepancies, and absent SAFFIRE sensor payloads. Row counts alone are not a basis for a statistical model. No fire-safety probability or classification should be exposed.

## 8. First analysis if predictive modelling remains unsupported

First reconcile the 129 BASS-II PSI rows against the 126-test NASA summary and PI-specific Appendix A tables, then double-review a small sample of row-to-source mappings and outcome wording. In parallel, resolve the BASS 121-to-130 matrix crosswalk and the nine additional matrix rows. Once any records are verified, the first analysis should be an **evidence/coverage audit and within-configuration descriptive summary** (O2, measured flow, fuel/geometry, and source-supported outcome counts) stratified by PI/investigation and gravity. Do not calculate cross-study probabilities until outcome and measurement comparability are demonstrated.
