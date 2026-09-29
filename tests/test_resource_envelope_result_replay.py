"""Read-only exact result and foreign-checkout tamper checks."""

from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from lib import resource_envelope_result_replay as result_replay
from lib.resource_envelope_result_replay import replay_result
from lib.resource_envelope_replay import REL, ReplayError


ROOT = Path(__file__).resolve().parents[1]


class ResourceEnvelopeResultReplayTests(unittest.TestCase):
    def test_committed_matrix_and_foreign_checkout_without_host_tools(self):
        self.assertTrue((ROOT / REL / "final-closure-2026-09-29-r2"
                         / "supervisor-receipts/normal.with.dots.receipt.json").is_file())
        self.assertEqual(replay_result(ROOT), {
            "status": "PASS", "science_cells": 24, "baselines": 12,
            "accepted": 36, "official_sampled_runs": 18,
            "nanoda_sampled_runs": 0, "process_receipts": 73,
            "host_launches": 0})
        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory) / "foreign-checkout"
            copied = checkout / REL
            copied.parent.mkdir(parents=True)
            shutil.copytree(ROOT / REL, copied)
            for relative in (
                "lib/resource_envelope_supervisor.py",
                "lib/resource_envelope_observe.py",
                "lib/resource_envelope_control.py",
                "lib/resource_envelope_construct.py",
                "tests/test_resource_envelope_control.py",
                "results/research/valid-dependent-term-pilot-1/prepare-run-0003/"
                "staged/exports/vdtp1-pi-01.ndjson",
                "results/research/valid-dependent-term-pilot-1/prepare-run-0003/"
                "staged/cases/vdtp1-pi-01.json",
                "results/research/valid-dependent-term-pilot-1/prepare-run-0003/"
                "staged/audits/vdtp1-pi-01.json",
            ):
                target = checkout / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, target)
            original_read = Path.read_bytes

            def reject_original(path):
                if Path(path).is_relative_to(ROOT):
                    raise AssertionError("portable replay opened original checkout")
                return original_read(path)

            with patch.object(Path, "read_bytes", reject_original), \
                 patch.object(subprocess, "Popen", side_effect=AssertionError("host launch")), \
                 patch.object(subprocess, "run", side_effect=AssertionError("host launch")):
                self.assertEqual(replay_result(checkout)["accepted"], 36)

            # A valid duplicate receipt inside the scientific attempt remains
            # in discovery scope, even while closure fixtures coexist nearby.
            extra = copied / "science-run-0001/processes/unexpected.receipt.json"
            shutil.copy2(copied / "science-run-0001/processes/official-before-01.receipt.json",
                         extra)
            with self.assertRaisesRegex(ReplayError,
                                        "complete preserved process inventory differs"):
                replay_result(checkout)
            extra.unlink()

            ledger = copied / "science-run-0001/ledger.ndjson"
            original_ledger = ledger.read_bytes()
            ledger.write_bytes(original_ledger + b"\n")
            with self.assertRaisesRegex(ReplayError, "bound bytes differ"):
                replay_result(checkout)
            ledger.write_bytes(original_ledger)

            output = copied / "science-run-0001/processes/nanoda-rep1-let-512.stdout"
            original_output = output.read_bytes()
            output.write_bytes(original_output + b"extra")
            with self.assertRaisesRegex(ReplayError, "bound bytes differ"):
                replay_result(checkout)
            output.write_bytes(original_output)

            # A matching raw/receipt rewrite is still rejected by the frozen
            # smoke result, even if review checks are intentionally bypassed.
            smoke_output = copied / "smoke-run-0001/processes/nanoda.stdout"
            smoke_receipt = copied / "smoke-run-0001/processes/nanoda.receipt.json"
            old_smoke_output = smoke_output.read_bytes()
            old_smoke_receipt = smoke_receipt.read_bytes()
            changed = b"X" * len(old_smoke_output)
            smoke_output.write_bytes(changed)
            receipt = json.loads(old_smoke_receipt)
            receipt["stdout_sha256"] = hashlib.sha256(changed).hexdigest()
            smoke_receipt.write_text(json.dumps(receipt, sort_keys=True,
                                                separators=(",", ":")) + "\n")
            with patch.object(result_replay, "_replay_reviews", return_value=None):
                with self.assertRaisesRegex(ReplayError, "bound bytes differ"):
                    replay_result(checkout)
            smoke_output.write_bytes(old_smoke_output)
            smoke_receipt.write_bytes(old_smoke_receipt)

            construction_output = copied / (
                "construction-run-0003/processes/rep1-pi-016-export.stdout")
            construction_receipt = copied / (
                "construction-run-0003/processes/rep1-pi-016-export.receipt.json")
            old_construction_output = construction_output.read_bytes()
            old_construction_receipt = construction_receipt.read_bytes()
            changed = b"X" * len(old_construction_output)
            construction_output.write_bytes(changed)
            receipt = json.loads(old_construction_receipt)
            receipt["stdout_sha256"] = hashlib.sha256(changed).hexdigest()
            construction_receipt.write_text(json.dumps(receipt, sort_keys=True,
                                                       separators=(",", ":")) + "\n")
            with patch.object(result_replay, "_replay_reviews", return_value=None):
                with self.assertRaisesRegex(ReplayError, "bound bytes differ"):
                    replay_result(checkout)
            construction_output.write_bytes(old_construction_output)
            construction_receipt.write_bytes(old_construction_receipt)

            missing = copied / "science-run-0001/processes/official-before-01.receipt.json"
            missing.rename(missing.with_suffix(".held"))
            with self.assertRaisesRegex(ReplayError, "missing bound file"):
                replay_result(checkout)


if __name__ == "__main__":
    unittest.main()
