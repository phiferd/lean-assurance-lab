import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ITEM = ROOT / "results/research/survivor-thread-one-determinism-1"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SurvivorThreadOneDeterminismClosureTests(unittest.TestCase):
    def test_assessment_binds_the_fixed_source_boundary(self):
        assessment = json.loads((ITEM / "determinism-assessment.json").read_text())
        self.assertEqual(assessment["status"], "SOURCE_SUPPORTED_PROTOCOL_CANDIDATE")
        self.assertFalse(assessment["scope"]["execution_used"])
        self.assertEqual(assessment["scope"]["public_configuration"], "num_threads=1")
        self.assertEqual(assessment["scope"]["baseline"], "check_all_declars_serial")
        self.assertEqual(assessment["scope"]["mutant"], "check_all_declars_par(1)")
        for binding in assessment["evidence_bindings"]:
            self.assertEqual(digest(ROOT / binding["path"]), binding["sha256"])

    def test_protocol_is_operational_and_has_four_fixed_cells(self):
        assessment = json.loads((ITEM / "determinism-assessment.json").read_text())
        cells = assessment["protocol_candidate"]["future_matrix"]
        self.assertEqual([cell["cell"] for cell in cells], [
            "control-baseline", "control-mutant", "candidate-baseline", "candidate-mutant",
        ])
        self.assertEqual([cell["expected"] for cell in cells[:2]], ["ACCEPT", "ACCEPT"])
        self.assertIn("JOIN", cells[-1]["expected"])
        self.assertIn("does not establish a semantic validation difference", assessment["conclusion"])

    def test_result_preserves_the_no_launch_boundary(self):
        result = json.loads((ITEM / "result.json").read_text())
        self.assertEqual(result["outcome"], "SUCCESS")
        self.assertGreater(result["execution_accounting"]["active_seconds"], 0)
        self.assertEqual(result["execution_accounting"]["local_source_or_evidence_inspections"], 8)
        for name, value in result["execution_accounting"].items():
            if name not in {"active_seconds", "local_source_or_evidence_inspections"}:
                self.assertEqual(value, 0)
        self.assertEqual(result["next_item"], "SURVIVOR-THREAD-ONE-CHILD-PANIC-REGRESSION-1")
        self.assertFalse(result["next_item_started"])


if __name__ == "__main__":
    unittest.main()
