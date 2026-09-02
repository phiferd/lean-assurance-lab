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
        cls.schema = validator.load_json(validator.SCHEMA_PATH)

    def test_schema_is_valid_draft_2020_12(self):
        jsonschema.Draft202012Validator.check_schema(self.schema)

    def test_actual_preregistration_validates(self):
        self.assertEqual(validator.validate_preregistration(), [])

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
