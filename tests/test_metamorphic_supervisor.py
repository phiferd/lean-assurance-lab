from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from lib.metamorphic_pilot_runner import classify, run_supervised


ROOT = Path(__file__).resolve().parents[1]
MEMORY_LIMIT = 64 * 1024 * 1024
PRODUCTION_MEMORY_LIMIT = 2 * 1024 * 1024 * 1024


class SupervisorTests(unittest.TestCase):
    def run_case(self, name: str, script: str, *, timeout: int,
                 memory: int = PRODUCTION_MEMORY_LIMIT) -> tuple[dict, bytes, bytes]:
        def execute(directory: Path) -> tuple[dict, bytes, bytes]:
            prefix = directory / name
            if any(Path(str(prefix) + suffix).exists()
                   for suffix in (".stdout", ".stderr", ".receipt.json")):
                self.fail(f"refusing to overwrite supervisor receipt prefix {prefix}")
            receipt = run_supervised(
                argv=[sys.executable, "-c", script], cwd=ROOT, stdin=None,
                env=os.environ.copy(), timeout_seconds=timeout,
                memory_bytes=memory, raw_prefix=prefix,
            )
            stdout_path = Path(str(prefix) + ".stdout")
            stderr_path = Path(str(prefix) + ".stderr")
            stdout = stdout_path.read_bytes()
            stderr = stderr_path.read_bytes()
            Path(str(prefix) + ".receipt.json").write_text(
                json.dumps(receipt, indent=2, sort_keys=True) + "\n"
            )
            self.assertEqual(ROOT / receipt["raw_stdout_path"], stdout_path)
            self.assertEqual(ROOT / receipt["raw_stderr_path"], stderr_path)
            return receipt, stdout, stderr

        retained = os.environ.get("METAMORPHIC_SUPERVISOR_RECEIPT_DIR")
        if retained:
            directory = (ROOT / retained).resolve()
            if ROOT != directory and ROOT not in directory.parents:
                self.fail("supervisor receipt directory escapes repository")
            directory.mkdir(parents=True, exist_ok=True)
            return execute(directory)
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            return execute(Path(temporary))

    def assert_observed_and_clean(self, receipt: dict) -> None:
        detail = json.dumps(receipt, sort_keys=True)
        self.assertIsNone(receipt["memory_monitor_error"], detail)
        self.assertGreater(receipt["memory_monitor_samples"], 0, detail)
        self.assertGreater(receipt["maximum_observed_rss_bytes"], 0, detail)
        self.assertGreater(receipt["memory_backend"]["preflight_samples"], 0, detail)
        self.assertTrue(receipt["cleanup_complete"], detail)
        self.assertIn("real_seconds", receipt["metrics"])

    def test_classification_rejects_missing_runtime_sample(self):
        receipt = {
            "memory_monitor_error": None,
            "memory_monitor_samples": 0,
            "maximum_observed_rss_bytes": 0,
            "memory_exceeded": False,
            "timed_out": False,
            "cleanup_complete": True,
            "exit_code": 0,
        }
        self.assertEqual(
            classify("nanoda-6ae1f0c", receipt, b"", b""),
            ("INFRASTRUCTURE_AUDIT_FAILURE", "no child process-group RSS sample recorded"),
        )
        receipt["memory_monitor_samples"] = 1
        self.assertEqual(
            classify("nanoda-6ae1f0c", receipt, b"", b""),
            ("INFRASTRUCTURE_AUDIT_FAILURE", "child process-group RSS samples contained no positive value"),
        )

    def test_normal_exit_is_observed(self):
        receipt, stdout, stderr = self.run_case(
            "normal.with.dots", "print('supervised-ok')", timeout=5,
        )
        self.assertEqual(receipt["exit_code"], 0, json.dumps(receipt, sort_keys=True))
        self.assertFalse(receipt["timed_out"])
        self.assertFalse(receipt["memory_exceeded"])
        self.assertEqual(stdout, b"supervised-ok\n")
        self.assertEqual(stderr, b"")
        self.assert_observed_and_clean(receipt)

    def test_nonzero_exit_is_preserved(self):
        receipt, stdout, stderr = self.run_case(
            "nonzero", "import sys; print('refusal', file=sys.stderr); sys.exit(7)", timeout=5,
        )
        self.assertEqual(receipt["exit_code"], 7, json.dumps(receipt, sort_keys=True))
        self.assertFalse(receipt["timed_out"])
        self.assertFalse(receipt["memory_exceeded"])
        self.assertEqual(stdout, b"")
        self.assertEqual(stderr, b"refusal\n")
        self.assert_observed_and_clean(receipt)

    def test_child_memory_breach_kills_process_group(self):
        script = (
            "import subprocess,sys,time; "
            "subprocess.Popen([sys.executable,'-c',"
            "'import time; x=bytearray(128*1024*1024); time.sleep(30)']); "
            "time.sleep(30)"
        )
        receipt, _, _ = self.run_case(
            "memory", script, timeout=10, memory=MEMORY_LIMIT,
        )
        detail = json.dumps(receipt, sort_keys=True)
        self.assertTrue(receipt["memory_exceeded"], detail)
        self.assertGreater(receipt["maximum_observed_rss_bytes"], MEMORY_LIMIT, detail)
        self.assert_observed_and_clean(receipt)

    def test_timeout_kills_process_group(self):
        script = (
            "import subprocess,sys,time; "
            "subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)']); "
            "time.sleep(30)"
        )
        receipt, _, _ = self.run_case("timeout", script, timeout=1)
        self.assertTrue(receipt["timed_out"], json.dumps(receipt, sort_keys=True))
        self.assert_observed_and_clean(receipt)


if __name__ == "__main__":
    unittest.main()
