import json
import sys
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

from current_assurance import trend  # noqa: E402


class CurrentAssuranceTests(unittest.TestCase):
    def test_snapshot_and_policy_schemas_are_valid(self):
        for name in ("assurance-policy.schema.json", "current-assurance-snapshot.schema.json"):
            schema = json.loads((ROOT / "schemas" / name).read_text())
            jsonschema.Draft202012Validator.check_schema(schema)

    def test_context_threshold_never_becomes_a_gate(self):
        policy = {"minimum": 1.0, "enabled_as_gate": False, "context": "bounded sample"}
        result = trend(0.25, policy)
        self.assertEqual(result["assessment"], "BELOW_CONTEXT_THRESHOLD")
        self.assertFalse(result["enabled_as_gate"])

    def test_current_gate_fails_only_for_semantic_disagreement(self):
        snapshot = json.loads((ROOT / "results" / "assurance" / "current.json").read_text())
        self.assertEqual(snapshot["gate"]["status"], "FAIL")
        self.assertEqual(snapshot["gate"]["failure_reasons"], ["semantic_checker_disagreements"])
        self.assertEqual(snapshot["cross_validator_disagreements"]["semantic_unresolved_count"], 15)
        self.assertEqual(snapshot["cross_validator_disagreements"]["parse_behavior_count"], 1)

    def test_snapshot_has_every_plan_metric(self):
        snapshot = json.loads((ROOT / "results" / "assurance" / "current.json").read_text())
        required = {
            "identity", "validators", "corpus", "mutation_testing", "witness_synthesis",
            "generated_regressions", "cross_validator_disagreements", "held_out_evaluation",
            "coverage", "execution_cost",
        }
        self.assertTrue(required <= set(snapshot))
        self.assertTrue(snapshot["scope"]["injected_faults_are_not_discovered_bugs"])

    def test_generated_witness_kills_are_derived_from_current_evidence(self):
        snapshot = json.loads((ROOT / "results" / "assurance" / "current.json").read_text())
        self.assertEqual(snapshot["mutation_testing"]["killed_by_existing_corpus"], 136)
        self.assertEqual(snapshot["mutation_testing"]["killed_by_generated_corpus"], 3)
        self.assertEqual(
            snapshot["mutation_testing"]["killed_by_existing_corpus"]
            + snapshot["mutation_testing"]["killed_by_generated_corpus"]
            + snapshot["mutation_testing"]["surviving_mutants"],
            snapshot["mutation_testing"]["total_semantic_mutants"],
        )
        self.assertEqual(snapshot["generated_regressions"]["artifact_count"], 25)
        self.assertEqual(snapshot["witness_synthesis"]["witnesses_minimized"], 3)

    def test_pending_mechanical_survivors_are_not_conflated_with_modeled_results(self):
        snapshot = json.loads((ROOT / "results" / "assurance" / "current.json").read_text())
        pending = snapshot["mutation_testing"]["pending_survivor_triage"]
        self.assertEqual(pending["classification"], "SURVIVED_WITHOUT_WITNESS")
        self.assertEqual(pending["count"], len(pending["mutant_ids"]))
        self.assertEqual(pending["count"], 2)
        self.assertNotIn("nanoda-gen-e9648d8c028d", pending["mutant_ids"])
        self.assertNotIn("nanoda-gen-399895fa0b72", pending["mutant_ids"])
        self.assertNotIn("nanoda-gen-93b21593b0d8", pending["mutant_ids"])
        self.assertNotIn("nanoda-gen-af1dac9744e9", pending["mutant_ids"])
        self.assertEqual(snapshot["mutation_testing"]["equivalent_mutants"], 14)
        self.assertEqual(snapshot["mutation_testing"]["meaningful_survivors"], 5)
        self.assertIn("modeled denominator", pending["scope"])


if __name__ == "__main__":
    unittest.main()
