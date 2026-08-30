import copy
import hashlib
import importlib.machinery
import importlib.util
import json
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-declaration-validation-source-lock"
loader = importlib.machinery.SourceFileLoader("declaration_source_lock", str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)


class DeclarationValidationSourceLockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lock = module.load_json(module.LOCK_PATH)
        cls.schema = module.load_json(module.SCHEMA_PATH)
        cls.target = module.load_json(module.TARGET_PATH)
        cls.closure = module.load_json(module.CLOSURE_PATH)
        cls.registry = module.load_json(module.REGISTRY_PATH)

    def errors(self, lock=None, rendered=None):
        candidate = self.lock if lock is None else lock
        synchronized = candidate if rendered is None else rendered
        errors, _ = module.validate_lock(
            candidate,
            self.schema,
            self.target,
            self.closure,
            self.registry,
            rendered_lock=synchronized,
            check_git_tracking=False,
        )
        return errors

    def test_schema_is_valid_and_frozen_lock_passes(self):
        jsonschema.Draft202012Validator.check_schema(self.schema)
        self.assertEqual(self.errors(), [])

    def test_renderer_is_deterministic_and_synchronized(self):
        renderer = module.load_renderer()
        self.assertEqual(renderer.render(), renderer.render())
        self.assertEqual(renderer.render(), self.lock)

    def test_repository_tuple_is_exactly_the_pinned_target_tuple(self):
        actual = {
            (row["repository_url"], row["revision"])
            for row in self.lock["repositories"]
        }
        self.assertEqual(actual, module.expected_repository_keys(self.target))
        self.assertEqual(len(actual), 9)

    def test_every_discovery_source_is_content_bound(self):
        source_ids = {row["id"] for row in self.lock["source_files"]}
        closure_ids = {row["id"] for row in self.closure["sources"]}
        self.assertTrue(closure_ids.issubset(source_ids))
        self.assertEqual(len(closure_ids), 22)

    def test_missing_discovery_source_fails(self):
        lock = copy.deepcopy(self.lock)
        source_id = self.closure["sources"][0]["id"]
        lock["source_files"] = [row for row in lock["source_files"] if row["id"] != source_id]
        self.assertTrue(any("Milestone 4 source is missing" in error for error in self.errors(lock)))

    def test_tracked_evidence_hash_drift_fails(self):
        lock = copy.deepcopy(self.lock)
        lock["tracked_evidence"][0]["file_sha256"] = "0" * 64
        self.assertTrue(any("tracked-evidence hash is stale" in error for error in self.errors(lock)))

    def test_invalid_json_pointer_fails(self):
        lock = copy.deepcopy(self.lock)
        lock["tracked_evidence"][0]["json_pointer_or_case_id"] = ["/does/not/exist"]
        self.assertTrue(any("unresolved JSON locator" in error for error in self.errors(lock)))

    def test_witness_hash_drift_fails(self):
        lock = copy.deepcopy(self.lock)
        lock["generated_witnesses"][0]["artifact_sha256"] = "0" * 64
        self.assertTrue(any("witness hash is stale" in error for error in self.errors(lock)))

    def test_witness_must_reference_a_stable_identity(self):
        lock = copy.deepcopy(self.lock)
        lock["generated_witnesses"][0]["relevant_case_id"] = ["DECL.UNKNOWN.IDENTITY"]
        self.assertTrue(any("unknown stable identity" in error for error in self.errors(lock)))

    def test_witness_origin_must_be_content_bound(self):
        lock = copy.deepcopy(self.lock)
        lock["generated_witnesses"][0]["generator_or_origin"] = "README.md"
        self.assertTrue(any("not content-bound as tracked evidence" in error for error in self.errors(lock)))

    def test_missing_optional_local_observation_does_not_fail(self):
        lock = copy.deepcopy(self.lock)
        lock["optional_local_observations"][0]["path_hint"] = "external/not-present/optional.bin"
        errors, counts = module.validate_lock(
            lock,
            self.schema,
            self.target,
            self.closure,
            self.registry,
            rendered_lock=lock,
            check_git_tracking=False,
        )
        self.assertEqual(errors, [])
        self.assertGreaterEqual(counts["optional_local_missing"], 1)

    def test_absolute_optional_local_path_fails(self):
        lock = copy.deepcopy(self.lock)
        lock["optional_local_observations"][0]["path_hint"] = "/tmp/not-reproducible"
        self.assertTrue(any("unsafe or absolute" in error for error in self.errors(lock)))

    def test_observer_vector_cannot_shrink(self):
        lock = copy.deepcopy(self.lock)
        lock["observer_configurations"].pop()
        self.assertTrue(self.errors(lock))

    def test_observer_configuration_digest_drift_fails(self):
        lock = copy.deepcopy(self.lock)
        lock["observer_configurations"][0]["configuration_sha256"] = "0" * 64
        self.assertTrue(any("configuration digest is stale" in error for error in self.errors(lock)))

    def test_entrypoint_requires_mechanical_locator_tokens(self):
        lock = copy.deepcopy(self.lock)
        entrypoint_id = lock["observer_configurations"][0]["entrypoint_source_file_id"]
        entrypoint = next(row for row in lock["source_files"] if row["id"] == entrypoint_id)
        entrypoint["locator_verification"] = {
            "mode": "HASH_ONLY_DESCRIPTIVE_LOCATOR",
            "tokens": [],
        }
        self.assertTrue(any("entrypoint lacks mechanical token" in error for error in self.errors(lock)))

    def test_absent_normative_and_mechanized_evidence_is_explicit(self):
        for section_name in ("normative_documentation", "mechanized_results"):
            section = self.lock[section_name]
            self.assertEqual(
                section["selection_status"],
                "NONE_SELECTED_BEFORE_CATALOG_AUTHORITY_REVIEW",
            )
            self.assertEqual(section["records"], [])

    def test_no_catalog_or_authority_assignment_crosses_milestone_boundary(self):
        boundary = self.lock["completion_boundary"]
        self.assertFalse(boundary["catalog_entries_created"])
        self.assertFalse(boundary["authority_assigned"])
        self.assertFalse(
            self.lock["validation_modes"]["offline"]["ignored_external_checkout_required"]
        )

    def test_online_verifier_checks_revision_content_and_tokens(self):
        revision = "a" * 40
        content = b"prefix requiredToken suffix\n"
        lock = {
            "repositories": [{
                "id": "REPO.TEST",
                "repository_url": "https://github.com/example/project",
                "revision": revision,
            }],
            "source_files": [{
                "id": "SRC.TEST.FILE",
                "repository_id": "REPO.TEST",
                "path": "src/file.txt",
                "blob_sha256": hashlib.sha256(content).hexdigest(),
                "locator_verification": {"mode": "TOKENS", "tokens": ["requiredToken"]},
            }],
        }

        def fetcher(url):
            if "api.github.com" in url:
                return json.dumps({"sha": revision}).encode()
            return content

        errors, counts = module.verify_online_sources(lock, fetcher=fetcher)
        self.assertEqual(errors, [])
        self.assertEqual(counts["repository_revisions_checked"], 1)
        self.assertEqual(counts["source_files_checked"], 1)
        self.assertEqual(counts["locator_tokens_checked"], 1)

    def test_online_verifier_rejects_wrong_content(self):
        revision = "b" * 40
        lock = {
            "repositories": [{
                "id": "REPO.TEST",
                "repository_url": "https://github.com/example/project",
                "revision": revision,
            }],
            "source_files": [{
                "id": "SRC.TEST.FILE",
                "repository_id": "REPO.TEST",
                "path": "src/file.txt",
                "blob_sha256": "0" * 64,
                "locator_verification": {"mode": "TOKENS", "tokens": ["missingToken"]},
            }],
        }

        def fetcher(url):
            if "api.github.com" in url:
                return json.dumps({"sha": revision}).encode()
            return b"different content"

        errors, _ = module.verify_online_sources(lock, fetcher=fetcher)
        self.assertTrue(any("raw-content SHA-256 mismatch" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
