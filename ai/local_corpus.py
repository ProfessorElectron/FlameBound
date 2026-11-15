"""Local, read-only lexical retrieval over inventoried PSI files.

Every indexed source is hash-checked against the repository inventory and remains
marked unreviewed. This index is local-only and is never written into Git-tracked data.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import zipfile
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Any
from xml.etree import ElementTree

from ai.retrieval.chunker import chunk_documents


_SUPPORTED = {".pdf", ".csv", ".txt", ".xlsx", ".docx", ".pptx", ".zip"}
_TOKEN = re.compile(r"[a-z0-9]+", re.IGNORECASE)
_STOP = {
    "a", "an", "and", "are", "as", "at", "be", "by", "does", "for", "from",
    "how", "in", "is", "it", "of", "on", "or", "the", "these", "this", "to",
    "was", "were", "what", "which", "who", "with", "you", "your",
}
_MAX_FILE_BYTES = 60_000_000
_MAX_ARCHIVE_UNPACKED_BYTES = 100_000_000
_MAX_ARCHIVE_MEMBERS = 500
_MAX_PAGES = 1200


def _tokens(text: str) -> list[str]:
    raw = [token.casefold() for token in _TOKEN.findall(text) if token.casefold() not in _STOP]
    expanded = []
    for index, token in enumerate(raw):
        expanded.append(token)
        if token in {"i", "ii", "iii"} and index and raw[index - 1] in {"bass", "saffire"}:
            expanded.append({"i": "1", "ii": "2", "iii": "3"}[token])
    return expanded


def _requested_psi_numbers(query: str) -> set[str]:
    return {match.group(1) for match in re.finditer(r"\bPSI[-\s]?(\d{2,3})\b", query, re.IGNORECASE)}


def _query_terms(query: str) -> tuple[list[str], set[str]]:
    requested_numbers = _requested_psi_numbers(query)
    terms = _tokens(query)
    if requested_numbers:
        terms = [term for term in terms if term != "psi" and term not in requested_numbers]
    return terms, requested_numbers


def _xml_text(data: bytes, tags: set[str]) -> list[str]:
    root = ElementTree.fromstring(data)
    return ["".join(node.itertext()).strip() for node in root.iter() if node.tag.rsplit("}", 1)[-1] in tags]


def _xlsx_pages(data: bytes) -> list[dict[str, Any]]:
    with zipfile.ZipFile(io.BytesIO(data)) as book:
        names = set(book.namelist())
        shared: list[str] = []
        if "xl/sharedStrings.xml" in names:
            root = ElementTree.fromstring(book.read("xl/sharedStrings.xml"))
            shared = ["".join(node.itertext()) for node in root if node.tag.rsplit("}", 1)[-1] == "si"]
        workbook = ElementTree.fromstring(book.read("xl/workbook.xml"))
        rels_root = ElementTree.fromstring(book.read("xl/_rels/workbook.xml.rels"))
        rels = {node.attrib["Id"]: node.attrib["Target"] for node in rels_root}
        pages = []
        for sheet in workbook.iter():
            if sheet.tag.rsplit("}", 1)[-1] != "sheet":
                continue
            sheet_name = sheet.attrib.get("name", "Sheet")
            relation = next((v for k, v in sheet.attrib.items() if k.endswith("}id")), None)
            target = rels.get(relation or "")
            if not target:
                continue
            part = (PurePosixPath("xl") / target).as_posix()
            part = str(PurePosixPath(part))
            if part.startswith("xl/../") or part not in names:
                continue
            root = ElementTree.fromstring(book.read(part))
            for row_number, row in enumerate((n for n in root.iter() if n.tag.rsplit("}", 1)[-1] == "row"), 1):
                cells = []
                for cell in row:
                    if cell.tag.rsplit("}", 1)[-1] != "c":
                        continue
                    ref = cell.attrib.get("r", "cell")
                    kind = cell.attrib.get("t", "")
                    value_node = next((n for n in cell if n.tag.rsplit("}", 1)[-1] in {"v", "is"}), None)
                    if value_node is None:
                        continue
                    value = "".join(value_node.itertext()).strip()
                    if kind == "s" and value.isdigit() and int(value) < len(shared):
                        value = shared[int(value)]
                    if value:
                        cells.append(f"{ref}={value}")
                if cells:
                    page_number = len(pages) + 1
                    pages.append({"page_number": page_number, "location_label": f"worksheet {sheet_name}, row {row_number}", "text": f"Worksheet {sheet_name}, row {row_number}: " + " | ".join(cells)})
                    if len(pages) >= _MAX_PAGES:
                        return pages
        return pages


def _office_pages(suffix: str, data: bytes) -> list[dict[str, Any]]:
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = sorted(archive.namelist())
        if suffix == ".xlsx":
            return _xlsx_pages(data)
        if suffix == ".docx":
            raw = archive.read("word/document.xml")
            paragraphs = _xml_text(raw, {"p"})
            return [{"page_number": i + 1, "location_label": f"paragraph {i + 1}", "text": text} for i, text in enumerate(paragraphs) if text]
        if suffix == ".pptx":
            slide_names = [n for n in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]
            pages = []
            for i, name in enumerate(sorted(slide_names, key=lambda n: int(re.search(r"slide(\d+)", n).group(1))), 1):
                parts = _xml_text(archive.read(name), {"t"})
                text = " ".join(item for item in parts if item)
                if text:
                    slide_number = re.search(r"slide(\d+)", name).group(1)
                    pages.append({"page_number": i, "location_label": f"slide {slide_number}", "text": text})
            return pages
    return []


def _csv_pages(data: bytes) -> list[dict[str, Any]]:
    try:
        content = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        content = data.decode("cp1252", errors="replace")
    rows = list(csv.reader(io.StringIO(content)))
    if not rows:
        return []
    header = [cell.strip() or f"column_{i + 1}" for i, cell in enumerate(rows[0])]
    pages = []
    for row_number, row in enumerate(rows[1:], 2):
        fields = [f"{header[i]}: {value.strip()}" for i, value in enumerate(row[:len(header)]) if value.strip()]
        if fields:
            pages.append({"page_number": row_number, "location_label": f"row {row_number}", "text": " | ".join(fields)})
            if len(pages) >= _MAX_PAGES:
                break
    return pages


def _extract(data: bytes, suffix: str, *, archive_depth: int = 0) -> list[dict[str, Any]]:
    if len(data) > _MAX_FILE_BYTES:
        return []
    if suffix == ".txt":
        text = data.decode("utf-8-sig", errors="replace").strip()
        return [{"page_number": 1, "location_label": "text file", "text": text}] if text else []
    if suffix == ".csv":
        return _csv_pages(data)
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            return []
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted or len(reader.pages) > _MAX_PAGES:
            return []
        return [{"page_number": i + 1, "location_label": f"page {i + 1}", "text": (page.extract_text() or "").strip()}
                for i, page in enumerate(reader.pages) if (page.extract_text() or "").strip()]
    if suffix in {".xlsx", ".docx", ".pptx"}:
        return _office_pages(suffix, data)
    if suffix == ".zip" and archive_depth < 1:
        pages = []
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = [i for i in archive.infolist() if not i.is_dir() and Path(i.filename).suffix.casefold() in _SUPPORTED - {".zip"}]
            if len(members) > _MAX_ARCHIVE_MEMBERS or sum(i.file_size for i in members) > _MAX_ARCHIVE_UNPACKED_BYTES:
                return []
            for member in members:
                member_suffix = Path(member.filename).suffix.casefold()
                for page in _extract(archive.read(member), member_suffix, archive_depth=archive_depth + 1):
                    member_name = Path(member.filename).name
                    location = page.get("location_label", f"page {page['page_number']}")
                    pages.append({**page, "location_label": f"{member_name}, {location}", "text": f"Archive member {member_name}: {page['text']}"})
                    if len(pages) >= _MAX_PAGES:
                        return pages
        return pages
    return []


class LocalPSICorpus:
    """Hash-verified local PSI corpus with corpus-calibrated lexical abstention."""

    def __init__(self, repo_root: str | Path):
        self.root = Path(repo_root).resolve()
        self._records: list[dict[str, Any]] | None = None
        self._threshold: float | None = None
        self._document_frequency: dict[str, int] | None = None
        self.indexed_sources = 0
        self.skipped_sources: list[str] = []

    def _load(self) -> list[dict[str, Any]]:
        if self._records is not None:
            return self._records
        inventory_path = self.root / "data/metadata/dataset_inventory.csv"
        source_path = self.root / "data/metadata/source_registry.csv"
        if not inventory_path.is_file() or not source_path.is_file():
            self._records = []
            return self._records
        with source_path.open(encoding="utf-8-sig", newline="") as f:
            sources = {r["source_id"]: r for r in csv.DictReader(f)}
        records = []
        valid_entries = []
        source_hashes = {}
        allowed_root = (self.root / "data/raw/nasa_psi").resolve()
        with inventory_path.open(encoding="utf-8-sig", newline="") as f:
            for asset in csv.DictReader(f):
                source_id = asset.get("dataset_id", "")
                source = sources.get(source_id)
                rel = asset.get("local_path", "")
                path = (self.root / rel).resolve()
                suffix = path.suffix.casefold()
                notes = (asset.get("notes") or "").casefold()
                if any(flag in notes for flag in ("credential-like", "local-only", "sensitive")):
                    self.skipped_sources.append(f"{source_id}: excluded by local sensitivity note")
                    continue
                if not source or not path.is_relative_to(allowed_root) or suffix not in _SUPPORTED or not path.is_file():
                    continue
                if path.stat().st_size > _MAX_FILE_BYTES:
                    self.skipped_sources.append(f"{source_id}: source exceeds the local indexing size limit")
                    continue
                raw = path.read_bytes()
                content_hash = hashlib.sha256(raw).hexdigest()
                if content_hash.casefold() != (asset.get("checksum_sha256") or "").casefold():
                    self.skipped_sources.append(f"{source_id}: source hash differs from inventory")
                    continue
                source_hashes[source_id] = content_hash
                valid_entries.append((asset, source, path, content_hash))

        cache_path = self.root / "data/index/local_psi_corpus.json"
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
            if (cache.get("cache_version") == 4 and cache.get("source_hashes") == source_hashes
                    and isinstance(cache.get("records"), list)):
                self._records = cache["records"]
                for record in self._records:
                    record.setdefault("source_id_tokens", _tokens(record["source_id"]))
                self.indexed_sources = int(cache.get("indexed_sources", 0))
                self.skipped_sources = list(cache.get("skipped_sources", []))
                return self._records
        except (OSError, ValueError, TypeError):
            pass

        for asset, source, path, content_hash in valid_entries:
                raw = path.read_bytes()
                if hashlib.sha256(raw).hexdigest() != content_hash:
                    self.skipped_sources.append(f"{asset.get('dataset_id')}: source changed during indexing")
                    continue
                source_id = asset["dataset_id"]
                suffix = path.suffix.casefold()
                try:
                    pages = _extract(raw, suffix)
                except Exception as exc:
                    self.skipped_sources.append(f"{source_id}: extraction failed ({type(exc).__name__})")
                    continue
                if not pages:
                    self.skipped_sources.append(f"{source_id}: no extractable text (check PDF dependency or file format)")
                    continue
                title = source.get("title") or path.name
                if suffix == ".zip":
                    title = f"{title} (archive)"
                chunks = chunk_documents(pages, source_id=source_id, content_hash=content_hash,
                                         chunk_size=1100, overlap=100, max_chunks=10000)
                for chunk in chunks:
                    records.append({
                        **chunk, "title": title, "uri": source["uri"],
                        "review_status": "unreviewed",
                        "publication_date": source.get("publication_date", ""),
                        "document_type": source.get("document_type", ""),
                        "tokens": _tokens(chunk["text"]),
                        "title_tokens": _tokens(title),
                        "source_id_tokens": _tokens(source_id),
                    })
                self.indexed_sources += 1
        self._records = records
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = cache_path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps({
            "cache_version": 4, "source_hashes": source_hashes,
            "indexed_sources": self.indexed_sources,
            "skipped_sources": self.skipped_sources,
            "records": records,
        }, ensure_ascii=False), encoding="utf-8")
        temporary.replace(cache_path)
        return records

    @staticmethod
    def _coverage(query_tokens: list[str], record: dict[str, Any], document_frequency: dict[str, int], total: int) -> float:
        if not query_tokens:
            return 0.0
        weights = {term: math.log(1.0 + (total + 1) / (document_frequency.get(term, 0) + 1)) for term in set(query_tokens)}
        denominator = sum(weights.values())
        text_terms = set(record["tokens"])
        title_terms = set(record["title_tokens"])
        source_terms = set(record.get("source_id_tokens", _tokens(record["source_id"])))
        text_coverage = sum(weight for term, weight in weights.items() if term in text_terms) / denominator
        title_coverage = sum(weight for term, weight in weights.items() if term in title_terms) / denominator
        source_coverage = sum(weight for term, weight in weights.items() if term in source_terms) / denominator
        # Source identity and document titles are stronger relevance evidence than
        # isolated mentions inside a large unrelated report.
        return (0.55 * title_coverage + 0.25 * source_coverage + 0.2 * text_coverage) if denominator else 0.0

    def _frequencies(self, records: list[dict[str, Any]]) -> dict[str, int]:
        if self._document_frequency is None:
            frequency: dict[str, int] = {}
            for record in records:
                for token in set(record["tokens"]) | set(record["title_tokens"]) | set(record.get("source_id_tokens", [])):
                    frequency[token] = frequency.get(token, 0) + 1
            self._document_frequency = frequency
        return self._document_frequency

    def retrieve(self, query: str) -> list[dict[str, Any]]:
        records = self._load()
        query_tokens, requested_numbers = _query_terms(query)
        if not records or not query_tokens:
            return []
        df = self._frequencies(records)
        scored = [(self._coverage(query_tokens, record, df, len(records)), record) for record in records]
        if requested_numbers:
            scored = [
                (score, record) for score, record in scored
                if any(re.search(rf"\bPSI[-\s]?{number}(?:\b|[-_])", record["source_id"], re.IGNORECASE)
                       for number in requested_numbers)
            ]
        scored.sort(key=lambda pair: (-pair[0], pair[1]["chunk_id"]))
        threshold = self._threshold
        if threshold is None:
            calibration_path = self.root / "ai/evaluation/local_retrieval_calibration.json"
            try:
                calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
                if calibration.get("status") == "calibrated":
                    threshold = float(calibration["threshold"])
                    self._threshold = threshold
            except (OSError, ValueError, TypeError):
                threshold = None
        if threshold is None:
            return []
        accepted = []
        seen = set()
        seen_sources = set()
        for score, record in scored:
            if (score < threshold or record["chunk_id"] in seen
                    or (not requested_numbers and record["source_id"] in seen_sources)):
                continue
            seen.add(record["chunk_id"])
            seen_sources.add(record["source_id"])
            accepted.append({
                "citation_id": record["chunk_id"], "text": record["text"],
                "similarity": score, "page": record["page_number"],
                "location_label": record.get("location_label", f"page {record['page_number']}"),
                "source_id": record["source_id"], "title": record["title"],
                "source_uri": record["uri"], "review_status": "unreviewed",
                "content_hash": record["content_hash"],
                "publication_date": record["publication_date"],
                "document_type": record["document_type"],
            })
            if len(accepted) >= 4:
                break
        return accepted

    def evaluate_case(self, query: str, expected_source_ids: list[str]) -> dict[str, Any]:
        records = self._load()
        tokens, requested_numbers = _query_terms(query)
        df = self._frequencies(records)
        scored = [(self._coverage(tokens, record, df, len(records)), record["source_id"]) for record in records]
        if requested_numbers:
            scored = [
                (score, source) for score, source in scored
                if any(re.search(rf"\bPSI[-\s]?{number}(?:\b|[-_])", source, re.IGNORECASE)
                       for number in requested_numbers)
            ]
        expected = [score for score, source in scored if source in expected_source_ids]
        return {
            "expected_best": max(expected, default=0.0),
            "best_any": max((score for score, _ in scored), default=0.0),
            "expected_is_top": bool(expected) and max(expected) >= max((score for score, _ in scored), default=0.0),
            "top_sources": [
                {"source_id": source, "score": score}
                for score, source in sorted(scored, key=lambda row: (-row[0], row[1]))[:5]
            ],
            "top_distinct_sources": list(dict.fromkeys(
                source for _, source in sorted(scored, key=lambda row: (-row[0], row[1]))
            ))[:4],
        }


@lru_cache(maxsize=1)
def local_psi_corpus(repo_root: str) -> LocalPSICorpus:
    return LocalPSICorpus(repo_root)
