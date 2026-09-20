from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results/research/metamorphic-representation-pilot-2/result.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MetamorphicPilotClosureTests(unittest.TestCase):
    def setUp(self):
        self.result = load(RESULT)

    def assert_binding(self, binding: dict) -> Path:
        path = ROOT / binding["path"]
        self.assertTrue(path.is_file(), binding["path"])
        self.assertEqual(digest(path), binding["sha256"], binding["path"])
        return path

    def test_predecessor_remains_exact_unresolved_history(self):
        predecessor_path = self.assert_binding(self.result["predecessor_preserved"]["result"])
        predecessor = load(predecessor_path)
        self.assertEqual(predecessor["outcome"], "BOUNDED_UNRESOLVED")
        self.assertEqual(predecessor["execution"]["variants_generated"], 0)
        self.assertEqual(predecessor["execution"]["checker_attempts"], 0)
        self.assertFalse(self.result["predecessor_preserved"]["reopened_or_reset"])

    def test_generation_bindings_and_eligibility_are_complete(self):
        summary = load(self.assert_binding(self.result["generation"]["summary"]))
        self.assertEqual(summary["item_id"], "METAMORPHIC-REPRESENTATION-PILOT-2")
        self.assertEqual(summary["variant_count"], 4)
        self.assertEqual(sum(row["eligible"] for row in summary["variants"]), 2)
        for row in summary["variants"]:
            for key in ("variant", "transform_report", "audit"):
                self.assert_binding(row[key])
            audit = load(ROOT / row["audit"]["path"])
            self.assertTrue(audit["equivalent"])
            self.assertEqual(audit["eligible"], row["eligible"])

    def test_final_run_is_observed_clean_and_exact(self):
        run = load(self.assert_binding(self.result["execution"]["run_02"]["raw_result"]))
        self.assertEqual(run["status"], "COMPLETE")
        self.assertEqual(run["checker_attempts"], 8)
        self.assertEqual(len(run["cells"]), 8)
        for row in run["cells"]:
            receipt = row["receipt"]
            self.assertEqual(row["outcome"], "ACCEPT")
            self.assertEqual(receipt["exit_code"], 0)
            self.assertFalse(receipt["timed_out"])
            self.assertFalse(receipt["memory_exceeded"])
            self.assertIsNone(receipt["memory_monitor_error"])
            self.assertGreater(receipt["memory_monitor_samples"], 0)
            self.assertGreater(receipt["maximum_observed_rss_bytes"], 0)
            self.assertTrue(receipt["cleanup_complete"])
            for key, digest_key in (("raw_stdout_path", "stdout_sha256"),
                                    ("raw_stderr_path", "stderr_sha256")):
                path = ROOT / receipt[key]
                self.assertTrue(path.is_file(), str(path))
                self.assertEqual(digest(path), receipt[digest_key])

    def test_twelve_cell_matrix_and_four_relations_are_complete(self):
        science = load(self.assert_binding(self.result["scientific_inputs"]["manifest"]))
        frozen = {row["cell"] for row in science["maximum_observation_matrix"]}
        matrix = self.result["matrix"]
        self.assertEqual(len(matrix), 12)
        self.assertEqual({row["cell"] for row in matrix}, frozen)
        executed = [row for row in matrix if row["disposition"] == "EXECUTED"]
        ineligible = [row for row in matrix if row["disposition"] == "INELIGIBLE"]
        self.assertEqual(len(executed), 8)
        self.assertTrue(all(row["outcome"] == "ACCEPT" for row in executed))
        self.assertEqual(len(ineligible), 4)
        self.assertTrue(all(row["cell"].endswith("kind-round-robin-v1") for row in ineligible))
        relations = self.result["within_checker_relations"]
        self.assertEqual(len(relations), 4)
        self.assertTrue(all(row["baseline"] == row["variant"] == "ACCEPT"
                            and row["relation_holds"] for row in relations))

    def test_claim_and_recommendation_stay_scoped(self):
        self.assertEqual(self.result["status"], "COMPLETE")
        self.assertEqual(self.result["outcome"], "SUCCESS")
        self.assertTrue(self.result["question_answered"])
        self.assertIn("No representation sensitivity", self.result["scientific_conclusion"])
        self.assertIn("no global invariance", self.result["scientific_conclusion"])
        recommendation = self.result["recommendation"]
        self.assertEqual(recommendation["action"], "RETAIN_LOCAL_CONFORMANCE_ASSET")
        self.assertEqual(recommendation["external_action"], "NO_ACTION_NOW")
        self.assertEqual(self.result["execution"]["checker_attempts_total"], 16)


if __name__ == "__main__":
    unittest.main()
