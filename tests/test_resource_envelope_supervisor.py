"""Disjoint synthetic process controls; no resource pilot observer is invoked."""

import os
from pathlib import Path
import signal
import time
import unittest
from unittest.mock import patch

from lib import resource_envelope_supervisor as supervisor
from lib.resource_envelope_observe import classify


ROOT = Path(__file__).resolve().parents[1]


def synthetic_snapshot(pgid, _ps, _timeout):
    try:
        os.kill(pgid, 0)
    except ProcessLookupError:
        return []
    return [{"pid": pgid, "rss_bytes": 1_000_000, "state": "S"}]


def run(argv, **overrides):
    options = dict(argv=argv, cwd=ROOT, env=dict(os.environ), stdin_bytes=None,
                   timeout_seconds=1.0, memory_ceiling_bytes=100_000_000,
                   sample_interval_seconds=0.005, max_trace_gap_seconds=0.5,
                   cleanup_seconds=0.2)
    options.update(overrides)
    return supervisor.run_direct(**options)


class ResourceSupervisorTests(unittest.TestCase):
    def test_success_raw_accounting(self):
        with patch.object(supervisor, "_group_snapshot", side_effect=synthetic_snapshot):
            result = run(["/bin/sh", "-c", "sleep 0.04; printf ok"])
        r = result.receipt
        self.assertEqual(result.stdout, b"ok")
        self.assertEqual(result.stderr, b"")
        self.assertEqual(r["exit_code"], 0)
        self.assertGreater(r["sample_count"], 0)
        self.assertEqual(r["maximum_sampled_group_rss_bytes"], 1_000_000)
        self.assertGreater(r["child_peak_rss_bytes"], 0)
        self.assertEqual(r["accounting_error"], None)
        self.assertEqual(r["monitor_errors"], [])
        self.assertTrue(r["cleanup_complete"])
        self.assertTrue(all(s["monotonic_ns"] <= r["reaped_monotonic_ns"] for s in r["samples"]))

    def test_nonzero_exit_is_retained(self):
        with patch.object(supervisor, "_group_snapshot", side_effect=synthetic_snapshot):
            result = run(["/bin/sh", "-c", "printf bad >&2; exit 7"])
        self.assertEqual(result.receipt["exit_code"], 7)
        self.assertEqual(result.stderr, b"bad")
        self.assertTrue(result.receipt["cleanup_complete"])

    def test_timeout_kills_group_and_preserves_receipt(self):
        with patch.object(supervisor, "_group_snapshot", side_effect=synthetic_snapshot):
            result = run(["/bin/sh", "-c", "sleep 2"], timeout_seconds=0.04)
        r = result.receipt
        self.assertEqual(r["stop_reason"], "OBSERVED_TIME_LIMIT")
        self.assertEqual(r["exit_code"], -signal.SIGKILL)
        self.assertTrue(r["cleanup_complete"])

    def test_sampled_memory_limit(self):
        with patch.object(supervisor, "_group_snapshot", side_effect=synthetic_snapshot):
            result = run(["/bin/sh", "-c", "sleep 2"], memory_ceiling_bytes=500_000)
        self.assertEqual(result.receipt["stop_reason"], "OBSERVED_MEMORY_LIMIT")
        self.assertTrue(result.receipt["cleanup_complete"])

    def test_monitor_fault_cannot_be_success(self):
        with patch.object(supervisor, "_group_snapshot", side_effect=PermissionError("synthetic EPERM")):
            result = run(["/bin/sh", "-c", "sleep 2"])
        r = result.receipt
        self.assertEqual(r["stop_reason"], "MONITOR_FAULT")
        self.assertTrue(any("synthetic EPERM" in error for error in r["monitor_errors"]))
        self.assertFalse(r["cleanup_complete"])

    def test_cleanup_fault_is_explicit(self):
        with patch.object(supervisor, "_group_snapshot", side_effect=synthetic_snapshot), \
             patch.object(supervisor, "_cleanup_group", return_value=(False, ["synthetic leak"])):
            result = run(["/bin/sh", "-c", "printf ok"])
        self.assertFalse(result.receipt["cleanup_complete"])
        self.assertEqual(result.receipt["cleanup_errors"], ["synthetic leak"])

    def test_late_snapshot_after_exit_is_discarded(self):
        def delayed(_pgid, _ps, _timeout):
            time.sleep(0.06)
            return [{"pid": 999, "rss_bytes": 1_000_000, "state": "S"}]
        with patch.object(supervisor, "_group_snapshot", side_effect=delayed):
            result = run(["/bin/sh", "-c", "exit 0"], timeout_seconds=0.02)
        self.assertEqual(result.receipt["exit_code"], 0)
        self.assertEqual(result.receipt["sample_count"], 0)
        self.assertEqual(result.receipt["stop_reason"], None)

    def test_wait4_fault_preserves_accounting_failure(self):
        def broken_wait4(pid, options):
            raise OSError("synthetic wait4 fault")
        with patch.object(supervisor, "_group_snapshot", side_effect=synthetic_snapshot), \
             patch.object(supervisor.os, "wait4", side_effect=broken_wait4):
            result = run(["/bin/sh", "-c", "sleep 2"])
        self.assertIn("synthetic wait4 fault", result.receipt["accounting_error"])
        self.assertIsNone(result.receipt["child_peak_rss_bytes"])
        self.assertTrue(result.receipt["reap_complete"])
        self.assertIsNotNone(result.receipt["fallback_waitpid_status"])

    def test_healthy_fast_exit_can_have_zero_group_samples(self):
        calls = [0]
        def late_then_empty(_pgid, _ps, _timeout):
            calls[0] += 1
            if calls[0] == 1:
                time.sleep(0.04)
            return []
        with patch.object(supervisor, "_group_snapshot", side_effect=late_then_empty):
            result = run(["/bin/sh", "-c", "printf ok"], max_trace_gap_seconds=0.5)
        self.assertEqual(result.receipt["sample_count"], 0)
        self.assertEqual(result.receipt["monitor_errors"], [])
        self.assertEqual(classify(result.receipt, result.stdout, result.stderr,
                                  expected_stdout=b"ok", baseline=False)["status"], "ACCEPTED")

    def test_delayed_wait4_normal_exit_is_not_a_limit(self):
        original = supervisor.os.wait4
        def delayed_wait4(pid, options):
            answer = original(pid, options)
            time.sleep(0.12)
            return answer
        with patch.object(supervisor, "_group_snapshot", side_effect=synthetic_snapshot), \
             patch.object(supervisor.os, "wait4", side_effect=delayed_wait4):
            result = run(["/bin/sh", "-c", "exit 0"], timeout_seconds=0.01)
        disposition = classify(result.receipt, result.stdout, result.stderr,
                               expected_stdout=b"", baseline=False)
        self.assertEqual(result.receipt["exit_code"], 0)
        self.assertEqual(disposition["status"], "REPAIR_PAUSE")

    def test_failed_group_signal_is_not_a_valid_limit(self):
        with patch.object(supervisor, "_group_snapshot", side_effect=synthetic_snapshot), \
             patch.object(supervisor, "_signal_group", return_value="synthetic EPERM"):
            result = run(["/bin/sh", "-c", "sleep 2"], timeout_seconds=0.03)
        disposition = classify(result.receipt, result.stdout, result.stderr,
                               expected_stdout=b"", baseline=False)
        self.assertEqual(disposition["status"], "REPAIR_PAUSE")
        self.assertTrue(any("synthetic EPERM" in x for x in result.receipt["monitor_errors"]))

    def test_malformed_wait4_and_sample_accounting_rejected(self):
        with patch.object(supervisor, "_group_snapshot", side_effect=synthetic_snapshot):
            result = run(["/bin/sh", "-c", "sleep 0.03; printf ok"])
        receipt = dict(result.receipt)
        receipt["child_ru_maxrss_raw"] = None
        self.assertEqual(classify(receipt, result.stdout, result.stderr,
                                  expected_stdout=b"ok", baseline=False)["status"], "REPAIR_PAUSE")
        receipt = dict(result.receipt)
        receipt["wait_status"] = 0 if receipt["exit_code"] != 0 else 9
        self.assertEqual(classify(receipt, result.stdout, result.stderr,
                                  expected_stdout=b"ok", baseline=False)["status"], "REPAIR_PAUSE")

    def test_malformed_wait4_usage_returns_structured_fault(self):
        original = supervisor.os.wait4
        def malformed_usage(pid, options):
            reaped_pid, status, _usage = original(pid, options)
            return reaped_pid, status, object()
        with patch.object(supervisor, "_group_snapshot", side_effect=synthetic_snapshot), \
             patch.object(supervisor.os, "wait4", side_effect=malformed_usage):
            result = run(["/bin/sh", "-c", "printf ok"])
        self.assertEqual(result.stdout, b"ok")
        self.assertIn("invalid wait4 usage", result.receipt["accounting_error"])
        self.assertIsNone(result.receipt["child_peak_rss_bytes"])
        self.assertEqual(classify(result.receipt, result.stdout, result.stderr,
                                  expected_stdout=b"ok", baseline=False)["status"], "REPAIR_PAUSE")

    def test_postexit_over_ceiling_does_not_hide_wrong_output(self):
        def zero_rss(pgid, _ps, _timeout):
            try:
                os.kill(pgid, 0)
            except ProcessLookupError:
                return []
            return [{"pid": pgid, "rss_bytes": 0, "state": "S"}]
        with patch.object(supervisor, "_group_snapshot", side_effect=zero_rss):
            result = run(["/bin/sh", "-c", "printf wrong"], memory_ceiling_bytes=1)
        self.assertEqual(result.receipt["stop_reason"], "OBSERVED_OVER_CEILING_AFTER_EXIT")
        self.assertEqual(classify(result.receipt, result.stdout, result.stderr,
                                  expected_stdout=b"right", baseline=False)["status"], "REPAIR_PAUSE")

    def test_timeout_signal_must_not_precede_threshold(self):
        with patch.object(supervisor, "_group_snapshot", side_effect=synthetic_snapshot):
            result = run(["/bin/sh", "-c", "sleep 2"], timeout_seconds=0.03)
        self.assertEqual(result.receipt["stop_reason"], "OBSERVED_TIME_LIMIT")
        receipt = dict(result.receipt)
        receipt["signal_events"] = [dict(event) for event in result.receipt["signal_events"]]
        receipt["signal_events"][0]["monotonic_ns"] = receipt["started_monotonic_ns"] + 1
        receipt["signal_events"].append({"method": "cleanup", "signal": "SIGKILL", "error": None,
                                         "monotonic_ns": receipt["reaped_monotonic_ns"]})
        self.assertEqual(classify(receipt, result.stdout, result.stderr,
                                  expected_stdout=b"", baseline=False)["status"], "REPAIR_PAUSE")

    def test_memory_signal_must_follow_above_ceiling_sample(self):
        with patch.object(supervisor, "_group_snapshot", side_effect=synthetic_snapshot):
            result = run(["/bin/sh", "-c", "sleep 2"], memory_ceiling_bytes=500_000)
        receipt = dict(result.receipt)
        receipt["signal_events"] = [dict(event) for event in result.receipt["signal_events"]]
        receipt["signal_events"][0]["monotonic_ns"] = receipt["started_monotonic_ns"]
        self.assertEqual(classify(receipt, result.stdout, result.stderr,
                                  expected_stdout=b"", baseline=False)["status"], "REPAIR_PAUSE")
        receipt = dict(result.receipt)
        receipt["sample_count"] += 1
        self.assertEqual(classify(receipt, result.stdout, result.stderr,
                                  expected_stdout=b"ok", baseline=False)["status"], "REPAIR_PAUSE")


if __name__ == "__main__":
    unittest.main()
