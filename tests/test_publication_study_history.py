import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("publication_study_history", ROOT / "scripts" / "publication_study_history.py")
history = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(history)


class PublicationStudyHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name, "repo")
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Test")
        self.write("artifacts/result.json", '{"result":"old"}\n')
        self.write("scripts/validator.py", "#!/usr/bin/env python3\nimport json, pathlib, sys\nassert sys.argv[1:] == ['--content-only']\nassert json.loads(pathlib.Path('artifacts/result.json').read_text())['result'] == 'old'\n")
        self.commit("content")
        self.content_commit = self.head()
        manifest = {
            "schema_version": 1,
            "artifact_type": "PUBLICATION_STUDY_CONTENT_MANIFEST",
            "files": [
                self.file_record("artifacts/result.json"),
                self.file_record("scripts/validator.py"),
            ],
        }
        self.write("results/content-manifest.json", json.dumps(manifest, sort_keys=True) + "\n")
        self.commit("manifest")
        self.freeze_commit = self.head()
        # A two-phase freeze binds manifest and all content at the manifest commit.
        self.attestation = history.make_attestation(self.repo, self.freeze_commit, "results/content-manifest.json")

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, check=True, stdout=subprocess.PIPE).stdout

    def head(self):
        return self.git("rev-parse", "HEAD").decode().strip()

    def write(self, path, content):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "-qm", message)

    def file_record(self, path):
        content = (self.repo / path).read_bytes()
        return {"path": path, "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)}

    def validate(self, attestation=None):
        return history.validate_historical(
            self.repo, attestation or self.attestation, "results/content-manifest.json", "scripts/validator.py", ["--content-only"]
        )

    def test_old_snapshot_validates_after_live_content_and_validator_change(self):
        self.write("artifacts/result.json", '{"result":"new"}\n')
        self.write("scripts/validator.py", "raise SystemExit('mutable validator must not run')\n")
        self.write("schemas/current.json", '{"future": true}\n')
        self.commit("later mutable successor")
        self.assertEqual(self.validate(), [])

    def test_git_binding_requires_full_exact_commit(self):
        with self.assertRaises(ValueError):
            history.git_binding(self.repo, self.freeze_commit[:12], "artifacts/result.json")
        binding = history.git_binding(self.repo, self.freeze_commit, "artifacts/result.json")
        self.assertEqual(binding["git_commit"], self.freeze_commit)

    def test_tampered_manifest_blob_commit_and_artifact_fail_before_execution(self):
        tampered = copy.deepcopy(self.attestation)
        tampered["manifest"]["git_blob"] = "0" * 40
        self.assertTrue(any("blob identity" in item for item in self.validate(tampered)))
        tampered = copy.deepcopy(self.attestation)
        tampered["historical_commit"] = "0" * 40
        self.assertTrue(any("unavailable" in item for item in self.validate(tampered)))
        tampered = copy.deepcopy(self.attestation)
        tampered["artifacts"][1]["sha256"] = "0" * 64
        self.assertTrue(any("SHA-256" in item for item in self.validate(tampered)))
        tampered = copy.deepcopy(self.attestation)
        tampered["artifacts"][1]["git_commit"] = self.content_commit
        self.assertTrue(any("differs from historical" in item for item in self.validate(tampered)))

    def test_omitted_or_changed_artifact_and_unbound_validator_are_rejected(self):
        omitted = copy.deepcopy(self.attestation)
        omitted["artifacts"].pop()
        self.assertTrue(any("exactly match" in item for item in self.validate(omitted)))
        changed = copy.deepcopy(self.attestation)
        changed["artifacts"][0]["path"] = "other.json"
        self.assertTrue(self.validate(changed))
        self.assertTrue(any("not bound" in item for item in history.validate_historical(
            self.repo, self.attestation, "results/content-manifest.json", "scripts/not-bound.py", ["--content-only"]
        )))

    def test_invalid_manifest_is_rejected_by_attestation_creation(self):
        bad = {
            "schema_version": 1,
            "artifact_type": "PUBLICATION_STUDY_CONTENT_MANIFEST",
            "files": [self.file_record("artifacts/result.json"), self.file_record("artifacts/result.json")],
        }
        self.write("results/bad.json", json.dumps(bad))
        self.commit("bad manifest")
        with self.assertRaises(ValueError):
            history.make_attestation(self.repo, self.head(), "results/bad.json")


if __name__ == "__main__":
    unittest.main()
