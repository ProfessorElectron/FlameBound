# Harmonisation Plan

**Status:** proposed and deliberately conservative. This is a field mapping plan, not an assertion that the investigation rows are comparable or already verified. No model fitting or physical-value conversion was performed.

## Row grain and output contract

The core table will have one row per independently identified experiment/run condition **only after** the source identifier, condition, outcome, and locator have been reviewed. Sample labels, image sets, time-indexed images, and apparatus/settings rows do not automatically become test points. Preserve source text and original row references alongside any normalized field.

`data/processed/harmonised/test_points.csv` currently contains only the header from `data/template/test_points_template.csv`. The per-investigation audit files preserve all experimental-table rows, including annotation rows, with source sheet/row locators and original cells in JSON. Candidate status does not imply verification.

The detailed 75-row source-field comparison, including exact original column names, units, statuses, source references, conversion rules, and decisions, is in `data/metadata/harmonisation_log.csv`.

## Variable comparison matrix

| Variable | BASS | BASS-II | SAFFIRE-I | SAFFIRE-II | SAFFIRE-III | Harmonisation decision |
|---|---|---|---|---|---|---|
| Test/run/sample identity | `As Run Test #`, `Test #`, `Sample #` | `PI`, `Test #`, `Sample #` | `Sample Number` S1/S2 | `Sample Number` 2-1..2-9 | `Sample Number` S1/S2 | Preserve all raw identifiers. BASS CSV composite keys match 121 main-matrix rows; nine more matrix keys remain. BASS-II needs the 129-versus-126 test-count reconciliation. Sample IDs do not by themselves establish an independent run. |
| Fuel/material | `Fuel Sample Material`; matrix `material` | `Fuel Sample Material` | `Material` | `Material` | `Material` | Populate `fuel_name_raw` only. Do not infer broad fuel classes or parse size from a material name. |
| Sample dimensions | Often embedded in material/configuration; planned dimensions in SRD | Embedded in material text, mixed units | Thickness/Length/Width headers say cm; orientation conflict | Thickness/Length/Width values mix mm/cm and text | Units are embedded in cells; orientation not reconciled | Use mm in standardized fields only for explicit scalar measurements with verified dimension orientation. Keep current values raw. |
| Oxygen | Matrix `O2 % by volume`, values such as 0.221 | Calibrated initial/final O2, vol% | `Percent O2`, approximate/range values | `Percent O2 (Note 1)`, approximate | No experimental-table column; sensors are described | Keep each raw field and initial/final distinction. BASS numeric scale is unresolved. Percent-to-fraction division by 100 is allowed only for an unambiguous scalar and verified volumetric basis. |
| Total pressure | Matrix `pressure, atm`; basis not stated | Not in the PSI table | No row value; sensor described | No row value; sensor described | No row value; sensor described | Standardize to kPa only after unit and absolute basis are verified. Do not fill study-level nominal pressure into rows. |
| Oxygen partial pressure | Not validly derivable | No paired row pressure | Pressure missing | Pressure missing | O2/pressure payloads missing | Keep `pO2` separate and derive only as `oxygen_mole_fraction × total_pressure_kpa` from verified same-row inputs. No current values qualify. |
| Flow speed | `Air display`/`Fan display`; strings may be sequences | `Air display`; NASA/TM p. 5 identifies cm/s, but strings may be sequences | `Air Flow (cm/s)`; nominal 20 | `Air Flow (cm/s)` | `Air Flow` cells include cm/s; nominal 30 | Preserve raw strings. Convert a single explicit cm/s value to m/s only after row segmentation and measurement meaning are checked. |
| Flow direction/configuration | Not structured in candidate CSV | In NASA/TM Appendix A, not in PSI-25 CSV | `Flow Direction` | `Flow Direction` | `Direction` | Keep source category and apparatus. Do not pool directions until each source's reference direction is documented. |
| Gravity | Microgravity investigation context; no row-level SAMS trace | ISS/MSG microgravity context; no run trace in collected files | Microgravity investigation context | `?-g` and `1-g` columns | Microgravity investigation context | Keep gravity categories distinct. Do not translate `?-g` to microgravity or infer numeric g from mission context. |
| Categorical outcome | Free-text as-run observations | Free-text observations in NASA/TM Appendix A, not PSI CSV | No outcome field | Mixed burn/spread lengths and notes | No outcome field | Retain `outcome_raw`. Use a controlled label only after a reviewer verifies the exact source meaning; otherwise `unknown` or `ambiguous`. |
| Spread measurement | Prose observations; no structured rate in PSI table | PI reports contain measurements; PSI CSV lacks a rate | No spread rate | `?-g Spread Length` and `1-g Spread Rate` are distinct | No spread rate in local table | Keep length, rate, burn length, damage length, flame growth, and steady-state claims separate. |
| Temperature | No row-level values | No row-level temperature field in PSI CSV | Thermocouples described; payload missing | Sensors described; payload missing | Thermocouples described; payload missing | No standardized temperature values until sensor payloads and measurement locations are obtained. |
| Combustion gases | O2/CO2 fields in BASS matrix; O2 scale ambiguous | Initial/final O2 and CO2 vol%, CO ppm | Sensors described; data workbook missing | Sensors described; data workbook missing | Sensors described; data workbook missing | Preserve as separate ancillary sensor observations, not as outcomes. Add a dedicated sidecar schema if these measurements are recovered. |
| Ignition | Igniter configuration in matrix; hot wire in SRD | Procedure describes hot-wire protocol; no PSI CSV value | Ignition Power (W), Ignition Time (s) | Ignition Power (W), Ignition Time (s) | Not in table | Keep method, power, and time separate; do not assume equivalent igniters across apparatuses. |
| Image/raw data | Data lists and run matrix; no raw payloads in local `raw_data/` | NASA/TM and summary tables; no raw payloads in local `raw_data/` | JPEG index workbook only | JPEG index workbook only | JPEG and RAW file index workbooks only | Treat manifests as indexes. Do not use file IDs, timestamps, or image acquisition settings as flame/oxygen/temperature measurements. |

