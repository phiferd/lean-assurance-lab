"""Small, prospective controls for a repository item closure.

The scope file declares which inputs the item binds. This module verifies those
bytes exactly; it does not infer that the declaration covers every scientific
input or replace any item-specific validator.
"""
from __future__ import annotations

from datetime import datetime, timezone
from contextlib import contextmanager
import fcntl
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import os
import tempfile
from typing import Iterator

ROOT = Path(__file__).resolve().parents[1]
SUITE = ["scripts/run-unit-tests-with-signal-retry", "--require-full-payload"]
STATUS_PREFLIGHT = ["python3", "-m", "unittest", "discover", "-s", "tests",
                    "-p", "test_arena_let_regression_erratum.py"]
CHECKS = [
    ["scripts/validate-research-queue", "--require-ready"],
    ["scripts/build-external-contributions", "--check"],
    ["scripts/build-project-review", "--check"],
    ["scripts/artifact-status", "--require-current"],
    ["git", "diff", "--check"],
]


def _git(root: Path, *args: str) -> bytes:
    result = subprocess.run(["git", *args], cwd=root, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise ValueError(f"git {' '.join(args[:2])} failed: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def host_rss_preflight(*, run=subprocess.run, pid: int | None = None) -> dict:
    """Exercise the actual /bin/ps backend and require positive self RSS."""
    if pid is None:
        pid = os.getpid()
    command = ["/bin/ps", "-o", "rss=", "-p", str(pid)]
    try:
        result = run(command, capture_output=True, text=True, check=False)
    except OSError as error:
        raise ValueError(f"host RSS preflight failed: {error}; enable /bin/ps for this execution context before the full suite") from error
    raw = result.stdout.strip()
    if result.returncode or not re.fullmatch(r"[0-9]+", raw) or int(raw) <= 0:
        raise ValueError(f"host RSS preflight failed: /bin/ps returned {result.returncode}, stdout={raw!r}, stderr={result.stderr.strip()!r}; enable /bin/ps for this execution context before the full suite")
    return {"command": command, "rss_kib": int(raw), "status": "PASS"}


STAGE_DEPENDENCY_KEYS = {"status", "suite", "publication"}


def _scope(root: Path, scope_file: str) -> tuple[str, list[str], dict[str, list[str]], dict[str, list[str]]]:
    path = Path(scope_file)
    if path.is_absolute() or path.as_posix().startswith("../") or ".." in path.parts:
        raise ValueError("scope file must be a repository-relative path")
    try:
        scope = json.loads((root / path).read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"could not read scope file: {error}") from error
    allowed_fields = {"schema_version", "scope", "paths", "stage_dependencies",
                      "stage_dependency_trees"}
    if (not isinstance(scope, dict) or not set(scope).issubset(allowed_fields)
        or scope.get("schema_version") not in {1, 2, 3}
        or not isinstance(scope["scope"], str) or not scope["scope"].strip()
        or not isinstance(scope["paths"], list) or not scope["paths"]):
        raise ValueError("invalid declared inventory scope")
    paths = [scope_file, *scope["paths"]]
    if (any(not isinstance(p, str) or not p or Path(p).is_absolute()
            or ".." in Path(p).parts or Path(p).as_posix() != p for p in paths)
        or len(set(paths)) != len(paths) or scope["paths"] != sorted(scope["paths"])):
        raise ValueError("scope paths must be sorted, unique repository-relative files")
    if scope["schema_version"] == 1:
        if "stage_dependencies" in scope or "stage_dependency_trees" in scope:
            raise ValueError("schema v1 cannot declare stage dependencies")
        dependencies = {name: list(paths) for name in STAGE_DEPENDENCY_KEYS}
        tree_dependencies = {name: [] for name in STAGE_DEPENDENCY_KEYS}
    else:
        dependencies = scope.get("stage_dependencies")
        if (not isinstance(dependencies, dict)
                or set(dependencies) != STAGE_DEPENDENCY_KEYS):
            raise ValueError("schema v2 must declare status, suite and publication dependencies")
        declared = set(scope["paths"])
        for name, values in dependencies.items():
            if (not isinstance(values, list) or not values
                    or values != sorted(values) or len(values) != len(set(values))
                    or any(not isinstance(value, str) or value not in declared
                           for value in values)):
                raise ValueError(f"invalid {name} stage dependencies")
        if set(dependencies["publication"]) != declared:
            raise ValueError("publication dependencies must cover every declared path")
        if set().union(*(set(values) for values in dependencies.values())) != declared:
            raise ValueError("every declared path must belong to at least one stage dependency set")
        dependencies = {name: [scope_file, *values]
                        for name, values in dependencies.items()}
        tree_dependencies = scope.get("stage_dependency_trees")
        if scope["schema_version"] == 2:
            if tree_dependencies is not None:
                raise ValueError("schema v2 cannot declare tree dependencies")
            tree_dependencies = {name: [] for name in STAGE_DEPENDENCY_KEYS}
        elif (not isinstance(tree_dependencies, dict)
              or set(tree_dependencies) != STAGE_DEPENDENCY_KEYS):
            raise ValueError("schema v3 must declare status, suite and publication tree dependencies")
        else:
            for name, values in tree_dependencies.items():
                if (not isinstance(values, list) or values != sorted(values)
                        or len(values) != len(set(values))
                        or any(not isinstance(value, str) or not value
                               or Path(value).is_absolute() or ".." in Path(value).parts
                               or Path(value).as_posix() != value for value in values)):
                    raise ValueError(f"invalid {name} stage tree dependencies")
            if not set(tree_dependencies["status"] + tree_dependencies["suite"]).issubset(
                    set(tree_dependencies["publication"])):
                raise ValueError("publication tree dependencies must cover status and suite trees")
    return scope["scope"], paths, dependencies, tree_dependencies


def _tree_binding(root: Path, relative: str) -> dict:
    path = root / relative
    if path.is_symlink() or not path.is_dir() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"declared dependency tree is absent or unsafe: {relative}")
    changed = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", relative],
                             cwd=root, check=False).returncode
    if changed:
        raise ValueError(f"declared dependency tree differs from committed bytes: {relative}")
    tree = _git(root, "rev-parse", f"HEAD:{relative}").decode().strip()
    kind = _git(root, "cat-file", "-t", tree).decode().strip()
    if kind != "tree":
        raise ValueError(f"declared dependency is not a Git tree: {relative}")
    return {"path": relative, "git_tree": tree}


