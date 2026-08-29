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

    def test_expected_candidate_split_and_controls(self):
        self.assertEqual(len(self.report["cases"]), 7)
        for case in self.report["cases"]:
            self.assertEqual(set(case["control_outcomes"].values()), {"ACCEPT"})
        proof = next(case for case in self.report["cases"] if "proof_parameter" in case["boundary"])
        self.assertEqual(proof["candidate_outcomes"]["kiota"], "ACCEPT")
        self.assertEqual(
            {outcome for checker, outcome in proof["candidate_outcomes"].items() if checker != "kiota"},
            {"REJECT"},
        )

    def test_survival_is_not_reported_as_equivalence(self):
        probes = [case["mutation_sensitivity"] for case in self.report["cases"] if case["mutation_sensitivity"]]
        self.assertEqual(len(probes), 4)
        self.assertEqual(
            {probe["classification"] for probe in probes},
            {"SURVIVED_EXACT_CANDIDATE", "KILLED_BY_CANDIDATE"},
        )
        self.assertIn("does not establish positivity", self.report["observed_rules"]["mutation_interpretation"])

    def test_continued_local_investigation_is_recommended(self):
        recommendation = self.report["recommended_action"]
        self.assertEqual(recommendation["action"], "CONTINUE_INVESTIGATION")
        self.assertTrue(recommendation["external_action"])
        self.assertEqual(recommendation["human_gate"], "REVIEW_REQUIRED")


if __name__ == "__main__":
    unittest.main()
