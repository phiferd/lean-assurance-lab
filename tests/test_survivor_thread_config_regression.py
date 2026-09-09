"""Inert controller regressions; these tests launch neither Cargo nor Nanoda."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib import survivor_thread_config_regression as p


def start():
    return [{"kind": "START", "run_id": p.RUN}]


def reserve(number, phase, cell, active=3780):
    return {"kind": "RESERVED", "number": number, "phase": phase, "cell": cell,
            "reserved_seconds": 180 if phase == "build" else 30,
            "active_seconds": active}


def terminal(number, status="COMPLETE", classification=None, binary=False,
             cleanup=True, pause=False, charged=1):
    row = {"kind": "TERMINAL", "number": number, "status": status,
           "charged_seconds": charged, "cleanup_completed": cleanup,
           "engineering_pause": pause}
    if classification is not None:
        row["classification"] = classification
    if binary:
        row["binary"] = {"path": "external/binary", "sha256": "a" * 64}
    return row


def built():
    return (start() + [reserve(1, "build", "baseline"), terminal(1, binary=True),
                       reserve(2, "build", "mutant"), terminal(2, binary=True)])


def controls():
    return (built() + [reserve(3, "checker", 0), terminal(3, classification="ACCEPT"),
                       reserve(4, "checker", 1), terminal(4, classification="ACCEPT")])


def receipt(**changes):
    row = {"status": "COMPLETE", "returncode": 0, "cleanup_completed": True,
           "deadline_exceeded": False}
    row.update(changes)
    return row


def refusal_trace():
    return (b"panicked at src/tc.rs:921:71:\n"
            b"assertion failed: self.def_eq(u, v)\n"
            b"nanoda::tc::TypeChecker::infer\n"
            b"nanoda::tc::TypeChecker::check_declar\n")


class ClassificationTests(unittest.TestCase):
    def test_exact_success_is_accept(self):
        self.assertEqual(p.classify("control-baseline", receipt(), p.SUCCESS, b""), "ACCEPT")

    def test_extra_stdout_is_indeterminate(self):
        self.assertEqual(p.classify("control-baseline", receipt(), p.SUCCESS + b"x", b""),
                         "INDETERMINATE")

    def test_stderr_on_success_is_indeterminate(self):
        self.assertEqual(p.classify("control-baseline", receipt(), p.SUCCESS, b"warning"),
                         "INDETERMINATE")

    def test_candidate_refusal_is_source_attributed(self):
        failed = receipt(status="FAILED", returncode=101)
        for cell in ("candidate-baseline", "candidate-mutant"):
            self.assertEqual(p.classify(cell, failed, b"", refusal_trace()),
                             "TYPECHECK_REFUSAL")

    def test_refusal_not_transferred_to_control(self):
        self.assertEqual(p.classify("control-baseline",
                                   receipt(status="FAILED", returncode=101), b"", refusal_trace()),
                         "CRASH")

    def test_refusal_requires_assertion_site(self):
        trace = refusal_trace().replace(b"src/tc.rs:921:71:", b"src/tc.rs:1:1:")
        self.assertEqual(p.classify("candidate-baseline",
                                   receipt(status="FAILED", returncode=101), b"", trace), "CRASH")

    def test_refusal_requires_infer_frame(self):
        trace = refusal_trace().replace(b"::infer\n", b"")
        self.assertEqual(p.classify("candidate-baseline",
                                   receipt(status="FAILED", returncode=101), b"", trace), "CRASH")

    def test_parse_error_is_preserved(self):
        self.assertEqual(p.classify("candidate-baseline",
                                   receipt(status="FAILED", returncode=1), b"", b"parser error"),
                         "PARSE_ERROR")

    def test_timeout_is_preserved(self):
        self.assertEqual(p.classify("candidate-baseline",
                                   receipt(status="TIMED_OUT", returncode=None), b"", b""), "TIMEOUT")

    def test_cleanup_failure_is_indeterminate(self):
        self.assertEqual(p.classify("candidate-baseline",
                                   receipt(cleanup_completed=False), p.SUCCESS, b""), "INDETERMINATE")


class SequenceTests(unittest.TestCase):
    def test_first_action_is_baseline_build(self):
        self.assertEqual(p.derive(start())["next_action"], ("build", "baseline"))

    def test_second_action_is_mutant_build(self):
        rows = start() + [reserve(1, "build", "baseline"), terminal(1, binary=True)]
        self.assertEqual(p.derive(rows)["next_action"], ("build", "mutant"))

    def test_controls_precede_candidates(self):
        self.assertEqual(p.derive(built())["next_action"], ("checker", 0))
        self.assertEqual(p.derive(controls())["next_action"], ("checker", 2))

    def test_wrong_build_order_is_rejected(self):
        with self.assertRaises(ValueError):
            p.derive(start() + [reserve(1, "build", "mutant")])

    def test_checker_before_builds_is_rejected(self):
        with self.assertRaises(ValueError):
            p.derive(start() + [reserve(1, "checker", 0)])

    def test_control_mismatch_stops(self):
        rows = built() + [reserve(3, "checker", 0), terminal(3, classification="CRASH")]
        self.assertEqual(p.derive(rows)["next_action"], ("STOP", None))

    def test_baseline_candidate_accept_is_interpretable(self):
        rows = controls() + [reserve(5, "checker", 2), terminal(5, classification="ACCEPT")]
        self.assertEqual(p.derive(rows)["next_action"], ("checker", 3))

    def test_expected_fixed_pair_completes(self):
        rows = controls() + [
            reserve(5, "checker", 2), terminal(5, status="FAILED", classification="TYPECHECK_REFUSAL"),
            reserve(6, "checker", 3), terminal(6, classification="ACCEPT")]
        self.assertEqual(p.derive(rows)["next_action"], ("DONE", None))

    def test_mutant_candidate_refusal_is_interpretable_falsification(self):
        rows = controls() + [
            reserve(5, "checker", 2), terminal(5, status="FAILED", classification="TYPECHECK_REFUSAL"),
            reserve(6, "checker", 3), terminal(6, status="FAILED", classification="TYPECHECK_REFUSAL")]
        self.assertEqual(p.derive(rows)["next_action"], ("DONE", None))

    def test_candidate_crash_pauses(self):
        rows = controls() + [reserve(5, "checker", 2),
                             terminal(5, status="FAILED", classification="CRASH", pause=True)]
        self.assertEqual(p.derive(rows)["next_action"], ("PAUSED", None))

    def test_repair_replays_only_paused_cell(self):
        rows = controls() + [reserve(5, "checker", 2),
                             terminal(5, status="FAILED", classification="CRASH", pause=True)]
        repair = {"kind": "REPAIR", "after_number": 5, "phase": "checker", "cell": 2}
        self.assertEqual(p.derive(rows + [repair])["next_action"], ("checker", 2))
        with self.assertRaises(ValueError):
            p.derive(rows + [{**repair, "cell": 3}])

    def test_orphan_reservation_is_conservatively_charged(self):
        rows = built() + [reserve(3, "checker", 0)]
        self.assertEqual(p.derive(rows)["charged_seconds"], 32)
        with self.assertRaises(ValueError):
            p.derive(rows + [reserve(4, "checker", 1)])

    def test_reservation_cannot_cross_active_cap(self):
        with self.assertRaises(ValueError):
            p.derive(start() + [reserve(1, "build", "baseline", active=7021)])

    def test_unknown_event_is_rejected(self):
        with self.assertRaises(ValueError):
            p.derive(start() + [{"kind": "ERASE"}])


class GateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        work = self.root / p.WORK
        work.parent.mkdir(parents=True)
        work.write_text(json.dumps({
            "item_id": p.ITEM, "status": "ACTIVE", "authorization": p.EXPECTED_AUTHORIZATION,
            "budget": p.LIMITS, "pre_record_work_conservative_seconds": 180,
            "research_counts": {"offline_build_launches": 0, "checker_launches": 0,
                                "lean_proof_launches": 0, "research_network_requests": 0,
                                "new_export_byte_variants": 0, "new_mutation_identities": 0,
                                "external_actions": 0},
        }))
        self.queue = {"frontier_id": p.FRONTIER, "selected_item": p.ITEM,
                      "items": [{"id": p.ITEM, "status": "ACTIVE"}]}
        self.manifest = {"prelaunch_active_seconds": 3600}

    def call(self, charged=100, reservation=30, queue=None):
        with patch("lib.research_queue_v3.load_queue", return_value=queue or self.queue):
            return p.gate(self.root, self.manifest, charged, reservation)

    def test_exact_gate_passes(self):
        self.assertEqual(self.call(), 3320)

    def test_unselected_frontier_is_rejected(self):
        queue = copy.deepcopy(self.queue)
        queue["frontier_id"] = "F-OTHER"
        with self.assertRaises(ValueError):
            self.call(queue=queue)

    def test_cap_is_checked_before_reservation(self):
        with self.assertRaises(ValueError):
            self.call(charged=3250, reservation=180)

    def test_work_closure_blocks_launch(self):
        closure = self.root / p.BASE / "work-closure.json"
        closure.write_text("{}")
        with self.assertRaises(ValueError):
            self.call()


class FilesystemTests(unittest.TestCase):
    def test_manifest_names_are_narrow(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in (p.MANIFEST, "config/survivor-thread-config-regression-0001-r2.json"):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("{}")
                self.assertEqual(p.manifest_path(root, name), path)
            with self.assertRaises(ValueError):
                p.manifest_path(root, "config/other.json")

    def test_copy_exact_is_idempotent_and_detects_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, destination = root / "source", root / "destination"
            source.write_bytes(b"fixed")
            digest = hashlib.sha256(b"fixed").hexdigest()
            p._copy_exact(source, destination, digest)
            p._copy_exact(source, destination, digest)
            destination.write_bytes(b"drift")
            with self.assertRaises(ValueError):
                p._copy_exact(source, destination, digest)

    def test_materialization_applies_only_frozen_mutation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = (b"padding\n" * 146) + b"if self.config.num_threads > 1 {\n"
            donor = root / "donor/tc.rs"
            donor.parent.mkdir(parents=True)
            donor.write_bytes(original)
            readme = root / "donor/README.md"
            readme.write_bytes(b"readme")
            lock_path = root / p.SOURCE_LOCK
            lock_path.parent.mkdir(parents=True)
            lock_path.write_text(json.dumps({"files": [{"source_path": "src/tc.rs",
                "binding": {"path": "donor/tc.rs", "sha256": hashlib.sha256(original).hexdigest(),
                            "bytes": len(original)}}]}))
            changed = original.replace(b"self.config.num_threads > 1",
                                       b"!(self.config.num_threads > 1)")
            source = {
                "readme": {"path": "donor/README.md", "sha256": hashlib.sha256(b"readme").hexdigest()},
                "baseline": {"workspace": "external/baseline"},
                "mutant": {"workspace": "external/mutant",
                           "patch": {"line": 147, "original": "self.config.num_threads > 1",
                                     "mutated": "!(self.config.num_threads > 1)"},
                           "tc_after_patch": {"bytes": len(changed),
                                              "sha256": hashlib.sha256(changed).hexdigest()}},
            }
            with patch.object(p, "validate_source", return_value=source):
                p.materialize(root, {"source_materialization": {}})
                p.materialize(root, {"source_materialization": {}})
            self.assertEqual((root / "external/baseline/src/tc.rs").read_bytes(), original)
            self.assertEqual((root / "external/mutant/src/tc.rs").read_bytes(), changed)

    def test_ledger_refuses_truncation(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(p, "OUT", "out"):
            ledger = p.Ledger(Path(temporary))
            ledger.initialize()
            ledger.path.write_bytes(b"")
            with self.assertRaises(ValueError):
                ledger.read()


if __name__ == "__main__":
    unittest.main()
