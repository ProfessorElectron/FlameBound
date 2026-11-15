"""Strict, server-owned allowlist for deterministic atmospheric tools."""

from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from backend.app.schemas.atmosphere import AtmosphericComparisonRequest, AtmosphericConditionRequest
from backend.app.services.atmospheric_service import calculate_partial_pressure, compare_conditions, serialize_result


_CONDITION_SCHEMA = {"type": "object", "additionalProperties": False,
    "properties": {
        "oxygen_mole_fraction": {"type": "number", "minimum": 0, "maximum": 1},
        "total_pressure": {"type": "number", "exclusiveMinimum": 0},
        "pressure_unit": {"type": "string", "enum": ["Pa", "kPa", "bar", "atm", "psi"]},
        "pressure_basis": {"type": "string", "enum": ["absolute"]},
    }, "required": ["oxygen_mole_fraction", "total_pressure", "pressure_unit", "pressure_basis"]}

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {"type": "function", "function": {
        "name": "calculate_oxygen_partial_pressure",
        "description": "Calculate oxygen partial pressure from an explicit gas-phase oxygen mole fraction and absolute total pressure.",
        "parameters": {"type": "object", "additionalProperties": False,
            "properties": {
                "oxygen_mole_fraction": {"type": "number", "minimum": 0, "maximum": 1},
                "total_pressure": {"type": "number", "exclusiveMinimum": 0},
                "pressure_unit": {"type": "string", "enum": ["Pa", "kPa", "bar", "atm", "psi"]},
                "pressure_basis": {"type": "string", "enum": ["absolute"]},
            }, "required": ["oxygen_mole_fraction", "total_pressure", "pressure_unit", "pressure_basis"]},
    }},
    {"type": "function", "function": {
        "name": "compare_atmospheres",
        "description": "Compare a scenario atmosphere with a reference atmosphere.",
        "parameters": {"type": "object", "additionalProperties": False,
            "properties": {"scenario": _CONDITION_SCHEMA, "reference": _CONDITION_SCHEMA},
            "required": ["scenario", "reference"]},
    }},
]


class MissingToolInputs(Exception):
    def __init__(self, fields: list[str]):
        self.fields = fields


class ToolRejected(Exception):
    pass


class AtmosphericToolRegistry:
    def __init__(self):
        self.executions = 0

    @staticmethod
    def validate(name: str, arguments: Any):
        if name not in {"calculate_oxygen_partial_pressure", "compare_atmospheres"}:
            raise ToolRejected("Tool name is not allowlisted")
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError as exc:
                raise ToolRejected("Tool arguments must be a JSON object") from exc
        if not isinstance(arguments, dict):
            raise ToolRejected("Tool arguments must be a JSON object")
        required = ({"oxygen_mole_fraction", "total_pressure", "pressure_unit", "pressure_basis"}
                    if name == "calculate_oxygen_partial_pressure" else {"scenario", "reference"})
        missing = sorted(required - arguments.keys())
        if missing:
            raise MissingToolInputs(missing)
        try:
            if name == "calculate_oxygen_partial_pressure":
                return AtmosphericConditionRequest.model_validate(arguments, strict=True)
            return AtmosphericComparisonRequest.model_validate(arguments, strict=True)
        except ValidationError as exc:
            missing_errors = [error for error in exc.errors() if error.get("type") == "missing"]
            if missing_errors and len(missing_errors) == len(exc.errors()):
                fields = [".".join(str(part) for part in error.get("loc", ())) for error in missing_errors]
                raise MissingToolInputs(fields) from exc
            raise ToolRejected("Tool arguments failed the strict atmospheric request schema") from exc

    def execute(self, name: str, arguments: Any) -> dict[str, object]:
        if self.executions >= 1:
            raise ToolRejected("At most one calculation tool may run per request")
        request = self.validate(name, arguments)
        if name == "calculate_oxygen_partial_pressure":
            result = calculate_partial_pressure(request)
        else:
            result = compare_conditions(request)
        self.executions += 1
        return serialize_result(result)
