"""Choose a retrieval threshold only from labeled scores and a zero-FP gate."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

POSITIVE = {"relevant", "partially_relevant"}
NEGATIVE = {"unrelated", "absent"}


def calibrate_threshold(observations: list[dict[str, Any]], *, embedding_model: str) -> dict[str, Any]:
    """Find the lowest zero-false-positive threshold; abstain if not separable."""
    positives = [float(row["score"]) for row in observations if row.get("label") in POSITIVE]
    negatives = [float(row["score"]) for row in observations if row.get("label") in NEGATIVE]
    if not positives or not negatives or any(not math.isfinite(x) for x in positives + negatives):
        return {"status": "pending", "embedding_model": embedding_model, "threshold": None,
                "reason": "Both positive and negative labeled score examples are required."}
    max_negative = max(negatives)
    min_positive = min(positives)
    if max_negative >= min_positive:
        return {"status": "pending", "embedding_model": embedding_model, "threshold": None,
                "reason": "Labeled positive and negative scores are not separable without false support."}
    threshold = (max_negative + min_positive) / 2
    accepted = sum(score >= threshold for score in positives)
    return {
        "status": "calibrated", "embedding_model": embedding_model,
        "threshold": threshold,
        "method": "midpoint between the maximum negative and minimum positive score; zero false positives on calibration set",
        "positive_examples": len(positives), "negative_examples": len(negatives),
        "positive_recall": accepted / len(positives), "false_positive_rate": 0.0,
    }


def evaluate_labeled_dataset(dataset_path: str | Path, retrieved_scores: dict[str, list[dict[str, Any]]], *,
                            embedding_model: str) -> dict[str, Any]:
    dataset = json.loads(Path(dataset_path).read_text(encoding="utf-8"))
    rows = []
    for case in dataset["cases"]:
        if case["id"] not in retrieved_scores:
            raise ValueError(f"Missing retrieval results for case {case['id']}")
        results = retrieved_scores[case["id"]]
        expected = set(case["expected_source_ids"])
        expected_scores = [float(item["similarity"]) for item in results if item.get("source_id") in expected]
        distractor_scores = [float(item["similarity"]) for item in results if item.get("source_id") not in expected]
        if case["label"] in POSITIVE and expected:
            if expected_scores:
                rows.append({"label": case["label"], "score": max(expected_scores)})
            else:
                # Missing expected source is a retrieval miss, not an invented low score.
                rows.append({"label": case["label"], "score": -1.0})
        elif case["label"] not in NEGATIVE:
            raise ValueError(f"Unknown evaluation label {case['label']}")
        for score in distractor_scores:
            rows.append({"label": "unrelated", "score": score})
        if case["label"] in NEGATIVE:
            rows.append({"label": case["label"],
                         "score": max((float(item["similarity"]) for item in results), default=-1.0)})
    return calibrate_threshold(rows, embedding_model=embedding_model)
