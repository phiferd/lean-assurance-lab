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


if __name__ == "__main__":
    unittest.main()
