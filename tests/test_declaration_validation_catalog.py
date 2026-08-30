import copy
import hashlib
import importlib.machinery
import importlib.util
import json
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-declaration-validation-catalog"


def load_module(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


module = load_module("declaration_catalog_validator", SCRIPT)
model_module = load_module(
    "declaration_characterization_model_validator",
    ROOT / "scripts" / "validate-declaration-validation-characterization-model",
)


class DeclarationValidationCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = module.load_json(module.CATALOG_PATH)
        cls.catalog_schema = module.load_json(module.CATALOG_SCHEMA_PATH)
        cls.entry_schema = module.load_json(module.ENTRY_SCHEMA_PATH)
        cls.authority = module.load_json(module.AUTHORITY_PATH)
        cls.authority_schema = module.load_json(module.AUTHORITY_SCHEMA_PATH)
        cls.decisions = module.load_json(module.DECISIONS_PATH)
        cls.decisions_schema = module.load_json(module.DECISIONS_SCHEMA_PATH)
        cls.freeze = module.load_json(module.FREEZE_PATH)
        cls.freeze_schema = module.load_json(module.FREEZE_SCHEMA_PATH)
        cls.target = module.load_json(module.TARGET_PATH)
        cls.model = module.load_json(module.MODEL_PATH)
        cls.identities_document = module.load_json(module.IDENTITY_PATH)
        cls.identities = {
            row["id"]: row for row in cls.identities_document["identities"]
        }
        cls.source_lock = module.load_json(module.SOURCE_LOCK_PATH)
        cls.prior_decisions = module.load_json(module.PRIOR_DECISIONS_PATH)

    def errors(self, catalog=None, authority=None, decisions=None):
        return module.validate_artifacts(
            self.catalog if catalog is None else catalog,
            self.catalog_schema,
            self.entry_schema,
            self.authority if authority is None else authority,
            self.authority_schema,
            self.decisions if decisions is None else decisions,
            self.decisions_schema,
            self.freeze,
            self.freeze_schema,
            self.target,
            self.identities_document,
            self.source_lock,
            self.prior_decisions,
            check_generated=False,
        )

    def populated_catalog(self, *entries):
        catalog = copy.deepcopy(self.catalog)
        catalog["status"] = "MILESTONE_8_CHARACTERIZATION_INVENTORY"
        catalog["completion_boundary"] = {
            "canonical_data_authoritative": True,
            "generated_report_required": True,
            "inventory_populated": True,
            "authority_assignments_created": True,
            "next_milestone": "MILESTONE_9_ADVERSARIAL_REVIEW",
        }
        catalog["entries"] = list(entries)
        return catalog

    def normative_wrapper(self, stable_id="DECL.THEOREM.TYPE_PROP"):
        identity = self.identities[stable_id]
        entry = model_module.normative_fixture()
        entry["id"] = stable_id
        entry["name"] = "In-memory catalog validation fixture"
        entry["authority"]["basis"]["qualification_rule"] = (
            "AUTH.NORMATIVE.ESTABLISHED.V1"
        )
        entry["evidence"][0]["source_lock"] = {
            "registry": "SEMANTIC_TARGET_PROFILE",
            "lock_id": self.target["profile_id"],
        }
        entry["evidence"][0]["exact_locator"] = {
            "kind": "DOCUMENT_SECTION",
            "value": "/logical_target/modeled_judgment",
        }
        return {
            "characterization": entry,
            "identity_statement_sha256": identity["statement_sha256"],
            "decision_ids": identity["decision_ids"],
            "observer_vector": [
                {
                    "profile_pointer": pointer,
                    "outcome": "NOT_INSPECTED",
                    "attribution": "In-memory test fixture; no observer claim.",
                    "evidence_refs": [],
                }
                for pointer in self.catalog["observer_order"]
            ],
            "source_mappings": [],
        }

    def empirical_wrapper(self):
        stable_id = "SCENARIO.EXPORT.FREE_VAR_REPRESENTABILITY"
        identity = self.identities[stable_id]
        entry = model_module.empirical_fixture(self.model)
        entry["id"] = stable_id
        entry["name"] = "In-memory empirical catalog validation fixture"
        entry["authority"]["basis"]["qualification_rule"] = (
            "AUTH.EMPIRICAL.ESTABLISHED.V1"
        )
        entry["statement"]["profile_specific_effects"][0]["outcome"] = "REJECT"
        witness = self.source_lock["generated_witnesses"][0]
        control = next(item for item in entry["evidence"] if item["role"] == "CONTROL")
        control["source_lock"] = {
            "registry": "DECLARATION_VALIDATION_SOURCE_LOCK",
            "lock_id": witness["id"],
        }
        control["exact_locator"] = {
            "kind": "ARTIFACT_SHA256",
            "value": witness["artifact_sha256"],
        }
        observations = []
        for pointer in self.catalog["observer_order"]:
            concrete = pointer == "/observer_profiles/lean4lean"
            observations.append(
                {
                    "profile_pointer": pointer,
                    "outcome": "REJECT" if concrete else "NOT_INSPECTED",
                    "attribution": "In-memory fixture observation." if concrete else "Not inspected in fixture.",
                    "evidence_refs": ["EVID.FIXTURE.OBSERVATION"] if concrete else [],
                }
            )
        return {
            "characterization": entry,
            "identity_statement_sha256": identity["statement_sha256"],
            "decision_ids": identity["decision_ids"],
            "observer_vector": observations,
            "source_mappings": [],
        }

    def test_schemas_are_valid_and_frozen_artifacts_pass(self):
        for schema in (
            self.catalog_schema,
            self.entry_schema,
            self.authority_schema,
            self.decisions_schema,
            self.freeze_schema,
        ):
            jsonschema.Draft202012Validator.check_schema(schema)
        self.assertEqual(self.errors(), [])

    def test_milestone_7_catalog_is_authoritative_but_empty(self):
        self.assertEqual(self.catalog["status"], "MILESTONE_7_INFRASTRUCTURE_ONLY")
        self.assertEqual(self.catalog["entries"], [])
        self.assertTrue(
            self.catalog["completion_boundary"]["canonical_data_authoritative"]
        )
        self.assertFalse(self.catalog["completion_boundary"]["inventory_populated"])

    def test_six_authority_rules_cover_both_kinds_and_all_statuses(self):
        errors, rules = module.validate_rule_set(self.authority)
        self.assertEqual(errors, [])
        self.assertEqual(len(rules), 6)

    def test_report_is_deterministic_synchronized_and_content_bound(self):
        renderer = module.load_module("catalog_report_test", module.REPORT_RENDERER_PATH)
        first = renderer.render(self.catalog, self.source_lock)
        self.assertEqual(first, renderer.render(self.catalog, self.source_lock))
        self.assertEqual(first, module.REPORT_PATH.read_text(encoding="utf-8"))
        self.assertIn(module.sha256_file(module.CATALOG_PATH), first)

    def test_report_contains_all_required_generated_views(self):
        report = module.REPORT_PATH.read_text(encoding="utf-8")
        for heading in (
            "Counts by Kind",
            "Counts by Layer",
            "Counts by Authority Status",
            "Counts by Lifecycle Status",
            "Checker Observation Summary",
            "Unresolved Items",
            "Source Mappings",
            "Normative Candidate Obligations",
            "Empirical Contract Scenarios",
        ):
            self.assertIn(heading, report)

    def test_freeze_is_deterministic_acyclic_and_does_not_bind_itself(self):
        renderer = module.load_module("catalog_freeze_test", module.FREEZE_RENDERER_PATH)
        self.assertEqual(renderer.render(), self.freeze)
        self.assertEqual(module.validate_freeze(self.freeze), [])
        paths = {binding["path"] for binding in self.freeze["artifacts"].values()}
        self.assertNotIn(str(module.FREEZE_PATH.relative_to(ROOT)), paths)

    def test_valid_normative_fixture_satisfies_established_rule(self):
        catalog = self.populated_catalog(self.normative_wrapper())
        self.assertEqual(self.errors(catalog), [])

    def test_valid_empirical_fixture_satisfies_established_rule(self):
        catalog = self.populated_catalog(self.empirical_wrapper())
        self.assertEqual(self.errors(catalog), [])

    def test_duplicate_stable_id_fails(self):
        entry = self.normative_wrapper()
        catalog = self.populated_catalog(entry, copy.deepcopy(entry))
        self.assertTrue(any("duplicate catalog stable ID" in item for item in self.errors(catalog)))

    def test_unregistered_stable_id_fails(self):
        entry = self.normative_wrapper()
        entry["characterization"]["id"] = "DECL.UNKNOWN.FIXTURE"
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("absent from the frozen identity registry" in item for item in self.errors(catalog)))

    def test_identity_statement_hash_drift_fails(self):
        entry = self.normative_wrapper()
        entry["identity_statement_sha256"] = "0" * 64
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("identity statement hash is stale" in item for item in self.errors(catalog)))

    def test_unknown_decision_id_fails(self):
        entry = self.normative_wrapper()
        entry["decision_ids"] = ["DEC.UNKNOWN.001"]
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("unknown decision ID" in item for item in self.errors(catalog)))

    def test_missing_lifecycle_target_fails(self):
        entry = self.normative_wrapper()
        entry["characterization"]["lifecycle"] = {
            "status": "SUPERSEDED",
            "reason": "In-memory target validation fixture.",
            "target_ids": ["DECL.VALUE.WELL_FORMED"],
        }
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("lifecycle target is not a catalog entry" in item for item in self.errors(catalog)))

    def test_lifecycle_target_cycle_fails(self):
        first = self.normative_wrapper("DECL.THEOREM.TYPE_PROP")
        second = self.normative_wrapper("DECL.VALUE.WELL_FORMED")
        first["characterization"]["lifecycle"] = {
            "status": "SUPERSEDED",
            "reason": "Cycle fixture.",
            "target_ids": ["DECL.VALUE.WELL_FORMED"],
        }
        second["characterization"]["lifecycle"] = {
            "status": "SUPERSEDED",
            "reason": "Cycle fixture.",
            "target_ids": ["DECL.THEOREM.TYPE_PROP"],
        }
        catalog = self.populated_catalog(first, second)
        self.assertTrue(any("lifecycle target cycle" in item for item in self.errors(catalog)))

    def test_incomplete_observer_vector_fails(self):
        entry = self.normative_wrapper()
        entry["observer_vector"].pop()
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("observer_vector" in item for item in self.errors(catalog)))

    def test_concrete_observer_outcome_requires_evidence(self):
        entry = self.normative_wrapper()
        entry["observer_vector"][0]["outcome"] = "REJECT"
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("concrete observer outcome lacks evidence" in item for item in self.errors(catalog)))

    def test_unknown_source_mapping_fails(self):
        entry = self.normative_wrapper()
        entry["source_mappings"] = [
            {
                "implementation": "LOGICAL_TARGET",
                "source_file_id": "SRC.UNKNOWN.FILE",
                "symbol_or_range": "fixture",
                "role": "ENFORCEMENT",
                "evidence_refs": ["EVID.FIXTURE.NORMATIVE"],
            }
        ]
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("unknown mapped source file" in item for item in self.errors(catalog)))

    def test_unresolved_evidence_reference_fails(self):
        entry = self.normative_wrapper()
        entry["observer_vector"][0]["outcome"] = "REJECT"
        entry["observer_vector"][0]["evidence_refs"] = ["EVID.UNKNOWN.REFERENCE"]
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("unresolved evidence refs" in item for item in self.errors(catalog)))

    def test_unknown_source_lock_reference_fails(self):
        entry = self.normative_wrapper()
        entry["characterization"]["evidence"][0]["source_lock"] = {
            "registry": "DECLARATION_VALIDATION_SOURCE_LOCK",
            "lock_id": "LOCAL.DOES_NOT_EXIST",
        }
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("unknown source-lock id" in item for item in self.errors(catalog)))

    def test_invalid_claim_pointer_fails(self):
        entry = self.normative_wrapper()
        entry["characterization"]["evidence"][0]["claim_supported"][
            "entry_json_pointer"
        ] = "/does/not/exist"
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("claim JSON Pointer does not resolve" in item for item in self.errors(catalog)))

    def test_tracked_evidence_descendant_json_pointer_resolves(self):
        evidence = copy.deepcopy(self.normative_wrapper()["characterization"]["evidence"][0])
        evidence["source_lock"] = {
            "registry": "DECLARATION_VALIDATION_SOURCE_LOCK",
            "lock_id": "LOCAL.CORE_DECL_MATRIX",
        }
        evidence["exact_locator"] = {
            "kind": "JSON_POINTER",
            "value": "results/investigations/nanoda-core-declaration-contract-matrix.json#/cases/0",
        }
        self.assertEqual(
            module.evidence_source_errors(evidence, self.target, self.source_lock), []
        )

    def test_unknown_case_id_fails_source_lock_resolution(self):
        evidence = copy.deepcopy(self.normative_wrapper()["characterization"]["evidence"][0])
        evidence["source_lock"] = {
            "registry": "DECLARATION_VALIDATION_SOURCE_LOCK",
            "lock_id": "LOCAL.CORE_DECL_MATRIX",
        }
        evidence["exact_locator"] = {
            "kind": "CASE_ID",
            "value": "case-that-does-not-exist",
        }
        self.assertTrue(
            any(
                "case ID does not resolve" in item
                for item in module.evidence_source_errors(
                    evidence, self.target, self.source_lock
                )
            )
        )

    def test_implementation_observation_cannot_establish_normativity(self):
        entry = self.normative_wrapper()
        evidence = entry["characterization"]["evidence"][0]
        evidence["role"] = "IMPLEMENTATION_OBSERVATION"
        evidence["source_type"] = "IMPLEMENTATION_SOURCE"
        evidence["lineage"] = {
            "group": "FIXTURE_IMPLEMENTATION",
            "relationship_to_target": "DISTINCT_CODEBASE",
            "independence_scope": "DISTINCT_LINEAGE_ONLY",
            "basis": "In-memory fixture only.",
        }
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("lacks NORMATIVE_SUPPORT" in item for item in self.errors(catalog)))

    def test_unresolved_authority_requires_durable_blocker(self):
        entry = self.normative_wrapper()
        authority = entry["characterization"]["authority"]
        authority["status"] = "UNRESOLVED"
        authority["basis"]["qualification_rule"] = "AUTH.NORMATIVE.UNRESOLVED.V1"
        authority["basis"]["unmet_requirements"] = ["Fixture missing authority resolution."]
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("lacks a blocking unknown or contradiction" in item for item in self.errors(catalog)))

    def test_established_empirical_authority_requires_concrete_observation(self):
        entry = self.empirical_wrapper()
        for observation in entry["observer_vector"]:
            observation["outcome"] = "NOT_INSPECTED"
            observation["evidence_refs"] = []
        entry["characterization"]["statement"]["profile_specific_effects"][0][
            "outcome"
        ] = "NOT_INSPECTED"
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("has no concrete observer outcome" in item for item in self.errors(catalog)))

    def test_dynamic_report_is_derived_from_catalog_entry(self):
        entry = self.normative_wrapper()
        catalog = self.populated_catalog(entry)
        renderer = module.load_module("catalog_dynamic_report_test", module.REPORT_RENDERER_PATH)
        report = renderer.render(catalog, self.source_lock)
        self.assertIn("DECL.THEOREM.TYPE_PROP", report)
        self.assertIn("| NORMATIVE_CANDIDATE_OBLIGATION | 1 |", report)


if __name__ == "__main__":
    unittest.main()
