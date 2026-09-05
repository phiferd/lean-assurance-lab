import copy
import importlib.machinery
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("corpus_integration_closure", str(ROOT / "scripts/build-corpus-integration-closure"))
spec = importlib.util.spec_from_loader(loader.name, loader)
closure = importlib.util.module_from_spec(spec)
loader.exec_module(closure)


class CorpusIntegrationClosureTests(unittest.TestCase):
    def clone_safe_build(self):
        real_verify = closure.verify
        with patch.object(closure, "verify", side_effect=lambda row: None if row["path"].startswith("external/") else real_verify(row)):
            return closure.build()

    def test_renders_bounded_human_gated_successor_without_processes(self):
        with patch("subprocess.run", side_effect=AssertionError("closure must not launch a process")):
            outputs = self.clone_safe_build()
        packet = closure.json.loads(outputs[closure.PACKET])
        self.assertEqual(packet["status"], "CORPUS_INTEGRATION_CLOSED_WITH_HUMAN_GATES")
        self.assertEqual(len(packet["witness_admissions"]), 2)
        self.assertEqual([row["disposition"] for row in packet["findings"]], ["ACTION_TAKEN", "NO_EXTERNAL_ACTION", "ACTION_RECOMMENDED", "ACTION_RECOMMENDED"])
        self.assertEqual([row["semantic_status"] for row in packet["triage"]], ["UNRESOLVED", "UNRESOLVED"])
        self.assertEqual(len(packet["next_steps"]), 4)
        self.assertEqual(packet["arena_tutorial_comparison"]["exact_companion_matches"], 0)
        actions = closure.json.loads(outputs[closure.ACTIONS])
        self.assertEqual(actions["schema_version"], 1)
        self.assertEqual(actions["findings"][2]["recommendations"][1]["execution_status"], "NOT_STARTED")
        self.assertNotIn("closure_packet", actions)
        self.assertEqual(sum(item["id"] == "positivity-no-implementation-issue" for item in actions["findings"][3]["recommendations"]), 1)
        self.assertIn("proposed `reject`", outputs[closure.DRAFT])

    def test_rejects_checker_or_download_bound_changes(self):
        actual = closure.read
        def changed(path):
            value = actual(path)
            if path.endswith("corpus-integration-2026-09-05/result.json"):
                value = copy.deepcopy(value); value["checker_launches"] = 1
            return value
        with patch.object(closure, "read", side_effect=changed), self.assertRaisesRegex(ValueError, "bounds changed"):
            self.clone_safe_build()

    def test_rejects_admission_predicate_tampering(self):
        actual = closure.read
        def changed(path):
            value = actual(path)
            if path.endswith("nanoda-gen-f19ffc8a2e9b-witness/confirmation.json"):
                value = copy.deepcopy(value); value["mechanical_predicate"] = "forged"
            return value
        with patch.object(closure, "read", side_effect=changed), self.assertRaisesRegex(ValueError, "predicate changed"):
            self.clone_safe_build()


if __name__ == "__main__":
    unittest.main()
