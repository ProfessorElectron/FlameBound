# Third-party notices, provenance, and compliance audit

**Audit date:** 2026-11-15

**Branch reviewed:** `codex/flamebound-phase0`

**Scope:** repository manifests, lockfile metadata, locally installed package license metadata, source inventory, frontend assets, scientific references, and public official NASA Space Apps pages. This is a provenance inventory, not legal advice or a legal clearance.

## Status key

- **VERIFIED** — supported by a repository record, installed package license text, or the cited official source.
- **NEEDS ATTRIBUTION** — cite the named source/author in the submission or preserve its license notice.
- **NEEDS MANUAL REVIEW** — a person on the team must confirm ownership, terms, or required disclosures.
- **UNKNOWN** — repository evidence does not establish the answer.
- **NOT APPLICABLE** — no bundled asset/source of that type was found in the scanned project tree.

## FlameBound source code and project license

| Material | Path/source | Status | Finding/action |
|---|---|---|---|
| Project source code | Root `LICENSE` | NEEDS MANUAL REVIEW | The file is MIT and names Arkaprava Bishnu (2026). Git history also records contributions by SHWETARKA BANERJEE and umernawazneal-afk (including commits `08e22c9` and `6944c98`). Confirm all contributors with copyrightable contributions agreed to the MIT license and can authorize public distribution. Current uncommitted AI files have no Git author metadata. Do not treat the existing single-name notice as proof of all contributors’ consent. |
| Challenge submission license | Official NASA Space Apps legal terms | VERIFIED / NEEDS MANUAL REVIEW | NASA terms require original Solution content to be freely available or under an OSI-approved open-source license. MIT is OSI-approved; team ownership/authorization across contributors still needs confirmation. |
| Copied/adapted code | Git history and current source | UNKNOWN | No source-attribution record identifies any code copied/adapted from third-party repositories. Git history only establishes project commits and authors; it does not prove code originality. Each contributor should confirm their additions and disclose any borrowed snippets/libraries. |

## Python dependencies and license evidence

Python declares a minimum of 3.10. Core runtime dependencies are FastAPI, HTTPX, Pydantic, and Uvicorn. Optional groups are `ai` (pypdf for PDF ingestion), `audit` (openpyxl for the PSI audit builder), and `dev` (pytest). `requirements.txt` installs only core runtime and is not locked; `uv.lock` is the reproducible dependency resolution. Code import inspection found no current Python imports of NumPy, SciPy, pandas, Plotly, or Matplotlib; these were removed from the dependency groups because they are not required by current source code. The local build backend is pinned to setuptools 79.0.1 and wheel 0.45.1 in `pyproject.toml`.

`uv.lock` was generated on 2026-11-15 with uv 0.13.8 for `requires-python >=3.10`. It resolves 37 unique dependency name/version pairs (with marker-specific package entries for some Python/platform variants). Core runtime plus the `dev` extra installed and passed the full unittest suite in a clean CPython 3.13.0 environment on Windows. Other Python versions/platforms were not executed. During resolution uv reported and normalized one malformed upstream version specifier by removing a trailing comma; the package was not identified in the resolver output and should be reviewed before treating this lock as a deployment-grade SBOM.

[`docs/submission/python_dependency_inventory.csv`](docs/submission/python_dependency_inventory.csv) records the exact locked version, dependency scope, PyPI release metadata URL, and the SPDX license expression where PyPI provides one. Twelve package/version entries lack an SPDX expression; their raw PyPI `License` metadata is preserved where present, otherwise blank. Do not treat a raw descriptive string as an SPDX identifier or a license clearance. Review each resolved package's actual license files and bundled components before redistributing an environment or binary.

[`docs/submission/python_sbom.cdx.json`](docs/submission/python_sbom.cdx.json) is a generated CycloneDX 1.5 SBOM containing resolved package references, dependency relationships, distribution URLs, and SHA-256 hashes. The exported SBOM has no populated license fields; use it with the CSV inventory, not instead of the license review. The separate PEP 517 build backend is pinned in `pyproject.toml` but not represented in `uv.lock`'s application dependency graph.

## JavaScript packages (locked frontend dependency graph)

`frontend/package-lock.json` pins 52 package entries, including optional platform packages. Every entry has a `license` field in the lockfile. The table below reproduces the exact package name, locked version, and license identifier from that file. `node_modules/` is generated and should not be included; the package lock is the audit source. Preserve upstream license/notice files for redistributed production bundles.