_HOST_DIGEST_CACHE: dict[tuple[str, int, int, int, int], str] = {}


def _cached_file_sha(path: Path) -> str:
    stat = path.stat()
    key = (path.resolve().as_posix(), stat.st_ino, stat.st_size,
           stat.st_mtime_ns, stat.st_ctime_ns)
    digest = _HOST_DIGEST_CACHE.get(key)
    if digest is None:
        digest = _sha(path.read_bytes())
        _HOST_DIGEST_CACHE[key] = digest
    return digest


def _host_payload_inventory(root: Path) -> list[dict]:
    freeze = root / "results/research/declaration-validation-publication-study-gate-8-input-freeze.json"
    if not freeze.is_file():
        return []
    document = json.loads(freeze.read_text(encoding="utf-8"))
    bindings: dict[str, dict] = {}
    for observer in document["observer_profiles"]:
        row = observer["binary"]
        bindings[row["path"]] = row
    for inventory in document["materialized_corpora"]:
        if inventory["root"].startswith("external/"):
            for row in inventory["files"]:
                path = f"{inventory['root']}/{row['path']}"
                bindings[path] = {"path": path, "bytes": row["bytes"],
                                  "sha256": row["sha256"]}
    coverage = document["existing_coverage_excerpt"]
    for key in ("line_to_tests_binding", "test_to_lines_binding"):
        row = coverage[key]
        bindings[row["path"]] = row
    for profile in document["comparator_profiles"].values():
        for key in ("manifest", "build_manifest", "collection_state", "configuration"):
            row = profile.get(key)
            if row and "path" in row:
                bindings[row["path"]] = row
    rows = []
    for relative, expected in sorted(bindings.items()):
        path = root / relative
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"required host payload is missing or linked: {relative}")
        digest = _cached_file_sha(path)
        if digest != expected["sha256"] or ("bytes" in expected and path.stat().st_size != expected["bytes"]):
            raise ValueError(f"required host payload differs: {relative}")
        rows.append({"path": relative, "bytes": path.stat().st_size, "sha256": digest})
    arena = root / "external/lean-kernel-arena"
    if arena.is_dir():
        revision = _git(arena, "rev-parse", "HEAD").decode().strip()
        rows.append({"path": "external/lean-kernel-arena", "git_commit": revision})
    return rows


