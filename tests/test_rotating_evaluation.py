import json
import sys
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

from lean4lean_differential import classify_fold  # noqa: E402


def evaluation(baseline: str, mutant: str) -> dict:
    return {
        "baseline": {"normalized_outcome": baseline},
        "mutant": {"normalized_outcome": mutant},
        "different": baseline != mutant,
    }


class RotatingEvaluationTests(unittest.TestCase):
    def test_spec_declares_fresh_held_out_fold_without_outcomes(self):
        spec = json.loads((ROOT / "experiments" / "milestone-7" / "spec.json").read_text())
        self.assertEqual(spec["source_validator"], "kiota")
        self.assertEqual(spec["held_out_validator"], "lean4lean")
        self.assertFalse(spec["generation"]["uses_held_out_mutant_feedback"])
        self.assertNotIn("outcome", json.dumps(spec).lower())

    def test_positive_fold_requires_score_improvement_and_control(self):
        result = classify_fold(
            0, 1, evaluation("REJECT", "ACCEPT"), evaluation("ACCEPT", "ACCEPT"), "REJECT"
        )
        self.assertEqual(result[0], "POSITIVE")

    def test_rotating_fold_classifications_are_reachable(self):
        cases = {
            "NEUTRAL": (1, 1, evaluation("REJECT", "ACCEPT"), evaluation("ACCEPT", "ACCEPT"), "REJECT"),
            "NEGATIVE": (0, 1, evaluation("REJECT", "ACCEPT"), evaluation("ACCEPT", "REJECT"), "REJECT"),
            "INCONCLUSIVE": (0, 0, evaluation("TIMEOUT", "ACCEPT"), evaluation("ACCEPT", "ACCEPT"), "REJECT"),
            "INCOMPATIBLE": (0, 0, evaluation("REJECT", "ACCEPT"), evaluation("REJECT", "REJECT"), "REJECT"),
            "UNRESOLVED": (0, 0, evaluation("ACCEPT", "REJECT"), evaluation("ACCEPT", "ACCEPT"), "ACCEPT"),
        }
        for expected, args in cases.items():
            with self.subTest(expected=expected):
                self.assertEqual(classify_fold(*args)[0], expected)

    def test_rotating_schemas_are_valid(self):
        for name in (
            "rotating-fold-spec.schema.json",
            "rotating-fold-freeze.schema.json",
            "rotating-fold-evaluation.schema.json",
            "rotating-heldout-report.schema.json",
        ):
            schema = json.loads((ROOT / "schemas" / name).read_text())
            jsonschema.Draft202012Validator.check_schema(schema)

    def test_completed_report_has_rotated_validators_and_bounded_claim(self):
        report_path = ROOT / "results" / "rotating-heldout" / "milestone-7" / "report.json"
        if not report_path.exists():
            self.skipTest("Milestone 7 report not generated")
        report = json.loads(report_path.read_text())
        self.assertEqual(len({fold["held_out_validator"] for fold in report["folds"]}), 2)
        self.assertEqual(report["aggregate_score"]["score_change"], 0.5)
        self.assertIn("not a general transfer-rate estimate", report["interpretation"]["scope"])


if __name__ == "__main__":
    unittest.main()
