from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "results/research/pipeline-completeness-pilot-2/protocol.json"


class PipelineCompletenessPilot2ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))

    def test_inherited_scientific_inputs_are_exact(self):
        self.assertEqual(self.protocol["continuation_of"],
                         "PIPELINE-COMPLETENESS-PILOT-1")
        for row in self.protocol["inherited_scientific_inputs"]:
            self.assertEqual(row["sha256"],
                             hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest())

    def test_attempt_counts_are_observational_not_terminal(self):
        policy = self.protocol["execution_policy"]
        self.assertEqual(policy["attempt_caps"], "NONE")
        self.assertEqual(policy["accounting"], "OBSERVABILITY_ONLY")
        self.assertEqual(policy["engineering_failure"], "REPAIR_AND_RETRY_WITHIN_ITEM")
        self.assertFalse(self.protocol["process_safety"]["safety_event_is_terminal"])
        self.assertNotIn("limits", self.protocol)

    def test_scientific_matrix_remains_fixed(self):
        matrix = self.protocol["matrix"]
        self.assertEqual(matrix["scientific_cells"], 8)
        self.assertFalse(matrix["engineering_retries_change_scientific_matrix"])

    def test_preflight_precedes_new_producer(self):
        gate = self.protocol["entry_gate"]
        self.assertIn("no compilation", gate["preflight_before_producer"].lower())
        self.assertTrue(any("preflight evidence" in row for row in gate["commit_before_producer"]))


if __name__ == "__main__":
    unittest.main()
