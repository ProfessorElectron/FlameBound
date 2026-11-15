# NASA PSI Data Audit Report

**Audit date:** 2026-11-15
**Scope:** PSI-26 BASS, PSI-25 BASS-II, PSI-98 SAFFIRE-I, PSI-99 SAFFIRE-II, and PSI-100 SAFFIRE-III.
**Decision:** No predictive model was fit. No record was placed in the verified harmonised table.

## Status terms

- **VERIFIED** means the source file explicitly supports the stated field or study-level fact. It does not mean a row has passed the full test-point review.
- **DERIVED** means a value can be calculated from verified inputs with a documented equation. No physical values were derived in this audit.
- **INFERRED** means a plausible interpretation not established by the collected source. Inferences are not treated as facts.
- **UNVERIFIED** means the source contains a value or label, but its meaning, unit, crosswalk, or outcome mapping is unresolved.
- **MISSING** means the collected row-level files do not provide the field or its payload.

## Repository-wide findings

The raw tree contains **54 non-placeholder files**. All 54 are represented in `data/metadata/dataset_inventory.csv` and `data/metadata/source_registry.csv`; three PSI-25 documents merged by a teammate were missing from those registries and have now been added. File-level structure and extraction status are recorded in `data/processed/audit/source_file_review.csv`.

The `raw_data/` folder in each of the five investigation directories contains only `.gitkeep`. There are no downloaded instrument logs, image payloads, video payloads, or SAFFIRE sensor-data workbooks. The SAFFIRE `MergeResult` workbooks are **file indexes**: they contain timestamps, file IDs/names, file sizes, and receive/corruption status. They do not contain the referenced images or the physical sensor time series. This matches the SAFFIRE Data Organization Documents, which say sensor workbooks and original image archives are attached to separate PSI experiment-data records.

The BASS local-only file `BASS Test Matrix 050213.xlsx` was recorded by structure only (one sheet, 66 rows by 25 columns). The workbook was not fully content-reviewed, and no cell contents were exported, because it had already been flagged as containing credential-like content. Only its structure and the prior local-review flag informed this audit. It remains ignored and local. This is the one experimental-table file not content-audited.

The audit exports retain source row, sheet, original headers, and raw values. Duplicate or repeated source views are flagged and preserved; no rows are silently merged. **Candidate row counts below are not verified test-point counts.** A candidate row is not promoted until its experimental unit, outcome, and source crosswalk are clear.

### Audit files

- Per-investigation row audits: `data/processed/audit/bass_audit.csv`, `bass_ii_audit.csv`, `saffire_i_audit.csv`, `saffire_ii_audit.csv`, and `saffire_iii_audit.csv`.
- File-by-file review record: `data/processed/audit/source_file_review.csv`.
- Harmonised output: `data/processed/harmonised/test_points.csv` uses the existing template header and currently has **zero data rows**.
- Field crosswalk: `data/metadata/harmonisation_log.csv`.
- Processing provenance: `data/metadata/processing_log.csv`.

## BASS — PSI-26

### Files inspected

The folder contains 24 engineering documents, three experimental-table files, two investigation-metadata files, and two science documents. The searchable files reviewed for definitions include `DLD_BASS.pdf`, `SRD_BASS.pdf`, `BASS ERD.pptx`, `US National Meeting-070HE-0218-Final.docx`, and `SLICE ED-04`, `SLICE ED-05`, and `SLICE IP-A SRDR` PDFs. The 23 engineering PDFs were all checked for extractable text: 16 returned no text, four returned only 23–48 characters, and the three SLICE PDFs returned searchable text. The image-only/low-text drawings were not semantically verified from OCR or visual review. `BASS Test Matrix 050213.xlsx` is excluded as described above.

### Tables and candidate rows

`PSI-26_Experimental table_BASS.csv` has 122 data rows and six columns: `Date`, `GMT`, `As Run Test #`, `Test #`, `Sample #`, and `Fuel Sample Material`. One row is a `SOOT Cleaning` annotation with no test identifiers. The other 121 rows have run/test/sample identifiers and are candidate records. There are no exact duplicate full rows in this CSV.

`BASS test matrix.xlsx` has five sheets. The primary `as run matrix` sheet is 134 rows by 30 columns, with a three-row title/header area and 130 nonblank ID-bearing body rows. Its fields include run/test/sample identifiers, material, fan and air displays, radiometer settings, oxygen, pressure, CO2, and free-text `Test Observations and Anomalies`. The `2012` and `2013` sheets are alternate/year views (82 and 49 nonblank body rows); `Data without TP` and `TP without Data` are data-availability reconciliation lists, not independent test matrices. The PSI CSV's 121 composite identifier keys all match the primary matrix. Nine additional composite keys in the primary matrix have no matching PSI CSV row. The year sheets are preserved as source views rather than added to test counts.

