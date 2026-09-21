from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results/research/child-panic-confirmation-1"


def load(relative: str):
    return json.loads((BASE / relative).read_text(encoding="utf-8"))


class ChildPanicConfirmationClosureTests(unittest.TestCase):
    def test_fixed_four_cell_oracle(self):
        result = load("result.json")
        self.assertEqual(result["outcome"], "SUCCESS")
        self.assertEqual(
            [(row["cell"], row["actual"]) for row in result["cells"]],
            [
                ("control-baseline", "ACCEPT"),
                ("control-mutant", "ACCEPT"),
                ("candidate-baseline", "DIRECT_ASSERTION_REFUSAL"),
                ("candidate-mutant", "WORKER_PANIC_JOIN_REFUSAL"),
            ],
        )

    def test_all_six_processes_are_observed_and_clean(self):
        result = load("result.json")
        receipts = [row["receipt"] for row in result["builds"].values()]
        receipts.extend(row["receipt"] for row in result["cells"])
        self.assertEqual(len(receipts), 6)
        for binding in receipts:
            path = ROOT / binding["path"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), binding["sha256"])
            receipt = json.loads(path.read_text(encoding="utf-8"))
            self.assertIsNone(receipt["memory_monitor_error"])
            self.assertGreater(receipt["memory_monitor_samples"], 0)
            self.assertGreater(receipt["maximum_observed_rss_bytes"], 0)
            self.assertFalse(receipt["timed_out"])
            self.assertFalse(receipt["memory_exceeded"])
            self.assertTrue(receipt["cleanup_complete"])

    def test_claim_is_diagnostic_only_and_prelaunch_failure_is_preserved(self):
        result = load("result.json")
        self.assertIn("not an acceptance or soundness difference", result["claim_limit"])
        failure = load("prelaunch-rss-denied/failure.json")
        self.assertEqual(failure["classification"], "ENVIRONMENT_PERMISSION_FAILURE")
        self.assertFalse(failure["process_launched"])
        self.assertFalse(failure["scientific_attempt_consumed"])


if __name__ == "__main__":
    unittest.main()
