import unittest
from pathlib import Path

from lib.research_queue_v4 import load_queue

from lib.survivor_cache_historical import validate


ROOT = Path(__file__).resolve().parents[1]


class SurvivorCacheHistoricalTests(unittest.TestCase):
    def test_completed_result_survives_current_queue_transition(self):
        result = validate(ROOT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["historical_successor"], "SURVIVOR-CACHE-EXPORT-1")
        current = load_queue(ROOT, require_ready=True)
        selected = next(item for item in current["items"]
                        if item["id"] == current["selected_item"])
        self.assertEqual(result["current_successor"], current["selected_item"])
        self.assertEqual(result["current_successor_status"], selected["status"])


if __name__ == "__main__":
    unittest.main()
