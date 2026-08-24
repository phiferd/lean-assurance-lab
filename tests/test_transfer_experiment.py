import json
import sys
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

from kiota_differential import classify_transfer  # noqa: E402


def evaluation(baseline: str, mutant: str) -> dict:
    return {
        "baseline": {"normalized_outcome": baseline},
        "mutant": {"normalized_outcome": mutant},
        "different": baseline != mutant,
    }


class TransferExperimentTests(unittest.TestCase):
    def test_experiment_spec_declares_held_out_fault_without_results(self):
        spec = json.loads((ROOT / "experiments" / "milestone-6" / "spec.json").read_text())
        self.assertEqual(spec["held_out_validator"], "kiota")
        self.assertEqual(spec["source_mutant"], "nanoda-0001")
        self.assertNotIn("outcome", json.dumps(spec).lower())

    def test_positive_transfer_requires_modeled_direction_and_control(self):
        result = classify_transfer(evaluation("REJECT", "ACCEPT"), evaluation("ACCEPT", "ACCEPT"), "REJECT")
        self.assertEqual(result[0], "POSITIVE_TRANSFER")

    def test_every_exit_classification_is_reachable(self):
        cases = {
            "NEUTRAL_TRANSFER": (evaluation("REJECT", "REJECT"), evaluation("ACCEPT", "ACCEPT"), "REJECT"),
            "NEGATIVE_TRANSFER": (evaluation("ACCEPT", "REJECT"), evaluation("ACCEPT", "ACCEPT"), "REJECT"),
            "INCONCLUSIVE": (evaluation("TIMEOUT", "ACCEPT"), evaluation("ACCEPT", "ACCEPT"), "REJECT"),
            "INCOMPATIBLE": (evaluation("REJECT", "ACCEPT"), evaluation("REJECT", "ACCEPT"), "REJECT"),
            "UNRESOLVED": (evaluation("ACCEPT", "REJECT"), evaluation("ACCEPT", "ACCEPT"), "ACCEPT"),
        }
        for expected, args in cases.items():
            with self.subTest(expected=expected):
                self.assertEqual(classify_transfer(*args)[0], expected)

    def test_transfer_schemas_are_valid(self):
        for name in ("transfer-freeze.schema.json", "transfer-evaluation.schema.json"):
            schema = json.loads((ROOT / "schemas" / name).read_text())
            jsonschema.Draft202012Validator.check_schema(schema)


if __name__ == "__main__":
    unittest.main()
