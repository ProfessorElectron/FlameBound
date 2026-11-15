"""Deterministic atmospheric calculations with units and provenance.

The low-level functions retain the original numeric APIs. New integrations
should use :class:`AtmosphericCondition` and the ``calculate_*`` functions to
receive validated inputs and JSON-compatible, provenance-aware results.

All pressure inputs are absolute. Oxygen partial pressure uses Dalton's law,
``p_O2 = X_O2 * P``; the supplied oxygen value must be a verified gas-phase
mole fraction. Binary oxygen mass fraction requires an explicitly supplied,
verified diluent composition.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, TypedDict


# Conversion factors to kPa. 1 atm = 101325 Pa; 1 bar = 100000 Pa;
# 1 psi = 6894.757293168361 Pa (international avoirdupois pound/in^2).
# Calculations use IEEE-754 binary64 floats and do not round intermediate values.
_PRESSURE_TO_KPA = {
    "pa": 0.001,
    "kpa": 1.0,
    "mpa": 1000.0,  # retained for compatibility with the original function
    "bar": 100.0,
    "atm": 101.325,
    "psi": 6.894757293168361,
}


class PressureUnit(str, Enum):
    PA = "Pa"
    KPA = "kPa"
    BAR = "bar"
    ATM = "atm"
    PSI = "psi"
    MPA = "MPa"  # backward-compatible additional unit


class PressureBasis(str, Enum):
    ABSOLUTE = "absolute"


class VerificationStatus(str, Enum):
    MEASURED = "MEASURED"
    DERIVED = "DERIVED"
    MODELLED = "MODELLED"
    INFERRED = "INFERRED"
    UNVERIFIED = "UNVERIFIED"
    MISSING = "MISSING"


class InputOrigin(str, Enum):
    USER_SUPPLIED = "user_supplied"
    SOURCE_RECORD = "source_record"
    DERIVED = "derived"
    OTHER = "other"


@dataclass(frozen=True)
class InputProvenance:
    """Origin/status plus source raw value and its normalization metadata."""

    origin: InputOrigin = InputOrigin.USER_SUPPLIED
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    source_id: str | None = None
    source_locator: str | None = None
    raw_value: str | float | int | bool | None = None
    raw_unit: str | None = None
    normalization_method: str | None = None
    note: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "origin", InputOrigin(self.origin))
        object.__setattr__(
            self, "verification_status", VerificationStatus(self.verification_status)
        )
        if self.origin is InputOrigin.SOURCE_RECORD and not self.source_id:
            raise ValueError("source_id is required for source-record provenance")
        if self.verification_status is VerificationStatus.MEASURED:
            if self.origin is not InputOrigin.SOURCE_RECORD:
                raise ValueError("MEASURED inputs require source-record provenance")
            if not self.source_locator:
                raise ValueError("MEASURED inputs require a source locator")
        if not isinstance(self.raw_value, (str, int, float, bool, type(None))):
            raise TypeError("Provenance raw_value must be a JSON scalar")
        if isinstance(self.raw_value, float) and not math.isfinite(self.raw_value):
            raise ValueError("Provenance raw_value must be finite when numeric")
        for field_name in ("source_id", "source_locator", "raw_unit", "normalization_method", "note"):
            field_value = getattr(self, field_name)
            if field_value is not None and not isinstance(field_value, str):
                raise TypeError(f"{field_name} must be a string or None")

    def to_dict(self) -> dict[str, Any]:
        return {
            "origin": self.origin.value,
            "verification_status": self.verification_status.value,
            "source_id": self.source_id,
            "source_locator": self.source_locator,
            "raw_value": self.raw_value,
            "raw_unit": self.raw_unit,
            "normalization_method": self.normalization_method,
            "note": self.note,
        }


@dataclass(frozen=True)
class BinaryDiluent:
    """Explicit one-component balance gas for a binary O2/diluent mixture."""

    name: str
    molar_mass_g_mol: float
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    provenance: InputProvenance = field(default_factory=InputProvenance)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Diluent name must be a non-empty string")
        if not isinstance(self.provenance, InputProvenance):
            raise TypeError("Diluent provenance must be an InputProvenance")
        object.__setattr__(
            self, "verification_status", VerificationStatus(self.verification_status)
        )
        if self.provenance.verification_status is not self.verification_status:
            raise ValueError("Diluent provenance and verification status must agree")
        mass = _finite_number("diluent_molar_mass_g_mol", self.molar_mass_g_mol)
        if mass <= 0:
            raise ValueError("Diluent molar mass must be greater than zero")
        object.__setattr__(self, "molar_mass_g_mol", mass)


@dataclass(frozen=True)
class AtmosphericCondition:
    """One atmospheric state, with explicit units, basis and provenance."""

    oxygen_mole_fraction: float
    total_pressure: float
    pressure_unit: PressureUnit | str
    pressure_basis: PressureBasis | str
    gas_basis_verified: bool = False
    oxygen_verification: VerificationStatus = VerificationStatus.UNVERIFIED
    pressure_verification: VerificationStatus = VerificationStatus.UNVERIFIED
    diluent: BinaryDiluent | None = None
    provenance: Mapping[str, InputProvenance] = field(default_factory=dict)

    def __post_init__(self) -> None:
        fraction = _oxygen_fraction(self.oxygen_mole_fraction)
        pressure = _finite_number("total_pressure", self.total_pressure)
        if pressure <= 0:
            raise ValueError("total_pressure must be an absolute pressure greater than zero")
        unit = _pressure_unit(self.pressure_unit.value if isinstance(self.pressure_unit, PressureUnit) else self.pressure_unit)
        object.__setattr__(self, "oxygen_mole_fraction", fraction)
        object.__setattr__(self, "total_pressure", pressure)
        unit_enum = {
            "pa": PressureUnit.PA,
            "kpa": PressureUnit.KPA,
            "mpa": PressureUnit.MPA,
            "bar": PressureUnit.BAR,
            "atm": PressureUnit.ATM,
            "psi": PressureUnit.PSI,
        }[unit]
        object.__setattr__(self, "pressure_unit", unit_enum)
        try:
            pressure_basis = PressureBasis(self.pressure_basis)
        except (TypeError, ValueError) as exc:
            raise ValueError("pressure_basis must be explicitly 'absolute'") from exc
        object.__setattr__(self, "pressure_basis", pressure_basis)
        object.__setattr__(
            self, "oxygen_verification", VerificationStatus(self.oxygen_verification)
        )
        object.__setattr__(
            self, "pressure_verification", VerificationStatus(self.pressure_verification)
        )
        if not isinstance(self.gas_basis_verified, bool):
            raise TypeError("gas_basis_verified must be a boolean")
        if self.diluent is not None and not isinstance(self.diluent, BinaryDiluent):
            raise TypeError("diluent must be a BinaryDiluent or None")
        if not isinstance(self.provenance, Mapping):
            raise TypeError("provenance must be a mapping of field names to InputProvenance")
        for key, value in self.provenance.items():
            if not isinstance(key, str) or not isinstance(value, InputProvenance):
                raise TypeError("provenance values must be InputProvenance objects")
        oxygen_source = self.provenance.get("oxygen_mole_fraction")
        if oxygen_source and oxygen_source.raw_unit:
            raw_unit = oxygen_source.raw_unit.strip().lower().replace(" ", "")
            if raw_unit in {"%", "percent", "vol%", "%v/v", "percentbyvolume"} and not oxygen_source.normalization_method:
                raise ValueError("Oxygen percentage provenance requires a normalization method")
        pressure_source = self.provenance.get("total_pressure")
        if pressure_source and pressure_source.raw_unit:
            if _pressure_unit(pressure_source.raw_unit) != unit and not pressure_source.normalization_method:
                raise ValueError("Pressure provenance requires a normalization method when units differ")
        for field_name, status in (
            ("oxygen_mole_fraction", self.oxygen_verification),
            ("total_pressure", self.pressure_verification),
        ):
            if status is VerificationStatus.MISSING:
                raise ValueError(f"{field_name} has a numeric value and cannot be marked MISSING")
            if status is VerificationStatus.MEASURED:
                provenance = self.provenance.get(field_name)
                if provenance is None or provenance.verification_status is not VerificationStatus.MEASURED:
                    raise ValueError(f"MEASURED {field_name} requires matching source provenance")
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))


@dataclass(frozen=True)
class OxygenComposition:
    """Oxygen/diluent composition without unrelated pressure requirements."""

    oxygen_mole_fraction: float
    gas_basis_verified: bool
    diluent: BinaryDiluent | None = None
    oxygen_verification: VerificationStatus = VerificationStatus.UNVERIFIED
    provenance: Mapping[str, InputProvenance] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "oxygen_mole_fraction", _oxygen_fraction(self.oxygen_mole_fraction))
        object.__setattr__(
            self, "oxygen_verification", VerificationStatus(self.oxygen_verification)
        )
        if not isinstance(self.gas_basis_verified, bool):
            raise TypeError("gas_basis_verified must be a boolean")
        if self.oxygen_verification is VerificationStatus.MISSING:
            raise ValueError("oxygen_mole_fraction has a value and cannot be marked MISSING")
        if self.diluent is not None and not isinstance(self.diluent, BinaryDiluent):
            raise TypeError("diluent must be a BinaryDiluent or None")
        if not isinstance(self.provenance, Mapping):
            raise TypeError("provenance must be a mapping of field names to InputProvenance")
        for key, value in self.provenance.items():
            if not isinstance(key, str) or not isinstance(value, InputProvenance):
                raise TypeError("provenance values must be InputProvenance objects")
        evidence = self.provenance.get("oxygen_mole_fraction")
        if evidence and evidence.raw_unit:
            raw_unit = evidence.raw_unit.strip().lower().replace(" ", "")
            if raw_unit in {"%", "percent", "vol%", "%v/v", "percentbyvolume"} and not evidence.normalization_method:
                raise ValueError("Oxygen percentage provenance requires a normalization method")
        if self.oxygen_verification is VerificationStatus.MEASURED:
            if evidence is None or evidence.verification_status is not VerificationStatus.MEASURED:
                raise ValueError("MEASURED oxygen_mole_fraction requires matching source provenance")
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))


@dataclass(frozen=True)
class CalculationResult:
    """JSON-compatible envelope for a deterministic scientific calculation."""

    calculation: str
    formula: str
    inputs: Mapping[str, Any]
    outputs: Mapping[str, Any]
    units: Mapping[str, str]
    verification: Mapping[str, str]
    conversion_methods: Mapping[str, str] = field(default_factory=dict)
    provenance: Mapping[str, Any] = field(default_factory=dict)
    assumptions: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    status: str = "success"

    def to_dict(self) -> dict[str, Any]:
        """Return values containing only JSON-compatible primitives/containers."""
        return {
            "status": self.status,
            "calculation": self.calculation,
            "formula": self.formula,
            "inputs": _json_value(self.inputs),
            "outputs": _json_value(self.outputs),
            "units": _json_value(self.units),
            "verification": _json_value(self.verification),
            "conversion_methods": _json_value(self.conversion_methods),
            "provenance": _json_value(self.provenance),
            "assumptions": _json_value(self.assumptions),
            "limitations": _json_value(self.limitations),
            "warnings": _json_value(self.warnings),
        }


class AtmosphereSummary(TypedDict):
    oxygen_fraction: float
    total_pressure_kpa: float
    oxygen_partial_pressure_kpa: float


def _json_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, InputProvenance):
        return value.to_dict()
    if isinstance(value, BinaryDiluent):
        return {
            "name": value.name,
            "molar_mass_g_mol": value.molar_mass_g_mol,
            "verification_status": value.verification_status.value,
            "provenance": value.provenance.to_dict(),
        }
    if isinstance(value, AtmosphericCondition):
        return _condition_inputs(value)
    if isinstance(value, OxygenComposition):
        return _composition_inputs(value)
    if isinstance(value, Mapping):
        if any(not isinstance(k, str) for k in value):
            raise TypeError("JSON object keys must be strings")
        return {k: _json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(v) for v in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("JSON output cannot contain NaN or infinity")
        return value
    if isinstance(value, (str, int, bool, type(None))):
        return value
    raise TypeError(f"Unsupported JSON output value type: {type(value).__name__}")


def _condition_inputs(condition: AtmosphericCondition) -> dict[str, Any]:
    return {
        "oxygen_mole_fraction": condition.oxygen_mole_fraction,
        "total_pressure": condition.total_pressure,
        "pressure_unit": condition.pressure_unit.value,
        "pressure_basis": condition.pressure_basis.value,
        "gas_basis_verified": condition.gas_basis_verified,
        "oxygen_verification": condition.oxygen_verification.value,
        "pressure_verification": condition.pressure_verification.value,
        "diluent": _json_value(condition.diluent),
    }


def _composition_inputs(composition: OxygenComposition) -> dict[str, Any]:
    return {
        "oxygen_mole_fraction": composition.oxygen_mole_fraction,
        "gas_basis_verified": composition.gas_basis_verified,
        "oxygen_verification": composition.oxygen_verification.value,
        "diluent": _json_value(composition.diluent),
    }


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
        raise TypeError("pressure unit must be a string or PressureUnit")
    normalized = unit.strip().lower().replace(" ", "")
    aliases = {
        "pascal": "pa", "pascals": "pa", "kilopascal": "kpa",
        "kilopascals": "kpa", "megapascal": "mpa", "megapascals": "mpa",
        "atmosphere": "atm", "atmospheres": "atm",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in _PRESSURE_TO_KPA:
        supported = ", ".join(k for k in _PRESSURE_TO_KPA if k != "mpa")
        raise ValueError(f"unsupported pressure unit {unit!r}; use one of: {supported}")
    return normalized


def _provenance_dict(condition: AtmosphericCondition) -> dict[str, Any]:
    return {key: value.to_dict() for key, value in condition.provenance.items()}


def _oxygen_normalization_method(condition: AtmosphericCondition | OxygenComposition) -> str:
    evidence = condition.provenance.get("oxygen_mole_fraction")
    if evidence is not None and evidence.normalization_method:
        return evidence.normalization_method
    return "Input supplied as mole fraction; no scale conversion recorded."


def convert_pressure(value: float, from_unit: str | PressureUnit, to_unit: str | PressureUnit) -> float:
    """Convert positive absolute pressure between supported units.

    The return value uses ``to_unit``. Factors are defined in
    ``_PRESSURE_TO_KPA``; no intermediate rounding is applied. Gauge pressure
    is not supported.
    """
    pressure = _finite_number("pressure", value)
    if pressure <= 0:
        raise ValueError("absolute pressure must be greater than zero")
    source_value = from_unit.value if isinstance(from_unit, PressureUnit) else from_unit
    target_value = to_unit.value if isinstance(to_unit, PressureUnit) else to_unit
    source = _pressure_unit(source_value)
    target = _pressure_unit(target_value)
    factor = _PRESSURE_TO_KPA[source] / _PRESSURE_TO_KPA[target]
    result = pressure * factor
    if not math.isfinite(result):
        raise ValueError("Converted pressure is outside the finite numeric range")
    if result == 0.0:
        raise ValueError("Converted pressure underflows the finite numeric range")
    return result


def oxygen_partial_pressure(oxygen_fraction: float, total_pressure: float) -> float:
    """Return pO2 in the same pressure unit as ``total_pressure``.

    The oxygen value must be a mole fraction in [0,1], and pressure must be
    positive and absolute. Use ``calculate_oxygen_partial_pressure`` when an
    explicit gas-basis gate and provenance-bearing result are required.
    """
    fraction = _oxygen_fraction(oxygen_fraction)
    pressure = _finite_number("total_pressure", total_pressure)
    if pressure <= 0:
        raise ValueError("total_pressure must be an absolute pressure greater than zero")
    result = fraction * pressure
    if fraction > 0.0 and result == 0.0:
        raise ValueError("Oxygen partial pressure underflows the finite numeric range")
    return result


def oxygen_mass_fraction(
    oxygen_fraction: float,
    diluent_molar_mass_g_mol: float | None = None,
    oxygen_molar_mass_g_mol: float = 31.998,
    *,
    diluent_verified: bool = False,
) -> float:
    """Calculate mass fraction for an explicitly verified binary mixture.

    ``diluent_molar_mass_g_mol`` has no assumed default. For structured use,
    prefer :func:`calculate_oxygen_mass_fraction` with a verified
    :class:`BinaryDiluent`.
    """
    fraction = _oxygen_fraction(oxygen_fraction)
    if diluent_molar_mass_g_mol is None:
        raise ValueError("An explicit diluent molar mass is required")
    if not isinstance(diluent_verified, bool):
        raise TypeError("diluent_verified must be a boolean")
    if not diluent_verified:
        raise ValueError("Diluent composition must be explicitly verified")
    diluent_mass = _finite_number("diluent_molar_mass_g_mol", diluent_molar_mass_g_mol)
    oxygen_mass = _finite_number("oxygen_molar_mass_g_mol", oxygen_molar_mass_g_mol)
    if diluent_mass <= 0 or oxygen_mass <= 0:
        raise ValueError("molar masses must be greater than zero")
    oxygen_mass_in_mixture = fraction * oxygen_mass
    total_mass_per_mole_of_mixture = (
        oxygen_mass_in_mixture + (1.0 - fraction) * diluent_mass
    )
    if not math.isfinite(total_mass_per_mole_of_mixture):
        raise ValueError("Mixture molar-mass calculation exceeds the finite numeric range")
    result = oxygen_mass_in_mixture / total_mass_per_mole_of_mixture
    if not math.isfinite(result):
        raise ValueError("Mass-fraction calculation produced a non-finite result")
    if fraction > 0.0 and result == 0.0:
        raise ValueError("Oxygen mass fraction underflows the finite numeric range")
    return result


def calculate_pressure_conversion(
    value: float,
    from_unit: str | PressureUnit,
    to_unit: str | PressureUnit = PressureUnit.KPA,
    *,
    pressure_basis: PressureBasis | str,
    provenance: InputProvenance | None = None,
) -> CalculationResult:
    """Convert one caller-supplied positive absolute pressure with provenance."""
    try:
        basis = PressureBasis(pressure_basis)
    except (TypeError, ValueError) as exc:
        raise ValueError("pressure_basis must be explicitly 'absolute'") from exc
    source = from_unit.value if isinstance(from_unit, PressureUnit) else from_unit
    target = to_unit.value if isinstance(to_unit, PressureUnit) else to_unit
    result = convert_pressure(value, source, target)
    kpa = convert_pressure(value, source, PressureUnit.KPA)
    prov = provenance or InputProvenance()
    if prov.raw_unit and _pressure_unit(prov.raw_unit) != _pressure_unit(source) and not prov.normalization_method:
        raise ValueError("Pressure provenance requires a normalization method when units differ")
    return CalculationResult(
        calculation="pressure_conversion",
        formula="P_target = P_input * factor(source_unit) / factor(target_unit)",
        inputs={"value": value, "unit": source, "pressure_basis": basis.value},
        outputs={"value": result, "normalized_value_kpa": kpa},
        units={"input": source, "value": target, "normalized_value_kpa": "kPa"},
        verification={"input": prov.verification_status.value, "result": "DERIVED"},
        conversion_methods={"value": f"{source} to {target} via kPa factors"},
        provenance={"pressure": prov},
        assumptions=("Input pressure is absolute, as required by the conversion contract.",),
        limitations=("Unit conversion does not verify the source measurement or pressure basis.",),
    )


def _validated_condition(condition: AtmosphericCondition) -> tuple[float, float]:
    if not isinstance(condition, AtmosphericCondition):
        raise TypeError("condition must be an AtmosphericCondition")
    if not condition.gas_basis_verified:
        raise ValueError("Oxygen gas-phase mole-fraction basis must be verified")
    pressure_kpa = convert_pressure(
        condition.total_pressure, condition.pressure_unit, PressureUnit.KPA
    )
    return condition.oxygen_mole_fraction, pressure_kpa


def calculate_oxygen_partial_pressure(condition: AtmosphericCondition) -> CalculationResult:
    """Calculate pO2 in kPa and preserve state-input provenance."""
    fraction, pressure_kpa = _validated_condition(condition)
    p_o2 = oxygen_partial_pressure(fraction, pressure_kpa)
    return CalculationResult(
        calculation="oxygen_partial_pressure",
        formula="pO2 = X_O2 * P_total",
        inputs=_condition_inputs(condition),
        outputs={"oxygen_mole_fraction": fraction, "total_pressure_kpa": pressure_kpa,
                 "oxygen_partial_pressure_kpa": p_o2},
        units={"oxygen_mole_fraction": "1", "total_pressure_kpa": "kPa absolute",
               "oxygen_partial_pressure_kpa": "kPa"},
        verification={"oxygen": condition.oxygen_verification.value,
                      "total_pressure": condition.pressure_verification.value,
                      "result": "DERIVED"},
        conversion_methods={
            "oxygen_mole_fraction": _oxygen_normalization_method(condition),
            "total_pressure_kpa": f"{condition.pressure_unit.value} to kPa",
        },
        provenance=_provenance_dict(condition),
        assumptions=("Dalton's law is applied to the supplied gas-phase oxygen mole fraction.",),
        limitations=("This calculation does not establish combustion equivalence or fire safety.",
                     "Non-ideal mixture fugacity is not calculated."),
    )


def calculate_oxygen_mass_fraction(
    condition: AtmosphericCondition | OxygenComposition,
) -> CalculationResult:
    """Calculate binary O2/diluent mass fraction from verified composition."""
    if isinstance(condition, AtmosphericCondition):
        composition = OxygenComposition(
            oxygen_mole_fraction=condition.oxygen_mole_fraction,
            gas_basis_verified=condition.gas_basis_verified,
            diluent=condition.diluent,
            oxygen_verification=condition.oxygen_verification,
            provenance=condition.provenance,
        )
    elif isinstance(condition, OxygenComposition):
        composition = condition
    else:
        raise TypeError("condition must be an AtmosphericCondition or OxygenComposition")
    if not composition.gas_basis_verified:
        raise ValueError("Oxygen gas-phase mole-fraction basis must be verified")
    diluent = composition.diluent
    if diluent is None:
        raise ValueError("Verified binary diluent composition is required")
    if diluent.verification_status not in {VerificationStatus.MEASURED, VerificationStatus.DERIVED}:
        raise ValueError("Diluent composition must have MEASURED or DERIVED verification status")
    result = oxygen_mass_fraction(
        composition.oxygen_mole_fraction,
        diluent.molar_mass_g_mol,
        diluent_verified=True,
    )
    return CalculationResult(
        calculation="oxygen_mass_fraction",
        formula="Y_O2 = X_O2*M_O2 / (X_O2*M_O2 + (1-X_O2)*M_diluent)",
        inputs=_composition_inputs(composition),
        outputs={"oxygen_mass_fraction": result},
        units={"oxygen_mass_fraction": "1", "molar_mass": "g/mol"},
        verification={"oxygen": composition.oxygen_verification.value,
                      "diluent": diluent.verification_status.value, "result": "DERIVED"},
        conversion_methods={
            "oxygen_mole_fraction": _oxygen_normalization_method(composition),
            "oxygen_mass_fraction": "binary mixture mass-balance equation",
        },
        provenance={**{key: value.to_dict() for key, value in composition.provenance.items()},
                    "diluent": diluent.provenance},
        assumptions=(f"Binary mixture: O2 plus {diluent.name} as the sole diluent species.",),
        limitations=("Not valid for an unspecified or multi-species diluent mixture.",),
    )


def _atmosphere_summary(
    oxygen_fraction: float, total_pressure: float, pressure_unit: str | PressureUnit
) -> AtmosphereSummary:
    fraction = _oxygen_fraction(oxygen_fraction)
    pressure_kpa = convert_pressure(total_pressure, pressure_unit, PressureUnit.KPA)
    return {
        "oxygen_fraction": fraction,
        "total_pressure_kpa": pressure_kpa,
        "oxygen_partial_pressure_kpa": oxygen_partial_pressure(fraction, pressure_kpa),
    }


def compare_atmospheres(
    oxygen_fraction: float,
    total_pressure: float,
    reference_oxygen_fraction: float,
    reference_pressure: float,
    pressure_unit: str | PressureUnit = PressureUnit.KPA,
    reference_pressure_unit: str | PressureUnit | None = None,
) -> dict[str, AtmosphereSummary | float | None]:
    """Backward-compatible numeric comparison in normalized kPa.

    Similar pO2 does not imply combustion equivalence or safety.
    """
    scenario = _atmosphere_summary(oxygen_fraction, total_pressure, pressure_unit)
    reference_unit = pressure_unit if reference_pressure_unit is None else reference_pressure_unit
    reference = _atmosphere_summary(
        reference_oxygen_fraction,
        reference_pressure,
        reference_unit,
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
    if relative_difference is not None and not math.isfinite(relative_difference):
        raise ValueError("Relative pO2 difference exceeds the finite numeric range")
    return {
        "scenario": scenario,
        "reference": reference,
        "oxygen_partial_pressure_difference_kpa": difference,
        "relative_oxygen_partial_pressure_difference": relative_difference,
    }


def compare_atmospheric_conditions(
    scenario: AtmosphericCondition, reference: AtmosphericCondition
) -> CalculationResult:
    """Compare two verified-basis atmospheres; no combustion equivalence implied."""
    scenario_x, scenario_p = _validated_condition(scenario)
    reference_x, reference_p = _validated_condition(reference)
    scenario_o2 = scenario_x * scenario_p
    reference_o2 = reference_x * reference_p
    differences = {
        "oxygen_mole_fraction": scenario_x - reference_x,
        "total_pressure_kpa": scenario_p - reference_p,
        "oxygen_partial_pressure_kpa": scenario_o2 - reference_o2,
    }
    relative: dict[str, float | None] = {}
    warnings: list[str] = []
    for key, scenario_value, reference_value in (
        ("oxygen_mole_fraction", scenario_x, reference_x),
        ("total_pressure_kpa", scenario_p, reference_p),
        ("oxygen_partial_pressure_kpa", scenario_o2, reference_o2),
    ):
        relative[key] = (
            (scenario_value - reference_value) / reference_value
            if reference_value != 0 else None
        )
        if reference_value == 0:
            warnings.append(
                f"Relative difference for {key} is undefined because the reference value is zero."
            )
        if relative[key] is not None and not math.isfinite(relative[key]):
            raise ValueError(f"Relative difference for {key} is outside the finite numeric range")
    return CalculationResult(
        calculation="compare_atmospheric_conditions",
        formula="difference = scenario - reference; relative = difference / reference when reference != 0",
        inputs={"scenario": scenario, "reference": reference},
        outputs={
            "scenario": {"oxygen_mole_fraction": scenario_x,
                         "total_pressure_kpa": scenario_p,
                         "oxygen_partial_pressure_kpa": scenario_o2},
            "reference": {"oxygen_mole_fraction": reference_x,
                          "total_pressure_kpa": reference_p,
                          "oxygen_partial_pressure_kpa": reference_o2},
            "differences_scenario_minus_reference": differences,
            "relative_differences": relative,
        },
        units={"oxygen_mole_fraction": "1", "total_pressure_kpa": "kPa absolute",
               "oxygen_partial_pressure_kpa": "kPa"},
        verification={
            "scenario_oxygen": scenario.oxygen_verification.value,
            "scenario_pressure": scenario.pressure_verification.value,
            "reference_oxygen": reference.oxygen_verification.value,
            "reference_pressure": reference.pressure_verification.value,
            "result": "DERIVED",
        },
        conversion_methods={
            "scenario_oxygen_mole_fraction": _oxygen_normalization_method(scenario),
            "reference_oxygen_mole_fraction": _oxygen_normalization_method(reference),
            "scenario_pressure": f"{scenario.pressure_unit.value} to kPa",
            "reference_pressure": f"{reference.pressure_unit.value} to kPa",
        },
        provenance={"scenario": _provenance_dict(scenario),
                    "reference": _provenance_dict(reference)},
        assumptions=("Each oxygen value is a verified gas-phase mole fraction.",
                     "Dalton's law is used for oxygen partial pressure."),
        limitations=("Equal oxygen partial pressures do not establish combustion equivalence.",
                     "This comparison does not infer fire safety or certification."),
        warnings=tuple(warnings),
    )
