import unittest
from pathlib import Path

from lib.survivor_thread_config_regression_historical import validate

ROOT = Path(__file__).resolve().parents[1]


class SurvivorThreadConfigRegressionHistoricalTests(unittest.TestCase):
    def test_frozen_regression_survives_readiness_closure(self):
        result = validate(ROOT)
        self.assertEqual(result["frozen_regression_outcome"], "SUCCESS")
        self.assertEqual(result["readiness_gate_decision"], "NO_GO")
        self.assertEqual(result["selected_item"], "SURVIVOR-CACHE-PREDICATE-TRANSFER-1")


if __name__ == "__main__":
    unittest.main()
