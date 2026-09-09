import unittest
from pathlib import Path

from lib.survivor_fvar_reachability import validate


ROOT = Path(__file__).resolve().parents[1]


class SurvivorFvarReachabilityTests(unittest.TestCase):
    def test_public_export_path_exclusion_is_scoped(self):
        result = validate(ROOT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["classification"], "EQUIVALENT_AT_PUBLIC_EXPORT_PATH")
        self.assertEqual(result["public_entry_steps"], 5)
        self.assertEqual(result["internal_counterexamples"], 1)
        self.assertEqual(result["scientific_launches"], 0)


if __name__ == "__main__":
    unittest.main()
