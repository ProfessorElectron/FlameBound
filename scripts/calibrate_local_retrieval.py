"""Calibrate local PSI lexical retrieval against labeled source-level cases."""

from __future__ import annotations

import json
from pathlib import Path

from ai.local_corpus import LocalPSICorpus


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "ai/evaluation/retrieval_cases.json"
OUTPUT = ROOT / "ai/evaluation/local_retrieval_calibration.json"
POSITIVE = {"relevant", "partially_relevant"}
NEGATIVE = {"unrelated", "absent"}


def main() -> int:
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    corpus = LocalPSICorpus(ROOT)
    cases = dataset["cases"]
    positive_scores = []
    negative_scores = []
    expected_ranked = True
    expected_in_top_k = []
    for case in cases:
        result = corpus.evaluate_case(case["query"], case["expected_source_ids"])
        label = case["label"]
        if label in POSITIVE:
            positive_scores.append(result["expected_best"])
            expected_ranked = expected_ranked and result["expected_is_top"]
            expected_in_top_k.append(bool(set(case["expected_source_ids"]) & set(result["top_distinct_sources"])))
        elif label in NEGATIVE:
            negative_scores.append(result["best_any"])
        else:
            raise ValueError(f"Unsupported relevance label: {label}")
        print(f"{case['id']}: label={label} expected={result['expected_best']:.4f} best={result['best_any']:.4f} top={result['top_sources']}")

    payload = {
        "dataset_version": dataset.get("dataset_version"),
        "status": "pending",
        "retrieval_method": "IDF-weighted query-term coverage over verified local file chunks",
        "threshold": None,
        "method": "Midpoint between the highest negative-case score and lowest positive expected-source score; zero false positives on labeled cases.",
        "positive_cases": len(positive_scores),
        "negative_cases": len(negative_scores),
        "indexed_sources": corpus.indexed_sources,
        "expected_source_ranked_first": expected_ranked,
        "expected_source_top4_recall": sum(expected_in_top_k) / len(expected_in_top_k) if expected_in_top_k else 0.0,
        "reason": "Labeled positive and negative scores are not separable, or a labeled expected source is outside the top four distinct sources.",
        "ranking_note": "A known expected source may not be the only top result; retrieved passages remain unreviewed and must not be treated as verified evidence.",
        "limitations": "Provisional source-level labels. Threshold reports zero false positives only on the labeled unrelated/absent queries; the dataset is small and does not guarantee relevance for every query.",
    }
    if positive_scores and negative_scores and expected_in_top_k and all(expected_in_top_k):
        max_negative = max(negative_scores)
        min_positive = min(positive_scores)
        if max_negative < min_positive:
            threshold = (max_negative + min_positive) / 2
            payload.update({
                "status": "calibrated",
                "threshold": threshold,
                "positive_recall": sum(score >= threshold for score in positive_scores) / len(positive_scores),
                "false_positive_rate": sum(score >= threshold for score in negative_scores) / len(negative_scores),
                "max_negative_score": max_negative,
                "min_positive_score": min_positive,
                "reason": "",
            })
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"extraction_skips={corpus.skipped_sources}")
    return 0 if payload["status"] == "calibrated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
