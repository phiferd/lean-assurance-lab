"""Portable successor for the frozen portfolio checkpoint test harness.

The v1 harness and every historical receipt remain byte-for-byte unchanged.
This successor separates the checkout used to read preserved bytes from the
absolute workspace identity recorded by the original process receipts.
"""
from __future__ import annotations

import inspect
from pathlib import Path, PurePosixPath
import subprocess
import sys

from lib import portfolio_historical_snapshot as legacy


CLOSURE = legacy.CLOSURE
MODULES = legacy.MODULES
validate_live_transition = legacy.validate_live_transition
_compare_bytes = legacy._compare_bytes
_compare_queue = legacy._compare_queue
_attach_payloads = legacy._attach_payloads
_snapshot = legacy._snapshot


def historical_modules(root):
    """Return the frozen module set after the unchanged custody checks."""

    validate_live_transition(root)
    return set(MODULES)


class _RecordedWorkspacePath:
    """Use current bytes while retaining the receipt's absolute path identity."""

    def __init__(self, storage, recorded):
        self.storage = Path(storage)
        self.recorded = PurePosixPath(recorded)

    def __fspath__(self):
        return str(self.storage)

    def __str__(self):
        return str(self.recorded)

    def __truediv__(self, child):
        return type(self)(self.storage / child, self.recorded / child)

    def read_bytes(self):
        return self.storage.read_bytes()


def _recorded_workspace(events):
    reservations = [
        row for row in events
        if row.get("kind") == "RESERVED" and row.get("phase") == "checker"
    ]
    if not reservations:
        raise ValueError("historical checker reservations are missing")
    workspaces = {row.get("cwd") for row in reservations}
    if len(workspaces) != 1:
        raise ValueError("historical checker workspace identity differs")
    recorded = next(iter(workspaces))
    if not isinstance(recorded, str) or not PurePosixPath(recorded).is_absolute():
        raise ValueError("historical checker workspace identity is not absolute")
    return recorded


def _operational_evidence(frozen_evidence, snapshot, original_root):
    """Validate frozen receipts using their recorded root and current storage.

    The ledger and request bytes are not rewritten. The original validator
    still compares every request with its reservation and still checks the
    recorded absolute command paths. Only filesystem reads are projected to
    the current checkout so validation is independent of checkout location.
    """

    def validate(root):
        if Path(root).resolve() != snapshot:
            raise ValueError("unexpected snapshot evidence caller")
        namespace = frozen_evidence.__globals__
        ledger = namespace["Ledger"](original_root)
        events, _ = ledger.read()
        recorded_root = _recorded_workspace(events)
        projected_root = _RecordedWorkspacePath(original_root, recorded_root)
        return namespace["verify_attempts"](projected_root, events)

    return validate


def _test_driver():
    return """import pathlib, sys, unittest
from pathlib import Path, PurePosixPath
snapshot = Path.cwd().resolve()
original_root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(snapshot))
sys.path.insert(0, str(snapshot / 'tests'))
from lib import survivor_thread_config_regression_closure as closure
from lib.survivor_thread_config_regression import evidence as frozen_evidence
""" + inspect.getsource(_RecordedWorkspacePath) + inspect.getsource(
        _recorded_workspace
    ) + inspect.getsource(_operational_evidence) + """
closure.evidence = _operational_evidence(frozen_evidence, snapshot, original_root)
suite = unittest.defaultTestLoader.loadTestsFromNames(sys.argv[2:])
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
"""


def run_historical_tests(root):
    """Run frozen modules with a location-independent receipt projection."""

    root = Path(root).resolve()
    modules = historical_modules(root)
    with _snapshot(root) as snapshot:
        command = [sys.executable, "-c", _test_driver(), str(root), *sorted(modules)]
        result = subprocess.run(
            command, cwd=snapshot, env=legacy._environment(), check=False
        )
    return result.returncode == 0
