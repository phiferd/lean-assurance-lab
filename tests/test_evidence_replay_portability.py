"""Fresh-checkout regressions for evidence created on a different host path."""
import os
import copy
import hashlib
from pathlib import Path
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


ROOT = Path(__file__).resolve().parents[1]


class EvidenceReplayPortabilityTests(unittest.TestCase):
    def alternate_checkout(self, directory):
        checkout = Path(directory) / "fresh-linux-checkout"
        os.symlink(ROOT, checkout, target_is_directory=True)
        return checkout

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


if __name__ == "__main__":
    unittest.main()
