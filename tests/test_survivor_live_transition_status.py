"""Current selected status is independent of frozen historical assertions."""
import unittest
from pathlib import Path

from lib.research_queue_v4 import load_queue
from lib import portfolio_historical_snapshot_v3 as portfolio
from lib import survivor_cache_historical, survivor_fvar_reachability_historical
from lib import survivor_thread_config_reachability_historical
from lib import survivor_universe_diff_historical, survivor_universe_equivalence_historical

ROOT = Path(__file__).resolve().parents[1]


class SurvivorLiveTransitionStatusTests(unittest.TestCase):
    def test_all_historical_results_preserve_exact_live_selection(self):
        queue = load_queue(ROOT, require_ready=False)
        selected = next(i for i in queue["items"] if i["id"] == queue["selected_item"])
        transition = portfolio.validate_live_transition(ROOT)
        self.assertEqual(transition["status"], "PASS")
        if queue["handoff"]["status"] == "PAUSED":
            self.assertIn(selected["status"], {"WAITING", "DEFERRED"})
        else:
            self.assertIn(selected["status"], {"READY", "ACTIVE"})
        preserved = portfolio._extra_paths(ROOT)
        for module in (survivor_cache_historical, survivor_fvar_reachability_historical,
                       survivor_thread_config_reachability_historical,
                       survivor_universe_diff_historical, survivor_universe_equivalence_historical):
            with self.subTest(module=module.__name__):
                path = Path(module.__file__).resolve().relative_to(ROOT).as_posix()
                self.assertIn(path, preserved)