| Package | Locked version | License |
|---|---:|---|
| `@emnapi/core` | `2.0.0-beta.2` | `MIT` |
| `@emnapi/runtime` | `2.0.0-beta.2` | `MIT` |
| `@emnapi/wasi-threads` | `2.2.0` | `MIT` |
| `@napi-rs/wasm-runtime` | `1.2.6` | `MIT` |
| `@oxc-project/types` | `0.156.0` | `MIT` |
| `@rolldown/binding-android-arm-eabi` | `1.2.19` | `MIT` |
| `@rolldown/binding-android-arm64` | `1.2.19` | `MIT` |
| `@rolldown/binding-darwin-arm64` | `1.2.19` | `MIT` |
| `@rolldown/binding-darwin-x64` | `1.2.19` | `MIT` |
| `@rolldown/binding-freebsd-x64` | `1.2.19` | `MIT` |
| `@rolldown/binding-linux-arm-gnueabihf` | `1.2.19` | `MIT` |
| `@rolldown/binding-linux-arm64-gnu` | `1.2.19` | `MIT` |
| `@rolldown/binding-linux-arm64-musl` | `1.2.19` | `MIT` |
| `@rolldown/binding-linux-ppc64-gnu` | `1.2.19` | `MIT` |
| `@rolldown/binding-linux-s390x-gnu` | `1.2.19` | `MIT` |
| `@rolldown/binding-linux-x64-gnu` | `1.2.19` | `MIT` |
| `@rolldown/binding-linux-x64-musl` | `1.2.19` | `MIT` |
| `@rolldown/binding-openharmony-arm64` | `1.2.19` | `MIT` |
| `@rolldown/binding-wasm32-wasi` | `1.2.19` | `MIT` |
| `@rolldown/binding-win32-arm64-msvc` | `1.2.19` | `MIT` |
| `@rolldown/binding-win32-x64-msvc` | `1.2.19` | `MIT` |
| `@rolldown/pluginutils` | `1.1.1` | `MIT` |
| `@tybys/wasm-util` | `0.10.4` | `MIT` |
| `@vitejs/plugin-react` | `6.3.0` | `MIT` |
| `detect-libc` | `2.1.2` | `Apache-2.0` |
| `fdir` | `6.5.0` | `MIT` |
| `fsevents` | `2.3.3` | `MIT` |
| `lightningcss` | `1.33.0` | `MPL-2.0` |
| `lightningcss-android-arm64` | `1.33.0` | `MPL-2.0` |
| `lightningcss-darwin-arm64` | `1.33.0` | `MPL-2.0` |
| `lightningcss-darwin-x64` | `1.33.0` | `MPL-2.0` |
| `lightningcss-freebsd-x64` | `1.33.0` | `MPL-2.0` |
| `lightningcss-linux-arm-gnueabihf` | `1.33.0` | `MPL-2.0` |
| `lightningcss-linux-arm64-gnu` | `1.33.0` | `MPL-2.0` |
| `lightningcss-linux-arm64-musl` | `1.33.0` | `MPL-2.0` |
| `lightningcss-linux-x64-gnu` | `1.33.0` | `MPL-2.0` |
| `lightningcss-linux-x64-musl` | `1.33.0` | `MPL-2.0` |
| `lightningcss-win32-arm64-msvc` | `1.33.0` | `MPL-2.0` |
| `lightningcss-win32-x64-msvc` | `1.33.0` | `MPL-2.0` |
| `lucide-react` | `1.73.0` | `ISC` |
| `nanoid` | `3.3.20` | `MIT` |
| `picocolors` | `1.1.1` | `ISC` |
| `picomatch` | `4.0.7` | `MIT` |
| `postcss` | `8.5.33` | `MIT` |
| `react` | `19.3.1` | `MIT` |
| `react-dom` | `19.3.1` | `MIT` |
| `rolldown` | `1.2.19` | `MIT` |
| `scheduler` | `0.28.0` | `MIT` |
| `source-map-js` | `1.2.2` | `BSD-3-Clause` |
| `tinyglobby` | `0.2.17` | `MIT` |
| `tslib` | `2.9.1` | `0BSD` |
| `vite` | `8.3.8` | `MIT` |

All JavaScript license identifiers above are **VERIFIED from lockfile metadata**; package terms/notice files should be retained when shipping built bundles. The graph includes **12 MPL-2.0 entries** for `lightningcss` and platform-specific packages; these packages are unmodified here. If any MPL-covered package source is modified and distributed, review MPL-2.0 source-availability obligations for those files. `detect-libc` is Apache-2.0; preserve its license and any applicable notices. Other entries are MIT, ISC, BSD-3-Clause, or 0BSD as listed. `lucide-react` is declared and locked (ISC); this audit does not remove it or infer usage rights from apparent lack of imports.

