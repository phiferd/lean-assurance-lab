from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results/research/pipeline-completeness-pilot-1"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PipelineCompletenessClosureTests(unittest.TestCase):
    def test_terminal_attempt_is_preserved_and_charged(self):
        attempt = load(BASE / "producer-run-0001/result.json")
        receipt = load(BASE / "producer-run-0001/process/supervisor.json")
        self.assertEqual(attempt["outcome"], "ENGINEERING_FAILURE")
        self.assertTrue(attempt["reservation_consumed"])
        self.assertEqual(attempt["producer_builds_consumed"],
                         attempt["producer_builds_cap"])
        self.assertEqual(attempt["process_receipt"]["sha256"],
                         digest(BASE / "producer-run-0001/process/supervisor.json"))
        self.assertEqual(receipt["exit_code"], 1)
        self.assertGreater(receipt["memory_monitor_samples"], 0)
        self.assertTrue(receipt["cleanup_complete"])
        for row in attempt["controller_workspace"]:
            self.assertEqual(row["sha256"], digest(ROOT / row["path"]))

    def test_closure_makes_no_scientific_claim(self):
        result = load(BASE / "result.json")
        self.assertEqual(result["outcome"], "BOUNDED_UNRESOLVED")
        self.assertFalse(result["question_answered"])
        self.assertEqual(result["execution"]["checker_attempts"], 0)
        self.assertEqual(result["execution"]["exports_retained"], 0)
        self.assertEqual(result["execution"]["producer_builds_consumed"], 1)

    def test_repair_binds_exact_regression_without_launch_authority(self):
        repair = load(BASE / "tooling-revision-02.json")
        self.assertEqual(repair["source"]["sha256"], digest(ROOT / repair["source"]["path"]))
        self.assertEqual(repair["tests"]["sha256"], digest(ROOT / repair["tests"]["path"]))
        self.assertFalse(repair["scientific_inputs_changed"])
        self.assertTrue(repair["launch_authority"].startswith("NONE:"))


if __name__ == "__main__":
    unittest.main()
