import copy
import hashlib
import importlib.machinery
import importlib.util
import json
import tempfile
import unittest
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
    def test_m8_current_catalog_transition_leaves_historical_attestations_unchanged(self):
        """This would fail when the pilot/M7 validators followed config/catalog.json."""

        attestation = history.load_json(history.M7_ATTESTATION_PATH)
        pilot = pilot_validator.load_json(pilot_validator.PILOT_PATH)
        before_blobs = {}
        for name in ("catalog", "freeze_manifest", "completion_record"):
            content, errors = history.git_blob_bytes(
                attestation["artifacts"][name], label=f"transition before {name}", expected_commit=history.M7_COMMIT
            )
            self.assertEqual(errors, [])
            before_blobs[name] = hashlib.sha256(content).hexdigest()
        before_pilot_sha = pilot_validator.sha256_file(pilot_validator.PILOT_PATH)
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
        self.assertEqual(pilot_validator.sha256_file(pilot_validator.PILOT_PATH), before_pilot_sha)

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
