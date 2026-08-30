import copy
import importlib.machinery
import importlib.util
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-declaration-validation-discovery-closure"
loader = importlib.machinery.SourceFileLoader("declaration_discovery_closure", str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)


class DeclarationValidationDiscoveryClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.closure = module.load_json(module.CLOSURE_PATH)
        cls.schema = module.load_json(module.SCHEMA_PATH)
        cls.target = module.load_json(module.TARGET_PATH)
        cls.model = module.load_json(module.MODEL_PATH)

    def errors(self, closure):
        return module.validate_closure(
            closure, self.schema, self.target, self.model
        )

    def test_schema_is_valid_and_frozen_closure_passes(self):
        jsonschema.Draft202012Validator.check_schema(self.schema)
        self.assertEqual(self.errors(self.closure), [])

    def test_required_starting_audit_surface_is_present(self):
        topic_ids = {topic["id"] for topic in self.closure["topics"]}
        self.assertTrue(module.REQUIRED_TOPICS.issubset(topic_ids))
        self.assertEqual(len(self.closure["topics"]), 22)

    def test_every_topic_has_exactly_four_observer_states(self):
        for topic in self.closure["topics"]:
            observers = [row["observer"] for row in topic["observer_matrix"]]
            self.assertEqual(set(observers), set(module.OBSERVERS))
            self.assertEqual(len(observers), 4)

    def test_missing_required_topic_fails(self):
        closure = copy.deepcopy(self.closure)
        closure["topics"] = [
            topic for topic in closure["topics"]
            if topic["id"] != "TOPIC.CURRENT_DECL_VISIBILITY"
        ]
        self.assertTrue(any("required starting-audit topics missing" in e for e in self.errors(closure)))

    def test_observer_vector_omission_fails(self):
        closure = copy.deepcopy(self.closure)
        closure["topics"][0]["observer_matrix"].pop()
        self.assertTrue(self.errors(closure))

    def test_site_source_cross_reference_is_bidirectional(self):
        closure = copy.deepcopy(self.closure)
        closure["sources"][0]["site_ids"].pop()
        self.assertTrue(any("missing from its source site ledger" in e for e in self.errors(closure)))

    def test_pinned_revision_drift_fails(self):
        closure = copy.deepcopy(self.closure)
        closure["sources"][0]["revision"] = "0" * 40
        self.assertTrue(any("revision does not match" in e for e in self.errors(closure)))

    def test_primary_scope_cannot_silently_shrink(self):
        closure = copy.deepcopy(self.closure)
        closure["scope"]["primary_declaration_kinds"].pop()
        self.assertTrue(any("primary declaration kinds" in e for e in self.errors(closure)))

    def test_seed_cannot_be_promoted_in_milestone_4(self):
        closure = copy.deepcopy(self.closure)
        closure["seed_groups"][0]["status"] = "ESTABLISHED"
        self.assertTrue(self.errors(closure))

    def test_catalog_and_stable_identity_boundary_is_mechanical(self):
        closure = copy.deepcopy(self.closure)
        closure["completion"]["catalog_entries_created"] = True
        self.assertTrue(self.errors(closure))

        closure = copy.deepcopy(self.closure)
        closure["completion"]["stable_semantic_ids_assigned"] = True
        self.assertTrue(self.errors(closure))

    def test_kiota_differences_are_explicit_not_normative_votes(self):
        topics = {topic["id"]: topic for topic in self.closure["topics"]}
        for topic_id in (
            "TOPIC.UNIVERSE_OWNERSHIP",
            "TOPIC.CURRENT_DECL_VISIBILITY",
        ):
            kiota = next(
                row for row in topics[topic_id]["observer_matrix"]
                if row["observer"] == "KIOTA"
            )
            self.assertEqual(kiota["state"], "OBSERVED_DIFFERENCE")
        self.assertIn(
            "No source site, official behavior, checker agreement, or absence establishes normative authority in Milestone 4.",
            self.closure["nonclaims"],
        )


if __name__ == "__main__":
    unittest.main()
