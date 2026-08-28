import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

from contribution_validation import load, sha256_file, validate_catalog, validate_manifest  # noqa: E402


class ContributionWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load(ROOT / "config" / "contribution-types.json")
        cls.catalog_schema = load(ROOT / "schemas" / "contribution-types.schema.json")
        cls.manifest_schema = load(ROOT / "schemas" / "contribution-manifest.schema.json")

    def manifest(self, contribution_type):
        row = next(item for item in self.catalog["contribution_types"] if item["id"] == contribution_type)
        artifact = {"path": "README.md", "sha256": sha256_file(ROOT / "README.md"), "role": "example"}
        result = {
            "path": "results/assurance/current.json",
            "sha256": sha256_file(ROOT / "results" / "assurance" / "current.json"),
            "role": "mechanical result",
        }
        return {
            "schema_version": 1,
            "contribution_type": contribution_type,
            "title": "Validation fixture",
            "summary": "Exercises the metadata contract.",
            "scope": {
                "exact_revisions": {"repository": "fixture"},
                "configurations": ["fixture"],
                "assumptions": ["fixture"],
                "non_claims": ["not an assurance claim"],
            },
            "artifacts": [artifact],
            "evidence": [{"command": "fixture", "result": result, "mechanical_condition": "result exists"}],
            "unresolved_states": ["fixture only"],
            "type_metadata": {name: "fixture" for name in row["required_type_metadata"]},
        }

    def test_catalog_is_valid_and_has_all_seven_paths(self):
        self.assertEqual(validate_catalog(self.catalog, self.catalog_schema), [])
        self.assertEqual(
            {row["id"] for row in self.catalog["contribution_types"]},
            {"validator", "corpus-test", "mutation-operator", "witness-generator", "report", "bug-investigation", "documentation"},
        )

    def test_every_contribution_type_has_a_valid_manifest_contract(self):
        for row in self.catalog["contribution_types"]:
            with self.subTest(contribution_type=row["id"]):
                self.assertEqual(
                    validate_manifest(ROOT, self.manifest(row["id"]), self.manifest_schema, self.catalog),
                    [],
                )

    def test_missing_type_metadata_is_rejected(self):
        manifest = self.manifest("validator")
        manifest["type_metadata"].pop("source_revision")
        errors = validate_manifest(ROOT, manifest, self.manifest_schema, self.catalog)
        self.assertTrue(any("source_revision" in error for error in errors))

    def test_stale_artifact_hash_is_rejected(self):
        manifest = copy.deepcopy(self.manifest("documentation"))
        manifest["artifacts"][0]["sha256"] = "0" * 64
        errors = validate_manifest(ROOT, manifest, self.manifest_schema, self.catalog)
        self.assertTrue(any("hash mismatch" in error for error in errors))

    def test_empty_required_type_metadata_is_rejected(self):
        manifest = self.manifest("validator")
        manifest["type_metadata"]["source_revision"] = ""
        errors = validate_manifest(ROOT, manifest, self.manifest_schema, self.catalog)
        self.assertTrue(any("source_revision" in error for error in errors))

    def test_bound_files_cannot_escape_repository(self):
        manifest = self.manifest("documentation")
        manifest["artifacts"][0]["path"] = "../outside.json"
        errors = validate_manifest(ROOT, manifest, self.manifest_schema, self.catalog)
        self.assertTrue(any("does not match" in error or "outside repository" in error for error in errors))

    def test_bug_investigations_require_action_and_authorization_metadata(self):
        row = next(item for item in self.catalog["contribution_types"] if item["id"] == "bug-investigation")
        self.assertTrue(
            {"recommended_action", "recommendation_status", "human_authorization_status"}
            <= set(row["required_type_metadata"])
        )


if __name__ == "__main__":
    unittest.main()
