"""Traceable, conservative data harmonisation helpers for FlameBound.

This module does not infer outcomes or repair ambiguous source values. Raw source
strings should remain stored alongside every converted value.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from typing import Any, Mapping, Sequence

OUTCOME_LABELS = {
    "sustained_spread", "extinction", "blow_off", "ignition_failure",
    "other", "ambiguous", "unknown",
}


def _numeric_or_none(value: Any) -> float | None:
    """Parse one numeric scalar. Blank and explicit missing tokens stay missing."""
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError("Boolean values are not measurements")
    if isinstance(value, str):
        value = value.strip()
        if value.lower() in {"", "n/a", "na", "none", "null", "not reported", "-", "--"}:
            return None
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Expected one numeric scalar, got {value!r}") from exc
    if not math.isfinite(number):
        raise ValueError("Measurement must be finite")
    return number


def oxygen_fraction(
    value: Any, source_unit: str, *, volume_percent_is_mole_fraction: bool = False
) -> float | None:
    """Convert fraction directly; convert vol% only after gas-basis equivalence is verified."""
    if not isinstance(volume_percent_is_mole_fraction, bool):
        raise TypeError("volume_percent_is_mole_fraction must be a boolean")
    number = _numeric_or_none(value)
    if number is None:
        return None
    unit = source_unit.strip().lower().replace(" ", "")
    if unit in {"fraction", "molefraction", "mol/mol"}:
        if not 0 <= number <= 1:
            raise ValueError("Fraction must be in [0, 1]")
        return number
    if unit in {"vol%", "%v/v", "percentbyvolume"}:
        if not volume_percent_is_mole_fraction:
            raise ValueError("Volume-percent to mole-fraction equivalence must be verified")
        if not 0 <= number <= 100:
            raise ValueError("Percent must be in [0, 100]")
        return number / 100
    raise ValueError(f"Unrecognized or insufficiently defined oxygen unit: {source_unit!r}")


def pressure_kpa(value: Any, source_unit: str, basis: str) -> float | None:
    """Convert absolute pressure to kPa; gauge/unspecified basis is rejected."""
    number = _numeric_or_none(value)
    if number is None:
        return None
    if basis.strip().lower() != "absolute":
        raise ValueError("Pressure basis must be verified as absolute")
    unit = source_unit.strip().lower().replace(" ", "")
    factors = {
        "pa": 0.001,
        "kpa": 1.0,
        "bar": 100.0,
        "atm": 101.325,
        "psi": 6.894757293168361,
    }
    if unit not in factors:
        raise ValueError(f"Unrecognized pressure unit: {source_unit!r}")
    if number <= 0:
        raise ValueError("Absolute pressure must be positive")
    return number * factors[unit]


def speed_m_s(value: Any, source_unit: str) -> float | None:
    """Convert a single, explicitly unit-labeled speed to m/s."""
    number = _numeric_or_none(value)
    if number is None:
        return None
    unit = source_unit.strip().lower().replace(" ", "")
    factors = {"m/s": 1.0, "cm/s": 0.01, "mm/s": 0.001}
    if unit not in factors:
        raise ValueError(f"Unrecognized speed unit: {source_unit!r}")
    if number < 0:
        raise ValueError("Speed cannot be negative")
    return number * factors[unit]


def oxygen_partial_pressure_kpa(x_o2: Any, p_kpa: Any) -> float | None:
    """Derive pO2 only when both normalized inputs are present and valid."""
    fraction = _numeric_or_none(x_o2)
    pressure = _numeric_or_none(p_kpa)
    if fraction is None or pressure is None:
        return None
    if not 0 <= fraction <= 1:
        raise ValueError("Oxygen fraction must be in [0, 1]")
    if pressure <= 0:
        raise ValueError("Absolute pressure must be positive")
    return fraction * pressure


def classify_outcome(
    outcome_raw: Any,
    definition_verified: bool,
    exact_mapping: Mapping[str, str] | None = None,
) -> str:
    """Map only exact reviewed source labels; never infer an outcome by default."""
    if outcome_raw is None or not str(outcome_raw).strip():
        return "unknown"
    if not definition_verified:
        return "unknown"
    mapping = {str(k).strip().casefold(): v for k, v in (exact_mapping or {}).items()}
    mapped = mapping.get(str(outcome_raw).strip().casefold())
    if mapped is None:
        return "ambiguous"
    if mapped not in OUTCOME_LABELS:
        raise ValueError(f"Unsupported outcome label: {mapped!r}")
    return mapped


def flag_duplicate_records(
    records: Sequence[Mapping[str, Any]], key_fields: Sequence[str]
) -> list[dict[str, Any]]:
    """Return all records in source order with duplicate flags; never deduplicate."""
    if not key_fields:
        raise ValueError("At least one duplicate-key field is required")
    keys = [tuple(json.dumps(row.get(k), ensure_ascii=False, sort_keys=True) for k in key_fields) for row in records]
    counts = Counter(keys)
    return [
        {**dict(row), "duplicate_source_record": counts[key] > 1, "duplicate_group_size": counts[key]}
        for row, key in zip(records, keys)
    ]
