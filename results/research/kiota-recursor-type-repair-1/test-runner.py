#!/usr/bin/env python3
"""Pure and fully mocked regressions for the recursor-repair supervisor.

No test in this file starts Cargo, a checker, an inert child, or a network
operation. Process execution is replaced with an in-process fake.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("kiota_recursor_repair_runner", HERE / "run-cell.py")
assert SPEC is not None and SPEC.loader is not None
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def good_receipt(**overrides):
    receipt = {
        "argv": ["mock"],
        "cwd": "/mock",
        "exit_code": 0,
        "timed_out": False,
        "memory_limit_bytes": 1024,
        "memory_enforcement": "per-process-rss-process-group-monitor-v2",
        "memory_exceeded": False,
        "memory_monitor_samples": 3,
        "maximum_observed_rss_bytes": 512,
        "memory_monitor_error": None,
        "cleanup_complete": True,
    }
    receipt.update(overrides)
    return receipt


def summary(passed, failed=0, ignored=0, measured=0, filtered=0):
    status = "ok" if failed == 0 else "FAILED"
    return (
        f"test result: {status}. {passed} passed; {failed} failed; {ignored} ignored; "
        f"{measured} measured; {filtered} filtered out; finished in 0.01s\n"
    )


class ReceiptAuditTests(unittest.TestCase):
    def test_positive_complete_receipt_passes_audit(self):
        self.assertIsNone(runner.receipt_failure(good_receipt()))

    def test_zero_samples_fail_closed(self):
        outcome = runner.receipt_failure(good_receipt(memory_monitor_samples=0))
        self.assertEqual(outcome[0], "INFRASTRUCTURE_AUDIT_FAILURE")

    def test_nonpositive_rss_fails_closed(self):
        outcome = runner.receipt_failure(good_receipt(maximum_observed_rss_bytes=0))
        self.assertEqual(outcome[0], "INFRASTRUCTURE_AUDIT_FAILURE")

    def test_monitor_error_fails_closed(self):
        outcome = runner.receipt_failure(good_receipt(memory_monitor_error="mock failure"))
        self.assertEqual(outcome[0], "INFRASTRUCTURE_AUDIT_FAILURE")

    def test_memory_limit_is_nonterminal_process_failure(self):
        outcome = runner.receipt_failure(good_receipt(memory_exceeded=True, exit_code=-9))
        self.assertEqual(outcome[0], "PROCESS_SAFETY_FAILURE")

    def test_timeout_is_nonterminal_process_failure(self):
        outcome = runner.receipt_failure(good_receipt(timed_out=True, exit_code=-9))
        self.assertEqual(outcome[0], "PROCESS_SAFETY_FAILURE")

    def test_unproven_cleanup_fails_closed(self):
        outcome = runner.receipt_failure(good_receipt(cleanup_complete=False))
        self.assertEqual(outcome[0], "INFRASTRUCTURE_AUDIT_FAILURE")

    def test_nonzero_cargo_is_engineering_not_scientific_failure(self):
        outcome = runner.receipt_failure(good_receipt(exit_code=101))
        self.assertEqual(outcome[0], "ENGINEERING_FAILURE")


class ClassificationTests(unittest.TestCase):
    def focused_manifest(self, cell, filtered):
        spec = runner.CELL_SPECS[cell]
        return {
            "argv": ["mock"],
            "cwd": "/mock",
            "memory_bytes": 1024,
            "expected": {
                "exit": 0,
                "outcome": spec["outcome"],
                "named_tests": list(spec["tests"]),
                "integration_passed": len(spec["tests"]),
                "failed": 0,
                "ignored": 0,
                "filtered_out": filtered,
            }
        }

    def focused_output(self, cell, filtered):
        lines = "".join(f"test {name} ... ok\n" for name in runner.CELL_SPECS[cell]["tests"])
        return (lines + "\n" + summary(len(runner.CELL_SPECS[cell]["tests"]), filtered=filtered)).encode()

    def test_candidate_confirmation_is_a_passing_scientific_cell(self):
        manifest = self.focused_manifest("003-candidate", 78)
        passed, outcome, _ = runner.classify(
            "003-candidate", manifest, good_receipt(), self.focused_output("003-candidate", 78), b""
        )
        self.assertTrue(passed)
        self.assertEqual(outcome, "EXPECTED_REJECT_CONFIRMED")

    def test_missing_named_test_fails_closed(self):
        manifest = self.focused_manifest("004-control", 78)
        output = summary(1, filtered=78).encode()
        passed, outcome, _ = runner.classify("004-control", manifest, good_receipt(), output, b"")
        self.assertFalse(passed)
        self.assertEqual(outcome, "INFRASTRUCTURE_AUDIT_FAILURE")

    def test_focused_count_drift_fails_closed(self):
        manifest = self.focused_manifest("002-focused", 72)
        output = self.focused_output("002-focused", 71)
        passed, outcome, _ = runner.classify("002-focused", manifest, good_receipt(), output, b"")
        self.assertFalse(passed)
        self.assertEqual(outcome, "INFRASTRUCTURE_AUDIT_FAILURE")

    def test_full_suite_requires_all_four_exact_harness_counts(self):
        manifest = {"argv": ["mock"], "cwd": "/mock", "memory_bytes": 1024, "expected": {
            "exit": 0,
            "outcome": "FULL_SUITE_PASS",
            "unit_passed": 83,
            "binary_passed": 0,
            "integration_passed": 79,
            "doctest_passed": 0,
            "total_passed": 162,
            "failed": 0,
            "ignored": 0,
        }}
        output = (summary(83) + summary(0) + summary(79) + summary(0)).encode()
        passed, outcome, _ = runner.classify("009-full", manifest, good_receipt(), output, b"")
        self.assertTrue(passed)
        self.assertEqual(outcome, "FULL_SUITE_PASS")
        drift = (summary(83) + summary(0) + summary(78) + summary(0)).encode()
        passed, outcome, _ = runner.classify("009-full", manifest, good_receipt(), drift, b"")
        self.assertFalse(passed)
        self.assertEqual(outcome, "INFRASTRUCTURE_AUDIT_FAILURE")

    def test_valid_output_cannot_override_bad_cleanup(self):
        manifest = self.focused_manifest("005-ordinary", 78)
        passed, outcome, _ = runner.classify(
            "005-ordinary", manifest, good_receipt(cleanup_complete=False),
            self.focused_output("005-ordinary", 78), b""
        )
        self.assertFalse(passed)
        self.assertEqual(outcome, "INFRASTRUCTURE_AUDIT_FAILURE")


class AccountingTests(unittest.TestCase):
    def test_attempts_are_observational_and_uncapped(self):
        account = runner.new_account()
        for number in range(1, 1001):
            account["attempts"].append({
                "attempt": number,
                "cell_id": "001-build",
                "directory": f"execution/attempt-{number:06d}-001-build",
                "status": "FAIL",
            })
        account["next_attempt"] = 1001
        account["observations"] = {"processes": 1000, "builds": 1000, "tests": 0}
        account["pending"] = None
        runner.validate_sequence(account, "001-build")
        self.assertEqual(account["policy"]["attempt_caps"], "NONE")

    def test_fixed_order_requires_predecessor_success(self):
        account = runner.new_account()
        with self.assertRaisesRegex(runner.RunnerError, "earlier fixed cells"):
            runner.validate_sequence(account, "002-focused")
        account["attempts"].append({"cell_id": "001-build", "status": "PASS"})
        runner.validate_sequence(account, "002-focused")

    def test_pending_cleanup_blocks_every_retry(self):
        account = runner.new_account()
        account["pending"] = 1
        with self.assertRaisesRegex(runner.RunnerError, "cleanup"):
            runner.validate_sequence(account, "001-build")


class MockedExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name) / "item"
        self.execution = self.base / "execution"
        self.execution.mkdir(parents=True)
        self.source = Path(self.temp.name) / "source"
        self.source.mkdir()
        self.manifest_path = self.execution / "001-build-manifest.json"
        self.manifest_path.write_text("{}\n")

    def tearDown(self):
        self.temp.cleanup()

    def manifest(self):
        return {
            "_path": self.manifest_path,
            "_sha256": "a" * 64,
            "argv": ["mock-cargo", "test", "--offline", "--locked", "--no-run"],
            "cwd": str(self.source),
            "environment": {"CARGO_NET_OFFLINE": "true"},
            "timeout_seconds": 1,
            "memory_bytes": 1024,
            "expected": {"exit": 0, "outcome": "BUILD_PASS"},
        }

    @staticmethod
    def fake_supervisor(*, raw_prefix, argv, cwd, memory_bytes, **_kwargs):
        Path(str(raw_prefix) + ".stdout").write_bytes(b"mock build\n")
        Path(str(raw_prefix) + ".stderr").write_bytes(b"")
        return good_receipt(argv=argv, cwd=str(cwd), memory_limit_bytes=memory_bytes)

    def test_execute_cell_uses_mock_and_writes_durable_receipts(self):
        with patch.object(runner, "BASE", self.base), \
             patch.object(runner, "verify_manifest", return_value=self.manifest()), \
             patch.object(runner, "run_supervised", side_effect=self.fake_supervisor) as mocked:
            result = runner.execute_cell("001-build")
        self.assertEqual(result["status"], "PASS")
        mocked.assert_called_once()
        attempt = self.execution / "attempt-000001-001-build"
        self.assertTrue((attempt / "reservation.json").is_file())
        self.assertTrue((attempt / "supervisor.json").is_file())
        self.assertTrue((attempt / "result.json").is_file())
        account = json.loads((self.execution / "accounting.json").read_text())
        self.assertIsNone(account["pending"])

    def test_mocked_unproven_cleanup_leaves_pending_block(self):
        def failed_supervisor(*, raw_prefix, argv, cwd, memory_bytes, **_kwargs):
            Path(str(raw_prefix) + ".stdout").write_bytes(b"mock build\n")
            Path(str(raw_prefix) + ".stderr").write_bytes(b"")
            return good_receipt(argv=argv, cwd=str(cwd), memory_limit_bytes=memory_bytes,
                                cleanup_complete=False)

        with patch.object(runner, "BASE", self.base), \
             patch.object(runner, "verify_manifest", return_value=self.manifest()), \
             patch.object(runner, "run_supervised", side_effect=failed_supervisor):
            result = runner.execute_cell("001-build")
        self.assertEqual(result["status"], "FAIL")
        account = json.loads((self.execution / "accounting.json").read_text())
        self.assertEqual(account["pending"], 1)
        with self.assertRaisesRegex(runner.RunnerError, "cleanup"):
            runner.validate_sequence(account, "001-build")

    def test_mocked_spawn_exception_is_preserved_without_claiming_cleanup(self):
        with patch.object(runner, "BASE", self.base), \
             patch.object(runner, "verify_manifest", return_value=self.manifest()), \
             patch.object(runner, "run_supervised", side_effect=OSError("mock spawn failure")):
            result = runner.execute_cell("001-build")
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["outcome"], "INFRASTRUCTURE_AUDIT_FAILURE")
        account = json.loads((self.execution / "accounting.json").read_text())
        self.assertEqual(account["pending"], 1)


if __name__ == "__main__":
    unittest.main()
