import math
import json
import unittest

from modelling.atmospheric import (
    AtmosphericCondition,
    BinaryDiluent,
    InputOrigin,
    InputProvenance,
    OxygenComposition,
    PressureBasis,
    PressureUnit,
    VerificationStatus,
    calculate_oxygen_mass_fraction,
    calculate_oxygen_partial_pressure,
    calculate_pressure_conversion,
    compare_atmospheric_conditions,
    compare_atmospheres,
    convert_pressure,
    oxygen_mass_fraction,
    oxygen_partial_pressure,
)


class ConvertPressureTests(unittest.TestCase):
    def test_psi_to_kpa(self):
        self.assertAlmostEqual(convert_pressure(1.0, "psi", "kPa"), 6.894757293168)

    def test_atmosphere_to_pascal(self):
        self.assertAlmostEqual(convert_pressure(1.0, "atm", "Pa"), 101325.0)

    def test_each_supported_pressure_unit_converts_to_kpa(self):
        cases = {
            "Pa": 1.0,
            "kPa": 1.0,
            "bar": 100.0,
            "atm": 101.325,
            "psi": 6.894757293168361,
            "MPa": 1000.0,
        }
        for unit, expected_kpa in cases.items():
            with self.subTest(unit=unit):
                self.assertAlmostEqual(convert_pressure(1000.0 if unit == "Pa" else 1.0, unit, "kPa"), expected_kpa)

    def test_pressure_round_trips_all_supported_units(self):
        for unit, value in (("Pa", 101325.0), ("kPa", 101.325), ("bar", 1.01325),
                            ("atm", 1.0), ("psi", 14.6959487755), ("MPa", 0.101325)):
            with self.subTest(unit=unit):
                converted = convert_pressure(value, unit, "kPa")
                restored = convert_pressure(converted, "kPa", unit)
                self.assertAlmostEqual(restored, value, places=10)

    def test_rejects_invalid_types_and_pressure_boundaries(self):
        for value in (True, "1"):
            with self.subTest(value=value), self.assertRaises(TypeError):
                convert_pressure(value, "kPa", "psi")

    def test_extreme_pressure_overflow_and_underflow_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "finite numeric range"):
            convert_pressure(1e308, "kPa", "Pa")
        with self.assertRaisesRegex(ValueError, "underflows"):
            convert_pressure(5e-324, "Pa", "kPa")
        self.assertEqual(convert_pressure(1e308, "MPa", "MPa"), 1e308)
        for value in (0.0, -1.0, math.inf, math.nan):
            with self.subTest(value=value), self.assertRaises(ValueError):
                convert_pressure(value, "kPa", "psi")

    def test_unit_names_are_case_and_space_insensitive(self):
        self.assertAlmostEqual(convert_pressure(100.0, " kilopascals ", "bar"), 1.0)

    def test_rejects_invalid_pressure_or_units(self):
        for value in (0.0, -1.0, math.inf, math.nan):
            with self.subTest(value=value), self.assertRaises(ValueError):
                convert_pressure(value, "kPa", "psi")
        with self.assertRaises(ValueError):
            convert_pressure(10.0, "mmHg", "kPa")


class OxygenCalculationTests(unittest.TestCase):
    def test_partial_pressure_preserves_pressure_unit(self):
        self.assertAlmostEqual(oxygen_partial_pressure(0.30, 10.2), 3.06)

    def test_partial_pressure_accepts_fraction_boundaries(self):
        self.assertEqual(oxygen_partial_pressure(0.0, 1.0), 0.0)
        self.assertEqual(oxygen_partial_pressure(1.0, 1.0), 1.0)
        self.assertAlmostEqual(oxygen_partial_pressure(0.21, 100.0), 21.0)
        self.assertAlmostEqual(oxygen_partial_pressure(0.30, 10.2), 3.06)

    def test_partial_pressure_rejects_percent_scale_and_nonpositive_pressure(self):
        with self.assertRaises(ValueError):
            oxygen_partial_pressure(30.0, 10.2)
        with self.assertRaises(ValueError):
            oxygen_partial_pressure(0.21, 0.0)

    def test_partial_pressure_rejects_underflow_and_boolean_inputs(self):
        with self.assertRaisesRegex(ValueError, "underflows"):
            oxygen_partial_pressure(5e-324, 5e-324)
        with self.assertRaises(TypeError):
            oxygen_partial_pressure(True, 1.0)

    def test_air_oxygen_mass_fraction_for_binary_o2_n2(self):
        expected = (0.21 * 31.998) / (0.21 * 31.998 + 0.79 * 28.014)
        self.assertAlmostEqual(
            oxygen_mass_fraction(0.21, 28.014, diluent_verified=True), expected
        )
        self.assertAlmostEqual(expected, 0.2329092179584231)

    def test_pure_species_mass_fraction_boundaries(self):
        self.assertEqual(oxygen_mass_fraction(0.0, 28.014, diluent_verified=True), 0.0)
        self.assertEqual(oxygen_mass_fraction(1.0, 28.014, diluent_verified=True), 1.0)

    def test_mass_fraction_rejects_nonpositive_molar_mass(self):
        for mass in (0.0, -1.0, math.nan, math.inf):
            with self.subTest(mass=mass), self.assertRaises(ValueError):
                oxygen_mass_fraction(0.21, diluent_molar_mass_g_mol=mass,
                                     diluent_verified=True)

    def test_mass_fraction_rejects_underflow_to_zero(self):
        with self.assertRaisesRegex(ValueError, "underflows"):
            oxygen_mass_fraction(5e-324, 1e308, diluent_verified=True)

    def test_mass_fraction_requires_explicit_verified_diluent(self):
        with self.assertRaises(ValueError):
            oxygen_mass_fraction(0.21)
        with self.assertRaises(ValueError):
            oxygen_mass_fraction(0.21, 28.014)
        with self.assertRaises(TypeError):
            oxygen_mass_fraction(0.21, 28.014, diluent_verified="yes")


