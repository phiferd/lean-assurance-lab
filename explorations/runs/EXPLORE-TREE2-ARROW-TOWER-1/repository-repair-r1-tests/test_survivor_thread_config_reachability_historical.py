import unittest
from pathlib import Path

from lib.research_queue_v3 import load_queue

from lib.survivor_thread_config_reachability_historical import validate


ROOT = Path(__file__).resolve().parents[1]


class SurvivorThreadConfigReachabilityHistoricalTests(unittest.TestCase):
    def test_entry_bytes_survive_scoped_thread_classification(self):
        result = validate(ROOT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["registry_predecessor_lines"], 609)
        self.assertEqual(result["registry_successor_lines"], 611)
        current = load_queue(ROOT, require_ready=True)
        selected = next(item for item in current["items"]
                        if item["id"] == current["selected_item"])
        self.assertEqual(result["current_successor"], current["selected_item"])
        self.assertEqual(result["current_successor_status"], selected["status"])
        self.assertEqual(result["pending_survivors"], 2)
        self.assertEqual(result["meaningful_survivors"], 5)
        self.assertEqual(result["equivalent_mutants"], 14)


if __name__ == "__main__":
    unittest.main()
