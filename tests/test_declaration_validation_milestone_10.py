import copy
import hashlib
import importlib.machinery
import importlib.util
import json
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


validator = load_module(
    "declaration_milestone_10_validator",
    ROOT / "scripts" / "validate-declaration-validation-milestone-10",
)
population_renderer = load_module(
    "declaration_milestone_10_population_renderer",
    ROOT / "scripts" / "render-declaration-validation-milestone-10-populations",
)
report_renderer = load_module(
    "declaration_milestone_10_report_renderer",
    ROOT / "scripts" / "render-declaration-validation-milestone-10-study",
)


class DeclarationValidationMilestone10Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = validator.load_json(validator.STUDY_PATH)
        cls.populations = validator.load_json(validator.POPULATIONS_PATH)

    def test_actual_m10_design_validates(self):
        self.assertEqual(validator.validate_document(), [])

    def test_immutable_m9_binding_is_exact(self):
        m9 = self.study["immutable_m9_input"]
        self.assertEqual(
            hashlib.sha256(validator.M9_ATTESTATION_PATH.read_bytes()).hexdigest(),
            m9["attestation_sha256"],
        )
        self.assertEqual(m9["historical_commit"], "69dad9d13e4802e5ef29c958c60d2ee387293847")
        self.assertEqual(m9["reviewed_catalog_binding"]["git_blob"], "f4e7fe07075e3070d740b1cb3e1993b6baef7da0")

    def test_complete_inventory_is_analyzed_without_authority_short_circuit(self):
        self.assertEqual(len(self.study["readiness"]), 30)
        for row in self.study["readiness"]:
            for name in validator.DETERMINATIONS:
                self.assertIn("status", row[name])
                self.assertTrue(row[name]["basis"])
                self.assertTrue(row[name]["evidence"])
                if row[name]["status"] == "YES":
                    self.assertIsNone(row[name]["blocking_reason_if_any"])
                else:
                    self.assertTrue(row[name]["blocking_reason_if_any"])

    def test_primary_denominator_is_empty_without_percentage(self):
        self.assertEqual(
            self.populations["primary_normative_denominator"],
            {
                "count": 0,
                "entry_ids": [],
                "coverage_percentage": None,
                "coverage_percentage_status": "NOT_REPORTED_EMPTY_DENOMINATOR",
            },
        )

    def test_exploratory_and_empirical_populations_remain_separate(self):
        exploratory = self.populations["provisional_exploratory_candidate_set"]
        empirical = self.populations["empirical_characterization_context"]
        self.assertEqual(exploratory["count"], 19)
        self.assertEqual(empirical["count"], 8)
        self.assertTrue(set(exploratory["entry_ids"]).isdisjoint(empirical["entry_ids"]))
        self.assertTrue(all(not row["primary_denominator_eligible"] for row in self.populations["entries"]))

    def test_deferred_and_reserved_identifications_are_closed(self):
        self.assertEqual(
            self.populations["deferred_or_reserved_identities"]["entry_ids"],
            [
                "DECL.SAFETY.SAFE_DEPENDENCY",
                "EXPR.PROJECTION.TYPING",
                "SCENARIO.LITERAL.AVAILABILITY_POLICY",
            ],
        )

    def test_authority_cannot_be_promoted_in_readiness(self):
        changed = copy.deepcopy(self.study)
        changed["readiness"][0]["authority_eligible"] = {
            "status": "YES",
            "basis": "Synthetic mutation that falsely treats provisional authority as established.",
            "evidence": ["M9.CATALOG.0"],
            "blocking_reason_if_any": None,
        }
        errors = validator.validate_document(changed, population_renderer.render(changed), check_generated=False)
        self.assertTrue(any("authority_eligible does not follow immutable M9" in item for item in errors))

    def test_authority_short_circuit_cannot_remove_other_dimensions(self):
        changed = copy.deepcopy(self.study)
        del changed["readiness"][0]["isolation_feasibility"]
        errors = validator.validate_document(changed, self.populations, check_generated=False)
        self.assertTrue(any("schema error" in item and "isolation_feasibility" in item for item in errors))

    def test_evidence_cannot_be_redirected_to_another_identity(self):
        changed = copy.deepcopy(self.study)
        changed["readiness"][0]["study_scope"]["evidence"] = ["M9.CATALOG.1"]
        errors = validator.validate_document(changed, self.populations, check_generated=False)
        self.assertTrue(any("study_scope evidence is attributed" in item for item in errors))

    def test_frozen_classification_cannot_follow_mutable_reinterpretation(self):
        changed = copy.deepcopy(self.study)
        changed["readiness"][0]["frozen_classification"]["authority_status"] = "ESTABLISHED"
        errors = validator.validate_document(changed, self.populations, check_generated=False)
        self.assertTrue(any("frozen classification differs from immutable M9" in item for item in errors))

    def test_derived_populations_are_not_authored_booleans(self):
        changed = copy.deepcopy(self.populations)
        changed["entries"][0]["primary_denominator_eligible"] = True
        changed["entries"][0]["primary_exclusion_reasons"] = []
        changed["primary_normative_denominator"] = {
            "count": 1,
            "entry_ids": [changed["entries"][0]["entry_id"]],
            "coverage_percentage": 0,
            "coverage_percentage_status": "AWAITING_SUCCESSOR_EXECUTION",
        }
        errors = validator.validate_document(self.study, changed, check_generated=False)
        self.assertTrue(any("canonical derivation" in item for item in errors))

    def test_current_catalog_path_is_not_an_eligibility_input(self):
        live_catalog = ROOT / "config" / "declaration-validation-catalog.json"
        original_text = Path.read_text
        original_bytes = Path.read_bytes

        def reject_text(path, *args, **kwargs):
            if path == live_catalog:
                raise AssertionError("M10 read mutable current catalog")
            return original_text(path, *args, **kwargs)

        def reject_bytes(path, *args, **kwargs):
            if path == live_catalog:
                raise AssertionError("M10 read mutable current catalog")
            return original_bytes(path, *args, **kwargs)

        with mock.patch.object(Path, "read_text", reject_text), mock.patch.object(Path, "read_bytes", reject_bytes):
            self.assertEqual(validator.validate_document(check_generated=False), [])

    def test_future_coverage_contract_preserves_reach_and_isolation(self):
        contract = self.study["future_isolated_negative_coverage_contract"]
        self.assertEqual(contract["semantic_obligation"], "Reach(x) AND NOT P(x)")
        self.assertTrue(contract["competing_obligations"]["unresolved_blocks_isolated_coverage"])
        self.assertFalse(contract["authority_scoped_expected_outcome"]["provisional_may_support_normative_rejection"])
        self.assertFalse(self.study["checker_attribution_contract"]["agreement_is_authority"])

    def test_execution_gates_and_prohibitions_stop_m10_before_campaigns(self):
        self.assertEqual(len(self.study["execution_gates"]), 10)
        self.assertTrue(all(gate["failure_effect"] == "BLOCK_SUBSTANTIVE_STUDY_EXECUTION" for gate in self.study["execution_gates"]))
        self.assertIn("NEW_ARENA_TEST_CAMPAIGN", self.study["prohibitions"])
        self.assertIn("AUTHORITY_PROMOTION", self.study["prohibitions"])
        self.assertIn("DENOMINATOR_CRITERION_WEAKENING", self.study["prohibitions"])

    def test_generated_population_and_report_are_synchronized(self):
        self.assertEqual(self.populations, population_renderer.render(self.study))
        self.assertEqual(validator.REPORT_PATH.read_text(encoding="utf-8"), report_renderer.render())


if __name__ == "__main__":
    unittest.main()
