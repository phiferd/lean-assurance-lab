import unittest
from pathlib import Path

from lib.survivor_cache_historical import validate


ROOT = Path(__file__).resolve().parents[1]


class SurvivorCacheHistoricalTests(unittest.TestCase):
    def test_completed_result_survives_current_queue_transition(self):
        result = validate(ROOT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["historical_successor"], "SURVIVOR-CACHE-EXPORT-1")
        self.assertEqual(result["current_successor"], "SURVIVOR-FVAR-REACHABILITY-1")


if __name__ == "__main__":
    unittest.main()
