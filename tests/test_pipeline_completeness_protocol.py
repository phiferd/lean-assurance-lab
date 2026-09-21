from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results/research/pipeline-completeness-pilot-1"


def load(name: str):
    return json.loads((BASE / name).read_text(encoding="utf-8"))


class PipelineCompletenessProtocolTests(unittest.TestCase):
    def test_independent_twelve_declaration_chain(self):
        expected = load("expected-module.json")
        declarations = expected["declarations"]
        self.assertEqual(len(declarations), 12)
        names = [f"PipelineCompleteness.d{number:02d}" for number in range(1, 13)]
        self.assertEqual([row["name"] for row in declarations], names)
        self.assertEqual(declarations[0]["direct_value_dependencies"], [])
        for index, row in enumerate(declarations[1:], 1):
            self.assertEqual(row["direct_value_dependencies"], [names[index - 1]])
        self.assertEqual(expected["root_target"], names[-1])

    def test_fixed_fault_matrix_and_limits(self):
        protocol = load("protocol.json")
        self.assertEqual([row["id"] for row in protocol["adapters"]], ["official", "lean4lean"])
        self.assertEqual([row["id"] for row in protocol["faults"]],
                         ["OMISSION", "SUBSTITUTION", "TRUNCATION"])
        matrix = protocol["matrix"]
        self.assertEqual(len(matrix["artifacts"]) * len(matrix["adapters"]), 8)
        self.assertEqual(matrix["primary_checker_launches"], 8)
        self.assertEqual(matrix["maximum_checker_launches"], 12)
        self.assertEqual(protocol["limits"]["network_requests"], 0)
        self.assertEqual(protocol["limits"]["external_actions"], 0)

    def test_process_success_is_not_the_completeness_oracle(self):
        rule = load("protocol.json")["receipt_contract"]["success_rule"]
        self.assertIn("necessary but never sufficient", rule)
        self.assertIn("independently expected target", rule)
        self.assertIn("exact artifact hash", rule)


if __name__ == "__main__":
    unittest.main()