def committed_inventory(root: Path, scope_file: str) -> dict:
    scope, paths, dependencies, tree_dependencies = _scope(root, scope_file)
    commit = _git(root, "rev-parse", "--verify", "HEAD^{commit}").decode().strip()
    rows = []
    for path in paths:
        source = root / path
        if not source.is_file() or source.is_symlink() or not source.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"declared input is absent or unsafe: {path}")
        blob = _git(root, "rev-parse", f"HEAD:{path}").decode().strip()
        committed = _git(root, "cat-file", "blob", blob)
        actual = source.read_bytes()
        if actual != committed:
            raise ValueError(f"declared input differs from committed bytes: {path}")
        rows.append({"path": path, "git_blob": blob, "sha256": _sha(actual), "bytes": len(actual)})
    tree_paths = sorted(set().union(*(set(values) for values in tree_dependencies.values())))
    trees = [_tree_binding(root, path) for path in tree_paths]
    return {"schema_version": 3, "scope": scope, "scope_file": scope_file,
            "commit": commit, "files": rows, "stage_dependencies": dependencies,
            "trees": trees, "stage_dependency_trees": tree_dependencies,
            "host_payload": _host_payload_inventory(root)}


def dependency_inventory(inventory: dict, dependency_set: str) -> dict:
    """Return the content-only inputs for one stage, deliberately excluding HEAD."""
    if dependency_set not in STAGE_DEPENDENCY_KEYS:
        raise ValueError(f"unknown stage dependency set: {dependency_set}")
    rows = inventory.get("files")
    if not isinstance(rows, list):
        raise ValueError("inventory has no file bindings")
    by_path = {row.get("path"): row for row in rows if isinstance(row, dict)}
    declared = inventory.get("stage_dependencies")
    paths = declared.get(dependency_set) if isinstance(declared, dict) else list(by_path)
    if (not isinstance(paths, list) or len(paths) != len(set(paths))
            or any(path not in by_path for path in paths)):
        raise ValueError(f"inventory has incomplete {dependency_set} dependencies")
    tree_rows = inventory.get("trees", [])
    tree_by_path = {row.get("path"): row for row in tree_rows if isinstance(row, dict)}
    tree_sets = inventory.get("stage_dependency_trees", {})
    tree_paths = tree_sets.get(dependency_set, []) if isinstance(tree_sets, dict) else []
    if (not isinstance(tree_paths, list) or len(tree_paths) != len(set(tree_paths))
            or any(path not in tree_by_path for path in tree_paths)):
        raise ValueError(f"inventory has incomplete {dependency_set} tree dependencies")
    value = {"schema_version": 2, "scope_file": inventory.get("scope_file"),
             "dependency_set": dependency_set, "files": [by_path[path] for path in paths],
             "trees": [tree_by_path[path] for path in tree_paths]}
    if dependency_set in {"suite", "publication"}:
        value["host_payload"] = inventory.get("host_payload", [])
    return value


def matching_publication_inputs(root: Path, scope_file: str, validated: dict) -> dict:
    """Require current publication bytes to match the validated content snapshot."""
    current = committed_inventory(root, scope_file)
    expected = dependency_inventory(validated, "publication")
    actual = dependency_inventory(current, "publication")
    if actual != expected:
        raise ValueError("publication inputs no longer match validated snapshot")
    return actual


