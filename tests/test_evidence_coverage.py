
import unittest

from modelling.evidence_coverage import FeatureSpec, gower_distance

from modelling.evidence_coverage import nearest_neighbours

from modelling.evidence_coverage import filter_eligible_experiments


class GowerDistanceTests(unittest.TestCase):

    def test_numeric_distance(self):
        features = [
            FeatureSpec(
                name="oxygen",
                kind="numeric",
                minimum=0.0,
                maximum=1.0,
            )
        ]

        result = gower_distance(
            {"oxygen": 0.2},
            {"oxygen": 0.7},
            features,
        )

        self.assertAlmostEqual(result["distance"], 0.5)

    def test_categorical_distance(self):
        features = [
            FeatureSpec(name="gravity", kind="categorical")
        ]

        same = gower_distance(
            {"gravity": "microgravity"},
            {"gravity": "microgravity"},
            features,
        )

        different = gower_distance(
            {"gravity": "microgravity"},
            {"gravity": "1g"},
            features,
        )

        self.assertEqual(same["distance"], 0.0)
        self.assertEqual(different["distance"], 1.0)

    def test_weighted_mixed_distance(self):
        features = [
            FeatureSpec(
                name="oxygen",
                kind="numeric",
                weight=2.0,
                minimum=0.0,
                maximum=1.0,
            ),
            FeatureSpec(
                name="gravity",
                kind="categorical",
                weight=1.0,
            ),
        ]

        result = gower_distance(
            {"oxygen": 0.2, "gravity": "microgravity"},
            {"oxygen": 0.7, "gravity": "1g"},
            features,
        )

        expected = (2.0 * 0.5 + 1.0 * 1.0) / 3.0
        self.assertAlmostEqual(result["distance"], expected)

    def test_missing_features_are_excluded(self):
        features = [
            FeatureSpec(
                name="oxygen",
                kind="numeric",
                minimum=0.0,
                maximum=1.0,
                weight=1.0,
            ),
            FeatureSpec(
                name="gravity",
                kind="categorical",
                weight=1.0,
            ),
        ]

        result = gower_distance(
            {"oxygen": 0.2, "gravity": None},
            {"oxygen": 0.7, "gravity": "1g"},
            features,
        )

        self.assertAlmostEqual(result["distance"], 0.5)
        self.assertAlmostEqual(
            result["compared_weight_fraction"], 0.5
        )

    def test_all_missing_features_return_no_distance(self):
        features = [
            FeatureSpec(
                name="oxygen",
                kind="numeric",
                minimum=0.0,
                maximum=1.0,
            )
        ]

        result = gower_distance(
            {"oxygen": None},
            {"oxygen": 0.5},
            features,
        )

        self.assertIsNone(result["distance"])
        self.assertEqual(result["compared_weight_fraction"], 0.0)

    def test_zero_numeric_range_is_handled(self):
        features = [
            FeatureSpec(
                name="pressure",
                kind="numeric",
                minimum=100.0,
                maximum=100.0,
            )
        ]

        result = gower_distance(
            {"pressure": 100.0},
            {"pressure": 100.0},
            features,
        )

        self.assertEqual(result["distance"], 0.0)

    def test_numeric_values_outside_reference_range_are_rejected(self):
        features = [
            FeatureSpec(
                name="oxygen",
                kind="numeric",
                minimum=0.0,
                maximum=1.0,
            )
        ]

        with self.assertRaises(ValueError):
            gower_distance(
                {"oxygen": 1.2},
                {"oxygen": 0.5},
                features,
            )

    def test_invalid_feature_weight_is_rejected(self):
        with self.assertRaises(ValueError):
            FeatureSpec(
                name="oxygen",
                kind="numeric",
                weight=-1.0,
                minimum=0.0,
                maximum=1.0,
            )


class NearestNeighbourTests(unittest.TestCase):

    def setUp(self):
        self.features = [
            FeatureSpec(
                name="oxygen",
                kind="numeric",
                minimum=0.0,
                maximum=1.0,
            )
        ]

        self.experiments = [
            {"record_id": "B1", "oxygen": 0.20},
            {"record_id": "B2", "oxygen": 0.50},
            {"record_id": "B3", "oxygen": 0.80},
            {"record_id": "B4", "oxygen": 0.30},
        ]

    def test_returns_nearest_records_in_ascending_order(self):
        results = nearest_neighbours(
            {"oxygen": 0.25},
            self.experiments,
            self.features,
            k=3,
        )

        self.assertEqual(
            [item["record_id"] for item in results],
            ["B1", "B4", "B2"],
        )

    def test_returns_requested_number_of_neighbours(self):
        results = nearest_neighbours(
            {"oxygen": 0.25},
            self.experiments,
            self.features,
            k=2,
        )

        self.assertEqual(len(results), 2)

    def test_excludes_records_with_no_comparable_features(self):
        experiments = [
            {"record_id": "B1", "oxygen": None},
            {"record_id": "B2", "oxygen": 0.30},
        ]

        results = nearest_neighbours(
            {"oxygen": 0.25},
            experiments,
            self.features,
            k=3,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["record_id"], "B2")

