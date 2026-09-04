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
denominator_deriver = load_module(
    "declaration_publication_study_denominator_deriver",
    ROOT / "scripts" / "derive-declaration-validation-publication-study-denominator",
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
        cls.adjudication = validator.load_json(validator.ADJUDICATION_PATH)
        cls.adjudication_schema = validator.load_json(validator.ADJUDICATION_SCHEMA_PATH)
        cls.denominator = validator.load_json(validator.DENOMINATOR_PATH)
        cls.denominator_schema = validator.load_json(validator.DENOMINATOR_SCHEMA_PATH)
        cls.catalog = validator.load_json(validator.CATALOG_PATH)
        cls.evidence_lock = validator.load_json(validator.SENTINEL_EVIDENCE_LOCK_PATH)
        cls.current_evidence_lock = validator.load_json(
            validator.ADJUDICATION_EVIDENCE_LOCK_PATH
        )
        cls.registry = validator.load_json(validator.APPROVED_SUCCESSOR_PATH)
        cls.gate5_catalog_bytes, catalog_errors = validator.binding_bytes(
            cls.adjudication["bindings"]["gate5_catalog"],
            label="test Gate-5 catalog",
            require_live_match=False,
        )
        cls.gate5_lock_bytes, lock_errors = validator.binding_bytes(
            cls.adjudication["bindings"]["gate5_evidence_lock"],
            label="test Gate-5 evidence lock",
            require_live_match=False,
        )
        schema_bytes, schema_error = validator.git_output(
            ["show", f"{validator.GATE5_COMMIT}:schemas/declaration-validation-evidence-lock.schema.json"]
        )
        if catalog_errors or lock_errors or schema_error or schema_bytes is None:
            raise AssertionError(catalog_errors + lock_errors + [schema_error or "missing schema"])
        cls.gate5_evidence_schema = json.loads(schema_bytes)
        cls.gate5_evidence_schema_sha256 = validator.sha256_bytes(schema_bytes)

    def historical_sentinel_errors(self, document):
        return validator.validate_sentinel(
            document,
            check_generated=False,
            catalog_bytes=self.gate5_catalog_bytes,
            evidence_lock_bytes=self.gate5_lock_bytes,
            evidence_lock_schema_document=self.gate5_evidence_schema,
            evidence_lock_schema_sha256_override=self.gate5_evidence_schema_sha256,
        )

    def test_schema_is_valid_draft_2020_12(self):
        jsonschema.Draft202012Validator.check_schema(self.schema)
        jsonschema.Draft202012Validator.check_schema(self.approval_schema)
        jsonschema.Draft202012Validator.check_schema(self.sentinel_schema)
        jsonschema.Draft202012Validator.check_schema(self.adjudication_schema)
        jsonschema.Draft202012Validator.check_schema(self.denominator_schema)

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
        self.assertEqual(self.historical_sentinel_errors(self.sentinel), [])
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
            self.current_evidence_lock,
            self.approval,
            self.registry,
            self.sentinel,
            predecessor_locks=[self.evidence_lock],
        )
        self.assertTrue(any("outside the exact human-approved claim scope" in item for item in errors))

    def test_gate_5_cannot_broaden_the_approved_candidate_scope(self):
        changed = copy.deepcopy(self.sentinel)
        changed["claim_scope_guard"]["candidate_ids"] = [
            "EXPR.LET.VALUE_TYPE_MATCH"
        ]
        errors = self.historical_sentinel_errors(changed)
        self.assertTrue(any("schema error" in item or "broadens" in item for item in errors))

    def test_gate_5_binds_the_m10_theorem_control_erratum(self):
        changed = copy.deepcopy(self.sentinel)
        changed["m10_erratum_application"]["matched_positive_control_rule"] = (
            "Use the definition-form artifact."
        )
        errors = self.historical_sentinel_errors(changed)
        self.assertTrue(any("schema error" in item or "theorem-control correction" in item for item in errors))

    def test_gate_5_scope_closure_stops_before_remaining_work(self):
        closure = self.sentinel["scope_closure"]
        self.assertEqual(closure["remaining_candidates_adjudicated"], 0)
        self.assertFalse(closure["denominator_derived"])
        self.assertFalse(closure["baseline_or_coverage_started"])
        self.assertFalse(closure["synthesis_started"])
        self.assertFalse(closure["mutation_or_checker_campaign_started"])
        self.assertFalse(closure["new_source_discovery_performed"])

    def test_actual_gate_6_complete_adjudication_validates(self):
        self.assertEqual(validator.validate_complete_adjudication(check_generated=False), [])
        self.assertEqual(
            self.adjudication["counts"],
            {
                "total_candidates": 15,
                "newly_adjudicated_at_gate6": 13,
                "established": 1,
                "provisional": 14,
                "unresolved": 0,
            },
        )
        self.assertEqual(
            sum(row["stage"] == "GATE_6_REMAINING_COHORT" for row in self.adjudication["decisions"]),
            13,
        )

    def test_gate_6_rejects_candidate_reordering(self):
        changed = copy.deepcopy(self.adjudication)
        changed["decisions"][0], changed["decisions"][1] = (
            changed["decisions"][1],
            changed["decisions"][0],
        )
        errors = validator.validate_complete_adjudication(changed, check_generated=False)
        self.assertTrue(any("preregistered cohort order" in item for item in errors))

    def test_gate_6_reproduces_every_gate_4_claim_disposition(self):
        changed = copy.deepcopy(self.adjudication)
        changed["decisions"][0]["gate4_claim_decision_counts"]["defer"] = 1
        errors = validator.validate_complete_adjudication(changed, check_generated=False)
        self.assertTrue(any("claim-decision counts" in item for item in errors))

    def test_gate_6_cannot_promote_an_unsupported_candidate(self):
        changed = copy.deepcopy(self.adjudication)
        changed["decisions"][0]["authority_status"] = "ESTABLISHED"
        changed["decisions"][0]["qualification_rule"] = "AUTH.NORMATIVE.ESTABLISHED.V1"
        errors = validator.validate_complete_adjudication(changed, check_generated=False)
        self.assertTrue(any("differs from the catalog" in item for item in errors))

    def test_gate_6_scope_closure_stops_before_denominator(self):
        closure = self.adjudication["scope_closure"]
        self.assertFalse(closure["candidate_set_changed"])
        self.assertFalse(closure["new_source_discovery_performed"])
        self.assertFalse(closure["source_approvals_changed"])
        self.assertFalse(closure["denominator_derived"])
        self.assertFalse(closure["baseline_or_coverage_started"])
        self.assertFalse(closure["synthesis_or_checker_work_started"])

    def test_actual_gate_7_denominator_validates(self):
        self.assertEqual(validator.validate_denominator(check_generated=False), [])
        self.assertEqual(
            self.denominator["primary_normative_denominator"],
            {
                "count": 1,
                "coverage_percentage": None,
                "coverage_percentage_status": "NOT_COMPUTED_BEFORE_GATE_8",
                "entry_ids": ["DECL.THEOREM.TYPE_PROP"],
            },
        )
        self.assertEqual(self.denominator["claim_tier"]["id"], "BOUNDED_PILOT")
        self.assertEqual(
            self.denominator["claim_tier"]["represented_semantic_family_ids"],
            ["DECLARATION_EXPRESSION_AND_TYPING_BOUNDARIES"],
        )

    def test_gate_7_is_the_exact_mechanical_derivation(self):
        self.assertEqual(
            self.denominator,
            denominator_deriver.render(self.denominator["recorded_at"]),
        )

    def test_gate_7_rejects_hand_selected_denominator(self):
        changed = copy.deepcopy(self.denominator)
        changed["primary_normative_denominator"]["entry_ids"] = [
            "EXPR.LET.VALUE_TYPE_MATCH"
        ]
        errors = validator.validate_denominator(changed, check_generated=False)
        self.assertTrue(any("exact mechanical derivation" in item for item in errors))

    def test_gate_7_rejects_hand_selected_claim_tier(self):
        changed = copy.deepcopy(self.denominator)
        changed["claim_tier"]["id"] = "NONTRIVIAL_BOUNDED_STUDY"
        errors = validator.validate_denominator(changed, check_generated=False)
        self.assertTrue(any("exact mechanical derivation" in item for item in errors))

    def test_gate_7_preserves_population_separation(self):
        populations = self.denominator["separate_populations"]
        self.assertEqual(
            {
                name: population["count"]
                for name, population in populations.items()
            },
            {
                "provisional_exploratory_candidate_set": 14,
                "unresolved_exploratory_candidate_set": 0,
                "technical_readiness_holdouts": 4,
                "empirical_characterization_context": 8,
                "deferred_or_reserved_identities": 3,
            },
        )

    def test_gate_7_stops_before_gate_8(self):
        closure = self.denominator["scope_closure"]
        self.assertFalse(closure["baseline_or_comparator_started"])
        self.assertFalse(closure["coverage_percentage_computed"])
        self.assertFalse(closure["synthesis_or_checker_work_started"])
        self.assertEqual(
            closure["next_gate"],
            "PUBLICATION_STUDY_GATE_8_BASELINE_AND_COMPARATOR_FREEZE",
        )

    def test_manuscript_is_a_pre_gate_7_presentation_skeleton(self):
        self.assertEqual(validator.validate_manuscript(), [])
        self.assertEqual(
            self.denominator["bindings"]["manuscript_skeleton"]["git_commit"],
            denominator_deriver.MANUSCRIPT_COMMIT,
        )

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
