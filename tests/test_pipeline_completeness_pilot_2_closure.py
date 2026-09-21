from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results/research/pipeline-completeness-pilot-2"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PipelineCompletenessPilot2ClosureTests(unittest.TestCase):
    def test_exact_matrix_completed_without_infrastructure_failure(self):
        result = load(BASE / "result.json")
        self.assertEqual(result["outcome"], "SUCCESS")
        self.assertEqual(len(result["cells"]), 8)
        self.assertEqual([(row["artifact"], row["adapter"]) for row in result["cells"]], [
            (artifact, adapter) for artifact in ("baseline", "omission", "substitution", "truncation")
            for adapter in ("official", "lean4lean")])
        for row in result["cells"]:
            receipt = load(ROOT / row["receipt"]["path"])
            self.assertEqual(row["receipt"]["sha256"], digest(ROOT / row["receipt"]["path"]))
            self.assertGreater(receipt["memory_monitor_samples"], 0)
            self.assertFalse(receipt["timed_out"])
            self.assertFalse(receipt["memory_exceeded"])
            self.assertTrue(receipt["cleanup_complete"])

    def test_baseline_and_fault_contract(self):
        cells = load(BASE / "result.json")["cells"]
        baseline = [row for row in cells if row["artifact"] == "baseline"]
        self.assertEqual({row["process_outcome"] for row in baseline}, {"ACCEPT"})
        self.assertEqual({row["sentinel"] for row in baseline}, {"PASS"})
        expected = {
            "omission": "FAIL_MISSING_TARGET",
            "substitution": "FAIL_ARTIFACT_OR_DECLARATION_IDENTITY",
            "truncation": "FAIL_PARSE_OR_DEPENDENCY_CLOSURE",
        }
        for artifact, classification in expected.items():
            rows = [row for row in cells if row["artifact"] == artifact]
            self.assertEqual(len(rows), 2)
            self.assertEqual({row["sentinel"] for row in rows}, {classification})

    def test_checker_success_alone_has_four_false_reassurances(self):
        result = load(BASE / "result.json")
        self.assertEqual(result["false_reassurance_cells"], [
            {"artifact": "omission", "adapter": "official"},
            {"artifact": "omission", "adapter": "lean4lean"},
            {"artifact": "substitution", "adapter": "official"},
            {"artifact": "substitution", "adapter": "lean4lean"},
        ])

    def test_closure_bindings_and_nonterminal_accounting(self):
        closure = load(BASE / "closure.json")
        self.assertEqual(closure["outcome"], "SUCCESS")
        self.assertTrue(closure["question_answered"])
        self.assertIn("no count authorized or terminated", closure["engineering_observations"]["interpretation"])
        for row in closure["bindings"].values():
            self.assertEqual(row["sha256"], digest(ROOT / row["path"]))
        protocol = load(BASE / "protocol.json")
        self.assertEqual(protocol["execution_policy"]["attempt_caps"], "NONE")
        self.assertFalse(protocol["process_safety"]["safety_event_is_terminal"])


if __name__ == "__main__":
    unittest.main()
