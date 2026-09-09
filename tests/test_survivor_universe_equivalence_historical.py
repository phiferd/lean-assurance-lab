import unittest
from pathlib import Path

from lib.survivor_universe_equivalence_historical import validate


ROOT = Path(__file__).resolve().parents[1]


class UniverseEquivalenceHistoricalTests(unittest.TestCase):
    def test_entry_bytes_survive_scoped_equivalence_admission(self):
        result = validate(ROOT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["registry_predecessor_lines"], 607)
        self.assertEqual(result["registry_successor_lines"], 610)
        self.assertEqual(result["current_successor_status"], "READY")
        self.assertEqual(result["pending_survivors"], 3)
        self.assertEqual(result["equivalent_mutants"], 14)


if __name__ == "__main__":
    unittest.main()
