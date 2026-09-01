import copy
import hashlib
import importlib.machinery
import importlib.util
import json
import tempfile
import unittest
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


history = load_module(
    "declaration_history_transition_validator",
    ROOT / "scripts" / "validate-declaration-validation-historical",
)
pilot_validator = load_module(
    "declaration_pilot_transition_validator",
    ROOT / "scripts" / "validate-declaration-validation-milestone-8-pilot",
)


class DeclarationValidationHistoricalTransitionTests(unittest.TestCase):
    def test_m9_current_catalog_transition_leaves_m8_historical_attestation_unchanged(self):
        """A future current catalog cannot redefine the corrected M8 content state."""

        attestation = history.load_json(history.M8_ATTESTATION_PATH)
        before_blobs = {}
        for name in ("catalog", "freeze_manifest", "completion_record"):
            content, errors = history.git_blob_bytes(
                attestation["artifacts"][name],
                label=f"M8 transition before {name}",
                expected_commit=history.M8_COMMIT,
            )
            self.assertEqual(errors, [])
            self.assertIsNotNone(content)
            assert content is not None
            before_blobs[name] = hashlib.sha256(content).hexdigest()

        historical_catalog = json.loads(
            history.git_blob_bytes(
                attestation["artifacts"]["catalog"],
                label="M8 transition catalog",
                expected_commit=history.M8_COMMIT,
            )[0]
        )
        future_catalog = copy.deepcopy(historical_catalog)
        future_catalog["status"] = "MILESTONE_9_PRE_REVIEW_FREEZE"
        future_catalog["completion_boundary"]["next_milestone"] = (
            "MILESTONE_9_ADVERSARIAL_REVIEW"
        )

        with tempfile.TemporaryDirectory() as directory:
            current_catalog = Path(directory) / "declaration-validation-catalog.json"
            current_catalog.write_text(
                json.dumps(future_catalog, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            future_sha = hashlib.sha256(current_catalog.read_bytes()).hexdigest()
            self.assertNotEqual(future_sha, attestation["artifacts"]["catalog"]["sha256"])

            live_catalog = ROOT / "config" / "declaration-validation-catalog.json"
            original_read_text = Path.read_text
            original_read_bytes = Path.read_bytes

            def reject_live_catalog_text(path, *args, **kwargs):
                if path == live_catalog:
                    raise AssertionError("historical validation read the mutable catalog path")
                return original_read_text(path, *args, **kwargs)

            def reject_live_catalog_bytes(path, *args, **kwargs):
                if path == live_catalog:
                    raise AssertionError("historical validation read the mutable catalog path")
                return original_read_bytes(path, *args, **kwargs)

            with mock.patch.object(Path, "read_text", reject_live_catalog_text), mock.patch.object(
                Path, "read_bytes", reject_live_catalog_bytes
            ):
                self.assertEqual(history.validate_m7_attestation(), [])
                self.assertEqual(history.validate_reviewed_m8_pilot(), [])
                self.assertEqual(history.validate_m8_attestation(), [])

        for name, expected_sha in before_blobs.items():
            content, errors = history.git_blob_bytes(
                attestation["artifacts"][name],
                label=f"M8 transition after {name}",
                expected_commit=history.M8_COMMIT,
            )
            self.assertEqual(errors, [])
            self.assertIsNotNone(content)
            assert content is not None
            self.assertEqual(hashlib.sha256(content).hexdigest(), expected_sha)

    def test_m8_historical_attestation_tampering_fails(self):
        attestation = history.load_json(history.M8_ATTESTATION_PATH)

        wrong_blob = copy.deepcopy(attestation)
        wrong_blob["artifacts"]["catalog"]["git_blob"] = "0" * 40
        errors = history.validate_m8_attestation(wrong_blob)
        self.assertTrue(any("blob identity is stale" in item for item in errors))

        wrong_sha = copy.deepcopy(attestation)
        wrong_sha["artifacts"]["catalog"]["sha256"] = "0" * 64
        errors = history.validate_m8_attestation(wrong_sha)
        self.assertTrue(any("SHA-256 is stale" in item for item in errors))

        wrong_commit = copy.deepcopy(attestation)
        wrong_commit["historical_commit"] = "0" * 40
        errors = history.validate_m8_attestation(wrong_commit)
        self.assertTrue(any("attestation commit is incorrect" in item for item in errors))

        wrong_completion_freeze = copy.deepcopy(attestation)
        wrong_completion_freeze["artifacts"]["freeze_manifest"] = copy.deepcopy(
            wrong_completion_freeze["artifacts"]["catalog"]
        )
        errors = history.validate_m8_attestation(wrong_completion_freeze)
        self.assertTrue(errors)

    def test_m8_current_catalog_transition_leaves_historical_attestations_unchanged(self):
        """This would fail when M7 or the reviewed pilot followed config/catalog.json."""

        attestation = history.load_json(history.M7_ATTESTATION_PATH)
        reviewed_context, reviewed_errors = pilot_validator.reviewed_pilot_context()
        self.assertEqual(reviewed_errors, [])
        self.assertIsNotNone(reviewed_context)
        assert reviewed_context is not None
        pilot = reviewed_context["pilot"]
        before_blobs = {}
        for name in ("catalog", "freeze_manifest", "completion_record"):
            content, errors = history.git_blob_bytes(
                attestation["artifacts"][name], label=f"transition before {name}", expected_commit=history.M7_COMMIT
            )
            self.assertEqual(errors, [])
            before_blobs[name] = hashlib.sha256(content).hexdigest()
        pilot_bytes, pilot_errors = history.git_blob_bytes(
            reviewed_context["attestation"]["pilot"],
            label="transition before reviewed pilot",
            expected_commit=pilot_validator.M8_REVIEWED_PILOT_COMMIT,
        )
        self.assertEqual(pilot_errors, [])
        self.assertIsNotNone(pilot_bytes)
        assert pilot_bytes is not None
        before_pilot_sha = hashlib.sha256(pilot_bytes).hexdigest()
        before_catalog_sha = pilot_validator.sha256_file(
            ROOT / "config" / "declaration-validation-catalog.json"
        )

        m8_current = copy.deepcopy(pilot_validator.load_json(ROOT / "config" / "declaration-validation-catalog.json"))
        m8_current["status"] = "MILESTONE_8_CHARACTERIZATION_INVENTORY"
        m8_current["entries"] = copy.deepcopy(pilot["entries"])
        m8_current["site_dispositions"] = copy.deepcopy(pilot["site_dispositions"])
        m8_current["completion_boundary"] = {
            "canonical_data_authoritative": True,
            "generated_report_required": True,
            "inventory_populated": False,
            "authority_assignments_created": False,
            "next_milestone": "MILESTONE_8_REPAIR_REVIEW",
        }

        with tempfile.TemporaryDirectory() as directory:
            transitioned_catalog = Path(directory) / "declaration-validation-catalog.json"
            transitioned_catalog.write_text(
                json.dumps(m8_current, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            after_catalog_sha = pilot_validator.sha256_file(transitioned_catalog)
            self.assertNotEqual(before_catalog_sha, after_catalog_sha)
            self.assertNotEqual(
                attestation["artifacts"]["catalog"]["sha256"], after_catalog_sha
            )

            original_catalog_path = pilot_validator.catalog.CATALOG_PATH
            pilot_validator.catalog.CATALOG_PATH = transitioned_catalog
            try:
                self.assertEqual(history.validate_m7_attestation(), [])
                self.assertEqual(pilot_validator.validate_document(check_generated=False), [])
            finally:
                pilot_validator.catalog.CATALOG_PATH = original_catalog_path

        for name, expected_sha in before_blobs.items():
            content, errors = history.git_blob_bytes(
                attestation["artifacts"][name], label=f"transition after {name}", expected_commit=history.M7_COMMIT
            )
            self.assertEqual(errors, [])
            self.assertEqual(hashlib.sha256(content).hexdigest(), expected_sha)
        pilot_bytes, pilot_errors = history.git_blob_bytes(
            reviewed_context["attestation"]["pilot"],
            label="transition after reviewed pilot",
            expected_commit=pilot_validator.M8_REVIEWED_PILOT_COMMIT,
        )
        self.assertEqual(pilot_errors, [])
        self.assertIsNotNone(pilot_bytes)
        assert pilot_bytes is not None
        self.assertEqual(hashlib.sha256(pilot_bytes).hexdigest(), before_pilot_sha)
        self.assertEqual(
            reviewed_context["attestation"]["pilot"]["sha256"], before_pilot_sha
        )

    def test_mutable_current_pilot_path_cannot_redefine_reviewed_pilot(self):
        """The historical validator must not read config/declaration-validation-milestone-8-pilot.json."""

        reviewed_context, reviewed_errors = pilot_validator.reviewed_pilot_context()
        self.assertEqual(reviewed_errors, [])
        self.assertIsNotNone(reviewed_context)
        assert reviewed_context is not None
        before_pilot_sha = reviewed_context["attestation"]["pilot"]["sha256"]
        mutated_current_pilot = copy.deepcopy(reviewed_context["pilot"])
        mutated_current_pilot["candidate_ids"] = []

        with tempfile.TemporaryDirectory() as directory:
            current_pilot = Path(directory) / "declaration-validation-milestone-8-pilot.json"
            current_pilot.write_text(
                json.dumps(mutated_current_pilot, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            self.assertNotEqual(pilot_validator.sha256_file(current_pilot), before_pilot_sha)
            original_pilot_path = pilot_validator.PILOT_PATH
            pilot_validator.PILOT_PATH = current_pilot
            try:
                self.assertEqual(pilot_validator.validate_document(check_generated=False), [])
            finally:
                pilot_validator.PILOT_PATH = original_pilot_path

        frozen_pilot, frozen_errors = history.git_blob_bytes(
            reviewed_context["attestation"]["pilot"],
            label="current-path replacement reviewed pilot",
            expected_commit=pilot_validator.M8_REVIEWED_PILOT_COMMIT,
        )
        self.assertEqual(frozen_errors, [])
        self.assertIsNotNone(frozen_pilot)
        assert frozen_pilot is not None
        self.assertEqual(hashlib.sha256(frozen_pilot).hexdigest(), before_pilot_sha)

    def test_reviewed_pilot_attestation_tampering_fails(self):
        reviewed_context, reviewed_errors = pilot_validator.reviewed_pilot_context()
        self.assertEqual(reviewed_errors, [])
        self.assertIsNotNone(reviewed_context)
        assert reviewed_context is not None

        wrong_blob = copy.deepcopy(reviewed_context["attestation"])
        wrong_blob["pilot"]["git_blob"] = "0" * 40
        _, errors = pilot_validator.reviewed_pilot_context(wrong_blob)
        self.assertTrue(any("blob identity is stale" in item for item in errors))

        wrong_sha = copy.deepcopy(reviewed_context["attestation"])
        wrong_sha["pilot"]["sha256"] = "0" * 64
        _, errors = pilot_validator.reviewed_pilot_context(wrong_sha)
        self.assertTrue(any("SHA-256 is stale" in item for item in errors))

        wrong_commit = copy.deepcopy(reviewed_context["attestation"])
        wrong_commit["historical_commit"] = "0" * 40
        _, errors = pilot_validator.reviewed_pilot_context(wrong_commit)
        self.assertTrue(any("attestation commit is incorrect" in item for item in errors))

    def test_pilot_rejects_a_mutable_current_catalog_as_its_predecessor(self):
        pilot = pilot_validator.load_json(pilot_validator.PILOT_PATH)
        pilot["predecessor_catalog"] = {
            "attestation_path": "config/declaration-validation-catalog.json",
            "attestation_sha256": "0" * 64,
            "artifact": "catalog",
        }
        errors = pilot_validator.validate_document(pilot, check_generated=False)
        self.assertTrue(any("attestation_path" in item for item in errors))

    def test_historical_m7_uses_its_own_schema_without_later_required_fields(self):
        attestation = history.load_json(history.M7_ATTESTATION_PATH)
        catalog, errors = history.historical_json(
            attestation["artifacts"]["catalog"], label="historical M7 catalog", expected_commit=history.M7_COMMIT
        )
        self.assertEqual(errors, [])
        self.assertNotIn("site_dispositions", catalog)
        self.assertEqual(history.validate_m7_attestation(), [])

    def test_historical_blob_identity_tampering_fails(self):
        attestation = history.load_json(history.M7_ATTESTATION_PATH)
        attestation["artifacts"]["catalog"]["git_blob"] = "0" * 40
        errors = history.validate_m7_attestation(attestation)
        self.assertTrue(any("blob identity is stale" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
