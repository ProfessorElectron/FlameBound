
"""Evidence coverage calculations for mixed experimental datasets."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class FeatureSpec:
    """Defines how one experimental feature is compared."""

    name: str
    kind: str
    weight: float = 1.0
    minimum: float | None = None
    maximum: float | None = None

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Feature name must be a non-empty string")

        if self.kind not in ("numeric", "categorical"):
            raise ValueError("Feature kind must be numeric or categorical")

        if isinstance(self.weight, bool) or not isinstance(
            self.weight, (int, float)
        ):
            raise ValueError("Feature weight must be numeric")

        if not math.isfinite(self.weight) or self.weight <= 0:
            raise ValueError("Feature weight must be finite and positive")

        if self.kind == "numeric":
            if self.minimum is None or self.maximum is None:
                raise ValueError("Numeric features require minimum and maximum")

            if (
                isinstance(self.minimum, bool)
                or not isinstance(self.minimum, (int, float))
                or not math.isfinite(self.minimum)
            ):
                raise ValueError("Minimum must be finite and numeric")

            if (
                isinstance(self.maximum, bool)
                or not isinstance(self.maximum, (int, float))
                or not math.isfinite(self.maximum)
            ):
                raise ValueError("Maximum must be finite and numeric")

            if self.maximum < self.minimum:
                raise ValueError("Maximum cannot be less than minimum")
        else:
           if self.minimum is not None or self.maximum is not None:
               raise ValueError(
            "Categorical features cannot have numeric ranges"
           )

def gower_distance(record_a, record_b, features):
    """Calculate weighted Gower distance between two records."""

    features = tuple(features)

    feature_names = [feature.name for feature in features]

    if len(feature_names) != len(set(feature_names)):
        raise ValueError("Feature names must be unique")

    total_weight = 0.0
    compared_weight = 0.0
    weighted_distance = 0.0

    for feature in features:
        total_weight += feature.weight

        value_a = record_a.get(feature.name)
        value_b = record_b.get(feature.name)

        # Missing values are excluded from this comparison.
        if value_a is None or value_b is None:
            continue

        if feature.kind == "numeric":
            for value in (value_a, value_b):
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not math.isfinite(value)
                ):
                    raise ValueError(
                        f"{feature.name} must contain finite numeric values"
                    )

                if not feature.minimum <= value <= feature.maximum:
                    raise ValueError(
                        f"{feature.name} is outside its reference range"
                    )

            reference_range = feature.maximum - feature.minimum

            if reference_range == 0:
                difference = 0.0
            else:
                difference = abs(value_a - value_b) / reference_range

        else:
            difference = 0.0 if value_a == value_b else 1.0

        weighted_distance += feature.weight * difference
        compared_weight += feature.weight

    if total_weight == 0:
        raise ValueError("At least one feature must be provided")

    if compared_weight == 0:
        distance = None
    else:
        distance = weighted_distance / compared_weight

    return {
        "distance": distance,
        "compared_weight_fraction": compared_weight / total_weight,
    }

def nearest_neighbours(
    scenario,
    experiments,
    features,
    k=3,
    min_compared_weight_fraction=0.0,
):
    """Return the k closest comparable experimental records."""

    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")
        if (
           isinstance(min_compared_weight_fraction, bool)
           or not isinstance(min_compared_weight_fraction, (int, float))
           or not math.isfinite(min_compared_weight_fraction)
           or not 0.0 <= min_compared_weight_fraction <= 1.0
        ):
           raise ValueError(
                  "min_compared_weight_fraction must be between 0 and 1"
           )

    results = []

    for experiment in experiments:
        if "record_id" not in experiment:
            raise ValueError("Every experiment must have a record_id")

        comparison = gower_distance(
            scenario,
            experiment,
            features,
        )

        # Skip records with no comparable features.
        if comparison["distance"] is None:
            continue
        if (
            comparison["compared_weight_fraction"]
            < min_compared_weight_fraction
        ):
            continue

        results.append({
            "record_id": experiment["record_id"],
            "distance": comparison["distance"],
            "compared_weight_fraction": (
                comparison["compared_weight_fraction"]
            ),
        })

    # Sort from smallest distance to largest distance.
    results.sort(key=lambda item: item["distance"])

    return results[:k]

def filter_eligible_experiments(experiments, requirements):
    """Separate eligible experiments from excluded ones.

    Eligibility requires exact matches for every field specified
    in requirements. Missing values are treated as incompatible.
    """

    if not isinstance(requirements, dict) or not requirements:
        raise ValueError("Requirements must be a non-empty dictionary")

    eligible = []
    excluded = []

    for experiment in experiments:
        if not isinstance(experiment, dict):
            raise TypeError("Every experiment must be a dictionary")

        if "record_id" not in experiment:
            raise ValueError("Every experiment must have a record_id")

        reasons = []

        for field, required_value in requirements.items():
            actual_value = experiment.get(field)

            if actual_value is None or actual_value != required_value:
                reasons.append(field)

        if reasons:
            excluded.append({
                "record_id": experiment["record_id"],
                "reasons": reasons,
            })
        else:
            eligible.append(experiment)

    return {
        "eligible": eligible,
        "excluded": excluded,
    }
