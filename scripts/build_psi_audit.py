"""Build provenance-preserving row audits from NASA PSI experimental tables.

This script copies raw row values into an audit layer but makes no scientific
outcome classifications and emits no verified harmonised records.
"""
from __future__ import annotations

import csv
import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "data" / "raw" / "nasa_psi"
AUDIT_DIR = REPO / "data" / "processed" / "audit"
HARM_DIR = REPO / "data" / "processed" / "harmonised"
TEMPLATE = REPO / "data" / "template" / "test_points_template.csv"
AUDIT_COLUMNS = [
    "investigation_id", "source_file", "source_sheet", "source_row",
    "source_locator", "row_role", "candidate_id_raw", "row_values_json",
    "verification_status", "unresolved_reason", "duplicate_key",
    "duplicate_source_record", "duplicate_group_size",
]


def scalar(value: Any) -> Any:
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except TypeError:
            pass
    return value


def nonblank(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def canon(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def append_raw_record(rows, investigation, source_file, sheet, row_num,
                      headers, values, role, candidate_id, reason, dup_key=""):
    payload = {"headers": [scalar(x) for x in headers],
               "values": [scalar(x) for x in values]}
    locator = f"{sheet} row {row_num}" if sheet else f"row {row_num}"
    rows.append({
        "investigation_id": investigation,
        "source_file": source_file,
        "source_sheet": sheet,
        "source_row": row_num,
        "source_locator": locator,
        "row_role": role,
        "candidate_id_raw": candidate_id,
        "row_values_json": json.dumps(payload, ensure_ascii=False, default=str),
        "verification_status": "unreviewed",
        "unresolved_reason": reason,
        "duplicate_key": dup_key,
        "duplicate_source_record": "false",
        "duplicate_group_size": 1,
    })


def load_csv_audit(rows, investigation, filename, id_fields, candidate_regex=None,
                   annotation_reason="Source row is not an identified test candidate."):
    path = RAW / investigation / "experimental_tables" / filename
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        headers = reader.fieldnames or []
        for row_num, row in enumerate(reader, 2):
            vals = [row.get(h, "") for h in headers]
            key_values = [canon(row.get(f, "")) for f in id_fields]
            candidate = any(key_values)
            if candidate_regex:
                candidate = bool(candidate_regex.fullmatch(key_values[0]))
            role = "candidate_record_unverified" if candidate else "annotation_or_note"
            identifier = " | ".join(key_values) if candidate else ""
            reason = (
                "Candidate row has not been fully cross-checked against source definitions and outcome evidence."
                if candidate else annotation_reason
            )
            dup_key = "|".join(key_values) if candidate else ""
            append_raw_record(rows, investigation, filename, "", row_num, headers,
                              vals, role, identifier, reason, dup_key)
    return sum(r["source_file"] == filename and r["investigation_id"] == investigation for r in rows)


def load_bass_workbook(rows):
    investigation = "BASS"
    filename = "BASS test matrix.xlsx"
    path = RAW / investigation / "experimental_tables" / filename
    workbook = load_workbook(path, read_only=True, data_only=True)
    configs = {"as run matrix": 3, "2012": 3, "2013": 2,
               "Data without TP": 1, "TP without Data": 1}
    for sheet_name, header_row in configs.items():
        sheet = workbook[sheet_name]
        values_iter = sheet.iter_rows(values_only=True)
        all_rows = list(values_iter)
        raw_headers = list(all_rows[header_row - 1])
        headers = [str(x).strip() if x is not None else "" for x in raw_headers]
        for idx, values in enumerate(all_rows[header_row:], header_row + 1):
            values = list(values)
            if not any(nonblank(v) for v in values):
                continue
            mapping = {h.casefold(): v for h, v in zip(headers, values) if h}
            as_run = mapping.get("as run test no.", "")
            test_no = mapping.get("test no.", "")
            sample_no = mapping.get("sample no.", "")
            key_values = [canon(as_run), canon(test_no), canon(sample_no)]
            candidate = (
                sheet_name not in {"Data without TP", "TP without Data"}
                and any(key_values)
                and canon(test_no).casefold() not in {"setup", "no data"}
                and not canon(as_run).casefold().startswith("no data")
            )
            role = "candidate_record_unverified" if candidate else (
                "availability_or_setup_annotation" if any(key_values) or sheet_name in {"Data without TP", "TP without Data"}
                else "annotation_or_note"
            )
            identifier = " | ".join(key_values) if candidate else ""
            reason = (
                "As-run observation is available, but row-level label mapping and the full PSI crosswalk remain unreviewed."
                if candidate else "Setup, file-availability, heading, or annotation row; not a verified test point."
            )
            dup_key = "|".join(key_values) if candidate else ""
            append_raw_record(rows, investigation, filename, sheet_name, idx,
                              headers, values, role, identifier, reason, dup_key)
    workbook.close()


def add_index_workbook_summary(rows, investigation, filename):
    path = RAW / investigation / "investigation_metadata" / filename
    workbook = load_workbook(path, read_only=True, data_only=True)
    summary = []
    for sheet in workbook:
        first = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True), ())
        summary.append({"sheet": sheet.title, "rows_including_header": sheet.max_row,
                        "columns": sheet.max_column,
                        "header": [scalar(v) for v in first]})
    workbook.close()
    append_raw_record(
        rows, investigation, filename, "workbook summary", "", [], summary,
        "image_or_raw_file_index_not_test_point", "",
        "Contains filenames, timestamps, file IDs, sizes, and retrieval status; it is not the sensor/image payload."
    )


