import copy
import importlib.machinery
import importlib.util
import json
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-declaration-validation-characterization-model"
loader = importlib.machinery.SourceFileLoader("declaration_characterization", str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)


class DeclarationValidationCharacterizationModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = module.load_json(module.MODEL_PATH)
        cls.model_schema = module.load_json(module.MODEL_SCHEMA_PATH)
        cls.entry_schema = module.load_json(module.ENTRY_SCHEMA_PATH)
        cls.target = module.load_json(module.TARGET_PATH)

    def errors(self, entry):
        return module.validate_entry(
            entry, self.model, self.entry_schema, self.target
        )

    def test_both_schemas_are_valid_and_model_conforms(self):
        jsonschema.Draft202012Validator.check_schema(self.model_schema)
        jsonschema.Draft202012Validator.check_schema(self.entry_schema)
        self.assertEqual(
            module.validate_model(
                self.model, self.model_schema, self.entry_schema, self.target
            ),
            [],
        )

    def test_both_kinds_have_distinct_valid_statement_shapes(self):
        normative = module.normative_fixture()
        empirical = module.empirical_fixture(self.model)
        self.assertEqual(self.errors(normative), [])
        self.assertEqual(self.errors(empirical), [])
        self.assertNotEqual(set(normative["statement"]), set(empirical["statement"]))

        normative["statement"] = copy.deepcopy(empirical["statement"])
        self.assertTrue(self.errors(normative))

    def test_empirical_scenario_can_span_multiple_layers(self):
        empirical = module.empirical_fixture(self.model)
        self.assertEqual(len(empirical["layers"]), 3)
        self.assertEqual(self.errors(empirical), [])

    def test_confidence_and_misplaced_policy_states_are_rejected(self):
        normative = module.normative_fixture()
        normative["confidence"] = "high"
        self.assertTrue(self.errors(normative))

        normative = module.normative_fixture()
        normative["authority"]["status"] = "POLICY"
        self.assertTrue(self.errors(normative))

        normative = module.normative_fixture()
        normative["lifecycle"]["status"] = "RECONSTRUCTION"
        self.assertTrue(self.errors(normative))

    def test_four_implementation_observations_do_not_establish_normativity(self):
        entry = module.implementation_consensus_fixture(
            self.model, module.normative_fixture()
        )
        errors = self.errors(entry)
        self.assertTrue(
            any("requires role-qualified NORMATIVE_SUPPORT" in error for error in errors)
        )

    def test_implementation_observation_requires_correct_lineage(self):
        empirical = module.empirical_fixture(self.model)
        del empirical["evidence"][0]["lineage"]
        self.assertTrue(self.errors(empirical))

        empirical = module.empirical_fixture(self.model)
        empirical["evidence"][0]["lineage"]["group"] = "FALSE_GROUP"
        self.assertTrue(
            any("lineage group does not match" in error for error in self.errors(empirical))
        )

    def test_mechanized_result_requires_and_accepts_full_qualification(self):
        entry = module.normative_fixture()
        evidence = entry["evidence"][0]
        evidence["source_type"] = "FORMAL_MECHANIZATION"
        evidence["lineage"] = {
            "group": "FIXTURE_FORMAL_LINEAGE",
            "relationship_to_target": "NON_IMPLEMENTATION_SOURCE",
            "independence_scope": "NOT_APPLICABLE",
            "basis": "Schema-only formal-source lineage.",
        }
        self.assertTrue(self.errors(entry))

        evidence["mechanized_result"] = {
            "theorem_or_definition": "Fixture.theorem",
            "relevant_assumptions_or_axioms": ["Fixture assumption"],
            "relationship_to_modeled_judgment": (
                "Schema-only example of an explicitly qualified relationship."
            ),
            "check_command": "fixture-check-command",
            "unchecked_command_reason": None,
        }
        self.assertEqual(self.errors(entry), [])

    def test_claim_pointer_and_evidence_references_are_checked(self):
        entry = module.normative_fixture()
        entry["evidence"][0]["claim_supported"]["entry_json_pointer"] = "/missing"
        self.assertTrue(any("invalid claim pointer" in error for error in self.errors(entry)))

        entry = module.normative_fixture()
        entry["authority"]["basis"]["evidence_refs"] = ["EVID.MISSING"]
        self.assertTrue(any("unknown authority evidence ref" in error for error in self.errors(entry)))

    def test_model_stops_before_discovery_and_catalog_entries(self):
        boundary = self.model["completion_boundary"]
        self.assertEqual(boundary["completed_milestones"], [2, 3])
        self.assertFalse(boundary["catalog_entries_created"])
        self.assertFalse(boundary["discovery_started"])
        self.assertEqual(boundary["next_milestone"], "MILESTONE_4_DEFINE_DISCOVERY_CLOSURE")

    def test_in_memory_conformance_suite_passes_every_check(self):
        errors, checks = module.conformance_suite(
            self.model, self.entry_schema, self.target
        )
        self.assertEqual(errors, [])
        self.assertEqual(len(checks), 14)
        self.assertTrue(all(checks.values()))


if __name__ == "__main__":
    unittest.main()
