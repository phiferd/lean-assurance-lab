"""Portable replay regression for checked-import confirmation evidence."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from lib import checked_import_confirmation_replay


ROOT = Path(__file__).resolve().parents[1]


class CheckedImportConfirmationReplayTests(unittest.TestCase):
    def test_replay_without_original_checkout_or_host_tools(self):
        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory) / "foreign-checkout"
            source = ROOT / checked_import_confirmation_replay.BASE
            destination = checkout / checked_import_confirmation_replay.BASE
            destination.parent.mkdir(parents=True)
            shutil.copytree(source, destination)
            with patch.object(subprocess, "Popen", side_effect=AssertionError("host process launch")), \
                 patch.object(subprocess, "run", side_effect=AssertionError("host process launch")):
                result = checked_import_confirmation_replay.replay(checkout)
            self.assertEqual(result, {
                "status": "PASS", "process_receipts": 91,
                "scientific_cells": 40, "reproduced_cell_identities": 20,
                "host_launches": 0,
            })
            raw = destination / "initial/attempts/cell-01-expression-v-control-lean/stdout.log"
            raw.write_bytes(raw.read_bytes() + b"tamper")
            with self.assertRaises(checked_import_confirmation_replay.ReplayError):
                checked_import_confirmation_replay.replay(checkout)


if __name__ == "__main__":
    unittest.main()
