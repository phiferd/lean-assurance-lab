"""Administrative launch-gate tests; the scientific launch API is always mocked."""
from contextlib import ExitStack
from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "results/research/kiota-ctor-index-test-1/run-cell.py"
spec = importlib.util.spec_from_file_location("kiota_ctor_index_runner_tests", RUNNER)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class LaunchGate(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base = self.root / "results/research/kiota-ctor-index-test-1"
        self.execution = self.base / "execution"
        self.execution.mkdir(parents=True)
        self.source = self.root / "source"
        self.source.mkdir()
        self.bound = self.root / "bound"
        self.bound.write_bytes(b"frozen")
        self.cell = "001-focused"
        self.manifest = {
            "item_id": runner.ITEM,
            "cell_id": self.cell,
            "bindings": [{"path": str(self.bound), "sha256": runner.digest(b"frozen"), "bytes": 6}],
            "cwd": str(self.source),
            "timeout_seconds": 120,
            "argv": ["never-executed"],
            "environment": {},
            "absent_paths": []
        }
        self.path = self.execution / (self.cell + "-manifest.json")
        self.save_manifest()
        self.write(self.base / "work-record.json", {
            "start_monotonic": 1000.0,
            "started_at": "2026-09-19T00:00:00+00:00"
        })
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(patch.object(runner, "ROOT", self.root))
        stack.enter_context(patch.object(runner, "BASE", self.base))
        stack.enter_context(patch.object(runner.sys, "argv", ["run-cell.py", self.cell]))
        stack.enter_context(patch.object(runner.time, "monotonic", return_value=1100.0))
        self.clock = stack.enter_context(patch.object(runner, "datetime", wraps=datetime))
        self.clock.now.side_effect = lambda tz: datetime(2026, 9, 19, tzinfo=timezone.utc) + timedelta(seconds=100)
        self.git = stack.enter_context(patch.object(runner.subprocess, "check_output", side_effect=self.git_output))
        stack.enter_context(patch.object(runner, "verify_dependencies"))
        stack.enter_context(patch.object(runner, "verify_source"))
        self.launch = stack.enter_context(patch.object(runner, "run_process", side_effect=AssertionError("unexpected launch")))

    @staticmethod
    def write(path, value):
        path.write_text(json.dumps(value))

    def save_manifest(self):
        self.path.write_text(json.dumps(self.manifest))
        self.committed = self.path.read_bytes()

    def git_output(self, argv, **kwargs):
        if argv[:2] == ["git", "show"]:
            return self.committed
        raise AssertionError(f"unexpected subprocess request: {argv!r}")

    def refuse(self, message):
        with self.assertRaisesRegex((ValueError, FileExistsError), message):
            runner.main()
        self.launch.assert_not_called()
        self.assertFalse((self.execution / self.cell).exists())

    def account(self, builds=0, tests=0, pending=None, reservations=None):
        self.write(self.execution / "accounting.json", {
            "builds": builds,
            "test_processes": tests,
            "pending": pending,
            "reservations": reservations or []
        })

    def test_manifest_must_be_committed(self):
        self.committed = b"different"
        self.refuse("manifest must be committed")

    def test_changed_binding_refuses(self):
        self.bound.write_bytes(b"changed")
        self.refuse("binding mismatch")

    def test_wrong_cell_refuses(self):
        self.manifest["cell_id"] = "002-full"
        self.save_manifest()
        self.refuse("wrong cell")

    def test_unbound_cargo_configuration_refuses(self):
        config = self.root / "config.toml"
        config.write_text("[build]\n")
        self.manifest["absent_paths"] = [str(config)]
        self.save_manifest()
        self.refuse("unbound Cargo configuration")

    def test_timeout_cannot_expand(self):
        self.manifest["timeout_seconds"] = 121
        self.save_manifest()
        self.refuse("process ceiling")

    def test_item_deadline_refuses(self):
        with patch.object(runner.time, "monotonic", return_value=6300.0):
            self.clock.now.side_effect = lambda tz: datetime(2026, 9, 19, tzinfo=timezone.utc) + timedelta(seconds=5300)
            self.refuse("remaining active time")

    def test_disagreeing_clocks_refuses(self):
        self.clock.now.side_effect = lambda tz: datetime(2026, 9, 19, tzinfo=timezone.utc)
        self.refuse("paired item clock")

    def test_pending_reservation_refuses(self):
        self.account(1, 1, "000-prior", [{"cell_id":"000-prior"}])
        self.refuse("unreconciled")

    def test_build_cap_refuses(self):
        rows = [{"cell_id": str(i)} for i in range(2)]
        self.account(2, 2, None, rows)
        self.refuse("exhausted budget")

    def test_completed_cell_cannot_repeat(self):
        self.account(1, 1, None, [{"cell_id":self.cell}])
        self.refuse("reuse")

    def test_missing_account_after_prior_directory_refuses(self):
        (self.execution / "000-prior").mkdir()
        self.refuse("missing accounting")

    def test_reservation_is_durable_before_launch(self):
        def observe(*args, **kwargs):
            account = json.loads((self.execution / "accounting.json").read_text())
            self.assertEqual((account["builds"], account["test_processes"], account["pending"]),
                             (1, 1, self.cell))
            raise RuntimeError("mock supervisor loss")
        self.launch.side_effect = observe
        with self.assertRaisesRegex(RuntimeError, "mock supervisor loss"):
            runner.main()

    def test_failed_process_remains_charged_and_clears_pending(self):
        self.launch.side_effect = None
        self.launch.return_value = {"status":"FAILED", "returncode":101,
                                    "cleanup_completed":True, "deadline_exceeded":False}
        self.assertEqual(runner.main(), 1)
        account = json.loads((self.execution / "accounting.json").read_text())
        self.assertEqual((account["builds"], account["test_processes"]), (1, 1))
        self.assertIsNone(account["pending"])

    def test_cleanup_failure_keeps_pending(self):
        self.launch.side_effect = None
        self.launch.return_value = {"status":"INTERRUPTED", "returncode":1,
                                    "cleanup_completed":False, "deadline_exceeded":False}
        self.assertEqual(runner.main(), 1)
        account = json.loads((self.execution / "accounting.json").read_text())
        self.assertEqual(account["pending"], self.cell)


if __name__ == "__main__":
    unittest.main()
