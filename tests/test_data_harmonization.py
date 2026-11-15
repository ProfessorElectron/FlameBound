import unittest

from modelling.data_harmonization import (
    classify_outcome,
    flag_duplicate_records,
    oxygen_fraction,
    oxygen_partial_pressure_kpa,
    pressure_kpa,
    speed_m_s,
)


class HarmonizationValidationTests(unittest.TestCase):
    def test_explicit_unit_conversions(self):
        self.assertAlmostEqual(oxygen_fraction(21.5, "vol%", volume_percent_is_mole_fraction=True), 0.215)
        self.assertAlmostEqual(oxygen_fraction(0.215, "fraction"), 0.215)
        self.assertAlmostEqual(pressure_kpa(1, "atm", "absolute"), 101.325)
        self.assertAlmostEqual(speed_m_s(30, "cm/s"), 0.3)
        self.assertAlmostEqual(oxygen_partial_pressure_kpa(0.215, 101.325), 21.784875)

    def test_missing_values_remain_missing_and_zero_is_not_missing(self):
        self.assertIsNone(oxygen_fraction("", "vol%"))
        self.assertIsNone(pressure_kpa("n/a", "kPa", "absolute"))
        self.assertIsNone(speed_m_s(None, "cm/s"))
        self.assertIsNone(oxygen_partial_pressure_kpa(None, 101.325))
        self.assertEqual(oxygen_fraction(0, "vol%", volume_percent_is_mole_fraction=True), 0)

    def test_unknown_units_and_unverified_pressure_basis_are_rejected(self):
        with self.assertRaises(ValueError):
            oxygen_fraction(21, "unknown")
        with self.assertRaises(ValueError):
            oxygen_fraction(21, "vol%")
        with self.assertRaises(ValueError):
            oxygen_fraction(21, "percent")
        with self.assertRaises(TypeError):
            oxygen_fraction(21, "vol%", volume_percent_is_mole_fraction="yes")
        with self.assertRaises(ValueError):
            pressure_kpa(14.7, "psi", "unspecified")
        with self.assertRaises(ValueError):
            speed_m_s(1, "fan setting")

    def test_unverified_outcome_is_never_classified(self):
        mapping = {"flame extinguished": "extinction"}
        self.assertEqual(classify_outcome("flame extinguished", False, mapping), "unknown")
        self.assertEqual(classify_outcome("", True, {"": "extinction"}), "unknown")
        self.assertEqual(classify_outcome("unclear result", True, {}), "ambiguous")
        self.assertEqual(classify_outcome("flame extinguished", True, mapping), "extinction")

    def test_duplicate_records_are_flagged_but_never_merged(self):
        rows = [
            {"source_row": 2, "test_id": "A", "value": 1},
            {"source_row": 3, "test_id": "A", "value": 1},
            {"source_row": 4, "test_id": "B", "value": 2},
        ]
        audited = flag_duplicate_records(rows, ["test_id", "value"])
        self.assertEqual(len(audited), len(rows))
        self.assertEqual([r["source_row"] for r in audited], [2, 3, 4])
        self.assertEqual([r["duplicate_source_record"] for r in audited], [True, True, False])
        self.assertEqual([r["duplicate_group_size"] for r in audited], [2, 2, 1])


if __name__ == "__main__":
    unittest.main()
