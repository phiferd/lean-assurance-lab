import copy
import importlib.machinery
import importlib.util
import json
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


validator = load_module(
    "declaration_publication_study_validator",
    ROOT / "scripts" / "validate-declaration-validation-publication-study",
)
deriver = load_module(
    "declaration_publication_study_deriver",
    ROOT / "scripts" / "derive-declaration-validation-publication-study-preregistration",
)


class DeclarationValidationPublicationStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.preregistration = validator.load_json(validator.PREREGISTRATION_PATH)
        cls.discovery = validator.load_json(validator.DISCOVERY_PATH)
        cls.schema = validator.load_json(validator.SCHEMA_PATH)
        cls.approval = validator.load_json(validator.APPROVAL_PATH)
        cls.approval_schema = validator.load_json(validator.APPROVAL_SCHEMA_PATH)
        cls.sentinel = validator.load_json(validator.SENTINEL_PATH)
        cls.sentinel_schema = validator.load_json(validator.SENTINEL_SCHEMA_PATH)
        cls.catalog = validator.load_json(validator.CATALOG_PATH)
        cls.evidence_lock = validator.load_json(validator.SENTINEL_EVIDENCE_LOCK_PATH)
        cls.registry = validator.load_json(validator.APPROVED_SUCCESSOR_PATH)

    def test_schema_is_valid_draft_2020_12(self):
        jsonschema.Draft202012Validator.check_schema(self.schema)
        jsonschema.Draft202012Validator.check_schema(self.approval_schema)
        jsonschema.Draft202012Validator.check_schema(self.sentinel_schema)

    def test_actual_preregistration_validates(self):
        self.assertEqual(validator.validate_preregistration(), [])

    def test_actual_frozen_discovery_and_review_packet_validate(self):
        self.assertEqual(validator.validate_discovery(), [])
        self.assertEqual(self.discovery["execution_summary"]["closure_status"], "CLOSED")
        self.assertEqual(len(self.discovery["sources"]), 18)

    def test_actual_human_authority_source_approval_validates(self):
        self.assertEqual(validator.validate_approval(), [])
        self.assertEqual(
            self.approval["source_decisions"][2]["claim_decisions"][0]["disposition"],
            "APPROVE",
        )
        self.assertEqual(
            self.approval["source_decisions"][2]["claim_decisions"][1]["disposition"],
            "REJECT",
        )

    def test_actual_gate_5_sentinel_validates(self):
        self.assertEqual(validator.validate_sentinel(check_generated=False), [])
        self.assertEqual(
            [row["entry_id"] for row in self.sentinel["sentinel_decisions"]],
            validator.EXPECTED_SENTINELS,
        )
        self.assertEqual(
            [row["authority_status"] for row in self.sentinel["sentinel_decisions"]],
            ["ESTABLISHED", "PROVISIONAL"],
        )
        self.assertEqual(self.sentinel["architecture"]["verdict"], "PASS_AFTER_REPAIR")

    def test_gate_5_scope_guard_rejects_cross_claim_source_reuse(self):
        changed = copy.deepcopy(self.catalog)
        theorem = next(
            row for row in changed["entries"]
            if row["characterization"]["id"] == "DECL.THEOREM.TYPE_PROP"
        )
        let_value = next(
            row for row in changed["entries"]
            if row["characterization"]["id"] == "EXPR.LET.VALUE_TYPE_MATCH"
        )
        forged = copy.deepcopy(next(
            row for row in theorem["characterization"]["evidence"]
            if row["id"] == validator.THEOREM_EVIDENCE_ID
        ))
        forged["id"] = "EVID.PUBLICATION_STUDY.LET_VALUE.NORMATIVE"
        forged["claim_supported"]["predicate_id"] = (
            "PRED.PUBLICATION_STUDY.LET_VALUE.NORMATIVE"
        )
        let_value["characterization"]["evidence"].append(forged)
        errors = validator.claim_scope_errors(
            changed,
            self.evidence_lock,
            self.approval,
            self.registry,
            self.sentinel,
        )
        self.assertTrue(any("outside the exact human-approved claim scope" in item for item in errors))

    def test_gate_5_cannot_broaden_the_approved_candidate_scope(self):
        changed = copy.deepcopy(self.sentinel)
        changed["claim_scope_guard"]["candidate_ids"] = [
            "EXPR.LET.VALUE_TYPE_MATCH"
        ]
        errors = validator.validate_sentinel(changed, check_generated=False)
        self.assertTrue(any("schema error" in item or "broadens" in item for item in errors))

    def test_gate_5_binds_the_m10_theorem_control_erratum(self):
        changed = copy.deepcopy(self.sentinel)
        changed["m10_erratum_application"]["matched_positive_control_rule"] = (
            "Use the definition-form artifact."
        )
        errors = validator.validate_sentinel(changed, check_generated=False)
        self.assertTrue(any("schema error" in item or "theorem-control correction" in item for item in errors))

    def test_gate_5_scope_closure_stops_before_remaining_work(self):
        closure = self.sentinel["scope_closure"]
        self.assertEqual(closure["remaining_candidates_adjudicated"], 0)
        self.assertFalse(closure["denominator_derived"])
        self.assertFalse(closure["baseline_or_coverage_started"])
        self.assertFalse(closure["synthesis_started"])
        self.assertFalse(closure["mutation_or_checker_campaign_started"])
        self.assertFalse(closure["new_source_discovery_performed"])

    def test_approval_cannot_widen_theorem_prop_source_scope(self):
        changed = copy.deepcopy(self.approval)
        changed["source_decisions"][2]["claim_decisions"][1]["disposition"] = "APPROVE"
        errors = validator.validate_approval(changed)
        self.assertTrue(any("HEADER_BEFORE_BODY" in item or "scope is not exactly" in item for item in errors))

    def test_approval_cannot_change_discovered_source_bytes(self):
        changed = copy.deepcopy(self.approval)
        changed["source_decisions"][2]["source_content_sha256"] = "0" * 64
        errors = validator.validate_approval(changed)
        self.assertTrue(any("content binding differs" in item for item in errors))

    def test_discovery_query_removal_is_rejected(self):
        changed = copy.deepcopy(self.discovery)
        changed["query_log"].pop()
        errors = validator.validate_discovery(changed)
        self.assertTrue(any("exact required query inventory" in item for item in errors))

    def test_discovery_evidence_tamper_is_rejected(self):
        changed = copy.deepcopy(self.discovery)
        changed["sources"][0]["retrieved_content_sha256"] = "0" * 64
        errors = validator.validate_discovery(changed)
        self.assertTrue(any("evidence SHA-256 is stale" in item for item in errors))

    def test_discovery_does_not_approve_sources(self):
        approved = validator.load_json(validator.APPROVED_SOURCES_PATH)
        self.assertFalse(approved.get("normative_documentation"))
        self.assertFalse(approved.get("mechanized_results"))
        self.assertEqual(self.discovery["status"], "FROZEN_BEFORE_AUTHORITY_SOURCE_APPROVAL")

    def test_cohort_is_mechanically_derived_from_immutable_m10(self):
        candidates, holdouts = deriver.derive(self.preregistration)
        self.assertEqual(self.preregistration["cohort_derivation"]["candidates"], candidates)
        self.assertEqual(
            self.preregistration["cohort_derivation"]["technical_readiness_holdouts"],
            holdouts,
        )
        self.assertEqual(len(candidates), 15)
        self.assertEqual(
            [row["id"] for row in holdouts],
            [
                "DECL.TYPE.NO_FREE_VARS",
                "DECL.TYPE.NO_METAVARS",
                "DECL.TYPE.WELL_FORMED",
                "DECL.VALUE.WELL_FORMED",
            ],
        )

    def test_candidate_substitution_is_rejected(self):
        changed = copy.deepcopy(self.preregistration)
        changed["cohort_derivation"]["candidates"][0]["id"] = "DECL.TYPE.NO_FREE_VARS"
        errors = validator.validate_preregistration(changed, check_predecessors=False)
        self.assertTrue(any("candidate cohort differs" in item for item in errors))

    def test_required_query_removal_is_rejected(self):
        changed = copy.deepcopy(self.preregistration)
        changed["source_discovery_protocol"]["required_queries"].pop()
        errors = validator.validate_preregistration(changed, check_predecessors=False)
        self.assertTrue(any("exactly 30 unique" in item for item in errors))

    def test_every_candidate_has_all_four_query_scopes(self):
        candidate_ids = [
            row["id"] for row in self.preregistration["cohort_derivation"]["candidates"]
        ]
        queries = self.preregistration["source_discovery_protocol"]["required_queries"]
        for candidate_id in candidate_ids:
            scopes = {row["scope"] for row in queries if candidate_id in row["candidate_ids"]}
            self.assertEqual(scopes, validator.EXPECTED_QUERY_SCOPES)

    def test_source_approval_is_reserved_to_separate_human_review(self):
        authority = self.preregistration["authority_protocol"]
        self.assertEqual(authority["roles"]["source_approver"], "SEPARATE_HUMAN_REVIEW_REQUIRED")
        self.assertIn(
            "NO_AUTHORITY_APPROVAL_BY_DISCOVERY_AGENT", self.preregistration["prohibitions"]
        )

    def test_bounded_pilot_and_comparator_budgets_are_fixed(self):
        pilot = self.preregistration["synthesis_budget_rules"]["bounded_pilot_per_target_ceiling"]
        self.assertEqual(pilot["tier_3_candidates"], 0)
        comparator = self.preregistration["comparator_budget_rules"]
        self.assertEqual(
            [
                comparator["new_checker_campaigns"],
                comparator["new_coverage_collection_runs"],
                comparator["new_mutants"],
                comparator["new_mutation_campaigns"],
            ],
            [0, 0, 0, 0],
        )

    def test_historical_bindings_use_exact_attestation_identities(self):
        actual = {
            row["path"]: (row["attestation_id"], row["historical_content_commit"])
            for row in self.preregistration["immutable_predecessors"]
        }
        self.assertEqual(actual, validator.EXPECTED_PREDECESSORS)


if __name__ == "__main__":
    unittest.main()
