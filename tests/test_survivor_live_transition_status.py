"""Current selected status is independent of frozen historical assertions."""
import unittest
from pathlib import Path

from lib.research_queue_v4 import load_queue
from lib import survivor_cache_historical, survivor_fvar_reachability_historical
from lib import survivor_thread_config_reachability_historical
from lib import survivor_universe_diff_historical, survivor_universe_equivalence_historical

ROOT = Path(__file__).resolve().parents[1]


class SurvivorLiveTransitionStatusTests(unittest.TestCase):
    def test_all_historical_results_preserve_exact_live_selection(self):
        queue = load_queue(ROOT, require_ready=True)
        selected = next(i for i in queue["items"] if i["id"] == queue["selected_item"])
        for module in (survivor_cache_historical, survivor_fvar_reachability_historical,
                       survivor_thread_config_reachability_historical,
                       survivor_universe_diff_historical, survivor_universe_equivalence_historical):
            with self.subTest(module=module.__name__):
                result = module.validate(ROOT)
                self.assertEqual(result["status"], "PASS")
                self.assertEqual(result["current_successor"], queue["selected_item"])
                self.assertEqual(result["current_successor_status"], selected["status"])
