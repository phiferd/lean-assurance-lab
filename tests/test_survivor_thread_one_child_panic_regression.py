"""Inert tests for the committed one-thread child-panic controller."""
from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib import survivor_thread_one_child_panic_regression as p


def receipt(**changes):
    value = {
        "exit_code": 0,
        "timed_out": False,
        "cleanup_complete": True,
        "memory_monitor_error": None,
        "memory_monitor_samples": 1,
        "maximum_observed_rss_bytes": 1,
        "memory_exceeded": False,
    }
    value.update(changes)
    return value


def terminal(number, *, status="COMPLETE", classification=None, binary=False, pause=False):
    row = {
        "kind": "TERMINAL", "number": number, "status": status,
        "charged_seconds": 1.0, "engineering_pause": pause,
    }
    if classification is not None:
        row["classification"] = classification
    if binary:
        row["binary"] = {"path": "external/nanoda_bin", "sha256": "a" * 64}
    return row


def reserve(number, phase, cell):
    return {
        "kind": "RESERVED", "number": number, "phase": phase, "cell": cell,
        "reserved_seconds": p.LIMITS["offline_build_timeout_seconds"] if phase == "build" else p.LIMITS["checker_timeout_seconds"],
        "active_seconds": 1200,
    }


class ClassificationTests(unittest.TestCase):
    def test_clean_success_is_accept(self):
        self.assertEqual(p.classify("control-baseline", receipt(), p.SUCCESS, b""), "ACCEPT")

    def test_direct_main_assertion_is_baseline_refusal(self):
        stderr = b"thread 'main' panicked\nassertion failed: self.def_eq(u, v)\n"
        self.assertEqual(p.classify("candidate-baseline", receipt(exit_code=101), b"", stderr),
                         "DIRECT_ASSERTION_REFUSAL")

    def test_worker_join_assertion_is_mutant_refusal(self):
        stderr = (b"thread 'thread_0' panicked\nassertion failed: self.def_eq(u, v)\n"
                  b"A thread in `check_all_declars` panicked while being joined\n")
        self.assertEqual(p.classify("candidate-mutant", receipt(exit_code=101), b"", stderr),
                         "WORKER_PANIC_JOIN_REFUSAL")

    def test_join_message_cannot_satisfy_baseline(self):
        stderr = (b"thread 'thread_0' panicked\nassertion failed: self.def_eq(u, v)\n"
                  b"A thread in `check_all_declars` panicked while being joined\n")
        self.assertEqual(p.classify("candidate-baseline", receipt(exit_code=101), b"", stderr), "CRASH")

    def test_monitor_failure_is_never_a_candidate_result(self):
        self.assertEqual(p.classify("candidate-mutant", receipt(memory_monitor_samples=0), p.SUCCESS, b""),
                         "INFRASTRUCTURE_FAILURE")


class ProtocolTests(unittest.TestCase):
    def test_fixed_protocol_order(self):
        attempts = []
        self.assertEqual(p.next_action(attempts), ("build", "baseline"))
        attempts.append({"reservation": reserve(1, "build", "baseline"), "terminal": terminal(1, binary=True)})
        self.assertEqual(p.next_action(attempts), ("build", "mutant"))
        attempts.append({"reservation": reserve(2, "build", "mutant"), "terminal": terminal(2, binary=True)})
        self.assertEqual(p.next_action(attempts), ("checker", 0))
        attempts.append({"reservation": reserve(3, "checker", 0), "terminal": terminal(3, classification="ACCEPT")})
        attempts.append({"reservation": reserve(4, "checker", 1), "terminal": terminal(4, classification="ACCEPT")})
        attempts.append({"reservation": reserve(5, "checker", 2), "terminal": terminal(5, status="FAILED", classification="DIRECT_ASSERTION_REFUSAL")})
        self.assertEqual(p.next_action(attempts), ("checker", 3))
        attempts.append({"reservation": reserve(6, "checker", 3), "terminal": terminal(6, status="FAILED", classification="WORKER_PANIC_JOIN_REFUSAL")})
        self.assertEqual(p.next_action(attempts), ("DONE", None))

    def test_control_failure_stops_before_candidate(self):
        attempts = [
            {"reservation": reserve(1, "build", "baseline"), "terminal": terminal(1, binary=True)},
            {"reservation": reserve(2, "build", "mutant"), "terminal": terminal(2, binary=True)},
            {"reservation": reserve(3, "checker", 0), "terminal": terminal(3, classification="CRASH")},
        ]
        self.assertEqual(p.next_action(attempts), ("STOP", None))

    def test_orphan_reservation_pauses(self):
        attempts = [{"reservation": reserve(1, "build", "baseline")}]
        self.assertEqual(p.next_action(attempts), ("PAUSED", None))


class SourceBindingTests(unittest.TestCase):
    def test_signal_retry_is_available_before_process_execution(self):
        self.assertTrue(callable(p.signal_retry))

    def test_only_relational_boundary_changes(self):
        source = (ROOT / "results/research/alt-survivors-2026-09-08/evidence/pinned-nanoda/src/tc.rs").read_bytes()
        self.assertEqual(source.count(b"self.config.num_threads > 1"), 1)
        mutant = source.replace(b"self.config.num_threads > 1", b"self.config.num_threads >= 1", 1)
        self.assertEqual((len(mutant), hashlib.sha256(mutant).hexdigest()),
                         (56603, "a2a41ceb83361d892cd260f60605338788267635baf33f19cedf43e9aa579fdb"))
        mutation = (ROOT / "mutations/nanoda-gen-2bdfe18a9ec2.json").read_text(encoding="utf-8")
        self.assertIn('"mutated": "(self.config.num_threads >= 1)"', mutation)

    def test_ledger_rejects_unreconciled_second_reservation(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(p, "OUT", "out"):
            ledger = p.Ledger(Path(temporary))
            ledger.initialize()
            ledger.add(reserve(1, "build", "baseline"))
            with self.assertRaises(ValueError):
                ledger.add(reserve(2, "build", "mutant"))


if __name__ == "__main__":
    unittest.main()
