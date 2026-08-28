import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReductionSemanticsMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(
            (ROOT / "results" / "investigations" / "nanoda-reduction-semantics-matrix.json").read_text()
        )

    def test_matrix_passes(self):
        self.assertEqual(self.report["status"], "PASS")
        self.assertTrue(all(self.report["checks"].values()))

    def test_all_candidates_and_controls_are_consensus_accepts(self):
        self.assertEqual(len(self.report["cases"]), 8)
        for case in self.report["cases"]:
            self.assertEqual(set(case["candidate_outcomes"].values()), {"ACCEPT"})
            self.assertEqual(set(case["control_outcomes"].values()), {"ACCEPT"})

    def test_mutation_sensitivity_preserves_observational_limits(self):
        by_boundary = {case["boundary"]: case for case in self.report["cases"]}
        self.assertEqual(
            by_boundary["quot_lift_reduction"]["mutation_sensitivity"]["classification"],
            "KILLED_BY_CANDIDATE",
        )
        self.assertEqual(
            by_boundary["quot_ind_proof_reduction"]["mutation_sensitivity"]["classification"],
            "OBSERVATIONALLY_EQUIVALENT",
        )
        self.assertEqual(
            by_boundary["native_nat_ble_reduction"]["mutation_sensitivity"]["classification"],
            "SURVIVED_EXACT_CANDIDATE",
        )
        self.assertEqual(
            by_boundary["native_nat_land_reduction"]["mutation_sensitivity"]["classification"],
            "KILLED_BY_CANDIDATE",
        )

    def test_no_external_action_is_recommended(self):
        recommendation = self.report["recommended_action"]
        self.assertEqual(recommendation["action"], "CONTINUE_INVESTIGATION")
        self.assertFalse(recommendation["external_action"])


if __name__ == "__main__":
    unittest.main()
