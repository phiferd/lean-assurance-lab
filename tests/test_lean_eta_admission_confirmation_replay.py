"""Portable replay regression for the PR15373 E1 prelaunch evidence."""

from pathlib import Path
import shutil
import tempfile
import unittest

from lib import lean_eta_admission_confirmation_replay as replay


ROOT = Path(__file__).resolve().parents[1]


class LeanEtaAdmissionConfirmationReplayTests(unittest.TestCase):
    def test_replay_without_original_checkout_or_host_tools(self):
        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory) / "foreign-checkout"
            destination = checkout / replay.REL
            destination.parent.mkdir(parents=True)
            shutil.copytree(ROOT / replay.REL, destination)
            result = replay.replay(checkout)
            self.assertEqual(result, {
                "status": "PASS",
                "receipts": 27,
                "successful_preparation_receipts": 12,
                "fixture_sources": 5,
                "generated_oleans": 4,
                "host_launches": 0,
            })
            raw = destination / "attempts/head-build-3/stdout.log"
            raw.write_bytes(raw.read_bytes() + b"tamper")
            with self.assertRaises(replay.ReplayError):
                replay.replay(checkout)


if __name__ == "__main__":
    unittest.main()