## Fonts and other frontend assets

| Asset | Usage/location | Author/source | License and attribution | Redistribution status |
|---|---|---|---|---|
| Inter | Remote Google Fonts CSS import in `frontend/src/App.css` | The Inter Project Authors; Google Fonts distribution | SIL Open Font License 1.1 (OFL-1.1); preserve copyright/license if font files are redistributed. [Google Fonts Inter license](https://github.com/google/fonts/blob/main/ofl/inter/OFL.txt). | Not bundled as local font files; browser fetches CSS/font assets from Google at runtime. Source URL and license recorded; no binary redistribution in repository. |
| DM Sans | Remote Google Fonts CSS import in `frontend/src/index.css` | DM Fonts Project / Google Fonts distribution | SIL Open Font License 1.1; preserve license if font files are redistributed. [DM Fonts project](https://github.com/googlefonts/dm-fonts). | Not bundled; remotely fetched at runtime. |
| DM Mono | Remote Google Fonts CSS imports in `frontend/src/App.css` and `frontend/src/index.css` | DM Mono Project / Google Fonts distribution | SIL Open Font License 1.1; preserve license if font files are redistributed. [DM Mono project](https://github.com/googlefonts/dm-mono). | Not bundled; remotely fetched at runtime. |
| Space Grotesk | Remote Google Fonts CSS import in `frontend/src/index.css` | Space Grotesk Project / Google Fonts distribution | SIL Open Font License 1.1; preserve license if font files are redistributed. [Google Fonts Space Grotesk license](https://github.com/google/fonts/blob/main/ofl/spacegrotesk/OFL.txt). | Imported remotely; no matching bundled font file found. |
| Local images, logos, icons, video, audio, or font files | Repository source/assets scan (excluding generated dependencies/builds) | — | NOT APPLICABLE: no standalone media/font assets were found. UI uses CSS and Unicode glyphs. NASA diagrams/images inside source PDFs and office files are part of the documents below and remain subject to those source terms. | — |

The page depends on Google Fonts network availability. If the team later downloads/embeds font binaries, include each family’s full OFL text and copyright notice and record the exact font version/source.

## NASA PSI datasets and documents

The 54 non-placeholder files listed below are copied source materials in `data/raw/nasa_psi/`. Dataset names and local paths are taken from `data/metadata/dataset_inventory.csv`; source URLs and usage notes are taken from `data/metadata/source_registry.csv`. For all rows, NASA PSI is the recorded repository/provider, but the individual author/copyright holder and exact applicable license are **UNKNOWN** from this repository metadata. The registry itself says to check the investigation page for license/citation. Treat every row as **NEEDS MANUAL REVIEW** before public redistribution; do not assume U.S. government public-domain status for every embedded document, figure, or third-party contribution. For any source used in the submission, cite its exact title, authors/organization, PSI record/page, and local source path after checking the original record.

| Source record/title | Repository path | Recorded source URL | Author, license, attribution and redistribution status |
|---|---|---|---|
| `PSI-26_Experimental table_BASS.csv` | `data/raw/nasa_psi/BASS/experimental_tables/PSI-26_Experimental table_BASS.csv` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `PSI-26_metadata_PSI-102_BASS.zip` | `data/raw/nasa_psi/BASS/investigation_metadata/PSI-26_metadata_PSI-102_BASS.zip` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `PSI-25_Experimental table_BASS-II.csv` | `data/raw/nasa_psi/BASS_II/experimental_tables/PSI-25_Experimental table_BASS-II.csv` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-25 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `PSI-25_metadata_PSI_metadata_PSI-101_BASS-II.zip` | `data/raw/nasa_psi/BASS_II/investigation_metadata/PSI-25_metadata_PSI_metadata_PSI-101_BASS-II.zip` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-25 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `PSI-98_Experimental table_SAFFIRE-1.csv` | `data/raw/nasa_psi/SAFFIRE_I/experimental_tables/PSI-98_Experimental table_SAFFIRE-1.csv` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-98 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `PSI-98_metadata_PSI-166_SAFFIRE-I.zip` | `data/raw/nasa_psi/SAFFIRE_I/investigation_metadata/PSI-98_metadata_PSI-166_SAFFIRE-I.zip` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-98 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `PSI-99_Experimental table_SAFFIRE-2.csv` | `data/raw/nasa_psi/SAFFIRE_II/experimental_tables/PSI-99_Experimental table_SAFFIRE-2.csv` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-99 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `PSI-99_metadata_PSI-167_SAFFIRE-II.zip` | `data/raw/nasa_psi/SAFFIRE_II/investigation_metadata/PSI-99_metadata_PSI-167_SAFFIRE-II.zip` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-99 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `PSI-100_Experimental table_SAFFIRE-3.csv` | `data/raw/nasa_psi/SAFFIRE_III/experimental_tables/PSI-100_Experimental table_SAFFIRE-3.csv` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-100 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `PSI-100_metadata_PSI-168_SAFFIRE-III.zip` | `data/raw/nasa_psi/SAFFIRE_III/investigation_metadata/PSI-100_metadata_PSI-168_SAFFIRE-III.zip` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-100 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `60054MAFH000_C.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/60054MAFH000_C.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `60054mdfh001.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/60054mdfh001.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `60054mdfh002.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/60054mdfh002.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `BASS ERD.pptx` | `data/raw/nasa_psi/BASS/engineering_documents/BASS ERD.pptx` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `PMMA sheet MFD1066.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/PMMA sheet MFD1066.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `S1183MFA1000_A.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/S1183MFA1000_A.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `S1183MFA1020.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/S1183MFA1020.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `S1183MFA1065.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/S1183MFA1065.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `s1183mfa1085-Spherical sample final.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/s1183mfa1085-Spherical sample final.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `s1183mfa1090-Cylindrical Samples.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/s1183mfa1090-Cylindrical Samples.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `s1183mfa1110-flat.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/s1183mfa1110-flat.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `s1183mfa1111-flat.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/s1183mfa1111-flat.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `S1183MFD1021_A.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/S1183MFD1021_A.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `S1183MFD1022.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/S1183MFD1022.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `S1183MFD1026_A.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/S1183MFD1026_A.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `S1183MFD1041.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/S1183MFD1041.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `s1183mfd1086_REV-.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/s1183mfd1086_REV-.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `s1183mfd1091_REV-.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/s1183mfd1091_REV-.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `s1183mfd1116_REV-.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/s1183mfd1116_REV-.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `Short Nozzle MFA10771.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/Short Nozzle MFA10771.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `SLICE ED-04 SLICE_BASS_SAR-1_FINAL.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/SLICE ED-04 SLICE_BASS_SAR-1_FINAL.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `SLICE ED-05 SLICE BASS SAR-2_FINAL.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/SLICE ED-05 SLICE BASS SAR-2_FINAL.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `SLICE IP-A SRDR.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/SLICE IP-A SRDR.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `SPICE-front-window.pdf` | `data/raw/nasa_psi/BASS/engineering_documents/SPICE-front-window.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `BASS test matrix.xlsx` | `data/raw/nasa_psi/BASS/experimental_tables/BASS test matrix.xlsx` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `BASS Test Matrix 050213.xlsx` | `data/raw/nasa_psi/BASS/experimental_tables/BASS Test Matrix 050213.xlsx` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `SRD_BASS.pdf` | `data/raw/nasa_psi/BASS/science_documents/SRD_BASS.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `US National Meeting-070HE-0218-Final.docx` | `data/raw/nasa_psi/BASS/science_documents/US National Meeting-070HE-0218-Final.docx` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `DLD_BASS.pdf` | `data/raw/nasa_psi/BASS/investigation_metadata/DLD_BASS.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-26 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `SAFFIRE-II DoD.docx` | `data/raw/nasa_psi/SAFFIRE_II/investigation_metadata/SAFFIRE-II DoD.docx` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-99 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `SAFFIRE-II_Image_Directory_Nomenclature_v3.0.pdf` | `data/raw/nasa_psi/SAFFIRE_II/investigation_metadata/SAFFIRE-II_Image_Directory_Nomenclature_v3.0.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-99 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `SAFFIRE-II_MergeResult-jpeg_v5_Final.xlsx` | `data/raw/nasa_psi/SAFFIRE_II/investigation_metadata/SAFFIRE-II_MergeResult-jpeg_v5_Final.xlsx` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-99 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `SAFFIRE-I and SAFFIRE-III DoD.docx` | `data/raw/nasa_psi/SAFFIRE_I/investigation_metadata/SAFFIRE-I and SAFFIRE-III DoD.docx` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-98 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `SAFFIRE-I Image Directory Nomenclature.pdf` | `data/raw/nasa_psi/SAFFIRE_I/investigation_metadata/SAFFIRE-I Image Directory Nomenclature.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-98 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `SAFFIRE-I Operations.pdf` | `data/raw/nasa_psi/SAFFIRE_I/engineering_documents/SAFFIRE-I Operations.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-98 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `SAFFIRE-1_MergeResult-jpeg_Update_Final_v2.xlsx` | `data/raw/nasa_psi/SAFFIRE_I/investigation_metadata/SAFFIRE-1_MergeResult-jpeg_Update_Final_v2.xlsx` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-98 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `SAFFIRE-I and SAFFIRE-III DoD.docx` | `data/raw/nasa_psi/SAFFIRE_III/investigation_metadata/SAFFIRE-I and SAFFIRE-III DoD.docx` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-100 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `SAFFIRE-III Image Directory Nomenclature_v3.0.pdf` | `data/raw/nasa_psi/SAFFIRE_III/investigation_metadata/SAFFIRE-III Image Directory Nomenclature_v3.0.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-100 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `SAFFIRE-III_MergeResult-jpeg_Final.xlsx` | `data/raw/nasa_psi/SAFFIRE_III/investigation_metadata/SAFFIRE-III_MergeResult-jpeg_Final.xlsx` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-100 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `SAFFIRE-III_MergeResult-raw_Final.xlsx` | `data/raw/nasa_psi/SAFFIRE_III/investigation_metadata/SAFFIRE-III_MergeResult-raw_Final.xlsx` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-100 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `SAFFIRE-III Operations.pdf` | `data/raw/nasa_psi/SAFFIRE_III/engineering_documents/SAFFIRE-III Operations.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-100 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `BASS-2 Engineering Requirements.pptx` | `data/raw/nasa_psi/BASS_II/engineering_documents/BASS-2 Engineering Requirements.pptx` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-25 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `BASS-II Procedure.docx` | `data/raw/nasa_psi/BASS_II/engineering_documents/BASS-II Procedure.docx` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-25 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |
| `TM-20210011385.pdf` | `data/raw/nasa_psi/BASS_II/science_documents/TM-20210011385.pdf` | https://psi.nasa.gov/physci/repo/data/investigations/PSI-25 | **UNKNOWN / NEEDS MANUAL REVIEW** — author and item-specific license not established; registry says check source page. Verify attribution and redistribution rights. |

The inventory rows currently have empty retrieval dates for many files and generic investigation-level URLs rather than exact item URLs. This audit does not convert these records to reviewed/redistributable status. `data/processed/audit/` reports are project-generated audit artifacts; their claims trace to these sources but the source-document license still applies to source content incorporated or quoted. The harmonised table is header-only, and audit scripts/exports are not verified NASA experimental results.

### NASA scientific references and project challenge sources

| Source | Use in project | Status / action |
|---|---|---|
| NASA BASS overview, https://www.nasa.gov/wp-content/uploads/2025/07/burning-and-suppression-of-solids-bass.pdf | Background on BASS scope in `docs/mathematical_framework.md` and `docs/NASA_DATA_SOURCES.md`. | NEEDS ATTRIBUTION: cite report title/author/date as shown on source document and review its specific terms before redistributing the PDF. |
| NASA Physical Sciences Informatics investigation catalogue, https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/ | NASA PSI context/source discovery. | NEEDS ATTRIBUTION: cite catalogue; not evidence that every linked document is freely redistributable. |
| NASA PSI data repository, https://psi.nasa.gov/physci/repo/data/investigations/ | Source URL family used in the inventory for PSI-25, -26, -98, -99, -100. | NEEDS MANUAL REVIEW: exact item records and terms are not resolved in the registry. |
| de Ris, J. N. (1969), “Spread of a laminar diffusion flame,” https://doi.org/10.1016/S0082-0784(69)80407-8 | A regime-limited theory reference in `docs/mathematical_framework.md`; not a FlameBound prediction/validation dataset. | NEEDS ATTRIBUTION: citation is present. Confirm reuse permissions before reproducing figures or substantial text. |
| NASA, Flame Spread Theory report, https://ntrs.nasa.gov/api/citations/19930004527/downloads/19930004527.pdf | Named theory reference in `docs/mathematical_framework.md`. | NEEDS ATTRIBUTION: cite the report; verify report-specific notices before reproducing content. |
| IUPAC Gold Book, “pressure,” https://goldbook.iupac.org/terms/view/P04819 | Authoritative definition of partial pressure, including `p_i = x_i p`; source added to the atmospheric equation documentation during this audit. | VERIFIED / NEEDS ATTRIBUTION: cite IUPAC when describing the equation. |
| IUPAC Gold Book, [“amount fraction”](https://goldbook.iupac.org/terms/view/A00296) and [“mass fraction”](https://goldbook.iupac.org/terms/view/M03722) | Definitions underlying the conditional binary-mixture oxygen mass-fraction equation. | VERIFIED / NEEDS ATTRIBUTION: links added to `docs/atmospheric_engine.md` and `docs/mathematical_framework.md`; the equation is not an available API operation. |
| 2026 NASA Space Apps challenge, https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/ | Challenge context and expected interactive dashboard aim. | NEEDS ATTRIBUTION: cite challenge statement; FlameBound limitations must remain clear. |

No external experimental citation was fabricated during this audit. Current documents explicitly state that the SAFFIRE MergeResult workbooks are file indexes, not measurements; the harmonised data has zero verified rows; dashboard fixtures are illustrative; and no lunar flame-spread prediction is implemented. Keep these boundaries in the submission.

## Ollama and model

| Component | Source/license | Status |
|---|---|---|
| Ollama runtime | Installed separately by the user; not in Python/npm manifests or repository archive. | Version `0.40.16` detected locally. Its license/redistribution is NOT APPLICABLE to this source archive; do not bundle the installer/runtime without checking its terms. |
| `qwen3:4b` model | Ollama library entry: https://ollama.com/library/qwen3%3A4b; upstream Qwen3 project: https://github.com/QwenLM/Qwen3 | VERIFIED as Apache-2.0 for the listed Qwen3 4B model card. Local tag was present with ID prefix `359d7dd4bcda`; model weights are not in this repository. Cite the model and retain the Apache license if redistributing weights or materials governed by its terms. |

## NASA Space Apps submission requirements (checked 2026-11-15)

| Requirement | Status | Source and interpretation |
|---|---|---|
| Submit/edit from the team Project Tab; global page lists Nov 14 9:00 AM through Nov 15 11:59 PM local time | VERIFIED | [2026 global page](https://www.spaceappschallenge.org/2026/). Confirm the team creator/event local-time basis in the account. |
| The selected challenge asks for an interactive SI-powered dashboard summarizing, ranking, and interpreting microgravity combustion findings | VERIFIED as the challenge objective | [Flame in Freefall](https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/). This prototype does not yet deliver evidence ranking from verified records; describe that gap plainly. |
| Cite every source and identify license terms for Solution Materials | VERIFIED | [Official participant terms](https://www.spaceappschallenge.org/legal/). NASA says source citations include open-source resources, and appropriate license documentation must accompany Solution Materials. |
| Team roster “should have no more than six participants” | VERIFIED wording; confirm applicability | Global page uses “should”; do not restate as a stricter absolute without the team/event rules. |
| Local judging cutoff, separate forms, exact Project Tab fields/attachments, video, hosting, slides, AI disclosure | UNKNOWN / requires team Project Tab and local event page | Not verifiable from the global sources listed above. Do not assume these are global requirements. |

Official page fetches timed out/returned 502 during this audit; search-indexed extracts from the exact official URLs were available on the audit date. The Project Tab itself is account-gated and was not inspected.

## Packaging findings and actions

- `THIRD_PARTY_NOTICES.md`, root `LICENSE`, README, manifests, source registries, source files, and tests should be included in any reviewed submission source archive.
- `.env.example` is not present and is not required for this app: there are no secrets or mandatory secret configuration. `.gitignore` excludes `.env` and `.env.*` except `.env.example`; current repo scan found no `.env*` file. Configuration defaults are documented in the README and release manifest.
- Exclude `.git`, `node_modules`, Python virtual environments/caches, `frontend/dist`, generated build output, local SQLite indexes, and local secret files. `frontend/public/` currently contains only `.gitkeep`; no standalone app assets are omitted by excluding build output.
- The release manifest lists `THIRD_PARTY_NOTICES.md` and excludes the local-only/ignored source workbook. The flagged local workbook mentioned in `docs/data_audit_report.md` is not present in the audited working tree.
- The existing backup predates this attribution audit and therefore does not contain this notice file. It was not overwritten. It remains an internal pre-audit snapshot, not a current submission archive.
- Do not publicly redistribute the 54 NASA PSI source files until source-specific citation and rights are checked. A file being downloadable from PSI is not, by itself, a license determination.
- Do not claim legal compliance until contributor authorization and the PSI document/source licenses have been confirmed.
