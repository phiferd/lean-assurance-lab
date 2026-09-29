"""Prospective terminal gate around the historically bound closure controller."""

from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

from lib import resource_envelope_final_closure as closure


class ResourceEnvelopeFinalClosureTests(unittest.TestCase):
    def test_full_inner_gate_and_fixture_receipts_are_both_required(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "results/workflow-refresh/resource-final"

            def old_gate(_root, _scope, controls_dir):
                controls_dir.mkdir(parents=True)
                for name in ("result.json", "input-inventory.json", "full-suite.log",
                             "validation.json"):
                    (controls_dir / name).write_bytes(name.encode())
                return 0

            def final_check(_root, command, log):
                self.assertEqual(command, ["scripts/artifact-status", "--require-current"])
                log.write_bytes(b"current\n")
                return 0

            with patch.object(closure.controls, "finish", side_effect=old_gate), \
                 patch.object(closure, "validate_receipts", return_value={"status": "PASS", "cases": 4}), \
                 patch.object(closure.controls, "_run_logged", side_effect=final_check):
                self.assertEqual(closure.finish(root, "scope.json", output), 0)
            result = json.loads((output / "result.json").read_text())
            self.assertEqual(result["status"], "COMPLETE")
            self.assertEqual(result["controls_returncode"], 0)
            self.assertEqual(result["final_freshness_returncode"], 0)
            self.assertEqual(result["supervisor_receipts_validation"]["path"],
                             "results/workflow-refresh/resource-final/supervisor-receipts-validation.json")
            self.assertEqual(len(result["completed_steps"]), 3)

    def test_inner_success_cannot_hide_missing_fixture_custody(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "results/workflow-refresh/resource-final"

            def old_gate(_root, _scope, controls_dir):
                controls_dir.mkdir(parents=True)
                for name in ("result.json", "input-inventory.json", "full-suite.log",
                             "validation.json"):
                    (controls_dir / name).write_bytes(name.encode())
                return 0

            with patch.object(closure.controls, "finish", side_effect=old_gate), \
                 patch.object(closure, "validate_receipts", side_effect=ValueError("missing fixture")), \
                 patch.object(closure.controls, "_run_logged") as final_check:
                self.assertEqual(closure.finish(root, "scope.json", output), 1)
                final_check.assert_not_called()
            result = json.loads((output / "result.json").read_text())
            self.assertEqual(result["status"], "FAILED")
            self.assertEqual(result["error"], "missing fixture")
            self.assertFalse((output / "supervisor-receipts-validation.json").exists())

    def test_inner_failure_stops_before_receipt_and_freshness_gates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "results/workflow-refresh/resource-final"

            def old_gate(_root, _scope, controls_dir):
                controls_dir.mkdir(parents=True)
                (controls_dir / "result.json").write_bytes(b"failed\n")
                return 1

            with patch.object(closure.controls, "finish", side_effect=old_gate), \
                 patch.object(closure, "validate_receipts") as receipt_gate, \
                 patch.object(closure.controls, "_run_logged") as final_check:
                self.assertEqual(closure.finish(root, "scope.json", output), 1)
                receipt_gate.assert_not_called()
                final_check.assert_not_called()
            result = json.loads((output / "result.json").read_text())
            self.assertEqual(result["status"], "FAILED")
            self.assertEqual(result["controls_returncode"], 1)

    def test_research_output_is_rejected_before_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "results/research/resource-envelope-pilot-1/final-closure-r3"
            with self.assertRaisesRegex(ValueError, "outside results/research"):
                closure.finish(root, "scope.json", output)
            self.assertFalse(output.exists())
