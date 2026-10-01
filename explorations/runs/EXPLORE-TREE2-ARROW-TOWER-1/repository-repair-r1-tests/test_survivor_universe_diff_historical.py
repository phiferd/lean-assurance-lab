import unittest
from pathlib import Path

from lib.research_queue_v3 import load_queue

from lib.survivor_universe_diff_historical import validate


ROOT = Path(__file__).resolve().parents[1]


class UniverseDiffHistoricalTests(unittest.TestCase):
    def test_predecessor_bytes_survive_live_successor_transition(self):
        result = validate(ROOT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["completed_item"], "SURVIVOR-UNIVERSE-DIFF-1")
        current = load_queue(ROOT, require_ready=True)
        selected = next(item for item in current["items"]
                        if item["id"] == current["selected_item"])
        self.assertEqual(result["current_successor"], current["selected_item"])
        self.assertEqual(result["current_successor_status"], selected["status"])
        self.assertTrue(result["canonical_classification_changed"])


if __name__ == "__main__":
    unittest.main()