### Column meaning, units, and outcome

- **VERIFIED:** The BASS Science Requirements Document (SRD), pp. 4–5, describes the fan-produced co-flow, anemometer, fuel shapes, and candidate materials. The SRD pp. 7–9 describes instrumentation, co-flow velocity requirements, hot-wire ignition, and oxygen checks. The SRD p. 10 test matrix is a *planned* matrix, not a count of completed runs. `DLD_BASS.pdf`, p. 1, says PSI organizes BASS data into BASS_2012 and BASS_2013 data records and image/video collections.
- **UNVERIFIED:** The as-run workbook's `O2 % by volume` header is paired with values such as `0.221`. The source does not resolve whether these are fractions or percent values; they are not converted. The workbook's `pressure, atm` field does not state pressure basis, so it is not converted to absolute kPa. `Air display` and `Fan display` contain sequences and display settings; a run-specific calibration and segmentation are needed before assigning a single flow speed. The free-text observations contain useful descriptions, but there is no reviewed mapping from each phrase to the project's controlled outcome labels.
- **MISSING:** No SAMS acceleration trace, raw video/image, or time-series measurement file is present in `raw_data/`.

The 2013 combustion paper in `US National Meeting-070HE-0218-Final.docx` describes opposed and concurrent SIBAL flame behavior in its abstract and experimental/results sections. It supports study-level context, but the collected paper does not by itself map those aggregate findings to every row in the PSI table.

### Candidate and verified counts

- Candidate rows in PSI CSV: **121**; annotation rows: **1**.
- ID-bearing rows in primary as-run matrix: **130**, including the 121 CSV matches and **9 unmatched matrix rows**.
- Verified outcome-bearing test points in the harmonised table: **0**. The row-level oxygen scale, pressure basis, flow representation, and outcome mappings are not resolved.

### Limitations

BASS includes multiple geometries and material configurations. Free-text notes, planned test-matrix values, and actual as-run values must not be mixed. The local-only workbook is not available for scientific review or version control. Engineering drawings without usable text may contain additional details that remain unverified.

## BASS-II — PSI-25

### Files inspected

The folder contains `PSI-25_Experimental table_BASS-II.csv`, the PSI metadata archive, `BASS-2 Engineering Requirements.pptx`, `BASS-II Procedure.docx`, and NASA/TM-20210011385. The procedure was reviewed for the repeated test sequence and fan calibration steps (notably steps 9.6–9.11). The NASA technical memorandum was text-extracted and the experiment description and Appendix A test matrices reviewed.

### Table and candidate rows

The CSV has **129 data rows**, 17 columns, and 129 distinct `Test #` values. Columns are `PI`, `Test #`, `Date`, `GMT`, `Sample #`, `Fuel Sample Material`, `Flow restrictor`, `Fan display`, `Air display`, `Radiometer gain`, `Total Frames Shot`, calibrated initial/final O2 (% by volume), initial/final CO2 (% by volume), and initial/final CO (ppm). There are no exact duplicate full rows. PI group counts in the CSV are Bhattacharjee 22, Ferkul 4, Fernandez-Pello 27, Miller 20, Olson 27, and T’ien 29.

### Definitions and discrepancies

- **VERIFIED:** NASA/TM-20210011385, printed pp. 3–6, describes ISS/MSG testing, the variables, sample geometries, instrument setup, the airspeed transducer, and gas sensors. Printed p. 5 says the air-velocity transducer display is in cm/s and the fan-voltage display is 10× volts. Printed p. 6 gives sensor ranges/resolution and the O2, CO2, and CO measurements. Appendix A, printed pp. 103–113, contains PI-specific test matrices and free-text observations/anomalies.
- **UNVERIFIED:** The `Air display` and `Fan display` CSV cells can contain multiple values or narrative sequences, not one scalar condition. No row-level flow-series segmentation was done. The CSV does not include the Appendix A flow type or observations, and the PI/Test crosswalk to those appendix rows has not been completed.
- **COUNT DISCREPANCY:** The NASA summary, printed p. 3, reports 126 tests conducted; the PSI CSV has 129 rows and 129 distinct test labels. These numbers are retained separately pending reconciliation. The same summary text says five PIs, while the report contains six Appendix A PI matrices and the CSV has six PI groups. This internal discrepancy also needs source-owner review.
- **MISSING:** Pressure and ambient temperature are not row fields in the PSI CSV. Do not assign a study-level nominal pressure to each row.

