import importlib.machinery
import importlib.util
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("execution", str(ROOT / "scripts/publication_study_execution.py"))
spec = importlib.util.spec_from_loader(loader.name, loader)
execution = importlib.util.module_from_spec(spec); sys.modules[spec.name] = execution; loader.exec_module(execution)


class ExecutionLedgerTests(unittest.TestCase):
    def setup_case(self, td):
        root = Path(td); (root / "protocol").write_text("frozen"); (root / "negative").write_text("bad"); (root / "control").write_text("good")
        dep = {"path": "protocol", "sha256": execution.sha256_file(root / "protocol")}
        run = {"dependencies": [dep], "observer_ids": [f"o{i}" for i in range(4)], "budget": {"checker_executions": 8, "wall_seconds": 600, "checker_timeout_seconds": 30}}
        candidate = {"candidate_id": "pair1", "dependencies": [dep], "negative": {"path": "negative", "sha256": execution.sha256_file(root / "negative")}, "control": {"path": "control", "sha256": execution.sha256_file(root / "control")}}
        observers = [execution.Observer(f"o{i}", "a" * 64, ("fake", "{artifact}")) for i in range(4)]
        return root, run, candidate, observers

    def prepared(self, root, run, candidate):
        ledger = execution.ExecutionLedger(root / "ledger")
        session = ledger.begin(run, root)
        ledger.reserve_candidate(session, candidate["candidate_id"])
        ledger.freeze_candidate(session, candidate, root)
        return ledger, session

    def test_fixed_eight_order_and_raw_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            root, run, candidate, observers = self.setup_case(td); ledger, session = self.prepared(root, run, candidate); seen=[]
            def runner(o, a, timeout): seen.append((o.observer_id, a.name, timeout)); return execution.Capture(0, b"out", b"err", .5)
            result = execution.execute_protocol(session, run, candidate, observers, root=root, process_runner=runner, attribute=lambda o,a,c: "ACCEPT")
            self.assertEqual(result["terminal_state"], "COMPLETE"); self.assertEqual(len(seen), 8)
            self.assertEqual(seen, [(f"o{i}", x, 30.0) for i in range(4) for x in ("control", "negative")])
            self.assertTrue((root / "ledger/raw" / hashlib.sha256(b"out").hexdigest()).exists())

    def test_tampered_dependency_and_candidate_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root, run, candidate, observers = self.setup_case(td); (root / "protocol").write_text("changed")
            with self.assertRaises(execution.TamperError): execution.ExecutionLedger(root / "l").begin(run, root)
            root, run, candidate, observers = self.setup_case(td); (root / "negative").write_text("changed")
            ledger = execution.ExecutionLedger(root / "l"); session = ledger.begin(run, root); ledger.reserve_candidate(session, candidate["candidate_id"])
            with self.assertRaises(execution.TamperError): ledger.freeze_candidate(session, candidate, root)

    def test_pending_reservation_is_unresolved_not_retried(self):
        with tempfile.TemporaryDirectory() as td:
            root, run, candidate, observers = self.setup_case(td); ledger=execution.ExecutionLedger(root / "l"); session=ledger.begin(run, root); ledger.reserve_candidate(session, candidate["candidate_id"]); ch=ledger.freeze_candidate(session, candidate, root); rh=session.run_manifest_sha256
            r={"kind":"CHECKER_RESERVATION","run_manifest_sha256":rh,"candidate_manifest_sha256":ch,"candidate_id":"pair1","sequence":1,"observer_id":"o0","observer_configuration_sha256":"a"*64,"artifact_id":"control","artifact_sha256":execution.sha256_file(root / "control")}; ledger._reserve_launch(r)
            with self.assertRaises(execution.InterruptedReservation): execution.execute_protocol(session, run, candidate, observers, root=root, process_runner=lambda *x: None, attribute=lambda *x: "ACCEPT")

    def test_resume_rejects_tampered_raw_result(self):
        with tempfile.TemporaryDirectory() as td:
            root, run, candidate, observers = self.setup_case(td); ledger, session = self.prepared(root, run, candidate)
            execution.execute_protocol(session, run, candidate, observers, root=root, process_runner=lambda *x: execution.Capture(0, b"out", b"err", .1), attribute=lambda *x: "ACCEPT")
            (ledger.directory / "raw" / hashlib.sha256(b"out").hexdigest()).write_bytes(b"altered")
            with self.assertRaises(execution.TamperError):
                execution.execute_protocol(session, run, candidate, observers, root=root, process_runner=lambda *x: execution.Capture(0, b"", b"", .1), attribute=lambda *x: "ACCEPT")

    def test_active_session_and_candidate_reservations_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root, run, candidate, _ = self.setup_case(td); ledger = execution.ExecutionLedger(root / "l")
            session = ledger.begin(run, root)
            with self.assertRaises(execution.InterruptedReservation): ledger.begin(run, root)
            ledger.reserve_candidate(session, candidate["candidate_id"])
            with self.assertRaises(execution.InterruptedReservation): ledger.reserve_candidate(session, candidate["candidate_id"])
            ledger.finish(session, terminal_state="EXECUTION_UNRESOLVED")
            with self.assertRaises(execution.ActiveSession): ledger.begin(run, root)

    def test_budget_stops_before_ninth_or_overrun(self):
        with tempfile.TemporaryDirectory() as td:
            root, run, candidate, observers = self.setup_case(td); run["budget"]["wall_seconds"]=600
            ledger, session = self.prepared(root, run, candidate)
            tick = [590.0]
            session.started_monotonic = 0.0; session.clock = lambda: tick[0]
            calls=[]
            def runner(o,a,t): calls.append(t); tick[0] += t; return execution.Capture(0,b"",b"",t)
            # The remaining ten seconds constrain one launch; no second launch occurs.
            result = execution.execute_protocol(session, run, candidate, observers, root=root, process_runner=runner, attribute=lambda *x:"ACCEPT")
            self.assertEqual(result["terminal_state"], "BOUNDED_FAILURE_ATTEMPT_OR_TIME_BUDGET_EXHAUSTED")
            self.assertEqual(calls, [10.0])


if __name__ == "__main__": unittest.main()
