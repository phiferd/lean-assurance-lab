"""Successor custody replay for lean-action; older portability module stays frozen."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

class LeanActionEvidenceReplayPortabilityTests(unittest.TestCase):
    def test_lean_action_controls_replay_without_original_checkout_or_host_tools(self):
        relative = Path("results/research/lean-action-regression-preparation-1")
        expected = {
            "bundled-install": 0, "bundled-action": 0, "bundled-oracle": 0,
            "bundled-missing-marker-oracle": 1,
            "neither-install": 0, "neither-action": 37, "neither-oracle": 1,
            "fallback-success-install": 0, "fallback-success-action": 0,
            "fallback-success-oracle": 1, "exporter-missing-install": 0,
            "exporter-missing-action": 0, "exporter-missing-oracle": 1,
            "checker-missing-install": 0, "checker-missing-action": 37,
            "checker-missing-oracle": 1,
            "original-absent": 0, "original-conventional": 2,
            "original-destination": 0, "original-both": 2,
            "original-healthy-destination": 0, "fixed-absent": 0,
            "fixed-conventional": 2, "fixed-destination": 2,
            "fixed-both": 2, "fixed-healthy-destination": 0,
        }

        def replay(checkout):
            manifest_raw = (checkout / relative / "input-manifest.json").read_bytes()
            manifest = json.loads(manifest_raw)
            for path, digest in manifest["sha256"].items():
                self.assertEqual(hashlib.sha256((checkout / path).read_bytes()).hexdigest(), digest)
            recorded_root = Path("/Users/danphifer/Documents/Codex/2026-09-30/task-3/lab")
            attempt = checkout / relative / "attempts/0001"
            rows = json.loads((attempt / "result.json").read_bytes())
            self.assertEqual(len(rows), 26)
            self.assertEqual({row["label"]: row["expected_exit"] for row in rows}, expected)
            for row in rows:
                receipt = json.loads((attempt / row["label"] / "receipt.json").read_bytes())
                command = json.loads((attempt / row["label"] / "command.json").read_bytes())
                self.assertEqual(command["manifest_sha256"], hashlib.sha256(manifest_raw).hexdigest())
                self.assertEqual(command["argv"], receipt["argv"])
                self.assertEqual(command["cwd"], receipt["cwd"])
                self.assertEqual(command["argv"][0], "/bin/bash")
                label = row["label"]
                kind = label.rsplit("-", 1)[-1]
                cell = label.removesuffix("-" + kind) if kind in ("install", "action", "oracle") else label
                if label == "bundled-missing-marker-oracle":
                    cell = "bundled"
                cwd = recorded_root / relative / "attempts/0001" / (cell + "-fixture")
                self.assertEqual(command["cwd"], str(cwd))
                if kind == "action":
                    script = recorded_root / "explorations/runs/EXPLORE-LEAN-ACTION-1/source/pr192-scripts_run_nanoda.sh"
                else:
                    script = cwd / ({"install": "setup.sh", "oracle": "check.sh"}.get(kind, "projected.sh"))
                self.assertEqual(command["argv"], ["/bin/bash", str(script)])
                self.assertTrue((checkout / script.relative_to(recorded_root)).is_file())
                self.assertEqual(receipt["exit_code"], expected[row["label"]])
                self.assertEqual(row["actual_exit"], receipt["exit_code"])
                self.assertTrue(row["cleanup"] and receipt["cleanup_complete"])
                self.assertTrue(receipt["reap_complete"])
                for fault in ("accounting_error", "monitor_errors", "pipe_errors",
                              "cleanup_errors", "stop_reason", "trace_gap_fault"):
                    self.assertFalse(receipt[fault], (row["label"], fault))
                for stream in ("stdout", "stderr"):
                    data = (attempt / row["label"] / stream).read_bytes()
                    self.assertEqual(len(data), receipt[stream + "_bytes"])
                    self.assertEqual(hashlib.sha256(data).hexdigest(),
                                     receipt[stream + "_sha256"])

        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory) / "foreign-checkout"
            destination = checkout / relative
            destination.parent.mkdir(parents=True)
            shutil.copytree(ROOT / relative, destination)
            manifest = json.loads((ROOT / relative / "input-manifest.json").read_bytes())
            for path in manifest["sha256"]:
                target = checkout / path
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    shutil.copy2(ROOT / path, target)
            original_read = Path.read_bytes

            def reject_original(path):
                if Path(path).is_relative_to(ROOT):
                    raise AssertionError("replay opened original evidence checkout")
                return original_read(path)

            with patch.object(Path, "read_bytes", reject_original), \
                 patch.object(subprocess, "Popen", side_effect=AssertionError("host process launch")), \
                 patch.object(subprocess, "run", side_effect=AssertionError("host process launch")):
                replay(checkout)
                command_path = destination / "attempts/0001/bundled-action/command.json"
                original_command = command_path.read_bytes()
                command = json.loads(original_command)
                command["argv"][0] = "/forged/observer"
                command_path.write_text(json.dumps(command))
                with self.assertRaises(AssertionError):
                    replay(checkout)
                command_path.write_bytes(original_command)
                raw = destination / "attempts/0001/bundled-action/stdout"
                raw.write_bytes(raw.read_bytes() + b"tamper")
                with self.assertRaises(AssertionError):
                    replay(checkout)