### Candidate and verified counts

- Candidate CSV rows: **129**.
- Verified outcome-bearing test points in the harmonised table: **0**. The NASA report contains richer outcomes, but the full row-by-row crosswalk, duplicate/repeat interpretation, and test-count reconciliation remain unfinished.

### Limitations

BASS-II contains distinct PI studies, geometries, and flow configurations. The 129 rows cannot be treated as a single interchangeable sample until the PI-specific table crosswalk and apparatus/variable definitions are resolved.

## SAFFIRE-I — PSI-98

### Files inspected

The folder contains the PSI experimental CSV, PSI metadata archive, `SAFFIRE-I and SAFFIRE-III DoD.docx`, `SAFFIRE-I Image Directory Nomenclature.pdf`, `SAFFIRE-I Operations.pdf`, and `SAFFIRE-1_MergeResult-jpeg_Update_Final_v2.xlsx`. There is no local science document or payload in `raw_data/`.

### Table and candidate rows

The CSV has four body rows and 13 columns. Two rows identify samples S1 and S2; two F1/F2 camera rows describe pre/post-flow visualization and are annotations, not sample test points. Sample fields include material, thickness/length/width (cm), air flow (cm/s), O2 percent, ignition power/time, burn time, direction, and camera references. The two candidate rows have no blank cells, but several values are approximate or ranges.

### Definitions and ambiguities

- **VERIFIED:** The PSI-98 metadata archive's `Comment[Approach]` describes SIBAL composition (75% cotton/25% fiberglass by weight), approximate sample size, nominal 20 cm/s airflow, two cameras, and instrument types. The DoD opening paragraphs and Table 1 distinguish sample and pre/post-flow camera records. `SAFFIRE-I Operations.pdf`, p. 1, describes mission operations, not sample-level outcomes.
- **UNVERIFIED:** The CSV labels `Sample Length = 40.6 cm` and `Sample Width = 94 cm`, while the DoD and metadata describe an approximate 0.4 m by 0.94 m sample with the long dimension described as tall. The dimension labels conflict; retain the original values and do not swap them. O2 values are ranges/approximations, not single verified values. The documents do not define the row-level meaning of burn time as a flame-spread outcome.
- **MISSING:** No pressure, spread-rate series, temperature readings, acceleration trace, or underlying camera/sensor files are present locally.

### Candidate and verified counts

- Candidate sample rows: **2**; F1/F2 annotation rows: **2**.
- Verified outcome-bearing test points: **0**.

## SAFFIRE-II — PSI-99

### Files inspected

The folder contains the PSI experimental CSV, PSI metadata archive, `SAFFIRE-II DoD.docx`, `SAFFIRE-II_Image_Directory_Nomenclature_v3.0.pdf`, and `SAFFIRE-II_MergeResult-jpeg_v5_Final.xlsx`. Engineering documents, science documents, and raw payloads are absent from the local folder.

### Table and candidate rows

The CSV has 15 body rows and 17 columns. Nine IDs (`2-1` to `2-9`) are sample candidates. The remaining six rows are F1/F2 image annotations and explanatory notes. Candidate columns include material, thickness/length/width, air flow, O2, ignition power/time, burn time, direction, `?-g` burn/spread length, `1-g` burn length/spread rate, and camera references. Among the nine candidate rows, Material is blank in two and Camera 1 is blank in one. No exact duplicate full rows were found.

### Definitions and ambiguities

- **VERIFIED:** `SAFFIRE-II DoD.docx`, opening paragraphs and Table 1, describes a nine-sample card and lists the sample/data organization. The PSI-99 metadata archive's `Comment[Approach]` describes materials, nominal 20 or 30 cm/s flow depending on sample/configuration, and instrumentation. Note 1 in the experimental CSV says its O2 estimate was derived from measured CO2 production and referenced to initial ISS O2; Notes 2–4 describe PMMA/Nomex behavior and the table's damage/spread observations.
- **UNVERIFIED:** The table's `?-g` fields are not defined by the collected documents; do not rename them microgravity. Keep them distinct from the explicit `1-g` comparator. Thickness entries mix units and include malformed `037 mm`; no decimal is inserted. Missing material/camera values remain missing. Burn length, spread length, spread rate, damage length, and outcome are not interchangeable.
- **MISSING:** The JPEG workbook is an index, not image payload or sensor data. No per-run pressure, temperature, acceleration, or full gas-sensor data are present locally.

### Candidate and verified counts