class EvidenceCoverageValidationTests(unittest.TestCase):

    def test_duplicate_feature_names_are_rejected(self):
        features = [
            FeatureSpec(
                name="oxygen",
                kind="numeric",
                minimum=0.0,
                maximum=1.0,
            ),
            FeatureSpec(
                name="oxygen",
                kind="numeric",
                minimum=0.0,
                maximum=1.0,
            ),
        ]

        with self.assertRaises(ValueError):
            gower_distance(
                {"oxygen": 0.2},
                {"oxygen": 0.5},
                features,
            )

    def test_categorical_features_reject_numeric_ranges(self):
        with self.assertRaises(ValueError):
            FeatureSpec(
                name="gravity",
                kind="categorical",
                minimum=0.0,
                maximum=1.0,
            )

    def test_neighbours_below_coverage_threshold_are_excluded(self):
        features = [
            FeatureSpec(
                name="oxygen",
                kind="numeric",
                minimum=0.0,
                maximum=1.0,
                weight=1.0,
            ),
            FeatureSpec(
                name="gravity",
                kind="categorical",
                weight=1.0,
            ),
        ]

        scenario = {
            "oxygen": 0.25,
            "gravity": None,
        }

        experiments = [
            {
                "record_id": "B1",
                "oxygen": 0.25,
                "gravity": None,
            },
            {
                "record_id": "B2",
                "oxygen": 0.30,
                "gravity": "microgravity",
            },
        ]

        results = nearest_neighbours(
            scenario,
            experiments,
            features,
            k=3,
            min_compared_weight_fraction=0.75,
        )

        self.assertEqual(len(results), 0)

class EligibilityFilterTests(unittest.TestCase):

    def setUp(self):
        self.experiments = [
            {
                "record_id": "B1",
                "gravity_category": "microgravity",
                "fuel_class": "thermoplastic",
                "sample_geometry": "film",
            },
            {
                "record_id": "B2",
                "gravity_category": "1g",
                "fuel_class": "thermoplastic",
                "sample_geometry": "film",
            },
            {
                "record_id": "B3",
                "gravity_category": "microgravity",
                "fuel_class": "cellulosic",
                "sample_geometry": "film",
            },
            {
                "record_id": "B4",
                "gravity_category": "microgravity",
                "fuel_class": "thermoplastic",
                "sample_geometry": "rod",
            },
        ]

        self.requirements = {
            "gravity_category": "microgravity",
            "fuel_class": "thermoplastic",
        }

    def test_excludes_incompatible_gravity_and_fuel(self):
        result = filter_eligible_experiments(
            self.experiments,
            self.requirements,
        )

        eligible_ids = [
            record["record_id"]
            for record in result["eligible"]
        ]

        self.assertEqual(eligible_ids, ["B1", "B4"])

    def test_optional_geometry_filter(self):
        result = filter_eligible_experiments(
            self.experiments,
            {
                **self.requirements,
                "sample_geometry": "film",
            },
        )

        eligible_ids = [
            record["record_id"]
            for record in result["eligible"]
        ]

        self.assertEqual(eligible_ids, ["B1"])

    def test_missing_required_metadata_is_excluded(self):
        experiments = [
            {
                "record_id": "B5",
                "gravity_category": None,
                "fuel_class": "thermoplastic",
            }
        ]

        result = filter_eligible_experiments(
            experiments,
            self.requirements,
        )

        self.assertEqual(len(result["eligible"]), 0)
        self.assertEqual(len(result["excluded"]), 1)

    def test_exclusion_reasons_are_returned(self):
        result = filter_eligible_experiments(
            self.experiments,
            self.requirements,
        )

        excluded = {
            item["record_id"]: item["reasons"]
            for item in result["excluded"]
        }

        self.assertIn("gravity_category", excluded["B2"])
        self.assertIn("fuel_class", excluded["B3"])


if __name__ == "__main__":
    unittest.main()
