"""Failure and success regressions for prospective item closure controls."""
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, mock
import hashlib
import json
import subprocess
import tempfile

from lib import closure_controls_v2 as cc
ROOT = cc.ROOT


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
        git(self.root, "config", "gc.auto", "0")
        git(self.root, "config", "maintenance.auto", "false")
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

    def test_v2_requires_complete_named_stage_dependencies(self):
        value = {"schema_version": 2, "scope": "fixed local test", "paths": ["input.txt"],
                 "stage_dependencies": {"status": ["input.txt"], "suite": ["input.txt"],
                                        "publication": ["input.txt"]}}
        (self.root / self.scope).write_text(json.dumps(value) + "\n")
        git(self.root, "add", self.scope)
        git(self.root, "commit", "-qm", "stage dependencies")
        inventory = cc.committed_inventory(self.root, self.scope)
        self.assertEqual(cc.dependency_inventory(inventory, "suite")["files"][1]["path"],
                         "input.txt")
        value["stage_dependencies"]["publication"] = []
        (self.root / self.scope).write_text(json.dumps(value) + "\n")
        with self.assertRaisesRegex(ValueError, "publication stage dependencies"):
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

    def test_status_preflight_failure_prevents_expensive_suite(self):
        inventory = {"commit": "a" * 40, "files": []}
        with tempfile.TemporaryDirectory() as d, \
             mock.patch.object(cc, "host_rss_preflight", return_value={"status": "PASS"}), \
             mock.patch.object(cc, "committed_inventory", return_value=inventory), \
             mock.patch.object(cc, "_run_logged", return_value=4) as run:
            out = Path(d) / "out"
            self.assertEqual(cc.finish(Path(d), "scope.json", out), 1)
            self.assertEqual(run.call_args.args[1], cc.STATUS_PREFLIGHT)
            run.assert_called_once()
            self.assertFalse((out / "full-suite.log").exists())
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
            self.assertEqual(run.call_count, 2)
            self.assertEqual(run.call_args.args[1], cc.SUITE)
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
            self.assertEqual(run.call_count, 3)
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
            self.assertEqual(calls[0], cc.STATUS_PREFLIGHT)
            self.assertEqual(calls[1], cc.SUITE)
            self.assertEqual(calls[2][0], "scripts/refresh-current-state")
            self.assertEqual(calls[3:], cc.CHECKS)
            self.assertEqual(json.loads((out / "result.json").read_text())["status"], "COMPLETE")
            self.assertEqual(json.loads((out / "validation.json").read_text())["status"], "PASS")

    def test_failed_suite_keeps_log_and_never_refreshes(self):
        inventory = {"schema_version": 1, "scope": "fixed", "scope_file": "scope.json",
                     "commit": "a" * 40, "files": []}
        with tempfile.TemporaryDirectory() as d, \
             mock.patch.object(cc, "host_rss_preflight", return_value={"status": "PASS"}), \
             mock.patch.object(cc, "committed_inventory", return_value=inventory), \
             mock.patch.object(cc, "_run_logged", side_effect=[0, 7]) as run:
            out = Path(d) / "out"
            self.assertEqual(cc.finish(Path(d), "scope.json", out), 1)
            self.assertEqual(run.call_count, 2)
            self.assertEqual(run.call_args.args[1], cc.SUITE)
            self.assertFalse((out / "validation.json").exists())
            self.assertEqual(json.loads((out / "result.json").read_text())["full_suite_returncode"], 7)


class FailedAttemptBindingTests(TestCase):
    def test_r1_failure_remains_bound_to_original_committed_inputs(self):
        base = ROOT / "results/research/workflow-closure-automation-1"
        repair = json.loads((base / "repair-r2.json").read_text())
        for ref in repair["failed_attempt"].values():
            with self.subTest(path=ref["path"]):
                raw = (ROOT / ref["path"]).read_bytes()
                self.assertEqual(len(raw), ref["bytes"])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), ref["sha256"])
        attempt = base / "final-closure-20260927-1"
        result = json.loads((attempt / "result.json").read_text())
        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(result["full_suite_returncode"], 1)
        self.assertFalse((attempt / "validation.json").exists())
        self.assertFalse((attempt / "refresh").exists())
        inventory = json.loads((attempt / "input-inventory.json").read_text())
        self.assertEqual(inventory["commit"], "1972a55f59458e9443507a1de824d4013ebd5819")
        for row in inventory["files"]:
            with self.subTest(input=row["path"]):
                committed = subprocess.check_output(
                    ["git", "show", inventory["commit"] + ":" + row["path"]], cwd=ROOT)
                self.assertEqual(len(committed), row["bytes"])
                self.assertEqual(hashlib.sha256(committed).hexdigest(), row["sha256"])
                blob = subprocess.check_output(
                    ["git", "rev-parse", inventory["commit"] + ":" + row["path"]],
                    cwd=ROOT, text=True).strip()
                self.assertEqual(blob, row["git_blob"])


class ResumableClosureTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Test")
        git(self.root, "config", "user.email", "test@example.invalid")
        git(self.root, "config", "gc.auto", "0")
        git(self.root, "config", "maintenance.auto", "false")
        (self.root / "input.txt").write_text("stable\n")
        self.scope = "scope.json"
        (self.root / self.scope).write_text(json.dumps({"schema_version": 1,
            "scope": "resumable fixture", "paths": ["input.txt"]}) + "\n")
        git(self.root, "add", "input.txt", self.scope)
        git(self.root, "commit", "-qm", "fixture")
        self.output = self.root / "results/workflow-validation/closure"

    def fake_run(self, calls, interrupt_suite=False, suite_action=None):
        interrupted = {"done": False}

        def run(command_root, command, log, **kwargs):
            calls.append(command)
            log.parent.mkdir(parents=True, exist_ok=True)
            log.write_text("passed\n")
            if command[0] == "suite" and interrupt_suite and not interrupted["done"]:
                interrupted["done"] = True
                raise KeyboardInterrupt()
            if command[0] == "suite" and suite_action is not None:
                suite_action(command_root)
            env = kwargs.get("env")
            if command[0] == "suite" and env:
                receipt_dir = Path(env["METAMORPHIC_SUPERVISOR_RECEIPT_DIR"])
                self.assertTrue(receipt_dir.is_relative_to(self.output / "stages/03-full-suite"))
                self.assertFalse(receipt_dir.is_relative_to(self.root / "results/research"))
                receipt_dir.mkdir(parents=True)
                (receipt_dir / "fixture.receipt.json").write_text("{}\n")
            if command[0] == "refresh":
                refresh_dir = Path(command[2])
                refresh_dir.mkdir(parents=True)
                (refresh_dir / "result.json").write_text("{}\n")
            return 0

        return run

    def controls(self, calls, *, interrupt_suite=False, suite_action=None):
        return (
            mock.patch.object(cc, "STATUS_PREFLIGHT", ["status"]),
            mock.patch.object(cc, "SUITE", ["suite"]),
            mock.patch.object(cc, "CHECKS", [["check-a"], ["check-b"]]),
            mock.patch.object(cc, "host_rss_preflight",
                              return_value={"status": "PASS", "rss_kib": 1}),
            mock.patch.object(cc, "_command_identity",
                              side_effect=lambda _root, command: {"command": command,
                                                                  "tool": command[0]}),
            mock.patch.object(cc, "_worktree_digest", return_value="0" * 64),
            mock.patch.object(cc, "_run_logged",
                              side_effect=self.fake_run(calls, interrupt_suite, suite_action)),
        )

    def test_repository_owner_is_exclusive_and_os_released(self):
        with cc.closure_owner(self.root):
            with self.assertRaisesRegex(ValueError, "another closure owner"):
                with cc.closure_owner(self.root):
                    pass
        with cc.closure_owner(self.root):
            pass

    def test_successful_resume_reuses_every_exact_stage_and_isolates_receipts(self):
        calls = []
        patches = self.controls(calls)
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
            self.assertEqual(cc.finish_resumable(self.root, self.scope, self.output), 0)
            first_count = len(calls)
            self.assertGreater(first_count, 0)
            self.assertEqual(cc.finish_resumable(self.root, self.scope, self.output), 0)
        self.assertEqual(len(calls), first_count)
        second = json.loads((self.output / "attempts/0002/result.json").read_text())
        self.assertEqual(second["status"], "COMPLETE")
        self.assertEqual(second["executed_stages"], [])
        self.assertIn("03-full-suite", second["reused_stages"])
        self.assertTrue((self.output / "stages/03-full-suite/0001/control-receipts"
                         "/fixture.receipt.json").is_file())

    def test_changed_dependency_invalidates_suite_and_every_dependent_stage(self):
        calls = []
        patches = self.controls(calls)
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
            self.assertEqual(cc.finish_resumable(self.root, self.scope, self.output), 0)
        first_count = len(calls)
        calls2 = []
        patches = self.controls(calls2)
        with patches[0], mock.patch.object(cc, "SUITE", ["suite-changed"]), \
             patches[2], patches[3], patches[4], patches[5], \
             mock.patch.object(cc, "_run_logged", side_effect=self.fake_run(calls2)):
            self.assertEqual(cc.finish_resumable(self.root, self.scope, self.output), 0)
        self.assertGreater(first_count, 0)
        self.assertEqual(calls2[0][0], "suite-changed")
        result = json.loads((self.output / "attempts/0002/result.json").read_text())
        invalidated = [row["stage"] for row in result["invalidated_stages"]]
        self.assertEqual(invalidated, ["03-full-suite", "04-sealed-validation",
                                       "05-dependency-ordered-refresh",
                                       "06-check-01", "07-check-02"])

    def test_live_edit_and_restore_cannot_contaminate_snapshot_suite(self):
        calls = []

        def aba(snapshot):
            self.assertNotEqual(snapshot.resolve(), self.root.resolve())
            (self.root / "input.txt").write_text("contaminating edit\n")
            self.assertEqual((snapshot / "input.txt").read_text(), "stable\n")
            (self.root / "input.txt").write_text("stable\n")

        patches = self.controls(calls, suite_action=aba)
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
            self.assertEqual(cc.finish_resumable(self.root, self.scope, self.output), 0)
        result = json.loads((self.output / "attempts/0001/result.json").read_text())
        self.assertEqual(result["publication_match"], "PASS")
        self.assertIn("03-full-suite", result["executed_stages"])

    def test_publication_change_after_snapshot_refuses_result(self):
        calls = []

        def replace_publication(_snapshot):
            (self.root / "input.txt").write_text("new committed input\n")
            git(self.root, "add", "input.txt")
            git(self.root, "commit", "-qm", "replace publication input")

        patches = self.controls(calls, suite_action=replace_publication)
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
            self.assertEqual(cc.finish_resumable(self.root, self.scope, self.output), 1)
        result = json.loads((self.output / "attempts/0001/result.json").read_text())
        self.assertIn("publication inputs no longer match validated snapshot", result["error"])
        self.assertNotIn("04-sealed-validation", result["executed_stages"])

    def test_unrelated_document_commit_reuses_suite(self):
        (self.root / "unrelated.md").write_text("first\n")
        (self.root / self.scope).write_text(json.dumps({
            "schema_version": 2, "scope": "stage-specific fixture",
            "paths": ["input.txt", "unrelated.md"],
            "stage_dependencies": {
                "status": ["input.txt"], "suite": ["input.txt"],
                "publication": ["input.txt", "unrelated.md"],
            },
        }) + "\n")
        git(self.root, "add", "unrelated.md", self.scope)
        git(self.root, "commit", "-qm", "unrelated report")
        calls = []
        patches = self.controls(calls)
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
            self.assertEqual(cc.finish_resumable(self.root, self.scope, self.output), 0)
        (self.root / "unrelated.md").write_text("second\n")
        git(self.root, "add", "unrelated.md")
        git(self.root, "commit", "-qm", "update unrelated report")
        calls2 = []
        patches = self.controls(calls2)
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
            self.assertEqual(cc.finish_resumable(self.root, self.scope, self.output), 0)
        result = json.loads((self.output / "attempts/0002/result.json").read_text())
        self.assertIn("03-full-suite", result["reused_stages"])
        self.assertFalse(any(command[0] == "suite" for command in calls2))

    def test_committed_test_dependency_change_invalidates_suite(self):
        calls = []
        patches = self.controls(calls)
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
            self.assertEqual(cc.finish_resumable(self.root, self.scope, self.output), 0)
        (self.root / "input.txt").write_text("changed test dependency\n")
        git(self.root, "add", "input.txt")
        git(self.root, "commit", "-qm", "change test dependency")
        calls2 = []
        patches = self.controls(calls2)
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
            self.assertEqual(cc.finish_resumable(self.root, self.scope, self.output), 0)
        result = json.loads((self.output / "attempts/0002/result.json").read_text())
        self.assertIn("03-full-suite", result["executed_stages"])
        self.assertTrue(any(command[0] == "suite" for command in calls2))

    def test_interruption_preserves_failure_and_resume_reuses_valid_prefix(self):
        calls = []
        patches = self.controls(calls, interrupt_suite=True)
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
            self.assertEqual(cc.finish_resumable(self.root, self.scope, self.output), 130)
        first = json.loads((self.output / "attempts/0001/result.json").read_text())
        self.assertTrue(first["interrupted"])
        self.assertTrue((self.output / "stages/03-full-suite/0001/failure.json").is_file())
        calls2 = []
        patches = self.controls(calls2)
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
            self.assertEqual(cc.finish_resumable(self.root, self.scope, self.output), 0)
        self.assertEqual(calls2[0], ["suite"])
        second = json.loads((self.output / "attempts/0002/result.json").read_text())
        self.assertIn("02-status-preflight", second["reused_stages"])

    def test_cached_output_tamper_fails_closed_without_rerun(self):
        calls = []
        patches = self.controls(calls)
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
            self.assertEqual(cc.finish_resumable(self.root, self.scope, self.output), 0)
        suite_log = self.output / "stages/03-full-suite/0001/command.log"
        suite_log.write_text("tampered\n")
        calls2 = []
        patches = self.controls(calls2)
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
            self.assertEqual(cc.finish_resumable(self.root, self.scope, self.output), 1)
        self.assertEqual(calls2, [])
        result = json.loads((self.output / "attempts/0002/result.json").read_text())
        self.assertIn("cached stage output bytes changed", result["error"])
