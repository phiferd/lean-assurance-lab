"""Failure and success regressions for prospective item closure controls."""
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, mock
import json
import subprocess
import tempfile

from lib import closure_controls as cc


def git(root, *args):
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


class CommittedInventoryTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Test")
        git(self.root, "config", "user.email", "test@example.invalid")
        (self.root / "input.txt").write_bytes(b"exact input\n")
        self.scope = "scope.json"
        (self.root / self.scope).write_text(json.dumps({"schema_version": 1,
            "scope": "fixed local test", "paths": ["input.txt"]}) + "\n")
        git(self.root, "add", "input.txt", self.scope)
        git(self.root, "commit", "-qm", "exact inputs")

    def test_exact_committed_bytes_and_scope_file_are_bound(self):
        inventory = cc.committed_inventory(self.root, self.scope)
        self.assertEqual([row["path"] for row in inventory["files"]], ["scope.json", "input.txt"])
        self.assertEqual(inventory["commit"], subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip())
        (self.root / "input.txt").write_bytes(b"changed\n")
        with self.assertRaisesRegex(ValueError, "differs from committed bytes"):
            cc.committed_inventory(self.root, self.scope)

    def test_scope_rebind_and_declared_untracked_file_fail(self):
        doc = json.loads((self.root / self.scope).read_text())
        doc["paths"] = ["other.txt"]
        (self.root / self.scope).write_text(json.dumps(doc) + "\n")
        (self.root / "other.txt").write_text("untracked")
        with self.assertRaisesRegex(ValueError, "git rev-parse|committed bytes"):
            cc.committed_inventory(self.root, self.scope)
        git(self.root, "add", self.scope)
        with self.assertRaisesRegex(ValueError, "committed bytes"):
            cc.committed_inventory(self.root, self.scope)

    def test_missing_declared_file_and_unsafe_path_fail(self):
        (self.root / "input.txt").unlink()
        with self.assertRaisesRegex(ValueError, "absent or unsafe"):
            cc.committed_inventory(self.root, self.scope)
        with self.assertRaisesRegex(ValueError, "repository-relative"):
            cc.committed_inventory(self.root, "../escape.json")

    def test_declared_path_set_must_be_sorted_unique_and_safe(self):
        for paths in (["z.txt", "input.txt"], ["input.txt", "input.txt"],
                      ["../outside.txt"], ["/tmp/outside.txt"]):
            with self.subTest(paths=paths):
                (self.root / self.scope).write_text(json.dumps({"schema_version": 1,
                    "scope": "fixed local test", "paths": paths}) + "\n")
                with self.assertRaisesRegex(ValueError, "sorted, unique repository-relative"):
                    cc.committed_inventory(self.root, self.scope)


