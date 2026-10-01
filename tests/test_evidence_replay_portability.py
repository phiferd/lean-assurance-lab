"""Fresh-checkout regressions for evidence created on a different host path."""
import os
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from lib import lazy_reduction_pilot
from lib import lazy_reduction_validation_r2 as lazy_reduction_validation
from lib import kiota_receipt_replay
from lib import stateful_validation_closure_portable as stateful_validation_closure
from lib import stateful_validation_pilot
from lib import trust_assumption_pilot_r2
from lib import trust_assumption_pilot_r3
from lib.portable_evidence_replay import portable_validation
import test_trust_assumption_pilot_r2 as legacy_trust_tests
from lib import real_proof_slices_replay
from lib import evidence_replay_portability
from lib import binder_model_replay
from lib import resource_envelope_replay


ROOT = Path(__file__).resolve().parents[1]


class EvidenceReplayPortabilityTests(unittest.TestCase):
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

    def alternate_checkout(self, directory):
        checkout = Path(directory) / "fresh-linux-checkout"
        os.symlink(ROOT, checkout, target_is_directory=True)
        return checkout

    def test_resource_envelope_replay_without_original_checkout_or_host_tools(self):
        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory) / "foreign-checkout"
            destination = checkout / resource_envelope_replay.REL
            destination.parent.mkdir(parents=True)
            shutil.copytree(ROOT / resource_envelope_replay.REL, destination)
            original_read = Path.read_bytes

            def reject_original(path):
                if Path(path).is_relative_to(ROOT):
                    raise AssertionError("replay opened original evidence checkout")
                return original_read(path)

            with patch.object(Path, "read_bytes", reject_original), \
                 patch.object(subprocess, "Popen", side_effect=AssertionError("host process launch")), \
                 patch.object(subprocess, "run", side_effect=AssertionError("host process launch")):
                result = resource_envelope_replay.replay(checkout)
            self.assertEqual(result["status"], "PASS")
            self.assertGreaterEqual(result["process_receipts"], 1)
            self.assertEqual(result["raw_streams"], 2 * result["process_receipts"])
            self.assertEqual(result["host_launches"], 0)
            failed = destination / "preflight-run-0002"
            failed.mkdir()
            (failed / "stdout.raw").write_bytes(b"partial")
            (failed / "stderr.raw").write_bytes(b"")
            fault = {"cwd": "/historical/checker-host", "argv": ["/bin/sh"],
                     "exit_code": None, "accounting_error": "synthetic wait4 fault",
                     "reap_complete": False,
                     "stdout_bytes": 7, "stdout_sha256": hashlib.sha256(b"partial").hexdigest(),
                     "stderr_bytes": 0, "stderr_sha256": hashlib.sha256(b"").hexdigest()}
            (failed / "process-receipt.json").write_text(json.dumps(fault) + "\n")
            with patch.object(subprocess, "Popen", side_effect=AssertionError("host process launch")), \
                 patch.object(subprocess, "run", side_effect=AssertionError("host process launch")):
                repaired = resource_envelope_replay.replay(checkout)
            self.assertEqual(repaired["process_receipts"], result["process_receipts"] + 1)
            self.assertEqual(repaired["preserved_accounting_faults"], 1)
            malformed = dict(fault)
            del malformed["accounting_error"]
            del malformed["reap_complete"]
            (failed / "process-receipt.json").write_text(json.dumps(malformed) + "\n")
            with self.assertRaises(resource_envelope_replay.ReplayError):
                resource_envelope_replay.replay(checkout)
            (failed / "process-receipt.json").write_text(json.dumps(fault) + "\n")
            raw = destination / "preflight-run-0001/stdout.raw"
            raw.write_bytes(raw.read_bytes() + b"tamper")
            with self.assertRaises(resource_envelope_replay.ReplayError):
                resource_envelope_replay.replay(checkout)

    def test_binder_model_replay_without_original_checkout_or_host_tools(self):
        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory) / "foreign-checkout"
            source = ROOT / binder_model_replay.BASE
            destination = checkout / binder_model_replay.BASE
            destination.parent.mkdir(parents=True)
            shutil.copytree(source, destination)
            original_read = Path.read_bytes

            def reject_original(path):
                if Path(path).is_relative_to(ROOT):
                    raise AssertionError("replay opened the evidence-production checkout")
                return original_read(path)

            with patch.object(Path, "read_bytes", reject_original):
                result = binder_model_replay.replay(checkout)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual((result["processes"], result["vector_observations"],
                              result["stage_outputs"], result["host_launches"]),
                             (40, 20000, 30000, 0))

            raw = destination / "runs/attempt-0001/kiota-2d2a9fa/batch-00/process.stdout"
            raw.write_bytes(raw.read_bytes() + b"\n")
            with self.assertRaises(binder_model_replay.ReplayError):
                binder_model_replay.replay(checkout)

    def test_lazy_replay_does_not_require_original_checkout_path(self):
        with tempfile.TemporaryDirectory() as directory:
            checkout = self.alternate_checkout(directory)
            def bind(path):
                candidate = Path(path)
                candidate = candidate if candidate.is_absolute() else checkout / candidate
                data = candidate.read_bytes()
                try:
                    name = str(candidate.relative_to(checkout))
                except ValueError:
                    name = str(candidate)
                return {"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            with patch.object(lazy_reduction_pilot, "ROOT", checkout), \
                 patch.object(lazy_reduction_pilot, "bind", bind):
                self.assertEqual(lazy_reduction_validation.validate()["status"], "PASS")

    def test_lazy_replay_rejects_self_authenticated_cwd_and_argv(self):
        original_load = lazy_reduction_pilot.load
        science_result = lazy_reduction_pilot.BASE / "science-0001/result.json"
        first_cell = lazy_reduction_pilot.BASE / "science-0001/cell-01.json"

        def load(path):
            value = copy.deepcopy(original_load(path))
            candidate = Path(path)
            if candidate in (science_result, first_cell):
                row = value["cells"][0] if candidate == science_result else value
                row["receipt"]["cwd"] = "/tmp/forged-research-root"
                row["receipt"]["argv"][0] = "/tmp/forged-research-root/lazylean-r1"
                row["receipt"]["argv"][-1] = "/tmp/forged-research-root/forged.olean"
            return value

        with patch.object(lazy_reduction_pilot, "load", side_effect=load), \
             self.assertRaisesRegex(ValueError, "bound build root"):
            lazy_reduction_validation.validate()

    def test_stateful_replay_does_not_require_original_host_tools_or_checkout(self):
        source = stateful_validation_pilot.read(stateful_validation_pilot.SOURCE)
        absent_host_tools = {Path(row["path"]) for row in source["host_tools"]}
        original_read_bytes = Path.read_bytes

        def read_bytes(path):
            if Path(path) in absent_host_tools:
                raise FileNotFoundError(path)
            return original_read_bytes(path)

        with tempfile.TemporaryDirectory() as directory:
            checkout = self.alternate_checkout(directory)
            with patch.object(stateful_validation_pilot, "ROOT", checkout), \
                 patch.object(Path, "read_bytes", read_bytes):
                result = stateful_validation_closure.validate_closure()
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["histories"], 12)

    def test_trust_replay_preserves_original_root_from_alternate_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            checkout = self.alternate_checkout(directory)
            with patch.object(trust_assumption_pilot_r2, "ROOT", checkout):
                result = trust_assumption_pilot_r2.validate_result(checkout)
                rebuilt = trust_assumption_pilot_r3.rebuild_result(
                    result["observations"], checkout,
                )
            self.assertEqual(result["status"], "SUCCESS")
            self.assertEqual(rebuilt, result)

    def test_full_trust_synthetic_custody_suite_runs_from_alternate_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            checkout = self.alternate_checkout(directory)
            case = legacy_trust_tests.ResultTests("test_synthetic_receipt_tampering")
            result = unittest.TestResult()
            with patch.object(trust_assumption_pilot_r2, "ROOT", checkout), \
                 portable_validation():
                case.run(result)
            self.assertEqual(result.errors, [])
            self.assertEqual(result.failures, [])

    def test_kiota_repair_receipts_replay_without_original_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            checkout = self.alternate_checkout(directory)
            result = kiota_receipt_replay.validate(checkout, "kiota-recursor-type-repair-1")
        self.assertEqual(result["attempts"], 31)
        self.assertEqual(result["manifest_bound_attempts"], 9)
        self.assertEqual(result["historical_manifest_mismatches"], 22)
        self.assertEqual(result["host_launches"], 0)

    def test_kiota_refinement_receipts_replay_without_original_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            checkout = self.alternate_checkout(directory)
            result = kiota_receipt_replay.validate(checkout, "kiota-recursor-pr-refinement-1")
        self.assertEqual(result["attempts"], 9)
        self.assertEqual(result["manifest_bound_attempts"], 9)
        self.assertEqual(result["historical_manifest_mismatches"], 0)
        self.assertEqual(result["host_launches"], 0)

    def test_real_proof_slices_replay_without_original_checkout_or_host_tools(self):
        with tempfile.TemporaryDirectory() as directory:
            checkout = self.alternate_checkout(directory)
            result = real_proof_slices_replay.replay(checkout)
            groups, receipts = evidence_replay_portability.discover(checkout)
            family = set(groups["real-proof-slices-pilot-1"])
            family_receipts = [(path, receipt) for path, receipt in receipts if path in family]
            streams, roots = evidence_replay_portability.validate_raw_custody(
                checkout, family_receipts)
        self.assertEqual(result, {"status": "PASS", "cases": 12, "ready": 9,
                                  "oversize": 3, "processes": 18, "accepted": 18,
                                  "host_launches": 0})
        self.assertEqual(len(family_receipts), 23)
        self.assertEqual(streams, 46)
        self.assertNotIn(str(checkout), roots)

    def test_real_proof_slices_replay_rejects_command_and_raw_tampering(self):
        original_json = real_proof_slices_replay._json
        original_read = real_proof_slices_replay._read
        result_path = real_proof_slices_replay.BASE / "execution/attempt-0001/result.json"
        def changed_command(root, relative):
            document = original_json(root, relative)
            if Path(relative) == result_path:
                document = copy.deepcopy(document)
                document["cells"][0]["process_receipt"]["argv"][0] = "/forged/kernel"
            return document
        with patch.object(real_proof_slices_replay, "_json", side_effect=changed_command):
            with self.assertRaisesRegex(real_proof_slices_replay.ReplayError,
                                        "recorded command/cwd differs"):
                real_proof_slices_replay.replay(ROOT)
        raw_path = Path("results/research/real-proof-slices-pilot-1/execution/attempt-0001/raw/001-init-01-official-lean-4.33.0.stdout")
        def changed_raw(root, relative):
            return b"forged\n" if Path(relative) == raw_path else original_read(root, relative)
        with patch.object(real_proof_slices_replay, "_read", side_effect=changed_raw):
            with self.assertRaisesRegex(real_proof_slices_replay.ReplayError,
                                        "bound bytes differ"):
                real_proof_slices_replay.replay(ROOT)


if __name__ == "__main__":
    unittest.main()
