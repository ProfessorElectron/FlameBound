import math
import unittest

from modelling.atmospheric import (
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

    def test_partial_pressure_rejects_percent_scale_and_nonpositive_pressure(self):
        with self.assertRaises(ValueError):
            oxygen_partial_pressure(30.0, 10.2)
        with self.assertRaises(ValueError):
            oxygen_partial_pressure(0.21, 0.0)

    def test_air_oxygen_mass_fraction_for_binary_o2_n2(self):
        expected = (0.21 * 31.998) / (0.21 * 31.998 + 0.79 * 28.014)
        self.assertAlmostEqual(oxygen_mass_fraction(0.21), expected)

    def test_pure_species_mass_fraction_boundaries(self):
        self.assertEqual(oxygen_mass_fraction(0.0), 0.0)
        self.assertEqual(oxygen_mass_fraction(1.0), 1.0)

    def test_mass_fraction_rejects_nonpositive_molar_mass(self):
        with self.assertRaises(ValueError):
            oxygen_mass_fraction(0.21, diluent_molar_mass_g_mol=0.0)


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

    def test_zero_reference_partial_pressure_has_no_relative_difference(self):
        result = compare_atmospheres(
            oxygen_fraction=0.21,
            total_pressure=101.325,
            reference_oxygen_fraction=0.0,
            reference_pressure=101.325,
            pressure_unit="kPa",
        )
        self.assertIsNone(result["relative_oxygen_partial_pressure_difference"])


if __name__ == "__main__":
    unittest.main()