class ClosureOrderTests(TestCase):
    def test_host_backend_requires_positive_rss_and_reports_permission(self):
        good = lambda *_a, **_k: SimpleNamespace(returncode=0, stdout=" 123 ", stderr="")
        self.assertEqual(cc.host_rss_preflight(run=good, pid=12)["rss_kib"], 123)
        bad = lambda *_a, **_k: SimpleNamespace(returncode=1, stdout="", stderr="Operation not permitted")
        with self.assertRaisesRegex(ValueError, "enable /bin/ps"):
            cc.host_rss_preflight(run=bad, pid=12)
        with self.assertRaisesRegex(ValueError, "enable /bin/ps"):
            cc.host_rss_preflight(run=lambda *_a, **_k: SimpleNamespace(returncode=0, stdout="0", stderr=""), pid=12)

    def test_denied_preflight_prevents_suite_and_refresh(self):
        with tempfile.TemporaryDirectory() as d, \
             mock.patch.object(cc, "host_rss_preflight", side_effect=ValueError("denied")), \
             mock.patch.object(cc, "_run_logged") as run:
            self.assertEqual(cc.finish(Path(d), "scope.json", Path(d) / "out"), 1)
            run.assert_not_called()
            self.assertEqual(json.loads((Path(d) / "out/result.json").read_text())["status"], "FAILED")

    def test_inventory_failure_prevents_suite_and_refresh(self):
        with tempfile.TemporaryDirectory() as d, \
             mock.patch.object(cc, "host_rss_preflight", return_value={"status": "PASS"}), \
             mock.patch.object(cc, "committed_inventory", side_effect=ValueError("dirty declared input")), \
             mock.patch.object(cc, "_run_logged") as run:
            out = Path(d) / "out"
            self.assertEqual(cc.finish(Path(d), "scope.json", out), 1)
            run.assert_not_called()
            self.assertFalse((out / "validation.json").exists())

    def test_post_suite_input_drift_prevents_validation_and_refresh(self):
        inventories = [{"commit": "a" * 40, "files": []}, {"commit": "b" * 40, "files": []}]
        with tempfile.TemporaryDirectory() as d, \
             mock.patch.object(cc, "host_rss_preflight", return_value={"status": "PASS"}), \
             mock.patch.object(cc, "committed_inventory", side_effect=inventories), \
             mock.patch.object(cc, "_run_logged") as run:
            out = Path(d) / "out"
            def fake_run(root, command, log, **_kwargs):
                log.write_bytes(b"passed\n")
                return 0
            run.side_effect = fake_run
            self.assertEqual(cc.finish(Path(d), "scope.json", out), 1)
            run.assert_called_once()
            self.assertFalse((out / "validation.json").exists())

    def test_refresh_failure_retains_validation_and_stops_final_checks(self):
        inventory = {"commit": "a" * 40, "files": []}
        with tempfile.TemporaryDirectory() as d, \
             mock.patch.object(cc, "host_rss_preflight", return_value={"status": "PASS"}), \
             mock.patch.object(cc, "committed_inventory", return_value=inventory), \
             mock.patch.object(cc, "_run_logged") as run:
            out = Path(d) / "out"
            def fake_run(root, command, log, **_kwargs):
                log.write_bytes(b"attempt\n")
                return 6 if command[0] == "scripts/refresh-current-state" else 0
            run.side_effect = fake_run
            self.assertEqual(cc.finish(Path(d), "scope.json", out), 1)
            self.assertEqual(run.call_count, 2)
            self.assertTrue((out / "validation.json").is_file())
            self.assertEqual(json.loads((out / "result.json").read_text())["status"], "FAILED")

    def test_generation_input_drift_fails_terminal_closure(self):
        before = {"commit": "a" * 40, "files": []}
        changed = {"commit": "a" * 40, "files": [{"path": "canonical", "sha256": "b" * 64}]}
        with tempfile.TemporaryDirectory() as d, \
             mock.patch.object(cc, "host_rss_preflight", return_value={"status": "PASS"}), \
             mock.patch.object(cc, "committed_inventory", side_effect=[before, before, changed]), \
             mock.patch.object(cc, "_run_logged") as run:
            out = Path(d) / "out"
            def fake_run(root, command, log, **_kwargs):
                log.parent.mkdir(parents=True, exist_ok=True)
                log.write_bytes(b"passed\n")
                return 0
            run.side_effect = fake_run
            self.assertEqual(cc.finish(Path(d), "scope.json", out), 1)
            self.assertEqual(json.loads((out / "result.json").read_text())["status"], "FAILED")
            self.assertTrue((out / "validation.json").is_file())

    def test_receipt_write_is_exclusive(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "record.json"
            cc.write_new(target, {"status": "first"})
            with self.assertRaises(FileExistsError):
                cc.write_new(target, {"status": "replacement"})
            self.assertEqual(json.loads(target.read_text()), {"status": "first"})

    def test_validation_is_sealed_before_refresh_then_checks(self):
        inventory = {"schema_version": 1, "scope": "fixed", "scope_file": "scope.json",
                     "commit": "a" * 40, "files": []}
        calls = []
        with tempfile.TemporaryDirectory() as d, \
             mock.patch.object(cc, "host_rss_preflight", return_value={"status": "PASS"}), \
             mock.patch.object(cc, "committed_inventory", return_value=inventory), \
             mock.patch.object(cc, "_run_logged") as run:
            out = Path(d) / "out"
            def fake_run(root, command, log, **_kwargs):
                calls.append(command)
                log.parent.mkdir(parents=True, exist_ok=True)
                log.write_bytes(b"passed\n")
                if command[0] == "scripts/refresh-current-state":
                    self.assertTrue((out / "validation.json").is_file())
                return 0
            run.side_effect = fake_run
            self.assertEqual(cc.finish(Path(d), "scope.json", out), 0)
            self.assertEqual(calls[0], cc.SUITE)
            self.assertEqual(calls[1][0], "scripts/refresh-current-state")
            self.assertEqual(calls[2:], cc.CHECKS)
            self.assertEqual(json.loads((out / "result.json").read_text())["status"], "COMPLETE")
            self.assertEqual(json.loads((out / "validation.json").read_text())["status"], "PASS")

    def test_failed_suite_keeps_log_and_never_refreshes(self):
        inventory = {"schema_version": 1, "scope": "fixed", "scope_file": "scope.json",
                     "commit": "a" * 40, "files": []}
        with tempfile.TemporaryDirectory() as d, \
             mock.patch.object(cc, "host_rss_preflight", return_value={"status": "PASS"}), \
             mock.patch.object(cc, "committed_inventory", return_value=inventory), \
             mock.patch.object(cc, "_run_logged", return_value=7) as run:
            out = Path(d) / "out"
            self.assertEqual(cc.finish(Path(d), "scope.json", out), 1)
            run.assert_called_once()
            self.assertFalse((out / "validation.json").exists())
            self.assertEqual(json.loads((out / "result.json").read_text())["full_suite_returncode"], 7)
