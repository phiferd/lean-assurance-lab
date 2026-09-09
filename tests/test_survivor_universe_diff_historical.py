import unittest
from pathlib import Path

from lib.survivor_universe_diff_historical import validate


ROOT = Path(__file__).resolve().parents[1]


class UniverseDiffHistoricalTests(unittest.TestCase):
    def test_predecessor_bytes_survive_live_successor_transition(self):
        result = validate(ROOT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["completed_item"], "SURVIVOR-UNIVERSE-DIFF-1")
        self.assertEqual(result["current_successor"], "SURVIVOR-THREAD-CONFIG-REACHABILITY-1")
        self.assertTrue(result["canonical_classification_changed"])


if __name__ == "__main__":
    unittest.main()
