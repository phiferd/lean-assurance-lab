import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class OrdinaryInductiveContractMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(
            (ROOT / "results" / "investigations" / "nanoda-ordinary-inductive-contract-matrix.json").read_text()
        )

    def test_matrix_passes(self):
        self.assertEqual(self.report["status"], "PASS")
        self.assertTrue(all(self.report["checks"].values()))

    def test_all_candidates_reject_and_controls_accept(self):
        self.assertEqual(len(self.report["cases"]), 6)
        for case in self.report["cases"]:
            self.assertEqual(set(case["candidate_outcomes"].values()), {"REJECT"})
            self.assertEqual(set(case["control_outcomes"].values()), {"ACCEPT"})

    def test_survival_is_not_reported_as_equivalence(self):
        probes = [case["mutation_sensitivity"] for case in self.report["cases"] if case["mutation_sensitivity"]]
        self.assertEqual(len(probes), 3)
        self.assertEqual({probe["classification"] for probe in probes}, {"SURVIVED_EXACT_CANDIDATE"})
        self.assertIn("does not establish", self.report["observed_rules"]["mutation_interpretation"])

    def test_continued_local_investigation_is_recommended(self):
        recommendation = self.report["recommended_action"]
        self.assertEqual(recommendation["action"], "CONTINUE_INVESTIGATION")
        self.assertFalse(recommendation["external_action"])


if __name__ == "__main__":
    unittest.main()