def flag_duplicate_keys(rows):
    counts = Counter(
        (r["investigation_id"], r["duplicate_key"])
        for r in rows if r["duplicate_key"]
    )
    for row in rows:
        key = (row["investigation_id"], row["duplicate_key"])
        size = counts.get(key, 1) if row["duplicate_key"] else 1
        row["duplicate_group_size"] = size
        row["duplicate_source_record"] = "true" if size > 1 else "false"


def write_rows(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=AUDIT_COLUMNS, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def append_processing_log(entries):
    path = REPO / "data" / "metadata" / "processing_log.csv"
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames or []
        existing = list(reader)
    existing = [r for r in existing if r.get("process_id") != "psi_audit_20261115_v1"]
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for source_path, output_path, input_count, output_count, action, warning in entries:
        source = REPO / source_path
        output = REPO / output_path
        existing.append({
            "process_id": "psi_audit_20261115_v1",
            "source_path": source_path,
            "output_path": output_path,
            "script": "scripts/build_psi_audit.py",
            "script_version": "0.1.0",
            "timestamp_utc": timestamp,
            "input_checksum_sha256": sha256(source) if source.is_file() else "",
            "output_checksum_sha256": sha256(output),
            "action": action,
            "records_in": str(input_count) if input_count is not None else "",
            "records_out": str(output_count) if output_count is not None else "",
            "warnings": warning,
        })
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(existing)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--overwrite-generated",
        action="store_true",
        help="Replace existing audit/harmonised outputs and this process ID's log entries.",
    )
    args = parser.parse_args()
    expected_outputs = [
        *(AUDIT_DIR / f"{name.lower()}_audit.csv" for name in
          ["BASS", "BASS_II", "SAFFIRE_I", "SAFFIRE_II", "SAFFIRE_III"]),
        HARM_DIR / "test_points.csv",
        REPO / "data" / "metadata" / "processing_log.csv",
    ]
    existing = [path for path in expected_outputs if path.exists()]
    if existing and not args.overwrite_generated:
        listing = "\n".join(f"  - {path.relative_to(REPO)}" for path in existing)
        raise SystemExit(
            "Refusing to overwrite existing generated outputs. Review them and "
            "rerun with --overwrite-generated only if replacement is intended:\n" + listing
        )

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    HARM_DIR.mkdir(parents=True, exist_ok=True)
    audits = {name: [] for name in ["BASS", "BASS_II", "SAFFIRE_I", "SAFFIRE_II", "SAFFIRE_III"]}
    logs = []

    load_csv_audit(audits["BASS"], "BASS", "PSI-26_Experimental table_BASS.csv",
                   ["As Run Test #", "Test #", "Sample #"])
    load_bass_workbook(audits["BASS"])
    # Do not load or export the locally ignored workbook: its cells were previously
    # identified as containing credential-like content. Record only the exclusion.
    append_raw_record(
        audits["BASS"], "BASS", "BASS Test Matrix 050213.xlsx", "", "", [], [],
        "excluded_local_sensitive_review", "",
        "Cell contents intentionally not extracted or exported due to previously identified credential-like content."
    )
    for inv, fn, ids in [
        ("BASS_II", "PSI-25_Experimental table_BASS-II.csv", ["Test #"]),
        ("SAFFIRE_I", "PSI-98_Experimental table_SAFFIRE-1.csv", ["Sample Number "]),
        ("SAFFIRE_II", "PSI-99_Experimental table_SAFFIRE-2.csv", ["Sample Number"]),
        ("SAFFIRE_III", "PSI-100_Experimental table_SAFFIRE-3.csv", ["Sample Number "]),
    ]:
        pattern = (re.compile(r"2-\d+") if inv == "SAFFIRE_II" else
                   re.compile(r"S[12]") if inv in {"SAFFIRE_I", "SAFFIRE_III"} else None)
        load_csv_audit(audits[inv], inv, fn, ids, candidate_regex=pattern)

    for inv, fn in [
        ("SAFFIRE_I", "SAFFIRE-1_MergeResult-jpeg_Update_Final_v2.xlsx"),
        ("SAFFIRE_II", "SAFFIRE-II_MergeResult-jpeg_v5_Final.xlsx"),
        ("SAFFIRE_III", "SAFFIRE-III_MergeResult-jpeg_Final.xlsx"),
        ("SAFFIRE_III", "SAFFIRE-III_MergeResult-raw_Final.xlsx"),
    ]:
        add_index_workbook_summary(audits[inv], inv, fn)

    for rows in audits.values():
        flag_duplicate_keys(rows)
    outputs = {}
    for inv, rows in audits.items():
        out = AUDIT_DIR / f"{inv.lower()}_audit.csv"
        write_rows(out, rows)
        outputs[inv] = out
    with TEMPLATE.open(encoding="utf-8-sig", newline="") as stream:
        headers = next(csv.reader(stream))
    harmonized = HARM_DIR / "test_points.csv"
    with harmonized.open("w", encoding="utf-8", newline="") as stream:
        csv.writer(stream).writerow(headers)

    # The row-level work is an audit export only. No row currently meets the
    # project definition of an independently identified, outcome-verified point.
    for inv, rows in audits.items():
        source_files = sorted({r["source_file"] for r in rows})
        for source_name in source_files:
            matches = list((RAW / inv).rglob(source_name))
            source_path = matches[0].relative_to(REPO).as_posix() if matches else ""
            role_rows = [r for r in rows if r["source_file"] == source_name]
            logs.append((source_path, outputs[inv].relative_to(REPO).as_posix(),
                         len(role_rows), len(role_rows), "row_audit_export_or_exclusion",
                         "Unreviewed candidates remain excluded from harmonised test_points.csv."))
    append_processing_log(logs)
    print("Audit row counts:", {k: len(v) for k, v in audits.items()})
    print("Candidate rows:", {k: sum(r["row_role"] == "candidate_record_unverified" for r in v) for k, v in audits.items()})
    print("Harmonised verified rows: 0")


if __name__ == "__main__":
    main()
