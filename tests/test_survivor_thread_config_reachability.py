import unittest
from pathlib import Path

from lib.survivor_thread_config_reachability import validate


ROOT = Path(__file__).resolve().parents[1]


class SurvivorThreadConfigReachabilityTests(unittest.TestCase):
    def test_public_dispatch_counterexample_and_boundary_are_split(self):
        result = validate(ROOT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["configuration_classes"], 3)
        self.assertEqual(result["registry_append_count"], 1)
        self.assertEqual(result["remaining_pending_mutations"],
                         ["nanoda-gen-2bdfe18a9ec2"])
        self.assertEqual(result["scientific_launches"], 0)


if __name__ == "__main__":
    unittest.main()
