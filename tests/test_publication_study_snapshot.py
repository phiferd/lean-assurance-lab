import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


snapshot = load_module("publication_study_snapshot", ROOT / "scripts" / "publication_study_snapshot.py")
history = load_module("publication_study_snapshot_history_test", ROOT / "scripts" / "publication_study_history.py")


class PublicationStudySnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name, "repo")
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Test")
        self.write("tracked/input.txt", "frozen input\n")
        self.write("scripts/publication_study_closure.py", "print('frozen validator')\n")
        self.write("scripts/publication_study_history.py", (ROOT / "scripts/publication_study_history.py").read_text())
        self.commit("content")
        manifest = {
            "schema_version": 1,
            "artifact_type": "PUBLICATION_STUDY_CONTENT_MANIFEST",
            "files": [self.record("scripts/publication_study_closure.py"), self.record("tracked/input.txt")],
        }
        self.write(snapshot.MANIFEST_PATH, json.dumps(manifest, sort_keys=True) + "\n")
        self.commit("manifest")
        attestation = history.make_attestation(self.repo, self.head(), snapshot.MANIFEST_PATH)
        self.attestation_bytes = json.dumps(attestation, sort_keys=True).encode() + b"\n"
        attestation_path = self.repo / snapshot.ATTESTATION_PATH
        attestation_path.parent.mkdir(parents=True, exist_ok=True)
        attestation_path.write_bytes(self.attestation_bytes)
        (self.repo / "external").mkdir()
        self.write("external/payload.txt", "payload\n")
        (self.repo / "results" / "coverage").mkdir(parents=True)
        self.write("results/coverage/coverage.txt", "coverage\n")

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, check=True, stdout=subprocess.PIPE).stdout

    def head(self):
        return self.git("rev-parse", "HEAD").decode().strip()

    def write(self, path, text):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def record(self, path):
        content = (self.repo / path).read_bytes()
        return {"path": path, "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)}

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "-qm", message)

    def test_attaches_only_ignored_payload_and_preserves_snapshot_inputs(self):
        original_head = self.head()
        with mock.patch.object(snapshot, "_load_history", return_value=history), mock.patch.object(
            history, "validate_historical", return_value=[]
        ):
            with snapshot.materialized_study(self.repo, attach_payload=True, include_attestation=True) as materialized:
                self.assertEqual((materialized / "tracked/input.txt").read_text(), "frozen input\n")
                self.assertTrue((materialized / "external").is_symlink())
                self.assertTrue((materialized / "results/coverage").is_symlink())
                self.assertEqual((materialized / snapshot.ATTESTATION_PATH).read_bytes(), self.attestation_bytes)
                self.assertEqual(
                    (materialized / ".git").read_text(),
                    f"gitdir: {(self.repo / '.git').resolve()}\n",
                )
                git = subprocess.run(
                    ["git", "rev-parse", "--is-inside-work-tree"], cwd=materialized,
                    env=snapshot.subprocess_env(), check=True, stdout=subprocess.PIPE, text=True,
                )
                self.assertEqual(git.stdout.strip(), "true")
                with tempfile.TemporaryDirectory() as clone_directory:
                    clone = Path(clone_directory, "clone")
                    subprocess.run(
                        ["git", "clone", "--local", "--no-hardlinks", str(materialized), str(clone)],
                        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    )
                    (clone / "successor.txt").write_text("successor only\n")
                    subprocess.run(["git", "add", "successor.txt"], cwd=clone, check=True)
                    subprocess.run(
                        ["git", "-c", "user.name=Snapshot Test", "-c", "user.email=test@example.invalid",
                         "commit", "-qm", "successor commit"],
                        cwd=clone, check=True,
                    )
                    self.assertNotEqual(
                        subprocess.run(["git", "rev-parse", "HEAD"], cwd=clone, check=True,
                                       stdout=subprocess.PIPE, text=True).stdout.strip(),
                        original_head,
                    )
                    self.assertEqual(self.head(), original_head)
        self.assertFalse(materialized.exists())

    def test_refuses_link_when_historical_tree_owns_payload_prefix(self):
        self.git("add", "external/payload.txt")
        self.git("commit", "-qm", "tracked external input")
        attestation = history.make_attestation(self.repo, self.head(), snapshot.MANIFEST_PATH)
        self.write(snapshot.ATTESTATION_PATH, json.dumps(attestation, sort_keys=True) + "\n")
        with mock.patch.object(snapshot, "_load_history", return_value=history), mock.patch.object(
            history, "validate_historical", return_value=[]
        ):
            with self.assertRaisesRegex(ValueError, "tracked historical path: external"):
                with snapshot.materialized_study(self.repo, attach_payload=True):
                    pass

    def test_refuses_attestation_overwrite_of_an_archived_path(self):
        self.git("add", snapshot.ATTESTATION_PATH)
        self.git("commit", "-qm", "tracked stale attestation path")
        forged = json.loads(self.attestation_bytes)
        forged["historical_commit"] = self.head()
        self.write(snapshot.ATTESTATION_PATH, json.dumps(forged, sort_keys=True) + "\n")
        with mock.patch.object(snapshot, "_load_history", return_value=history), mock.patch.object(
            history, "validate_historical", return_value=[]
        ):
            with self.assertRaisesRegex(ValueError, "overwrite an archived path"):
                with snapshot.materialized_study(self.repo, attach_payload=False, include_attestation=True):
                    pass

    def test_real_bound_validator_rejects_a_tampered_artifact_binding(self):
        attestation = json.loads((ROOT / snapshot.ATTESTATION_PATH).read_bytes())
        attestation["artifacts"][0]["sha256"] = "0" * 64
        errors = history.validate_historical(
            ROOT, attestation, snapshot.MANIFEST_PATH, snapshot.VALIDATOR_PATH, snapshot.VALIDATOR_ARGS
        )
        self.assertTrue(any("SHA-256 is stale" in error for error in errors), errors)

    def test_loads_historical_helper_bytes_instead_of_live_helper(self):
        frozen = snapshot._load_history(self.repo, self.head())
        self.assertEqual(frozen._ATTESTATION_TYPE, "PUBLICATION_STUDY_HISTORICAL_ATTESTATION")
        self.write("scripts/publication_study_history.py", "raise RuntimeError('live successor')\n")
        still_frozen = snapshot._load_history(self.repo, self.head())
        self.assertEqual(still_frozen._MANIFEST_TYPE, "PUBLICATION_STUDY_CONTENT_MANIFEST")

    def test_subprocess_environment_does_not_leak_git_overrides(self):
        with mock.patch.dict("os.environ", {"GIT_DIR": "bad", "GIT_WORK_TREE": "bad", "GIT_INDEX_FILE": "bad"}, clear=False):
            environment = snapshot.subprocess_env()
        self.assertNotIn("GIT_DIR", environment)
        self.assertNotIn("GIT_WORK_TREE", environment)
        self.assertNotIn("GIT_INDEX_FILE", environment)
        self.assertEqual(environment["PYTHONDONTWRITEBYTECODE"], "1")


if __name__ == "__main__":
    unittest.main()
