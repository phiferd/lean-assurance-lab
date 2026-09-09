"""Pure closure-state checks; no scientific process is launched."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib import survivor_thread_config_regression_closure as c


def reservation(phase, cell):
    return {"phase": phase, "cell": cell}


def terminal(classification=None, binary=False):
    row = {"status": "COMPLETE", "returncode": 0, "cleanup_completed": True,
           "engineering_pause": False}
    if classification is not None:
        row["classification"] = classification
    if binary:
        row["binary"] = {"path": "external/binary", "sha256": "a" * 64}
    return row


def valid_state():
    rows = [
        (reservation("build", "baseline"), terminal(binary=True)),
        (reservation("build", "mutant"), terminal(binary=True)),
        (reservation("checker", 0), terminal("ACCEPT")),
        (reservation("checker", 1), terminal("ACCEPT")),
        (reservation("checker", 2), terminal("TYPECHECK_REFUSAL")),
        (reservation("checker", 3), terminal("ACCEPT")),
    ]
    return {"next_action": ("DONE", None), "repairs": [],
            "attempts": [{"reservation": r, "terminal": t} for r, t in rows],
            "charged_seconds": c.PROCESS_SECONDS}


class ClosureStateTests(unittest.TestCase):
    def test_exact_completed_state_passes(self):
        self.assertEqual(c.validate_state(valid_state())["charged_seconds"], c.PROCESS_SECONDS)

    def test_control_mismatch_is_rejected(self):
        state = valid_state()
        state["attempts"][2]["terminal"]["classification"] = "CRASH"
        with self.assertRaises(ValueError):
            c.validate_state(state)

    def test_repair_or_missing_cleanup_is_rejected(self):
        state = valid_state()
        state["repairs"] = [{"kind": "REPAIR"}]
        with self.assertRaises(ValueError):
            c.validate_state(state)
        state = valid_state()
        state["attempts"][5]["terminal"]["cleanup_completed"] = False
        with self.assertRaises(ValueError):
            c.validate_state(state)

    def test_accounting_drift_is_rejected(self):
        state = valid_state()
        state["charged_seconds"] += 1
        with self.assertRaises(ValueError):
            c.validate_state(state)


if __name__ == "__main__":
    unittest.main()