class CompareAtmospheresTests(unittest.TestCase):
    def test_equivalent_mixed_unit_atmospheres_have_equal_partial_pressure(self):
        result = compare_atmospheres(
            oxygen_fraction=0.20,
            total_pressure=2.0,
            reference_oxygen_fraction=0.4053,
            reference_pressure=1.0,
            pressure_unit="atm",
            reference_pressure_unit="bar",
        )
        self.assertAlmostEqual(
            result["scenario"]["oxygen_partial_pressure_kpa"], 40.53
        )
        self.assertAlmostEqual(
            result["reference"]["oxygen_partial_pressure_kpa"], 40.53
        )
        self.assertAlmostEqual(
            result["oxygen_partial_pressure_difference_kpa"], 0.0
        )

    def test_empty_explicit_reference_unit_is_not_silently_replaced(self):
        with self.assertRaisesRegex(ValueError, "unsupported pressure unit"):
            compare_atmospheres(0.2, 1.0, 0.2, 1.0, "bar", "")

    def test_zero_reference_partial_pressure_has_no_relative_difference(self):
        result = compare_atmospheres(
            oxygen_fraction=0.21,
            total_pressure=101.325,
            reference_oxygen_fraction=0.0,
            reference_pressure=101.325,
            pressure_unit="kPa",
        )
        self.assertIsNone(result["relative_oxygen_partial_pressure_difference"])


