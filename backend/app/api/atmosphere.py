"""HTTP boundary for provenance-aware deterministic atmosphere calculations."""

from __future__ import annotations

from collections.abc import Callable
import json
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.routing import APIRoute

from backend.app.schemas.atmosphere import (
    APIErrorResponse,
    AtmosphericComparisonRequest,
    AtmosphericConditionRequest,
    OxygenMassFractionRequest,
)
from backend.app.services.diluent_registry import DiluentRegistry, get_diluent_registry
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
    calculate_oxygen_mass_fraction,
    calculate_oxygen_partial_pressure,
    compare_atmospheric_conditions,
)

class DecimalJSONRequest(Request):
    """Keep JSON decimal tokens intact until schema range/float validation."""

    async def json(self) -> object:
        if not hasattr(self, "_json"):
            body = await self.body()
            self._json = json.loads(
                body,
                parse_float=Decimal,
                parse_constant=Decimal,
            )
        return self._json


class DecimalJSONRoute(APIRoute):
    """Use decimal-preserving JSON parsing for calculation request bodies."""

    def get_route_handler(self) -> Callable:
        original_handler = super().get_route_handler()

        async def route_handler(request: Request):
            content_type = request.headers.get("content-type", "").split(";", 1)[0].lower()
            if not content_type or content_type == "application/json" or content_type.endswith("+json"):
                request = DecimalJSONRequest(request.scope, request.receive)
            return await original_handler(request)

        return route_handler


router = APIRouter(
    prefix="/api/atmosphere", tags=["atmosphere"], route_class=DecimalJSONRoute
)

_NUMERIC_RANGE_ERRORS = {
    "Converted pressure is outside the finite numeric range",
    "Converted pressure underflows the finite numeric range",
    "Oxygen partial pressure underflows the finite numeric range",
    "Relative pO2 difference exceeds the finite numeric range",
}


def _condition(request: AtmosphericConditionRequest) -> AtmosphericCondition:
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
        # The public field explicitly names the gas-phase mole-fraction contract.
        # Trust status remains UNVERIFIED and cannot be set by the client.
        gas_basis_verified=True,
        oxygen_verification=VerificationStatus.UNVERIFIED,
        pressure_verification=VerificationStatus.UNVERIFIED,
        provenance={
            "oxygen_mole_fraction": provenance,
            "total_pressure": provenance,
        },
    )


def _serialized_result(result: CalculationResult) -> dict[str, object]:
    # Keep the engine-owned result envelope intact; add only the API contract version.
    payload = result.to_dict()
    payload["api_schema_version"] = API_SCHEMA_VERSION
    # FastAPI's encoder can normalize non-finite numbers to null; reject instead of
    # silently changing a scientific result during response serialization.
    json.dumps(payload, allow_nan=False, separators=(",", ":"))
    return payload


def _calculate(
    operation: Callable[..., CalculationResult], *inputs: object
) -> dict[str, object]:
    """Map known finite-range failures to 422; let unexpected defects become 500."""
    try:
        result = operation(*inputs)
    except ValueError as exc:
        message = str(exc)
        if message in _NUMERIC_RANGE_ERRORS or message.startswith(
            "Relative difference for "
        ):
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "calculation_out_of_range",
                    "field": None,
                    "message": "The requested calculation is outside the supported finite numeric range.",
                },
            ) from None
        raise
    return _serialized_result(result)


@router.post(
    "/oxygen-partial-pressure",
    responses={422: {"model": APIErrorResponse}, 500: {"model": APIErrorResponse}},
)
def oxygen_partial_pressure_endpoint(request: AtmosphericConditionRequest) -> dict[str, object]:
    return _calculate(calculate_oxygen_partial_pressure, _condition(request))


@router.post(
    "/compare",
    responses={422: {"model": APIErrorResponse}, 500: {"model": APIErrorResponse}},
)
def compare_atmospheric_conditions_endpoint(
    request: AtmosphericComparisonRequest,
) -> dict[str, object]:
    return _calculate(
        compare_atmospheric_conditions,
        _condition(request.scenario),
        _condition(request.reference),
    )


@router.post(
    "/oxygen-mass-fraction",
    responses={
        422: {"model": APIErrorResponse},
        500: {"model": APIErrorResponse},
        503: {"model": APIErrorResponse},
    },
)
def oxygen_mass_fraction_endpoint(
    request: OxygenMassFractionRequest,
    registry: DiluentRegistry = Depends(get_diluent_registry),
) -> dict[str, object]:
    diluent = registry.resolve(request.diluent_id)
    if diluent is None or diluent.verification_status not in {
        VerificationStatus.MEASURED,
        VerificationStatus.DERIVED,
    }:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "unverified_diluent",
                "field": "diluent_id",
                "message": "No trusted diluent record is available for this identifier.",
            },
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
    return _calculate(calculate_oxygen_mass_fraction, composition)
