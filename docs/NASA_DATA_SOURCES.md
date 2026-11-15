# NASA Data Sources

## Primary source

Physical Sciences Informatics (PSI) is NASA's repository for physical-sciences investigation data, documentation, and related resources.

- [PSI investigations by research area](https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/)
- [NASA PSI investigation repository](https://psi.nasa.gov/physci/repo/data/investigations/)
- [NASA BASS investigation overview (PDF)](https://www.nasa.gov/wp-content/uploads/2025/07/burning-and-suppression-of-solids-bass.pdf)

## Initial scope

The planned solid-fuel candidates are BASS, BASS-II, and SAFFIRE-I, SAFFIRE-II, and SAFFIRE-III. Confirm exact investigation IDs, available files, test-level outcome labels, and gravity conditions in PSI before adding records. Do not assume every listed investigation contains comparable fields or machine-readable experimental tables.

## Files currently copied into the repository

The raw folders currently contain one experimental-table CSV and one original PSI metadata ZIP for each of PSI-26 (BASS), PSI-25 (BASS-II), PSI-98 (SAFFIRE-I), PSI-99 (SAFFIRE-II), and PSI-100 (SAFFIRE-III). The files were copied unchanged from the local Downloads folder. Their hashes and paths are recorded in `data/metadata/dataset_inventory.csv`; the source pages are recorded in `source_registry.csv`. They are marked `copied_unreviewed` and have not been harmonised into test-point rows.

The registry's `license_or_usage` field currently instructs reviewers to check the investigation page for applicable license and citation. It does not establish redistribution permission. Verify item-specific authorship, citation, license, and any embedded third-party material before publicly packaging a source file. See [third-party notices](../THIRD_PARTY_NOTICES.md) for the file-by-file inventory and unresolved rights status.

## Local organization

Store downloaded source material under `data/raw/nasa_psi/<INVESTIGATION>/` in the matching subfolder:

- `experimental_tables/` for tables containing test conditions or outcomes.
- `investigation_metadata/` for PSI metadata and investigation descriptions.
- `science_documents/` for papers, reports, and scientific summaries.
- `engineering_documents/` for apparatus and instrumentation documents.
- `raw_data/` for instrument files, images, videos, or other primary data.

Keep filenames intact where possible. Register each source in `data/metadata/source_registry.csv`; register each downloaded file in `dataset_inventory.csv`. Record retrieval date, source URL, file type, and checksum when feasible. Do not edit the source copy; put extracted or normalized content under `data/processed/` and log each transformation in `processing_log.csv`.

NASA source pages and the files themselves are authoritative for the investigation-specific meanings and units. When a value cannot be traced to a source location, leave it out of the harmonised table until it can be verified.
