"""Preserve four completed checkpoint suites while the live portfolio advances.

The frozen code and evidence are unchanged. Content checks run at the exact
closure; the original execution-receipt validator retains its original absolute
workspace identity. This is not a portability repair for those old receipts.
"""
from __future__ import annotations

import ast
from contextlib import contextmanager
import inspect
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import tempfile
import types

from lib.research_queue_v3 import load_queue


CLOSURE = "9b9c22a9e2c615fc0fe47ca66bea229ce0fa6718"
MODULES = frozenset({
    "test_survivor_cache_predicate_transfer",
    "test_nanoda_zero_thread_upstream_closure",
    "test_survivor_thread_config_regression_historical",
    "test_survivor_universe_diff",
})
BASES = (
    "results/research/survivor-cache-predicate-transfer-1/",
    "results/research/nanoda-zero-thread-upstream-readiness-1/",
    "results/research/survivor-thread-config-regression-1/",
    "results/research/survivor-universe-diff-1/",
)
MUTABLE_STATE = frozenset({
    "config/research-queue.json", "docs/RESEARCH_STATUS.md",
    "docs/RESEARCH_WORKFLOW.md", "results/assurance/current.json",
    "results/assurance/current-mutation-report.json",
})
APPEND_ONLY = frozenset({"results/mutants/registry.jsonl", "results/survivors/inventory.jsonl"})
PAYLOAD_PREFIXES = ("external", "results/coverage")
BOUND_DOCUMENTS = (
    BASES[0] + "evidence-manifest.json", BASES[0] + "work-record.json",
    BASES[0] + "predicate-transfer-assessment.json", BASES[0] + "historical-transition.json",
    BASES[1] + "evidence-manifest.json", BASES[2] + "evidence-manifest.json",
    "config/survivor-thread-config-regression-0001.json",
    BASES[3] + "evidence-manifest.json", BASES[3] + "work-record.json",
    BASES[3] + "reachability-assessment.json", BASES[3] + "historical-transition.json",
)
VALIDATORS = (
    "scripts/validate-survivor-cache-predicate-transfer",
    "scripts/validate-survivor-cache-predicate-transfer-historical",
    "lib/nanoda_zero_thread_upstream_closure.py",
    "lib/survivor_thread_config_regression_historical.py",
    "lib/survivor_thread_config_regression_closure.py",
    "lib/survivor_thread_config_regression.py",
)


