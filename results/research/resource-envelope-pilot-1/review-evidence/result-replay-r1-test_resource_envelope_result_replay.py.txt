"""Read-only exact result and foreign-checkout tamper checks."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from lib.resource_envelope_result_replay import replay_result
from lib.resource_envelope_replay import REL, ReplayError


ROOT = Path(__file__).resolve().parents[1]


class ResourceEnvelopeResultReplayTests(unittest.TestCase):
    def test_committed_matrix_and_foreign_checkout_without_host_tools(self):
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
            original_read = Path.read_bytes

            def reject_original(path):
                if Path(path).is_relative_to(ROOT):
                    raise AssertionError("portable replay opened original checkout")
                return original_read(path)

            with patch.object(Path, "read_bytes", reject_original), \
                 patch.object(subprocess, "Popen", side_effect=AssertionError("host launch")), \
                 patch.object(subprocess, "run", side_effect=AssertionError("host launch")):
                self.assertEqual(replay_result(checkout)["accepted"], 36)

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

            missing = copied / "science-run-0001/processes/official-before-01.receipt.json"
            missing.rename(missing.with_suffix(".held"))
            with self.assertRaisesRegex(ReplayError, "missing bound file"):
                replay_result(checkout)


if __name__ == "__main__":
    unittest.main()