class TypedAtmosphereTests(unittest.TestCase):
    def setUp(self):
        self.source = InputProvenance(
            origin=InputOrigin.SOURCE_RECORD,
            verification_status=VerificationStatus.MEASURED,
            source_id="TEST-SOURCE-1",
            source_locator="Table 2, row 4",
            raw_value="30 vol%",
            raw_unit="vol%",
            normalization_method="Normalized 30 vol% to 0.30 after gas-basis review.",
        )
        self.pressure_source = InputProvenance(
            origin=InputOrigin.SOURCE_RECORD,
            verification_status=VerificationStatus.MEASURED,
            source_id="TEST-SOURCE-1",
            source_locator="Table 2, row 4",
            raw_value=10.2,
            raw_unit="psi",
        )
        self.diluent_source = InputProvenance(
            origin=InputOrigin.SOURCE_RECORD,
            verification_status=VerificationStatus.MEASURED,
            source_id="TEST-GAS-SOURCE-1",
            source_locator="Gas composition, row 1",
            raw_value=28.014,
            raw_unit="g/mol",
        )
        self.condition = AtmosphericCondition(
            oxygen_mole_fraction=0.30,
            total_pressure=10.2,
            pressure_unit=PressureUnit.PSI,
            pressure_basis=PressureBasis.ABSOLUTE,
            gas_basis_verified=True,
            oxygen_verification=VerificationStatus.MEASURED,
            pressure_verification=VerificationStatus.MEASURED,
            provenance={"oxygen_mole_fraction": self.source,
                        "total_pressure": self.pressure_source},
        )

    def test_partial_pressure_reference_case_and_normalization(self):
        # Independent arithmetic: 0.30 * 10.2 psi = 3.06 psi.
        result = calculate_oxygen_partial_pressure(self.condition)
        self.assertAlmostEqual(result.outputs["oxygen_partial_pressure_kpa"], 3.06 * 6.894757293168361)
        self.assertAlmostEqual(result.outputs["total_pressure_kpa"], 10.2 * 6.894757293168361)
        self.assertEqual(result.verification["result"], "DERIVED")

    def test_unverified_gas_basis_is_rejected(self):
        unverified = AtmosphericCondition(0.3, 10.2, "psi", PressureBasis.ABSOLUTE)
        with self.assertRaisesRegex(ValueError, "gas-phase mole-fraction basis"):
            calculate_oxygen_partial_pressure(unverified)

    def test_invalid_condition_values_and_units(self):
        for fraction in (-0.01, 1.01, math.nan, True):
            with self.subTest(fraction=fraction), self.assertRaises((ValueError, TypeError)):
                AtmosphericCondition(fraction, 100.0, "kPa", PressureBasis.ABSOLUTE, gas_basis_verified=True)
        for pressure in (0.0, -1.0, math.inf):
            with self.subTest(pressure=pressure), self.assertRaises(ValueError):
                AtmosphericCondition(0.2, pressure, "kPa", PressureBasis.ABSOLUTE, gas_basis_verified=True)
        with self.assertRaises(ValueError):
            AtmosphericCondition(0.2, 100.0, "mmHg", PressureBasis.ABSOLUTE, gas_basis_verified=True)
        with self.assertRaises(TypeError):
            AtmosphericCondition(None, 100.0, "kPa", PressureBasis.ABSOLUTE, gas_basis_verified=True)
        for basis in ("gauge", "unspecified"):
            with self.subTest(basis=basis), self.assertRaises(ValueError):
                AtmosphericCondition(0.2, 100.0, "kPa", basis, gas_basis_verified=True)

    def test_mass_fraction_requires_verified_explicit_composition(self):
        with self.assertRaisesRegex(ValueError, "composition is required"):
            calculate_oxygen_mass_fraction(self.condition)
        unverified_diluent = BinaryDiluent("nitrogen", 28.014)
        condition = OxygenComposition(0.21, True, diluent=unverified_diluent)
        with self.assertRaisesRegex(ValueError, "must have MEASURED or DERIVED"):
            calculate_oxygen_mass_fraction(condition)
        with self.assertRaisesRegex(ValueError, "gas-phase mole-fraction basis"):
            calculate_oxygen_mass_fraction(OxygenComposition(0.21, False, diluent=unverified_diluent))
        verified_diluent = BinaryDiluent(
            "nitrogen", 28.014, VerificationStatus.MEASURED, self.diluent_source
        )
        verified = OxygenComposition(0.21, True, diluent=verified_diluent)
        result = calculate_oxygen_mass_fraction(verified)
        expected = (0.21 * 31.998) / (0.21 * 31.998 + 0.79 * 28.014)
        self.assertAlmostEqual(result.outputs["oxygen_mass_fraction"], expected)
        argon = BinaryDiluent(
            "argon", 39.948, VerificationStatus.MEASURED, self.source
        )
        argon_composition = OxygenComposition(0.21, True, diluent=argon)
        argon_result = calculate_oxygen_mass_fraction(argon_composition)
        self.assertNotAlmostEqual(argon_result.outputs["oxygen_mass_fraction"], expected)

    def test_comparison_reports_differences_and_relative_values(self):
        other = AtmosphericCondition(0.2, 1.0, "bar", PressureBasis.ABSOLUTE, True)
        result = compare_atmospheric_conditions(self.condition, other)
        self.assertAlmostEqual(
            result.outputs["scenario"]["oxygen_partial_pressure_kpa"],
            0.3 * 10.2 * 6.894757293168361,
        )
        self.assertIn(
            "Equal oxygen partial pressures do not establish combustion equivalence.",
            result.limitations,
        )

    def test_equal_atmospheres_produce_zero_differences(self):
        state = AtmosphericCondition(0.2, 1.0, "bar", PressureBasis.ABSOLUTE, True)
        result = compare_atmospheric_conditions(state, state)
        self.assertEqual(
            result.outputs["differences_scenario_minus_reference"],
            {"oxygen_mole_fraction": 0.0, "total_pressure_kpa": 0.0,
             "oxygen_partial_pressure_kpa": 0.0},
        )

    def test_typed_comparison_warns_when_reference_value_is_zero(self):
        zero_o2 = AtmosphericCondition(0.0, 100.0, "kPa", PressureBasis.ABSOLUTE, True)
        result = compare_atmospheric_conditions(self.condition, zero_o2)
        self.assertIsNone(result.outputs["relative_differences"]["oxygen_partial_pressure_kpa"])
        self.assertTrue(any("reference value is zero" in item for item in result.warnings))

    def test_result_is_json_compatible_and_preserves_provenance(self):
        result = calculate_oxygen_partial_pressure(self.condition)
        encoded = json.dumps(result.to_dict(), allow_nan=False)
        decoded = json.loads(encoded)
        self.assertEqual(decoded["status"], "success")
        self.assertEqual(decoded["formula"], "pO2 = X_O2 * P_total")
        self.assertEqual(decoded["provenance"]["oxygen_mole_fraction"]["source_id"], "TEST-SOURCE-1")
        self.assertEqual(decoded["provenance"]["oxygen_mole_fraction"]["raw_value"], "30 vol%")
        self.assertEqual(decoded["provenance"]["oxygen_mole_fraction"]["raw_unit"], "vol%")
        self.assertIn("gas-basis review", decoded["conversion_methods"]["oxygen_mole_fraction"])
        self.assertEqual(decoded["verification"]["oxygen"], "MEASURED")

    def test_user_supplied_input_is_not_automatically_measured(self):
        with self.assertRaisesRegex(ValueError, "MEASURED inputs require source-record provenance"):
            InputProvenance(verification_status=VerificationStatus.MEASURED)

    def test_measured_condition_requires_field_level_source_provenance(self):
        with self.assertRaisesRegex(ValueError, "MEASURED oxygen_mole_fraction requires"):
            AtmosphericCondition(
                0.21, 100.0, "kPa", PressureBasis.ABSOLUTE, True,
                oxygen_verification=VerificationStatus.MEASURED,
            )

    def test_numeric_condition_cannot_be_marked_missing(self):
        with self.assertRaisesRegex(ValueError, "numeric value and cannot be marked MISSING"):
            AtmosphericCondition(
                0.21, 100.0, "kPa", PressureBasis.ABSOLUTE, True,
                oxygen_verification=VerificationStatus.MISSING,
            )

    def test_result_serializer_rejects_nonfinite_values(self):
        from modelling.atmospheric import CalculationResult

        result = CalculationResult(
            calculation="invalid", formula="x", inputs={}, outputs={"bad": math.inf},
            units={}, verification={},
        )
        with self.assertRaisesRegex(ValueError, "NaN or infinity"):
            result.to_dict()
        bad_key = CalculationResult(
            calculation="invalid", formula="x", inputs={}, outputs={1: "bad"},
            units={}, verification={},
        )
        with self.assertRaisesRegex(TypeError, "keys must be strings"):
            bad_key.to_dict()

    def test_percentage_raw_value_requires_normalization_provenance(self):
        source = InputProvenance(
            origin=InputOrigin.SOURCE_RECORD,
            verification_status=VerificationStatus.UNVERIFIED,
            source_id="SOURCE-1",
            source_locator="Table row 1",
            raw_value="30 vol%",
            raw_unit="vol%",
        )
        with self.assertRaisesRegex(ValueError, "requires a normalization method"):
            AtmosphericCondition(
                0.30, 100.0, "kPa", PressureBasis.ABSOLUTE,
                provenance={"oxygen_mole_fraction": source},
            )

    def test_pressure_conversion_result_records_method_and_origin(self):
        result = calculate_pressure_conversion(
            10.2, "psi", pressure_basis=PressureBasis.ABSOLUTE,
            provenance=self.pressure_source
        ).to_dict()
        self.assertAlmostEqual(result["outputs"]["value"], 10.2 * 6.894757293168361)
        self.assertEqual(result["provenance"]["pressure"]["origin"], "source_record")
        self.assertEqual(result["verification"]["result"], "DERIVED")

    def test_pressure_conversion_requires_absolute_basis(self):
        with self.assertRaisesRegex(ValueError, "pressure_basis must be explicitly"):
            calculate_pressure_conversion(10.2, "psi", pressure_basis="gauge")

    def test_pressure_provenance_unit_mismatch_requires_normalization(self):
        evidence = InputProvenance(
            origin=InputOrigin.SOURCE_RECORD,
            verification_status=VerificationStatus.MEASURED,
            source_id="PRESSURE-SOURCE",
            source_locator="Table 1, row 2",
            raw_value=1.0,
            raw_unit="atm",
        )
        with self.assertRaisesRegex(ValueError, "Pressure provenance requires a normalization method"):
            calculate_pressure_conversion(
                101.325, "kPa", pressure_basis="absolute", provenance=evidence
            )


if __name__ == "__main__":
    unittest.main()
