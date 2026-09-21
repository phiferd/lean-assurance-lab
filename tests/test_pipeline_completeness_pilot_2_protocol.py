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

    def test_lineage_cost_and_new_limits_are_not_reset(self):
        limits = self.protocol["limits"]
        self.assertEqual(limits["new_producer_builds"], 1)
        self.assertEqual(limits["lineage_producer_builds_including_pilot_1"], 2)
        self.assertEqual(self.protocol["historical_attempt"]["producer_reservations_consumed"], 1)
        self.assertEqual(limits["maximum_checker_launches"], 12)

    def test_preflight_precedes_new_producer(self):
        gate = self.protocol["entry_gate"]
        self.assertIn("no compilation", gate["preflight_before_producer"].lower())
        self.assertTrue(any("preflight receipt" in row for row in gate["commit_before_producer"]))


if __name__ == "__main__":
    unittest.main()
