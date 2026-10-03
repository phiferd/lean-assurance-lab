from pathlib import Path
import unittest
from unittest import mock

from lib import survivor_cache_historical as historical
from lib import survivor_cache_historical_v2 as portable
from lib import portfolio_historical_snapshot_v3 as portfolio


ROOT = Path(__file__).resolve().parents[1]


class SurvivorCacheHistoricalPortabilityTests(unittest.TestCase):
    def test_evidence_separates_storage_from_recorded_workspace(self):
        storage = Path("/current/checkout").resolve()
        recorded = "/Users/researcher/original/checkout"
        events = [
            {"kind": "RESERVED", "phase": "checker", "cwd": recorded}
        ]
        state = {"attempts": [], "next_action": ("DONE", None)}

        with mock.patch.object(portable.runner, "Ledger") as ledger, \
             mock.patch.object(portable.runner, "verify_attempts") as verify:
            ledger.return_value.read.return_value = (events, state)
            self.assertIs(portable.evidence(storage), state)

        ledger.assert_called_once_with(storage)
        projected, actual_events = verify.call_args.args
        self.assertEqual(Path(projected), storage)
        self.assertEqual(str(projected), recorded)
        self.assertIs(actual_events, events)

    def test_execution_context_is_scoped_and_restored(self):
        original = historical.evidence
        with portable.portable_validation():
            self.assertIs(historical.evidence, portable.evidence)
        self.assertIs(historical.evidence, original)

    def test_actual_cache_history_remains_in_portfolio_custody(self):
        with portable.portable_validation():
            result = portfolio.validate_live_transition(ROOT)
        self.assertEqual(result["status"], "PASS")
        self.assertIn("lib/survivor_cache_historical.py", portfolio._extra_paths(ROOT))


if __name__ == "__main__":
    unittest.main()
