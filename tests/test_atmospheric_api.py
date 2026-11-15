"""HTTP contract tests for the deterministic atmospheric API."""

from __future__ import annotations

import json
import math
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app.main import app
from modelling.atmospheric import (
    calculate_oxygen_partial_pressure,
    compare_atmospheric_conditions,
)


client = TestClient(app)


def atmosphere(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "oxygen_mole_fraction": 0.30,
        "total_pressure": 10.2,
        "pressure_unit": "psi",
        "pressure_basis": "absolute",
    }
    payload.update(overrides)
    return payload


class HealthApiTests(unittest.TestCase):
    def test_api_health_reports_engine_only(self) -> None:
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["components"], {"atmospheric_engine": "available"})
        self.assertEqual(response.json()["api_schema_version"], "1.0")
        self.assertNotIn("evidence", response.json()["components"])

    def test_compatibility_health_remains_available(self) -> None:
        self.assertEqual(client.get("/health").json(), {"status": "ok"})


class AtmosphericApiTests(unittest.TestCase):
    def test_routes_call_typed_engine_operation_and_do_not_publish_legacy_operations(self) -> None:
        with patch(
            "backend.app.api.atmosphere.calculate_oxygen_partial_pressure",
            wraps=calculate_oxygen_partial_pressure,
        ) as calculation:
            response = client.post("/api/atmosphere/oxygen-partial-pressure", json=atmosphere())
        self.assertEqual(response.status_code, 200)
        condition = calculation.call_args.args[0]
        self.assertTrue(condition.gas_basis_verified)
        self.assertEqual(condition.oxygen_verification.value, "UNVERIFIED")
        registered_paths = set(app.openapi()["paths"])
        self.assertTrue(
            {
                "/api/atmosphere/oxygen-partial-pressure",
                "/api/atmosphere/oxygen-mass-fraction",
                "/api/atmosphere/compare",
            }.issubset(registered_paths)
        )
        self.assertFalse(any("convert_pressure" in path for path in registered_paths))

        with patch(
            "backend.app.api.atmosphere.compare_atmospheric_conditions",
            wraps=compare_atmospheric_conditions,
        ) as comparison:
            result = client.post(
                "/api/atmosphere/compare",
                json={"scenario": atmosphere(), "reference": atmosphere()},
            )
        self.assertEqual(result.status_code, 200)
        comparison.assert_called_once()

        with patch("backend.app.api.atmosphere.calculate_oxygen_mass_fraction") as mass_fraction:
            unavailable = client.post(
                "/api/atmosphere/oxygen-mass-fraction",
                json={"oxygen_mole_fraction": 0.21, "diluent_id": "no-record"},
            )
        self.assertEqual(unavailable.status_code, 503)
        mass_fraction.assert_not_called()

    def test_partial_pressure_preserves_engine_result_and_marks_inputs_unverified(self) -> None:
        response = client.post("/api/atmosphere/oxygen-partial-pressure", json=atmosphere())
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["api_schema_version"], "1.0")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["calculation"], "oxygen_partial_pressure")
        self.assertAlmostEqual(result["outputs"]["oxygen_partial_pressure_kpa"], 21.097957316495983)
        self.assertEqual(result["verification"]["oxygen"], "UNVERIFIED")
        self.assertEqual(result["verification"]["total_pressure"], "UNVERIFIED")
        self.assertEqual(result["provenance"]["oxygen_mole_fraction"]["origin"], "user_supplied")
        self.assertTrue(result["limitations"])
        json.dumps(result, allow_nan=False)

    def test_zero_oxygen_is_valid_and_returns_zero(self) -> None:
        result = client.post(
            "/api/atmosphere/oxygen-partial-pressure", json=atmosphere(oxygen_mole_fraction=0)
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["outputs"]["oxygen_partial_pressure_kpa"], 0.0)

    def test_very_low_nonzero_oxygen_remains_finite(self) -> None:
        response = client.post(
            "/api/atmosphere/oxygen-partial-pressure",
            json=atmosphere(oxygen_mole_fraction=1e-300, total_pressure=100.0, pressure_unit="kPa"),
        )
        self.assertEqual(response.status_code, 200)
        value = response.json()["outputs"]["oxygen_partial_pressure_kpa"]
        self.assertGreater(value, 0.0)
        self.assertTrue(math.isfinite(value))

    def test_json_decimal_underflow_is_not_silently_treated_as_exact_zero(self) -> None:
        response = client.post(
            "/api/atmosphere/oxygen-partial-pressure",
            content=(
                '{"oxygen_mole_fraction":1e-999,"total_pressure":10.0,'
                '"pressure_unit":"kPa","pressure_basis":"absolute"}'
            ),
            headers={"content-type": "application/json"},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["status"], "error")
        self.assertNotIn("outputs", response.json())

    def test_unit_boundary_and_pure_oxygen_boundary(self) -> None:
        one_atm = atmosphere(oxygen_mole_fraction=1.0, total_pressure=1.0, pressure_unit="atm")
        equivalent = atmosphere(
            oxygen_mole_fraction=1.0, total_pressure=101.325, pressure_unit="kPa"
        )
        result_a = client.post("/api/atmosphere/oxygen-partial-pressure", json=one_atm)
        result_b = client.post("/api/atmosphere/oxygen-partial-pressure", json=equivalent)
        self.assertEqual(result_a.status_code, 200)
        self.assertEqual(result_b.status_code, 200)
        self.assertAlmostEqual(
            result_a.json()["outputs"]["oxygen_partial_pressure_kpa"], 101.325
        )
        self.assertAlmostEqual(
            result_a.json()["outputs"]["oxygen_partial_pressure_kpa"],
            result_b.json()["outputs"]["oxygen_partial_pressure_kpa"],
        )

    def test_tiny_and_extreme_pressures_fail_as_structured_range_errors_when_unrepresentable(self) -> None:
        for payload in (
            atmosphere(total_pressure=1e308, pressure_unit="psi"),
            atmosphere(total_pressure=5e-324, pressure_unit="kPa"),
        ):
            with self.subTest(payload=payload):
                response = client.post("/api/atmosphere/oxygen-partial-pressure", json=payload)
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.json()["error"]["code"], "calculation_out_of_range")
                self.assertNotIn("outputs", response.json())

    def test_invalid_partial_pressure_requests_are_structured_and_have_no_outputs(self) -> None:
        cases = [
            atmosphere(pressure_basis="gauge"),
            atmosphere(pressure_basis="unspecified"),
            atmosphere(pressure_unit="MPa"),
            atmosphere(total_pressure=0),
            atmosphere(total_pressure=-1),
            atmosphere(oxygen_mole_fraction=-0.1),
            atmosphere(oxygen_mole_fraction=1.1),
            atmosphere(oxygen_mole_fraction=True),
            atmosphere(total_pressure="10.2"),
            atmosphere(total_pressure=10**1000),
            atmosphere(gas_basis_verified=True),
            atmosphere(verification_status="MEASURED"),
            atmosphere(diluent_verified=True),
            atmosphere(provenance={"oxygen_mole_fraction": {"verification_status": "MEASURED"}}),
            atmosphere(source_id="PSI-26", source_locator="table 1"),
            atmosphere(input_origin="source_record"),
            atmosphere(oxygen_mole_fraction=None),
            atmosphere(pressure_unit=""),
            {"oxygen_mole_fraction": 0.2},
        ]
        for payload in cases:
            with self.subTest(payload=payload):
                response = client.post("/api/atmosphere/oxygen-partial-pressure", json=payload)
                self.assertEqual(response.status_code, 422)
                body = response.json()
                self.assertEqual(body["status"], "error")
                self.assertIn("code", body["error"])
                self.assertNotIn("outputs", body)
                self.assertNotIn("traceback", response.text.lower())
                json.dumps(body, allow_nan=False)

    def test_malformed_json_and_wrong_content_type_are_structured_422(self) -> None:
        malformed = client.post(
            "/api/atmosphere/oxygen-partial-pressure",
            content="{broken",
            headers={"content-type": "application/json"},
        )
        wrong_type = client.post(
            "/api/atmosphere/oxygen-partial-pressure",
            content=json.dumps(atmosphere()),
            headers={"content-type": "text/plain"},
        )
        for response in (malformed, wrong_type):
            self.assertEqual(response.status_code, 422)
            self.assertEqual(response.json()["status"], "error")
            self.assertNotIn("outputs", response.json())

    def test_non_finite_numbers_rejected_by_json_parser_or_schema(self) -> None:
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                response = client.post(
                    "/api/atmosphere/oxygen-partial-pressure",
                    content=json.dumps(atmosphere(total_pressure=value)),
                    headers={"content-type": "application/json"},
                )
                self.assertGreaterEqual(response.status_code, 400)
                self.assertNotIn("outputs", response.json())

    def test_comparison_returns_scenario_minus_reference_and_zero_reference_nulls(self) -> None:
        request = {
            "scenario": atmosphere(oxygen_mole_fraction=0.3, total_pressure=10),
            "reference": atmosphere(oxygen_mole_fraction=0, total_pressure=15),
        }
        response = client.post("/api/atmosphere/compare", json=request)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        outputs = result["outputs"]
        self.assertEqual(outputs["differences_scenario_minus_reference"]["oxygen_mole_fraction"], 0.3)
        self.assertIsNone(outputs["relative_differences"]["oxygen_partial_pressure_kpa"])
        self.assertTrue(result["warnings"])
        self.assertIn("Equal oxygen partial pressures do not establish combustion equivalence.", result["limitations"])
        self.assertEqual(result["verification"]["scenario_oxygen"], "UNVERIFIED")
        self.assertEqual(result["verification"]["reference_oxygen"], "UNVERIFIED")

    def test_nested_comparison_validation_is_strict(self) -> None:
        for request in (
            {"scenario": atmosphere(), "reference": {"oxygen_mole_fraction": 0.2}},
            {"scenario": atmosphere(), "reference": atmosphere(pressure_basis="gauge")},
            {"scenario": atmosphere(gas_basis_verified=True), "reference": atmosphere()},
        ):
            with self.subTest(request=request):
                response = client.post("/api/atmosphere/compare", json=request)
                self.assertEqual(response.status_code, 422)
                self.assertNotIn("outputs", response.json())

    def test_identical_atmospheres_compare_to_zero_and_equal_units_are_normalized(self) -> None:
        request = {
            "scenario": atmosphere(oxygen_mole_fraction=0.2, total_pressure=1.0, pressure_unit="atm"),
            "reference": atmosphere(oxygen_mole_fraction=0.2, total_pressure=101.325, pressure_unit="kPa"),
        }
        response = client.post("/api/atmosphere/compare", json=request)
        self.assertEqual(response.status_code, 200)
        differences = response.json()["outputs"]["differences_scenario_minus_reference"]
        for value in differences.values():
            self.assertAlmostEqual(value, 0.0)

    def test_unexpected_backend_exception_is_a_generic_500_not_a_422(self) -> None:
        safe_client = TestClient(app, raise_server_exceptions=False)
        for error in (RuntimeError("secret traceback"), TypeError("internal type bug"), ValueError("internal invariant")):
            with self.subTest(error=type(error).__name__):
                with patch(
                    "backend.app.api.atmosphere.calculate_oxygen_partial_pressure",
                    side_effect=error,
                ):
                    response = safe_client.post(
                        "/api/atmosphere/oxygen-partial-pressure", json=atmosphere()
                    )
                self.assertEqual(response.status_code, 500)
                self.assertEqual(response.json()["error"]["code"], "internal_error")
                self.assertNotIn("secret traceback", response.text)
                self.assertNotIn("outputs", response.json())

    def test_nonfinite_response_serialization_becomes_generic_500(self) -> None:
        safe_client = TestClient(app, raise_server_exceptions=False)
        with patch(
            "backend.app.api.atmosphere.calculate_oxygen_partial_pressure",
            return_value=SimpleNamespace(
                to_dict=lambda: {"status": "success", "outputs": {"value": math.nan}}
            ),
        ):
            response = safe_client.post(
                "/api/atmosphere/oxygen-partial-pressure", json=atmosphere()
            )
        self.assertEqual(response.status_code, 500)
        self.assertNotIn("NaN", response.text)
        self.assertNotIn("outputs", response.json())

    def test_mass_fraction_requires_registry_and_rejects_client_assertions(self) -> None:
        unavailable = client.post(
            "/api/atmosphere/oxygen-mass-fraction",
            json={"oxygen_mole_fraction": 0.21, "diluent_id": "nitrogen"},
        )
        self.assertEqual(unavailable.status_code, 503)
        self.assertEqual(unavailable.json()["error"]["code"], "unverified_diluent")
        self.assertNotIn("outputs", unavailable.json())
        for extra in (
            {"diluent_molar_mass_g_mol": 28.014},
            {"diluent_verified": True},
            {"verification_status": "MEASURED"},
            {"gas_basis_verified": True},
        ):
            request = {"oxygen_mole_fraction": 0.21, "diluent_id": "nitrogen", **extra}
            with self.subTest(extra=extra):
                response = client.post("/api/atmosphere/oxygen-mass-fraction", json=request)
                self.assertEqual(response.status_code, 422)

    def test_mass_fraction_rejects_blank_and_null_diluent_ids(self) -> None:
        for diluent_id in ("", "  ", " nitrogen ", None):
            with self.subTest(diluent_id=diluent_id):
                response = client.post(
                    "/api/atmosphere/oxygen-mass-fraction",
                    json={"oxygen_mole_fraction": 0.21, "diluent_id": diluent_id},
                )
                self.assertEqual(response.status_code, 422)

    def test_error_and_success_versions_are_consistent(self) -> None:
        success = client.post("/api/atmosphere/oxygen-partial-pressure", json=atmosphere())
        invalid = client.post(
            "/api/atmosphere/oxygen-partial-pressure", json=atmosphere(total_pressure=0)
        )
        unavailable = client.post(
            "/api/atmosphere/oxygen-mass-fraction",
            json={"oxygen_mole_fraction": 0.21, "diluent_id": "nitrogen"},
        )
        versions = [
            success.json()["api_schema_version"],
            invalid.json()["api_schema_version"],
            unavailable.json()["api_schema_version"],
            client.get("/api/health").json()["api_schema_version"],
        ]
        self.assertEqual(versions, ["1.0"] * len(versions))

    def test_openapi_documents_the_runtime_error_envelope(self) -> None:
        spec = app.openapi()
        for path in (
            "/api/atmosphere/oxygen-partial-pressure",
            "/api/atmosphere/compare",
            "/api/atmosphere/oxygen-mass-fraction",
        ):
            responses = spec["paths"][path]["post"]["responses"]
            documented_422 = responses["422"]["content"]["application/json"]["schema"]
            self.assertEqual(documented_422["$ref"], "#/components/schemas/APIErrorResponse")
        self.assertIn(
            "503", spec["paths"]["/api/atmosphere/oxygen-mass-fraction"]["post"]["responses"]
        )


if __name__ == "__main__":
    unittest.main()