## Unit and value rules

1. Preserve every source value and source unit unchanged in the audit layer.
2. Store O2 fraction in `[0, 1]` only after verifying a scalar volumetric-percent reading. Keep initial and final concentrations as separate source fields.
3. Store total pressure in kPa absolute only when the original basis is explicit. Reject gauge or unspecified basis.
4. Store flow speed in m/s only for a single explicit speed. Do not turn a sequence of fan/display setpoints into one value.
5. Convert dimensions to mm only after unit and length/width/orientation definitions agree with the supporting document.
6. Derive O2 partial pressure only from same-row, verified O2 fraction and absolute total pressure. Record the equation and both inputs; never replace either input with the derived value.
7. Keep raw outcome wording. A missing or unclear label is not extinction. “Brief ignition,” “flame spread,” “burned completely,” quenching extinction, self-extinction, and blow-off may not be interchangeable.
8. Retain exact duplicate/repeated rows with source location. Flag them for review; never deduplicate automatically.
9. Keep extra source measurements (ignition power/time, CO/CO2, burn time, camera IDs) in audit/raw sidecars until the team agrees on an extension to the core schema.

## Comparability decisions

- **BASS and BASS-II:** Potential comparisons should be limited to matched materials, geometry, apparatus, flow configuration, oxygen conditions, and measurement definitions. BASS-II includes multiple PI studies, geometries, and sequences; do not pool all rows by investigation ID alone.
- **SAFFIRE-I and SAFFIRE-III:** The documents describe large SIBAL samples and distinct nominal flow speeds (20 and 30 cm/s). They may support a protocol-level comparison after the dimension labels and payloads are reconciled. The current local files do not provide verified run-level outcome series.
- **SAFFIRE-II:** Keep separate from the large SIBAL SAFFIRE-I/III configuration. It uses a nine-sample card and several materials; its `?-g` fields are unresolved.
- **Across all five:** Do not fit a common boundary from broad investigation membership or similar-looking column names. Pressure, O2 representation, flow setting, outcome definitions, sample scale, and available source granularity differ.

## Promotion checklist for a row

A candidate can move into `test_points.csv` only when a reviewer records the exact source file/sheet/page/row, confirms the row's experimental unit and identifier, verifies each standardized field's unit and conversion, documents the outcome definition or leaves it `unknown`, preserves ambiguities, and completes a second-person check. Any unresolved item stays in the audit file and is not counted as a verified test point.
