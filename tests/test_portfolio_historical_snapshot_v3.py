import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lib import portfolio_historical_snapshot_v3 as history

ROOT = Path(__file__).resolve().parents[1]


class HistoricalStatusCustodyTests(unittest.TestCase):
    def test_real_transition_preserves_old_tests_and_extends_replay(self):
        result = history.validate_live_transition(ROOT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(set(result["historical_modules"]), history.MODULES)
        self.assertEqual(len(history.EXTRA_MODULES), 5)
        self.assertGreater(result["extra_preserved_paths"], 5)

    def test_added_historical_test_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bound.py").write_bytes(b"changed")
            with patch.object(history.portable, "validate_live_transition", return_value={}), \
                 patch.object(history, "_extra_paths", return_value={"bound.py"}), \
                 patch.object(history.legacy, "_bytes", return_value=b"original"):
                with self.assertRaisesRegex(ValueError, "frozen portfolio input changed"):
                    history.validate_live_transition(root)

    def test_added_historical_test_missing_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(history.portable, "validate_live_transition", return_value={}), \
                 patch.object(history, "_extra_paths", return_value={"missing.py"}):
                with self.assertRaisesRegex(ValueError, "missing or linked"):
                    history.validate_live_transition(Path(directory))
