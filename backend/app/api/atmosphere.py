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
from backend.app.services.atmospheric_service import (
    CalculationOutOfRangeError,
    UnverifiedDiluentError,
    calculate_mass_fraction,
    calculate_partial_pressure,
    compare_conditions,
    serialize_result,
)
from backend.app.services.diluent_registry import DiluentRegistry, get_diluent_registry

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

@router.post(
    "/oxygen-partial-pressure",
    responses={422: {"model": APIErrorResponse}, 500: {"model": APIErrorResponse}},
)
def oxygen_partial_pressure_endpoint(request: AtmosphericConditionRequest) -> dict[str, object]:
    try:
        return serialize_result(calculate_partial_pressure(request))
    except CalculationOutOfRangeError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "calculation_out_of_range",
                "field": None,
                "message": str(exc),
            },
        ) from None


@router.post(
    "/compare",
    responses={422: {"model": APIErrorResponse}, 500: {"model": APIErrorResponse}},
)
def compare_atmospheric_conditions_endpoint(
    request: AtmosphericComparisonRequest,
) -> dict[str, object]:
    try:
        return serialize_result(compare_conditions(request))
    except CalculationOutOfRangeError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "calculation_out_of_range",
                "field": None,
                "message": str(exc),
            },
        ) from None


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
    try:
        return serialize_result(calculate_mass_fraction(request, registry))
    except UnverifiedDiluentError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "unverified_diluent",
                "field": "diluent_id",
                "message": str(exc),
            },
        ) from None
    except CalculationOutOfRangeError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "calculation_out_of_range",
                "field": None,
                "message": str(exc),
            },
        ) from None
