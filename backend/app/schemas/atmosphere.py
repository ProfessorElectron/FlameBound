"""Strict public request models for deterministic atmospheric calculations."""

from __future__ import annotations

import math
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _finite_json_float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValueError("must be a JSON number, not a boolean or numeric string")
    if isinstance(value, Decimal) and not value.is_finite():
        raise ValueError("must be finite")
    try:
        converted = float(value)
    except (OverflowError, ValueError):
        raise ValueError("must be representable as a finite floating-point number") from None
    if not math.isfinite(converted):
        raise ValueError("must be finite")
    if value != 0 and converted == 0.0:
        raise ValueError("nonzero input underflows the supported floating-point range")
    return converted


class StrictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class APIErrorDetail(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    code: str
    field: str | None
    message: str


class APIErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    status: Literal["error"]
    api_schema_version: Literal["1.0"]
    error: APIErrorDetail


class AtmosphericConditionRequest(StrictRequest):
    oxygen_mole_fraction: Annotated[float, Field(ge=0.0, le=1.0)]
    total_pressure: Annotated[float, Field(gt=0.0)]
    pressure_unit: Literal["Pa", "kPa", "bar", "atm", "psi"]
    pressure_basis: Literal["absolute"]

    @field_validator("oxygen_mole_fraction", "total_pressure", mode="before")
    @classmethod
    def require_finite_json_number(cls, value: object) -> object:
        return _finite_json_float(value)


class AtmosphericComparisonRequest(StrictRequest):
    scenario: AtmosphericConditionRequest
    reference: AtmosphericConditionRequest


class OxygenMassFractionRequest(StrictRequest):
    oxygen_mole_fraction: Annotated[float, Field(ge=0.0, le=1.0)]
    diluent_id: Annotated[str, Field(min_length=1, max_length=100)]

    @field_validator("oxygen_mole_fraction", mode="before")
    @classmethod
    def require_finite_json_number(cls, value: object) -> object:
        return _finite_json_float(value)

    @field_validator("diluent_id")
    @classmethod
    def reject_blank_or_padded_identifier(cls, value: str) -> str:
        if not value.strip() or value != value.strip():
            raise ValueError("must be a non-blank identifier without surrounding whitespace")
        return value
