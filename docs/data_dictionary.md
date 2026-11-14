# FlameBound Experimental Data Dictionary

**Status:** Proposed schema v0.1 for review with the NASA data collector. Do not treat this as a frozen team agreement until the collector confirms it against the source files.

## Row definition

One row represents one independently identified experimental test/run condition from one investigation. Repeated runs remain separate rows. Do not turn a plot point or time sample into an independent run unless the source identifies it as such. Keep raw source wording and values alongside normalized fields so every conversion and label can be reviewed.

Use `data/template/test_points_template.csv` as the header template. Leave numeric cells empty when no value is available; explain why in `missingness_notes` using `field:status` entries. Allowed statuses are `not_reported`, `not_extractable`, `ambiguous`, `not_applicable`, and `not_checked`. Empty is not zero. Do not put units in numeric cells.

## Fields

### Identity and provenance

| Field | Type | Meaning / rule |
|---|---|---|
| `record_id` | string | Stable unique ID for this dataset row, e.g. `BASS_run_001`; never reuse. |
| `investigation_id` | string | NASA PSI investigation name or identifier as recorded in the source. |
| `run_id_raw` | string | Run, test, sample, or experiment ID exactly as the source gives it. |
| `source_title` | string | Report, paper, PSI file, or experiment-table title. |
| `source_uri` | string | Source URL or repository-relative file path. |
| `source_locator` | string | Page, section, table, figure, data-file row, or time interval supporting this record. |
| `source_version_or_date` | string | Version, publication date, or retrieval date when available. |
| `extraction_method` | enum | `manual`, `table_extraction`, `text_extraction`, `instrument_file`, or `other`; explain `other` in notes. |
| `extracted_by` | string | Person or process that created the row. |
| `verified_by` | string | Second reviewer, or blank until checked. |
| `verification_status` | enum | `unreviewed`, `verified`, `disputed`; `verified` means values and labels were checked against the cited source. |
| `source_notes` | string | Short verbatim context or notes needed to understand the row; use quotation marks for exact source wording. |

### Experimental conditions

| Field | Type / unit | Meaning / rule |
|---|---|---|
| `gravity_category` | enum | `microgravity`, `1g`, `other_reported`, `unknown`; do not encode lunar/partial gravity unless explicitly measured and sourced. |
| `gravity_raw` | string | Exact gravity description from the source. |
| `fuel_name_raw` | string | Material/fuel name as reported. |
| `fuel_class` | string | Harmonized class only when justified (e.g. paper, fabric, polymer); preserve raw name too. |
| `sample_geometry` | string | Shape/configuration as reported (e.g. flat strip, cylindrical); avoid guessing. |
| `sample_orientation` | string | Orientation relative to flow or gravity if reported. |
| `sample_length_mm` | number, mm | Measured length; convert to mm and retain original in notes if needed. |
| `sample_width_mm` | number, mm | Measured width. |
| `sample_thickness_mm` | number, mm | Measured thickness. |
| `oxygen_mole_fraction` | number, fraction | Mole fraction on `[0,1]`; convert a reported percentage by dividing by 100. |
| `oxygen_fraction_raw` | string | Original value and representation, e.g. `30 vol%`; retain source basis if stated. |
| `total_pressure_kpa` | number, kPa absolute | Normalized absolute total pressure. Do not use gauge pressure without conversion and documentation. |
| `total_pressure_raw` | string | Original pressure value and unit. |
| `oxidizer_composition_raw` | string | Full oxidizer/diluent composition as reported, if available. |
| `ambient_temperature_k` | number, K | Initial ambient/fuel temperature where the source defines it. |
| `flow_speed_m_s` | number, m/s | Normalized flow speed at the stated reference location. |
| `flow_speed_raw` | string | Original flow value and unit. |
| `flow_direction` | enum/string | `opposed`, `concurrent`, `quiescent`, `crossflow`, `other_reported`, `unknown`; preserve source wording in `flow_direction_raw`. |
| `flow_direction_raw` | string | Exact source description, including apparatus reference if useful. |
| `ignition_method` | string | Ignition procedure/device, if reported. |

### Outcomes and measurements

| Field | Type / unit | Meaning / rule |
|---|---|---|
| `outcome_label` | enum | `sustained_spread`, `extinction`, `blow_off`, `ignition_failure`, `other`, `ambiguous`, `unknown`. Only map source language when its meaning is clear; otherwise use `ambiguous` and preserve its wording. |
| `outcome_raw` | string | Exact outcome wording or concise source description. |
| `spread_rate_m_s` | number, m/s | Reported spread rate normalized to m/s. Leave blank when not measured/reported; never infer from a plot without recording method. |
| `spread_rate_raw` | string | Original value, unit, and measurement description. |
| `flame_length_mm` | number, mm | Reported flame length with a consistent definition; preserve original measurement description. |
| `flame_length_raw` | string | Original value, unit, and definition/notes. |
| `extinction_limit_raw` | string | Reported limiting condition/value and unit; do not merge unlike limit definitions. |
| `measurement_uncertainty_raw` | string | Reported uncertainty, error bars, or instrument precision with units/method. |

### Quality and derived values

| Field | Type | Meaning / rule |
|---|---|---|
| `extraction_confidence` | enum | `high`, `medium`, `low`; confidence in transcription/mapping, not a probability that the physical result is correct. |
| `missingness_notes` | string | Semicolon-separated `field:status` entries for important missing fields, e.g. `flow_speed_m_s:not_reported; sample_thickness_mm:ambiguous`. |
| `derived_oxygen_partial_pressure_kpa` | number, kPa | Optional derived value `oxygen_mole_fraction * total_pressure_kpa`; calculate in code, never transcribe as an independent measurement. |
| `derived_value_notes` | string | Formula/version or reason a derived value is present. Keep source measurements unchanged. |
| `row_notes` | string | Other caveats, conflicts, or interpretation notes. |

## Controlled labels and normalization rules

- Preserve the source wording in every `*_raw` field. Normalization must not overwrite raw evidence.
- Store mole fractions from 0 to 1; store pressures as absolute kPa; store speed as m/s; store dimensions as mm; store temperature as K.
- Only convert units when the source unit is clear. Record unusual conversions in `row_notes` or `derived_value_notes`.
- `unknown` means the source does not establish a value or label. `ambiguous` means evidence exists but does not map cleanly to a category. Neither means extinction.
- Keep flow direction/configuration and investigation identity in any coverage/model row. A numerical match across different apparatuses does not prove physical comparability.
- `derived_oxygen_partial_pressure_kpa` is exactly dependent on oxygen fraction and total pressure. Do not treat all three as independent predictors without a specific statistical reason.
- Do not add derived Damköhler, Spalding, Reynolds, or Grashof values until required inputs, definitions, and validity conditions are recorded in the mathematical framework.

## Before calling the schema agreed

The data collector should confirm that the source formats can support one row per run, which IDs identify runs, the label mapping for outcomes, and whether pressure/flow definitions are comparable across the first investigations. If any field is not available, keep it optional and document the gap rather than inventing a value. A small sample of rows should be double-reviewed before bulk extraction.
