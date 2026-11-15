"""Shared typed service boundary for atmospheric scientific calculations.

HTTP routes and future assistant tools should call these operations so request
provenance, calculation dispatch, range errors, and serialization stay aligned.
"""

from __future__ import annotations

import json
from collections.abc import Callable

from backend.app.schemas.atmosphere import (
    AtmosphericComparisonRequest,
    AtmosphericConditionRequest,
    OxygenMassFractionRequest,
)
from backend.app.services.diluent_registry import DiluentRegistry
from backend.app.version import API_SCHEMA_VERSION
from modelling.atmospheric import (
    AtmosphericCondition,
    CalculationResult,
    InputOrigin,
    InputProvenance,
    OxygenComposition,
    PressureBasis,
    PressureUnit,
    VerificationStatus,
    calculate_oxygen_mass_fraction as engine_calculate_oxygen_mass_fraction,
    calculate_oxygen_partial_pressure as engine_calculate_oxygen_partial_pressure,
    compare_atmospheric_conditions as engine_compare_atmospheric_conditions,
)


_NUMERIC_RANGE_ERRORS = {
    "Converted pressure is outside the finite numeric range",
    "Converted pressure underflows the finite numeric range",
    "Oxygen partial pressure underflows the finite numeric range",
    "Relative pO2 difference exceeds the finite numeric range",
}


class CalculationOutOfRangeError(ValueError):
    """A valid-shaped request whose deterministic result is not representable."""


class UnverifiedDiluentError(ValueError):
    """No reviewed server-side diluent record is available for this operation."""


def condition_from_request(request: AtmosphericConditionRequest) -> AtmosphericCondition:
    """Build an engine condition with server-controlled, unverified provenance."""
    provenance = InputProvenance(
        origin=InputOrigin.USER_SUPPLIED,
        verification_status=VerificationStatus.UNVERIFIED,
        note="Submitted by API client; no source record was asserted or verified.",
    )
    return AtmosphericCondition(
        oxygen_mole_fraction=request.oxygen_mole_fraction,
        total_pressure=request.total_pressure,
        pressure_unit=PressureUnit(request.pressure_unit),
        pressure_basis=PressureBasis(request.pressure_basis),
        # This is the declared gas-phase input contract, not experimental verification.
        gas_basis_verified=True,
        oxygen_verification=VerificationStatus.UNVERIFIED,
        pressure_verification=VerificationStatus.UNVERIFIED,
        provenance={
            "oxygen_mole_fraction": provenance,
            "total_pressure": provenance,
        },
    )


def _run(
    operation: Callable[..., CalculationResult], *inputs: object
) -> CalculationResult:
    """Call one typed engine operation and normalize recognized range failures."""
    try:
        return operation(*inputs)
    except ValueError as exc:
        message = str(exc)
        if message in _NUMERIC_RANGE_ERRORS or message.startswith(
            "Relative difference for "
        ):
            raise CalculationOutOfRangeError(
                "The requested calculation is outside the supported finite numeric range."
            ) from None
        raise


def calculate_partial_pressure(
    request: AtmosphericConditionRequest,
) -> CalculationResult:
    """Calculate pO2 from one strict atmosphere request."""
    condition = condition_from_request(request)
    return _run(engine_calculate_oxygen_partial_pressure, condition)


def compare_conditions(
    request: AtmosphericComparisonRequest,
) -> CalculationResult:
    """Compare two strict atmosphere requests using the deterministic engine."""
    scenario = condition_from_request(request.scenario)
    reference = condition_from_request(request.reference)
    return _run(engine_compare_atmospheric_conditions, scenario, reference)


def calculate_mass_fraction(
    request: OxygenMassFractionRequest,
    registry: DiluentRegistry,
) -> CalculationResult:
    """Calculate binary-mixture mass fraction only with a reviewed diluent."""
    diluent = registry.resolve(request.diluent_id)
    if diluent is None or diluent.verification_status not in {
        VerificationStatus.MEASURED,
        VerificationStatus.DERIVED,
    }:
        raise UnverifiedDiluentError(
            "No trusted diluent record is available for this identifier."
        )

    provenance = InputProvenance(
        origin=InputOrigin.USER_SUPPLIED,
        verification_status=VerificationStatus.UNVERIFIED,
        note="Submitted by API client; no source record was asserted or verified.",
    )
    composition = OxygenComposition(
        oxygen_mole_fraction=request.oxygen_mole_fraction,
        gas_basis_verified=True,
        diluent=diluent,
        oxygen_verification=VerificationStatus.UNVERIFIED,
        provenance={"oxygen_mole_fraction": provenance},
    )
    return _run(engine_calculate_oxygen_mass_fraction, composition)


def serialize_result(result: CalculationResult) -> dict[str, object]:
    """Serialize the engine-owned envelope with the public API schema version."""
    payload = result.to_dict()
    payload["api_schema_version"] = API_SCHEMA_VERSION
    # Reject non-finite values rather than letting response encoding turn them null.
    json.dumps(payload, allow_nan=False, separators=(",", ":"))
    return payload