- Candidate sample rows: **9**; annotations/notes: **6**.
- Verified outcome-bearing test points: **0**.

## SAFFIRE-III — PSI-100

### Files inspected

The folder contains the PSI experimental CSV, PSI metadata archive, `SAFFIRE-I and SAFFIRE-III DoD.docx`, `SAFFIRE-III Image Directory Nomenclature_v3.0.pdf`, `SAFFIRE-III Operations.pdf`, and JPEG/RAW `MergeResult` workbooks. There is no local science document or raw sensor/image payload in `raw_data/`.

### Table and candidate rows

The CSV has two candidate sample rows, S1 and S2, with nine columns: sample number, material, thickness, length, width, air flow, direction, camera 1, and camera 2. Both are SIBAL fabric; the raw cells report .33 cm thickness, 94 cm length, 40.6 cm width, 30 cm/s airflow, and concurrent/opposed directions. No blanks or exact duplicate rows were found.

### Definitions and ambiguities

- **VERIFIED:** The PSI-100 metadata archive's `Comment[Approach]` and the combined DoD's opening paragraphs describe the large-scale SIBAL sample, nominal 30 cm/s airflow, two cameras, and sensors. The DoD says raw sensor data are provided in separate Excel files within PSI experiment-data records. `SAFFIRE-III Operations.pdf`, p. 1, describes flight operations and downlink, not flame outcomes. The image-directory guide, p. 1, distinguishes camera RAW/JPEG processing products; it also says the original camera data are archived separately.
- **UNVERIFIED:** Units are embedded in the CSV cells, and the length/width labels are not reconciled to the DoD's approximate physical orientation. The nominal 30 cm/s setting is not a time-resolved flow measurement.
- **MISSING:** The JPEG/RAW workbooks contain file-index entries and image-acquisition metadata, not the raw image or sensor payloads. O2, pressure, temperature, flow-sensor, and flame-outcome time series are unavailable locally.

### Candidate and verified counts

- Candidate sample rows: **2**.
- Verified outcome-bearing test points: **0**.

## Counts and missingness summary

| Investigation | Candidate rows in experimental CSV | Additional keyed source rows | Annotation/note rows in CSV | Verified harmonised test points |
|---|---:|---:|---:|---:|
| BASS | 121 | 9 unmatched rows in primary as-run matrix | 1 | 0 |
| BASS-II | 129 | 0 | 0 | 0 |
| SAFFIRE-I | 2 | 0 | 2 | 0 |
| SAFFIRE-II | 9 | 0 | 6 | 0 |
| SAFFIRE-III | 2 | 0 | 0 | 0 |
| **Total** | **263** | **9** | **9** | **0** |

There are **272 unresolved candidate source rows** when the nine additional BASS matrix rows are included. This is a count of rows needing review, **not a verified experiment/test count**. The NASA BASS-II summary's reported 126 tests is an additional aggregate that does not match the 129 CSV rows; it is not silently substituted for the candidate count.

Across the 263 candidate rows in the five primary CSVs, there are 22 blank cells among 3,116 source cells (**0.706%**): 19 in BASS-II and three in SAFFIRE-II. This is only a syntactic blank-cell rate for the source-table rows. It does not count `n/a`, `none`, ranges, ambiguous strings, fields absent from an entire table, or missing physical payloads; it is **not** the proportion of required harmonised fields missing.

No exact duplicate full rows were found within the five primary CSVs. Repeated BASS records across CSV, main matrix, and year-view sheets remain separately represented and are flagged in the audit CSVs.

## Unresolved questions that block verified rows

1. What exact relationship among BASS `As Run Test #`, `Test #`, and `Sample #` defines one experimental run, and what are the nine additional matrix records?
2. Why does the BASS-II PSI table contain 129 distinct Test # rows while NASA/TM-20210011385 reports 126 tests? Can the PI/Test IDs be reconciled against Appendix A and the merged source records?
3. Does the BASS `O2 % by volume` field store percent values or fractions, and is `pressure, atm` absolute pressure?
4. Which BASS display values are calibrated co-flow velocity, and how should multi-setting strings be split into test conditions?
5. What is the documented gravity meaning of SAFFIRE-II `?-g`, and how were its `1-g` comparator measurements defined?
6. What experiment-level outcome definitions are approved for sustained spread, extinction, blow-off, and ignition failure in each apparatus?
7. Can the team retrieve the missing SAFFIRE sensor workbooks and original image/raw payloads, and BASS/BASS-II run-level video/acceleration data?
8. Can a second reviewer verify a sample of row-to-document mappings before any row is marked `verified`?
