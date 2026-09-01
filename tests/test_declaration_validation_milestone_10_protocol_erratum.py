import copy
import hashlib
import importlib.machinery
import importlib.util
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
    "declaration_milestone_10_protocol_erratum_validator",
    ROOT / "scripts" / "validate-declaration-validation-milestone-10-protocol-erratum",
)
renderer = load_module(
    "declaration_milestone_10_protocol_erratum_renderer",
    ROOT / "scripts" / "render-declaration-validation-milestone-10-protocol-erratum",
)


class DeclarationValidationMilestone10ProtocolErratumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = validator.load_json(validator.ERRATUM_PATH)

    def test_actual_erratum_validates(self):
        self.assertEqual(validator.validate_document(), [])

    def test_correction_is_prop_valued_theorem_with_matching_proof(self):
        correction = self.document["operative_protocol_correction"]
        self.assertEqual(correction["entry_id"], "DECL.THEOREM.TYPE_PROP")
        self.assertEqual(
            correction["corrected_value"],
            "Use a Prop-valued theorem in the same construction family, with a matching valid proof.",
        )

    def test_definition_form_is_auxiliary_not_matched_positive_control(self):
        auxiliary = self.document["auxiliary_control_classification"]
        self.assertEqual(
            auxiliary["allowed_role"],
            "AUXILIARY_REPRESENTABILITY_AND_WELL_FORMEDNESS_CONTROL",
        )
        self.assertEqual(
            auxiliary["prohibited_role"],
            "MATCHED_POSITIVE_CONTROL_FOR_ISOLATED_DECL.THEOREM.TYPE_PROP_COVERAGE",
        )

    def test_immutable_m10_artifacts_remain_exact(self):
        history = validator.load_module("erratum_test_history", validator.HISTORICAL_VALIDATOR_PATH)
        attestation = validator.load_json(history.M10_ATTESTATION_PATH)
        self.assertEqual(history.validate_m10_attestation(), [])
        for name, path in validator.FROZEN_M10_CURRENT_PATHS.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                attestation["artifacts"][name]["sha256"],
            )

    def test_wrong_target_pointer_is_rejected(self):
        changed = copy.deepcopy(self.document)
        changed["operative_protocol_correction"]["target_json_pointer"] = (
            "/readiness/12/future_witness_strategy/positive_control"
        )
        errors = validator.validate_document(changed, check_generated=False)
        self.assertTrue(any("schema error" in item or "does not identify" in item for item in errors))

    def test_definition_form_cannot_be_reintroduced_as_matched_control(self):
        changed = copy.deepcopy(self.document)
        changed["operative_protocol_correction"]["corrected_value"] = (
            "Use the matched definition-form artifact."
        )
        errors = validator.validate_document(changed, check_generated=False)
        self.assertTrue(any("schema error" in item or "required Prop-valued theorem" in item for item in errors))

    def test_erratum_does_not_authorize_successor_execution(self):
        self.assertFalse(self.document["successor_execution_requirement"]["execution_authorized"])
        self.assertFalse(self.document["impact"]["successor_experiment_authorized"])
        self.assertTrue(self.document["impact"]["m10_stop_condition_unchanged"])

    def test_generated_report_is_synchronized(self):
        self.assertEqual(
            validator.REPORT_PATH.read_text(encoding="utf-8"),
            renderer.render(self.document),
        )

    @unittest.skipUnless(validator.ERRATUM_COMMIT, "Phase-B erratum attestation not created yet")
    def test_historical_attestation_validates_without_live_erratum(self):
        live_paths = {validator.ERRATUM_PATH, validator.REPORT_PATH}
        original_text = Path.read_text
        original_bytes = Path.read_bytes

        def reject_text(path, *args, **kwargs):
            if path in live_paths:
                raise AssertionError("historical erratum validation read mutable current content")
            return original_text(path, *args, **kwargs)

        def reject_bytes(path, *args, **kwargs):
            if path in live_paths:
                raise AssertionError("historical erratum validation read mutable current content")
            return original_bytes(path, *args, **kwargs)

        with mock.patch.object(Path, "read_text", reject_text), mock.patch.object(Path, "read_bytes", reject_bytes):
            self.assertEqual(validator.validate_historical_attestation(), [])

    @unittest.skipUnless(validator.ERRATUM_COMMIT, "Phase-B erratum attestation not created yet")
    def test_historical_attestation_tampering_fails(self):
        attestation = validator.load_json(validator.ATTESTATION_PATH)

        wrong_blob = copy.deepcopy(attestation)
        wrong_blob["artifacts"]["protocol_erratum"]["git_blob"] = "0" * 40
        self.assertTrue(any(
            "blob identity is stale" in item
            for item in validator.validate_historical_attestation(wrong_blob)
        ))

        wrong_sha = copy.deepcopy(attestation)
        wrong_sha["artifacts"]["protocol_erratum"]["sha256"] = "0" * 64
        self.assertTrue(any(
            "SHA-256 is stale" in item
            for item in validator.validate_historical_attestation(wrong_sha)
        ))

        wrong_commit = copy.deepcopy(attestation)
        wrong_commit["historical_commit"] = "0" * 40
        self.assertTrue(any(
            "historical commit is incorrect" in item
            for item in validator.validate_historical_attestation(wrong_commit)
        ))


if __name__ == "__main__":
    unittest.main()
