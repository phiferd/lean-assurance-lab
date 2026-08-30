import copy
import importlib.machinery
import importlib.util
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-declaration-validation-milestone-5"
loader = importlib.machinery.SourceFileLoader("declaration_milestone_5", str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)


class DeclarationValidationMilestone5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = module.load_json(module.REGISTRY_PATH)
        cls.registry_schema = module.load_json(module.REGISTRY_SCHEMA_PATH)
        cls.decision_log = module.load_json(module.DECISION_LOG_PATH)
        cls.decision_schema = module.load_json(module.DECISION_SCHEMA_PATH)
        cls.closure = module.load_json(module.CLOSURE_PATH)

    def errors(self, registry=None, decision_log=None, rendered=None):
        return module.validate_artifacts(
            registry or self.registry,
            self.registry_schema,
            decision_log or self.decision_log,
            self.decision_schema,
            self.closure,
            rendered_decision_log=(self.decision_log if rendered is None else rendered),
        )

    def test_schemas_are_valid_and_frozen_artifacts_pass(self):
        jsonschema.Draft202012Validator.check_schema(self.registry_schema)
        jsonschema.Draft202012Validator.check_schema(self.decision_schema)
        self.assertEqual(self.errors(), [])

    def test_every_milestone_4_seed_has_exactly_one_decision(self):
        seed_keys = {seed["key"] for seed in self.closure["seed_groups"]}
        resolutions = [row["seed_key"] for row in self.registry["seed_resolutions"]]
        self.assertEqual(set(resolutions), seed_keys)
        self.assertEqual(len(resolutions), len(seed_keys))

    def test_two_kind_model_is_preserved_without_forcing_unassigned_identities(self):
        kinds = {row["intended_kind"] for row in self.registry["identities"]}
        self.assertEqual(
            kinds - {None},
            {"NORMATIVE_CANDIDATE_OBLIGATION", "EMPIRICAL_CONTRACT_SCENARIO"},
        )
        self.assertEqual(sum(kind is None for kind in kinds), 1)
        self.assertEqual(
            sum(row["intended_kind"] is None for row in self.registry["identities"]),
            2,
        )

    def test_missing_seed_resolution_fails(self):
        registry = copy.deepcopy(self.registry)
        registry["seed_resolutions"].pop()
        self.assertTrue(any("seed-resolution closure mismatch" in e for e in self.errors(registry)))

    def test_checker_or_provenance_specific_id_fails(self):
        registry = copy.deepcopy(self.registry)
        registry["identities"][0]["id"] = "DECL.NANODA.NAME_FRESHNESS"
        self.assertTrue(any("implementation/provenance terminology" in e for e in self.errors(registry)))

    def test_statement_drift_requires_hash_change(self):
        registry = copy.deepcopy(self.registry)
        registry["identities"][0]["semantic_statement"] += " Altered."
        self.assertTrue(any("statement hash is stale" in e for e in self.errors(registry)))

    def test_kind_change_requires_a_new_identity(self):
        registry = copy.deepcopy(self.registry)
        registry["identities"][0]["intended_kind"] = "EMPIRICAL_CONTRACT_SCENARIO"
        registry["identities"][0]["statement_sha256"] = module.statement_sha256(
            registry["identities"][0]
        )
        errors = self.errors(registry)
        self.assertTrue(any("empirical scenario must use" in e for e in errors))

    def test_split_requires_multiple_results(self):
        registry = copy.deepcopy(self.registry)
        resolution = next(row for row in registry["seed_resolutions"] if row["action"] == "SPLIT")
        resolution["result_ids"] = resolution["result_ids"][:1]
        self.assertTrue(any("must resolve to at least two" in e for e in self.errors(registry)))

    def test_non_split_requires_one_result(self):
        registry = copy.deepcopy(self.registry)
        resolution = next(row for row in registry["seed_resolutions"] if row["action"] == "KEEP")
        resolution["result_ids"].append("DECL.ENV.NAME_FRESHNESS")
        self.assertTrue(any("must resolve to exactly one" in e for e in self.errors(registry)))

    def test_uncertain_kind_cannot_be_forced(self):
        registry = copy.deepcopy(self.registry)
        identity = next(row for row in registry["identities"] if row["identity_status"] == "DEFERRED_KIND")
        identity["intended_kind"] = "NORMATIVE_CANDIDATE_OBLIGATION"
        identity["statement_sha256"] = module.statement_sha256(identity)
        self.assertTrue(any("prematurely classified" in e for e in self.errors(registry)))

    def test_out_of_scope_decision_must_remain_reserved(self):
        registry = copy.deepcopy(self.registry)
        resolution = next(row for row in registry["seed_resolutions"] if row["action"] == "DEFER_OUT_OF_SCOPE")
        identity = next(row for row in registry["identities"] if row["id"] == resolution["result_ids"][0])
        identity["identity_status"] = "ACTIVE_PROVISIONAL"
        self.assertTrue(any("not reserved" in e for e in self.errors(registry)))

    def test_id_deletion_reuse_policy_is_frozen(self):
        registry = copy.deepcopy(self.registry)
        registry["id_evolution_rules"]["reuse"] = "ALLOWED"
        self.assertTrue(self.errors(registry))

    def test_authority_or_layer_fields_are_rejected(self):
        registry = copy.deepcopy(self.registry)
        registry["identities"][0]["authority"] = {"status": "ESTABLISHED"}
        self.assertTrue(any("Additional properties" in e for e in self.errors(registry)))

    def test_generated_decision_log_drift_fails(self):
        decision_log = copy.deepcopy(self.decision_log)
        decision_log["records"][0]["reason"] += " Altered."
        self.assertTrue(any("not synchronized" in e for e in self.errors(decision_log=decision_log)))

    def test_catalog_transition_hash_drift_fails(self):
        decision_log = copy.deepcopy(self.decision_log)
        decision_log["records"][0]["catalog_hash_after"] = "0" * 64
        self.assertTrue(any("catalog_hash_after is stale" in e for e in self.errors(decision_log=decision_log)))

    def test_decision_evidence_is_qualified_as_discovery_only(self):
        for record in self.decision_log["records"]:
            for evidence in record["evidence"]:
                self.assertEqual(evidence["role"], "DISCOVERY")
                self.assertEqual(evidence["source_type"], "LAB_EXPERIMENT")
                self.assertEqual(evidence["source_lock"]["registry"], "LOCAL_ARTIFACT_LOCK")
                self.assertEqual(evidence["exact_locator"]["kind"], "JSON_POINTER")
                self.assertEqual(evidence["assumptions"][0]["id"], "ASSUMPTION.M4.DISCOVERY_ONLY")

    def test_renderer_is_deterministic(self):
        renderer = module.load_renderer()
        self.assertEqual(renderer.render(), renderer.render())
        self.assertEqual(renderer.render(), self.decision_log)


if __name__ == "__main__":
    unittest.main()
