import copy
import importlib.machinery
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-declaration-validation-milestone-8-pilot"


def load_module(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


module = load_module("declaration_m8_pilot_validator_test", SCRIPT)


class DeclarationValidationMilestone8PilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pilot = module.load_json(module.PILOT_PATH)

    def test_pilot_passes_full_validation(self):
        self.assertEqual(module.validate_document(), [])

    def test_selection_must_remain_the_authorized_five_entries(self):
        pilot = copy.deepcopy(self.pilot)
        pilot["candidate_ids"][0] = "DECL.TYPE.NO_FREE_VARS"
        errors = module.validate_document(pilot, check_generated=False)
        self.assertTrue(any("authorized five-entry batch" in item for item in errors))

    def test_concrete_outcome_must_resolve_to_its_checker_result_bytes(self):
        pilot = copy.deepcopy(self.pilot)
        observation = pilot["entries"][0]["observer_vector"][0]
        observation["outcome"] = "ACCEPT"
        errors = module.validate_document(pilot, check_generated=False)
        self.assertTrue(any("profile/outcome-bound checker evidence" in item for item in errors))

    def test_pilot_entries_cannot_be_promoted_to_established_authority(self):
        pilot = copy.deepcopy(self.pilot)
        pilot["entries"][0]["characterization"]["authority"]["status"] = "ESTABLISHED"
        errors = module.validate_document(pilot, check_generated=False)
        self.assertTrue(any("must remain PROVISIONAL" in item for item in errors))

    def test_existing_lab_witness_cannot_be_promoted_to_isolation(self):
        pilot = copy.deepcopy(self.pilot)
        witness = next(
            item
            for item in pilot["entries"][0]["characterization"]["evidence"]
            if item["id"] == "EVID.M8.THEOREM.WITNESS"
        )
        witness["role"] = "ISOLATION"
        errors = module.validate_document(pilot, check_generated=False)
        self.assertTrue(any("EXISTING_LAB_EVIDENCE_ONLY artifact cannot by itself serve as ISOLATION" in item for item in errors))

    def test_checker_disagreement_may_not_be_modeled_as_authority_contradiction(self):
        pilot = copy.deepcopy(self.pilot)
        disagreement = next(
            item
            for item in pilot["entries"][1]["characterization"]["evidence"]
            if item["id"] == "EVID.M8.SELF_REFERENCE.KIOTA"
        )
        disagreement["role"] = "CONTRADICTION"
        disagreement["claim_supported"]["entry_json_pointer"] = "/authority"
        errors = module.validate_document(pilot, check_generated=False)
        self.assertTrue(any("CONTRADICTION requires a qualified normative interpretation source" in item for item in errors))

    def test_omitted_frozen_m4_site_fails_closure(self):
        pilot = copy.deepcopy(self.pilot)
        pilot["site_dispositions"].pop()
        errors = module.validate_document(pilot, check_generated=False)
        self.assertTrue(any("site-disposition closure omits frozen M4 site pairs" in item for item in errors))

    def test_observed_absence_is_a_valid_non_enforcement_disposition(self):
        pilot = copy.deepcopy(self.pilot)
        absence = next(
            item
            for item in pilot["site_dispositions"]
            if item["site_id"] == "SITE.KIOTA.LEVEL.NO_OWNERSHIP_CONTEXT"
        )
        absence["evidence_refs"] = []
        errors = module.validate_document(pilot, check_generated=False)
        self.assertFalse(any("NO_OWNERSHIP_CONTEXT" in item for item in errors))

    def test_arena_disposition_cannot_be_silent(self):
        pilot = copy.deepcopy(self.pilot)
        del pilot["entries"][0]["arena_disposition"]
        errors = module.validate_document(pilot, check_generated=False)
        self.assertTrue(any("arena_disposition" in item for item in errors))

    def test_historical_pilot_uses_its_bound_registry_snapshot(self):
        original = module.catalog.APPROVED_AUTHORITY_SOURCES_PATH
        module.catalog.APPROVED_AUTHORITY_SOURCES_PATH = ROOT / "config" / "mutable-current-registry.json"
        try:
            errors = module.validate_document(copy.deepcopy(self.pilot), check_generated=False)
        finally:
            module.catalog.APPROVED_AUTHORITY_SOURCES_PATH = original
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
