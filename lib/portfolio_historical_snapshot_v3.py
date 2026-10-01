"""Replay bound historical status tests while the live queue evolves.

The v1/v2 harnesses, old tests and scientific receipts remain unchanged.
Additional frozen modules run in the same original closure snapshot; new live
assertions are separate. The cached receipt projection preserves commands.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
import subprocess
import sys

from lib import portfolio_historical_snapshot_v2 as portable

legacy = portable.legacy
CLOSURE = portable.CLOSURE
EXTRA_MODULES = frozenset({
    "test_survivor_cache_historical",
    "test_survivor_fvar_reachability_historical",
    "test_survivor_thread_config_reachability_historical",
    "test_survivor_universe_diff_historical",
    "test_survivor_universe_equivalence_historical",
})
MODULES = portable.MODULES | EXTRA_MODULES


def _extra_paths(root):
    tree = legacy._tree(root)
    paths = {f"tests/{name}.py" for name in EXTRA_MODULES}
    pending = list(paths)
    while pending:
        path = pending.pop()
        if path not in tree:
            raise ValueError("unbound historical test/dependency: " + path)
        parsed = ast.parse(legacy._bytes(root, path), filename=path)
        for node in ast.walk(parsed):
            names = [node.module] if isinstance(node, ast.ImportFrom) else (
                [a.name for a in node.names] if isinstance(node, ast.Import) else [])
            for name in names:
                if name and name.startswith("lib."):
                    dependency = name.replace(".", "/") + ".py"
                    if dependency in tree and dependency not in paths:
                        paths.add(dependency)
                        pending.append(dependency)
    return paths - legacy.MUTABLE_STATE


def validate_live_transition(root):
    root = Path(root).resolve()
    result = portable.validate_live_transition(root)
    paths = _extra_paths(root)
    for path in sorted(paths):
        current = root / path
        if not current.is_file() or current.is_symlink():
            raise ValueError("frozen historical status input missing or linked: " + path)
        legacy._compare_bytes(path, current.read_bytes(), legacy._bytes(root, path))
    return {**result, "historical_modules": sorted(MODULES),
            "extra_preserved_paths": len(paths)}


def historical_modules(root):
    validate_live_transition(root)
    return set(MODULES)


def _test_driver():
    # The frozen cache validator expects ledger state, while the existing closure
    # validator expects the receipt replay result; retain each exact interface.
    extra = '''
from lib import survivor_cache_historical as cache_history
from lib import survivor_cache_runner as cache_runner
class _CacheWorkspacePath(_RecordedWorkspacePath):
    def relative_to(self, other):
        storage = other.storage if isinstance(other, _RecordedWorkspacePath) else other
        return self.storage.relative_to(storage)
def _cache_evidence(root):
    if Path(root).resolve() != snapshot:
        raise ValueError("unexpected cache snapshot evidence caller")
    events,state = cache_runner.Ledger(original_root).read()
    projected = _CacheWorkspacePath(original_root,_recorded_workspace(events))
    cache_runner.verify_attempts(projected,events)
    return state
cache_history.evidence = _cache_evidence
'''
    driver = portable._test_driver()
    anchor = "suite = unittest.defaultTestLoader.loadTestsFromNames(sys.argv[2:])"
    if driver.count(anchor) != 1:
        raise ValueError("historical driver anchor changed")
    return driver.replace(anchor, extra + "\n" + anchor)


def run_historical_tests(root):
    root = Path(root).resolve()
    modules = historical_modules(root)
    with portable._snapshot(root) as snapshot:
        command = [sys.executable, "-c", _test_driver(), str(root), *sorted(modules)]
        result = subprocess.run(command, cwd=snapshot,
                                env=legacy._environment(), check=False)
    return result.returncode == 0
