"""Atmospheric calculations with explicit units and mixture assumptions.

Oxygen fractions are mole fractions in [0, 1]. Pressure inputs are absolute
pressure values. ``oxygen_mass_fraction`` assumes a binary O2/balance-gas
mixture unless the caller supplies an explicitly chosen mean molar mass for
the balance gas.
"""

from __future__ import annotations

import math
from typing import TypedDict


_PRESSURE_TO_KPA = {
    "pa": 0.001,
    "kpa": 1.0,
    "mpa": 1000.0,
    "bar": 100.0,
    "atm": 101.325,
    "psi": 6.894757293168,
}

_PRESSURE_ALIASES = {
    "pascal": "pa",
    "pascals": "pa",
    "kilopascal": "kpa",
    "kilopascals": "kpa",
    "megapascal": "mpa",
    "megapascals": "mpa",
    "atmosphere": "atm",
    "atmospheres": "atm",
}


class AtmosphereSummary(TypedDict):
    oxygen_fraction: float
    total_pressure_kpa: float
    oxygen_partial_pressure_kpa: float


def _finite_number(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _oxygen_fraction(value: float) -> float:
    fraction = _finite_number("oxygen_fraction", value)
    if not 0.0 <= fraction <= 1.0:
        raise ValueError("oxygen_fraction must be between 0 and 1 inclusive")
    return fraction


def _pressure_unit(unit: str) -> str:
    if not isinstance(unit, str):
        raise TypeError("pressure unit must be a string")
    normalized = unit.strip().lower().replace(" ", "")
    normalized = _PRESSURE_ALIASES.get(normalized, normalized)
    if normalized not in _PRESSURE_TO_KPA:
        supported = ", ".join(_PRESSURE_TO_KPA)
        raise ValueError(f"unsupported pressure unit {unit!r}; use one of: {supported}")
    return normalized


def convert_pressure(value: float, from_unit: str, to_unit: str) -> float:
    """Convert positive absolute pressure between Pa, kPa, MPa, bar, atm, psi.

    Returns a float in ``to_unit``. Gauge pressure is not supported.
    """
    pressure = _finite_number("pressure", value)
    if pressure <= 0:
        raise ValueError("absolute pressure must be greater than zero")
    source = _pressure_unit(from_unit)
    target = _pressure_unit(to_unit)
    return pressure * _PRESSURE_TO_KPA[source] / _PRESSURE_TO_KPA[target]


def oxygen_partial_pressure(oxygen_fraction: float, total_pressure: float) -> float:
    """Return oxygen partial pressure in the same unit as ``total_pressure``.

    ``oxygen_fraction`` is a mole fraction, not a percentage from 0 to 100.
    The pressure must be an absolute pressure greater than zero.
    """
    fraction = _oxygen_fraction(oxygen_fraction)
    pressure = _finite_number("total_pressure", total_pressure)
    if pressure <= 0:
        raise ValueError("total_pressure must be an absolute pressure greater than zero")
    return fraction * pressure


def oxygen_mass_fraction(
    oxygen_fraction: float,
    diluent_molar_mass_g_mol: float = 28.014,
    oxygen_molar_mass_g_mol: float = 31.998,
) -> float:
    """Convert O2 mole fraction to mass fraction for a binary gas mixture.

    The balance gas is treated as one species with the supplied molar mass.
    For a mixture with multiple diluents, pass their mole-fraction-weighted
    mean molar mass or extend this calculation to use the full composition.
    Molar masses use g/mol; the result is a dimensionless mass fraction.
    """
    fraction = _oxygen_fraction(oxygen_fraction)
    diluent_mass = _finite_number("diluent_molar_mass_g_mol", diluent_molar_mass_g_mol)
    oxygen_mass = _finite_number("oxygen_molar_mass_g_mol", oxygen_molar_mass_g_mol)
    if diluent_mass <= 0 or oxygen_mass <= 0:
        raise ValueError("molar masses must be greater than zero")
    oxygen_mass_in_mixture = fraction * oxygen_mass
    total_mass_per_mole_of_mixture = (
        oxygen_mass_in_mixture + (1.0 - fraction) * diluent_mass
    )
    return oxygen_mass_in_mixture / total_mass_per_mole_of_mixture


def _atmosphere_summary(
    oxygen_fraction: float, total_pressure: float, pressure_unit: str
) -> AtmosphereSummary:
    fraction = _oxygen_fraction(oxygen_fraction)
    pressure_kpa = convert_pressure(total_pressure, pressure_unit, "kPa")
    return {
        "oxygen_fraction": fraction,
        "total_pressure_kpa": pressure_kpa,
        "oxygen_partial_pressure_kpa": fraction * pressure_kpa,
    }


def compare_atmospheres(
    oxygen_fraction: float,
    total_pressure: float,
    reference_oxygen_fraction: float,
    reference_pressure: float,
    pressure_unit: str = "kPa",
    reference_pressure_unit: str | None = None,
) -> dict[str, AtmosphereSummary | float | None]:
    """Compare two atmospheres using oxygen partial pressure in kPa.

    ``relative_difference`` is (scenario - reference) / reference. It is
    ``None`` when the reference oxygen partial pressure is zero.
    """
    scenario = _atmosphere_summary(oxygen_fraction, total_pressure, pressure_unit)
    reference = _atmosphere_summary(
        reference_oxygen_fraction,
        reference_pressure,
        reference_pressure_unit or pressure_unit,
    )
    difference = (
        scenario["oxygen_partial_pressure_kpa"]
        - reference["oxygen_partial_pressure_kpa"]
    )
    reference_partial_pressure = reference["oxygen_partial_pressure_kpa"]
    relative_difference = (
        difference / reference_partial_pressure
        if reference_partial_pressure != 0.0
        else None
    )
    return {
        "scenario": scenario,
        "reference": reference,
        "oxygen_partial_pressure_difference_kpa": difference,
        "relative_oxygen_partial_pressure_difference": relative_difference,
    }