def _environment():
    environment = os.environ.copy()
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "PYTHONPATH"):
        environment.pop(name, None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    return environment


def _git(root, *args):
    result = subprocess.run(["git", *args], cwd=root, env=_environment(),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise ValueError("portfolio historical Git input unavailable: " + " ".join(args))
    return result.stdout


def _bytes(root, path):
    return _git(root, "show", f"{CLOSURE}:{path}")


def _tree(root):
    if _git(root, "rev-parse", "--verify", f"{CLOSURE}^{{commit}}").decode().strip() != CLOSURE:
        raise ValueError("portfolio historical closure does not resolve exactly")
    return set(_git(root, "ls-tree", "-r", "-z", "--name-only", CLOSURE).decode().split("\0")) - {""}


def _bound_paths(value):
    if isinstance(value, dict):
        if isinstance(value.get("path"), str) and "sha256" in value:
            yield value["path"]
        for child in value.values():
            yield from _bound_paths(child)
    elif isinstance(value, list):
        for child in value:
            yield from _bound_paths(child)


def _preserved_paths(root, tree):
    paths = {path for path in tree if path.startswith(BASES)}
    paths.update(f"tests/{module}.py" for module in MODULES)
    paths.update(VALIDATORS)
    paths.update(BOUND_DOCUMENTS)
    for document in BOUND_DOCUMENTS:
        paths.update(path for path in _bound_paths(json.loads(_bytes(root, document))) if path in tree)
    # Include every direct/transitive repository import used by the unchanged
    # receipt validator and bound tests. Dynamic historical code remains loaded
    # from its original Git commit by the frozen validators themselves.
    pending = list(paths)
    inspected = set()
    while pending:
        path = pending.pop()
        if path in inspected or not (path.endswith(".py") or path.startswith("scripts/")):
            continue
        inspected.add(path)
        try:
            parsed = ast.parse(_bytes(root, path), filename=path)
        except SyntaxError:
            continue  # Shell entry points are preserved byte-for-byte too.
        for node in ast.walk(parsed):
            names = [node.module] if isinstance(node, ast.ImportFrom) else (
                [alias.name for alias in node.names] if isinstance(node, ast.Import) else [])
            for name in names:
                if name and name.startswith("lib."):
                    dependency = name.replace(".", "/") + ".py"
                    if dependency in tree and dependency not in paths:
                        paths.add(dependency)
                        pending.append(dependency)
    missing = paths - tree
    if missing:
        raise ValueError("historical selection contains unbound paths: " + ", ".join(sorted(missing)))
    return paths - MUTABLE_STATE


def _compare_bytes(path, current, frozen):
    if path in APPEND_ONLY:
        if not frozen.endswith(b"\n") or not current.startswith(frozen):
            raise ValueError("frozen append-only prefix changed: " + path)
    elif current != frozen:
        raise ValueError("frozen portfolio input changed: " + path)


def _compare_queue(old, current):
    by_id = {row["id"]: row for row in current["items"]}
    for previous in old["items"]:
        if previous["status"] != "COMPLETE":
            continue
        actual = by_id.get(previous["id"])
        omit_priority = lambda row: {key: value for key, value in row.items() if key != "priority"}
        if actual is None or omit_priority(actual) != omit_priority(previous):
            raise ValueError("completed predecessor queue record changed: " + previous["id"])
    selected = by_id.get(current["selected_item"])
    if selected is None or selected["status"] not in {"READY", "ACTIVE"}:
        raise ValueError("current portfolio selection is not executable")


def validate_live_transition(root):
    """Check live custody and current queue separately from old assertions."""
    root = Path(root).resolve()
    tree = _tree(root)
    paths = _preserved_paths(root, tree)
    for path in sorted(paths):
        current = root / path
        if not current.is_file() or current.is_symlink():
            raise ValueError("frozen portfolio input missing or linked: " + path)
        _compare_bytes(path, current.read_bytes(), _bytes(root, path))
    old = json.loads(_bytes(root, "config/research-queue.json"))
    current = load_queue(root, require_ready=True)
    _compare_queue(old, current)
    return {"status": "PASS", "historical_commit": CLOSURE,
            "preserved_paths": len(paths), "selected_item": current["selected_item"],
            "historical_modules": sorted(MODULES)}


def historical_modules(root):
    """Return the exact four modules only after fail-closed custody checks."""
    validate_live_transition(root)
    return set(MODULES)


def _archive_helper(root):
    module = types.ModuleType("portfolio_bound_archive_helper")
    module.__file__ = CLOSURE + ":scripts/publication_study_history.py"
    code = _bytes(root, "scripts/publication_study_history.py")
    exec(compile(code, module.__file__, "exec"), module.__dict__)
    return module


def _attach_payloads(root, snapshot, tree):
    for prefix in PAYLOAD_PREFIXES:
        source = root / prefix
        if not source.is_dir():
            continue
        if any(path == prefix or path.startswith(prefix + "/") for path in tree):
            raise ValueError("refusing payload over tracked historical path: " + prefix)
        destination = snapshot / prefix
        if destination.exists() or destination.is_symlink():
            raise ValueError("refusing payload over existing snapshot path: " + prefix)
        parent = destination.parent
        mode = stat.S_IMODE(parent.stat().st_mode)
        parent.chmod(mode | stat.S_IWUSR)
        try:
            destination.symlink_to(source, target_is_directory=True)
        finally:
            parent.chmod(mode)


@contextmanager
def _snapshot(root):
    tree = _tree(root)
    helper = _archive_helper(root)
    with tempfile.TemporaryDirectory(prefix="portfolio-history-") as temporary:
        snapshot = Path(temporary, "snapshot")
        snapshot.mkdir()
        errors = helper._archive_snapshot(root, CLOSURE, snapshot)
        if errors:
            raise ValueError("historical archive validation failed: " + "; ".join(errors))
        mode = stat.S_IMODE(snapshot.stat().st_mode)
        snapshot.chmod(mode | stat.S_IWUSR)
        try:
            git_path = snapshot / ".git"
            if git_path.exists() or git_path.is_symlink():
                raise ValueError("refusing historical Git-link overwrite")
            git_dir = _git(root, "rev-parse", "--absolute-git-dir").decode().strip()
            git_path.write_text(f"gitdir: {git_dir}\n", encoding="utf-8")
        finally:
            snapshot.chmod(mode)
        _attach_payloads(root, snapshot, tree)
        yield snapshot


def _operational_evidence(frozen_evidence, snapshot, original_root):
    """Keep original cwd/argv checks at their recorded absolute root.

    The unchanged function comes from the archive. Its failures propagate;
    nothing rewrites receipts or substitutes successful evidence.
    """
    def validate(root):
        if Path(root).resolve() != snapshot:
            raise ValueError("unexpected snapshot evidence caller")
        return frozen_evidence(original_root)
    return validate


def _test_driver():
    return """import pathlib, sys, unittest
from pathlib import Path
snapshot = Path.cwd().resolve()
original_root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(snapshot))
sys.path.insert(0, str(snapshot / 'tests'))
from lib import survivor_thread_config_regression_closure as closure
from lib.survivor_thread_config_regression import evidence as frozen_evidence
""" + inspect.getsource(_operational_evidence) + """
closure.evidence = _operational_evidence(frozen_evidence, snapshot, original_root)
suite = unittest.defaultTestLoader.loadTestsFromNames(sys.argv[2:])
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
"""


def run_historical_tests(root):
    """Run the complete unchanged modules and their original validator calls."""
    root = Path(root).resolve()
    modules = historical_modules(root)
    with _snapshot(root) as snapshot:
        command = [sys.executable, "-c", _test_driver(), str(root), *sorted(modules)]
        result = subprocess.run(command, cwd=snapshot, env=_environment(), check=False)
    return result.returncode == 0