@contextmanager
def validation_snapshot(root: Path, inventory: dict) -> Iterator[Path]:
    """Materialize the bound commit away from the mutable publication worktree."""
    parent = Path(tempfile.mkdtemp(prefix="lean-assurance-validation-snapshot-"))
    checkout = parent / "checkout"
    added = False
    try:
        result = subprocess.run(
            ["git", "worktree", "add", "--detach", str(checkout), inventory["commit"]],
            cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if result.returncode:
            raise ValueError("could not materialize validation snapshot: "
                             + result.stderr.decode(errors="replace").strip())
        added = True
        # Full-payload integration data are intentionally ignored by Git. Their
        # item validators bind their exact bytes; expose the same host payload to
        # the isolated tracked checkout without copying tens of gigabytes.
        arena = root / "external/lean-kernel-arena"
        if arena.is_dir():
            target = checkout / "external/lean-kernel-arena"
            shutil.copytree(arena, target, ignore=shutil.ignore_patterns("_build"))
            arena_build = arena / "_build"
            if arena_build.is_dir():
                _clone_tree(arena_build, target / "_build")
        coverage = root / "results/coverage"
        if coverage.is_dir():
            _clone_tree(coverage, checkout / "results/coverage")
        snapshot_inventory = committed_inventory(checkout, inventory["scope_file"])
        for name in STAGE_DEPENDENCY_KEYS:
            if dependency_inventory(snapshot_inventory, name) != dependency_inventory(inventory, name):
                raise ValueError(f"materialized validation snapshot changed {name} inputs")
        yield checkout
    finally:
        if added:
            subprocess.run(["git", "worktree", "remove", "--force", str(checkout)],
                           cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           check=False)
        shutil.rmtree(parent, ignore_errors=True)
        subprocess.run(["git", "worktree", "prune"], cwd=root,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def _clone_tree(source: Path, target: Path) -> None:
    """Create an isolated tree, using copy-on-write where the host supports it."""
    result = subprocess.run(["cp", "-cR", str(source), str(target)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        shutil.copytree(source, target)


def write_new(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as output:
        json.dump(value, output, indent=2)
        output.write("\n")


def _run_logged(root: Path, command: list[str], log: Path, *, env=None) -> int:
    with log.open("xb") as output:
        result = subprocess.run(command, cwd=root, stdout=output, stderr=subprocess.STDOUT,
                                env=env, check=False)
    return result.returncode


def finish(root: Path, scope_file: str, output_dir: Path) -> int:
    """Validate once, seal validation, generate, then verify fresh outputs."""
    output_dir.mkdir(parents=True, exist_ok=False)
    terminal = {"schema_version": 1, "status": "FAILED", "completed_steps": []}
    try:
        preflight = host_rss_preflight()
        write_new(output_dir / "preflight.json", preflight)
        terminal["completed_steps"].append("host-rss-preflight")
        before = committed_inventory(root, scope_file)
        write_new(output_dir / "input-inventory.json", before)
        terminal["completed_steps"].append("committed-input-inventory")
        status_log = output_dir / "status-preflight.log"
        code = _run_logged(root, STATUS_PREFLIGHT, status_log)
        terminal["status_preflight_returncode"] = code
        if code:
            raise ValueError(f"status/queue readiness preflight failed ({code}); see {status_log}")
        terminal["completed_steps"].append("status-queue-readiness-preflight")
        env = os.environ.copy()
        env["METAMORPHIC_SUPERVISOR_RECEIPT_DIR"] = str(output_dir / "supervisor-receipts")
        suite_log = output_dir / "full-suite.log"
        code = _run_logged(root, SUITE, suite_log, env=env)
        terminal["full_suite_returncode"] = code
        if code:
            raise ValueError(f"full current/historical suite failed ({code}); see {suite_log}")
        if committed_inventory(root, scope_file) != before:
            raise ValueError("declared committed inputs changed during full suite")
        terminal["completed_steps"].append("full-current-historical-suite")
        validation = {"schema_version": 1, "status": "PASS", "validated_at": datetime.now(timezone.utc).isoformat(),
                      "commit": before["commit"], "scope_file": scope_file,
                      "input_inventory_sha256": _sha((output_dir / "input-inventory.json").read_bytes()),
                      "suite_command": SUITE, "suite_log_sha256": _sha(suite_log.read_bytes()),
                      "suite_returncode": code}
        write_new(output_dir / "validation.json", validation)
        terminal["completed_steps"].append("sealed-validation-record")
        refresh_log = output_dir / "refresh.log"
        refresh_dir = output_dir / "refresh"
        code = _run_logged(root, ["scripts/refresh-current-state", "--log-dir", str(refresh_dir)], refresh_log)
        terminal["refresh_returncode"] = code
        if code:
            raise ValueError(f"current-state generation failed ({code}); see {refresh_log}")
        terminal["completed_steps"].append("dependency-ordered-refresh")
        for index, command in enumerate(CHECKS, 1):
            log = output_dir / f"check-{index:02d}.log"
            code = _run_logged(root, command, log)
            if code:
                raise ValueError(f"freshness check failed ({code}): {' '.join(command)}; see {log}")
            terminal["completed_steps"].append(" ".join(command))
        if committed_inventory(root, scope_file) != before:
            raise ValueError("declared committed inputs changed during generation or final checks")
        terminal["completed_steps"].append("final-committed-input-check")
        terminal["status"] = "COMPLETE"
        return 0
    except (ValueError, OSError) as error:
        terminal["error"] = str(error)
        print(str(error), file=sys.stderr)
        return 1
    finally:
        write_new(output_dir / "result.json", terminal)


class UnknownInvalidation(ValueError):
    """A cached stage or its output changed without a declared dependency change."""


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _file_binding(path: Path, base: Path) -> dict:
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(base.resolve()):
        raise UnknownInvalidation(f"unsafe or missing stage output: {path}")
    raw = path.read_bytes()
    return {"path": path.relative_to(base).as_posix(), "bytes": len(raw),
            "sha256": _sha(raw)}


def _tree_bindings(directory: Path, base: Path, *, omit: set[str] | None = None) -> list[dict]:
    omit = omit or set()
    files = []
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise UnknownInvalidation(f"symlink in stage output: {path}")
        if path.is_file() and path.relative_to(directory).as_posix() not in omit:
            files.append(_file_binding(path, base))
    return files


def _load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise UnknownInvalidation(f"cannot validate cached stage receipt: {path}: {error}") from error
    if type(value) is not dict:
        raise UnknownInvalidation(f"cached stage receipt is not an object: {path}")
    return value


def _command_identity(root: Path, command: list[str]) -> dict:
    """Bind the command plus the executable bytes used by this checkout/host."""
    candidate = root / command[0]
    executable = candidate if candidate.is_file() else Path(shutil.which(command[0]) or "")
    if not executable.is_file():
        raise ValueError(f"cannot resolve closure command executable: {command[0]}")
    raw = executable.resolve().read_bytes()
    identity = {"command": command, "executable_sha256": _sha(raw),
                "executable_bytes": len(raw)}
    if candidate.is_file():
        identity["executable"] = command[0]
    else:
        identity["executable"] = executable.resolve().as_posix()
    return identity


def _worktree_digest(root: Path) -> str:
    return _sha(_git(root, "diff", "--binary"))


def _lock_path(root: Path) -> Path:
    key = _sha(root.resolve().as_posix().encode())[:24]
    return Path(tempfile.gettempdir()) / f"lean-assurance-closure-{key}.lock"


@contextmanager
def closure_owner(root: Path):
    """Hold one OS-released repository closure lock for the complete lifecycle."""
    path = _lock_path(root)
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError("another closure owner holds the repository lock") from error
        os.ftruncate(descriptor, 0)
        os.write(descriptor, _canonical({"schema_version": 1, "pid": os.getpid(),
                                         "root_sha256": _sha(root.resolve().as_posix().encode())}) + b"\n")
        yield {"path": path.name, "pid": os.getpid()}
    finally:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)


def _next_directory(parent: Path) -> Path:
    parent.mkdir(parents=True, exist_ok=True)
    numbers = [int(path.name) for path in parent.iterdir()
               if path.is_dir() and re.fullmatch(r"[0-9]{4}", path.name)]
    path = parent / f"{(max(numbers, default=0) + 1):04d}"
    path.mkdir()
    return path


def _latest_receipt(stage_root: Path) -> tuple[Path, dict] | None:
    if not stage_root.is_dir():
        return None
    receipts = sorted(stage_root.glob("[0-9][0-9][0-9][0-9]/receipt.json"))
    if not receipts:
        return None
    path = receipts[-1]
    return path, _load_json(path)


def _validate_cached_receipt(receipt_path: Path, receipt: dict, output_root: Path,
                             stage: str) -> None:
    required = {"schema_version", "stage", "status", "specification_sha256",
                "command", "returncode", "outputs"}
    if (set(receipt) != required or receipt.get("schema_version") != 1
            or receipt.get("stage") != stage or receipt.get("status") != "PASS"
            or receipt.get("returncode") != 0 or type(receipt.get("outputs")) is not list):
        raise UnknownInvalidation(f"unknown cached stage receipt shape: {receipt_path}")
    stage_dir = receipt_path.parent
    for path in stage_dir.rglob("*"):
        if path.is_symlink():
            raise UnknownInvalidation(f"symlink in cached stage output: {path}")
        if path.is_dir() and not any(path.iterdir()):
            raise UnknownInvalidation(f"untracked empty directory in cached stage output: {path}")
    expected = {row.get("path") for row in receipt["outputs"]}
    if (None in expected or len(expected) != len(receipt["outputs"])
            or any(set(row) != {"path", "bytes", "sha256"} for row in receipt["outputs"])):
        raise UnknownInvalidation(f"invalid cached output inventory: {receipt_path}")
    actual = {path.relative_to(output_root).as_posix() for path in stage_dir.rglob("*")
              if path.is_file() and path != receipt_path}
    if actual != expected:
        raise UnknownInvalidation(f"cached stage output set changed: {stage}")
    for row in receipt["outputs"]:
        if _file_binding(output_root / row["path"], output_root) != row:
            raise UnknownInvalidation(f"cached stage output bytes changed: {row['path']}")


def _stage_spec(*, stage: str, inventory: dict, prior: list[dict], command: list[str],
                identity: dict, worktree_sha256: str | None = None) -> tuple[dict, str]:
    spec = {"schema_version": 1, "stage": stage, "inventory_sha256": _sha(_canonical(inventory)),
            "prior_receipts": prior, "command_identity": identity}
    if worktree_sha256 is not None:
        spec["worktree_diff_sha256"] = worktree_sha256
    return spec, _sha(_canonical(spec))


def _receipt_ref(path: Path, output_root: Path) -> dict:
    return _file_binding(path, output_root)


def _run_command_stage(root: Path, output_root: Path, stage: str, command: list[str],
                       inventory: dict, prior: list[dict], attempt: dict, *, env=None,
                       bind_worktree: bool = False,
                       execution_root: Path | None = None) -> dict:
    stage_root = output_root / "stages" / stage
    command_root = execution_root or root
    identity = _command_identity(command_root, command)
    spec, spec_hash = _stage_spec(stage=stage, inventory=inventory, prior=prior,
                                  command=command, identity=identity,
                                  worktree_sha256=_worktree_digest(root) if bind_worktree else None)
    latest = _latest_receipt(stage_root)
    if latest is not None:
        receipt_path, receipt = latest
        _validate_cached_receipt(receipt_path, receipt, output_root, stage)
        if receipt["specification_sha256"] == spec_hash:
            attempt["reused_stages"].append(stage)
            return _receipt_ref(receipt_path, output_root)
        attempt["invalidated_stages"].append({
            "stage": stage,
            "reason": "DECLARED_DEPENDENCY_CHANGED",
            "prior_receipt": _receipt_ref(receipt_path, output_root),
        })
    stage_dir = _next_directory(stage_root)
    log = stage_dir / "command.log"
    failure_path = stage_dir / "failure.json"
    actual_command = [part.replace("{stage_dir}", str(stage_dir)) for part in command]
    actual_env = None
    collected_receipts = None
    if env is not None:
        if any("{control_receipts}" in value for value in env.values()):
            collected_receipts = Path(tempfile.mkdtemp(
                prefix=".closure-control-receipts-", dir=command_root))
        actual_env = {name: value.replace("{stage_dir}", str(stage_dir))
                                      .replace("{control_receipts}", str(collected_receipts or ""))
                      for name, value in env.items()}
    def collect_control_receipts() -> None:
        if collected_receipts is not None and collected_receipts.is_dir():
            shutil.copytree(collected_receipts, stage_dir / "control-receipts")
            shutil.rmtree(collected_receipts)
    try:
        code = _run_logged(command_root, actual_command, log, env=actual_env)
    except BaseException as error:
        collect_control_receipts()
        controls = {"schema_version": 1, "stage": stage, "status": "INTERRUPTED",
                    "specification_sha256": spec_hash, "command": actual_command,
                    "error_type": type(error).__name__,
                    "outputs": _tree_bindings(stage_dir, output_root, omit={"failure.json"})}
        write_new(failure_path, controls)
        raise
    collect_control_receipts()
    if code:
        write_new(failure_path, {"schema_version": 1, "stage": stage, "status": "FAILED",
                  "specification_sha256": spec_hash, "command": actual_command,
                  "returncode": code,
                  "outputs": _tree_bindings(stage_dir, output_root, omit={"failure.json"})})
        raise ValueError(f"closure stage failed ({code}): {stage}; see {log}")
    receipt_path = stage_dir / "receipt.json"
    outputs = _tree_bindings(stage_dir, output_root, omit={"receipt.json"})
    write_new(receipt_path, {"schema_version": 1, "stage": stage, "status": "PASS",
              "specification_sha256": spec_hash, "command": actual_command,
              "returncode": 0, "outputs": outputs})
    attempt["executed_stages"].append(stage)
    return _receipt_ref(receipt_path, output_root)


def _run_value_stage(output_root: Path, stage: str, value: dict, inventory: dict,
                     prior: list[dict], attempt: dict) -> dict:
    stage_root = output_root / "stages" / stage
    command = ["internal", stage]
    identity = {"command": command, "implementation": "lib/closure_controls_v2.py",
                "implementation_sha256": _sha(Path(__file__).read_bytes())}
    spec, spec_hash = _stage_spec(stage=stage, inventory=inventory, prior=prior,
                                  command=command, identity=identity)
    latest = _latest_receipt(stage_root)
    if latest is not None:
        receipt_path, receipt = latest
        _validate_cached_receipt(receipt_path, receipt, output_root, stage)
        if receipt["specification_sha256"] == spec_hash:
            attempt["reused_stages"].append(stage)
            return _receipt_ref(receipt_path, output_root)
        attempt["invalidated_stages"].append({"stage": stage,
            "reason": "DECLARED_DEPENDENCY_CHANGED",
            "prior_receipt": _receipt_ref(receipt_path, output_root)})
    stage_dir = _next_directory(stage_root)
    write_new(stage_dir / "value.json", value)
    receipt_path = stage_dir / "receipt.json"
    write_new(receipt_path, {"schema_version": 1, "stage": stage, "status": "PASS",
              "specification_sha256": spec_hash, "command": command, "returncode": 0,
              "outputs": _tree_bindings(stage_dir, output_root, omit={"receipt.json"})})
    attempt["executed_stages"].append(stage)
    return _receipt_ref(receipt_path, output_root)


def finish_resumable(root: Path, scope_file: str, output_dir: Path) -> int:
    """Run or resume exact ordered closure under one repository owner.

    Successful stages are immutable and reused only when their complete declared
    specification and output inventory still match. Changed declared dependencies
    create a new stage version; malformed or changed cached evidence fails closed.
    """
    root = root.resolve()
    output_dir = output_dir if output_dir.is_absolute() else root / output_dir
    if (output_dir.is_symlink() or not output_dir.resolve().is_relative_to(root)
            or output_dir.resolve().is_relative_to(root / "results/research")):
        raise ValueError("closure control output must be safe and outside results/research")
    output_dir.mkdir(parents=True, exist_ok=True)
    attempt_dir = _next_directory(output_dir / "attempts")
    attempt = {"schema_version": 1, "status": "FAILED", "scope_file": scope_file,
               "executed_stages": [], "reused_stages": [], "invalidated_stages": []}
    try:
        with closure_owner(root) as owner:
            attempt["owner"] = owner
            preflight = host_rss_preflight()
            inventory = committed_inventory(root, scope_file)
            attempt["validated_commit"] = inventory["commit"]
            status_inputs = dependency_inventory(inventory, "status")
            suite_inputs = dependency_inventory(inventory, "suite")
            publication_inputs = dependency_inventory(inventory, "publication")
            preflight_ref = _run_value_stage(output_dir, "00-host-rss-preflight", preflight,
                                             status_inputs, [], attempt)
            inventory_ref = _run_value_stage(output_dir, "01-committed-input-inventory",
                                             {"schema_version": 1,
                                              "status": status_inputs,
                                              "suite": suite_inputs,
                                              "publication": publication_inputs},
                                             publication_inputs, [preflight_ref], attempt)
            suite_env = os.environ.copy()
            # Control-test receipts stay under this non-research stage directory.
            suite_env["METAMORPHIC_SUPERVISOR_RECEIPT_DIR"] = "{control_receipts}"
            with validation_snapshot(root, inventory) as snapshot:
                status_ref = _run_command_stage(root, output_dir, "02-status-preflight",
                                                STATUS_PREFLIGHT, status_inputs,
                                                [], attempt, execution_root=snapshot)
                suite_ref = _run_command_stage(root, output_dir, "03-full-suite", SUITE,
                                               suite_inputs, [status_ref], attempt,
                                               env=suite_env, execution_root=snapshot)
            matching_publication_inputs(root, scope_file, inventory)
            validation = {"schema_version": 1, "status": "PASS",
                          "validated_at": datetime.now(timezone.utc).isoformat(),
                          "commit": inventory["commit"], "scope_file": scope_file,
                          "validation_input_sha256": _sha(_canonical(suite_inputs)),
                          "publication_input_sha256": _sha(_canonical(publication_inputs)),
                          "suite_receipt": suite_ref}
            validation_ref = _run_value_stage(output_dir, "04-sealed-validation", validation,
                                              publication_inputs, [suite_ref], attempt)
            refresh_ref = _run_command_stage(
                root, output_dir, "05-dependency-ordered-refresh",
                ["scripts/refresh-current-state", "--log-dir", "{stage_dir}/refresh"],
                publication_inputs, [validation_ref], attempt)
            prior = [refresh_ref]
            for index, command in enumerate(CHECKS, 1):
                prior = [_run_command_stage(root, output_dir, f"{index + 5:02d}-check-{index:02d}",
                                            command, publication_inputs, prior, attempt,
                                            bind_worktree=True)]
            matching_publication_inputs(root, scope_file, inventory)
            attempt["publication_match"] = "PASS"
            attempt["status"] = "COMPLETE"
            attempt["validation_receipt"] = validation_ref
            attempt["terminal_receipt"] = prior[0]
            return 0
    except KeyboardInterrupt:
        attempt["error"] = "closure interrupted; rerun the same command to resume exact valid stages"
        attempt["interrupted"] = True
        return 130
    except (OSError, ValueError) as error:
        attempt["error"] = str(error)
        print(str(error), file=sys.stderr)
        return 1
    finally:
        write_new(attempt_dir / "result.json", attempt)
