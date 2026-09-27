"""Small, prospective controls for a repository item closure.

The scope file declares which inputs the item binds. This module verifies those
bytes exactly; it does not infer that the declaration covers every scientific
input or replace any item-specific validator.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import os

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


def _scope(root: Path, scope_file: str) -> tuple[str, list[str]]:
    path = Path(scope_file)
    if path.is_absolute() or path.as_posix().startswith("../") or ".." in path.parts:
        raise ValueError("scope file must be a repository-relative path")
    try:
        scope = json.loads((root / path).read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"could not read scope file: {error}") from error
    if (set(scope) != {"schema_version", "scope", "paths"} or scope["schema_version"] != 1
        or not isinstance(scope["scope"], str) or not scope["scope"].strip()
        or not isinstance(scope["paths"], list) or not scope["paths"]):
        raise ValueError("invalid declared inventory scope")
    paths = [scope_file, *scope["paths"]]
    if (any(not isinstance(p, str) or not p or Path(p).is_absolute()
            or ".." in Path(p).parts or Path(p).as_posix() != p for p in paths)
        or len(set(paths)) != len(paths) or scope["paths"] != sorted(scope["paths"])):
        raise ValueError("scope paths must be sorted, unique repository-relative files")
    return scope["scope"], paths


def committed_inventory(root: Path, scope_file: str) -> dict:
    scope, paths = _scope(root, scope_file)
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
    return {"schema_version": 1, "scope": scope, "scope_file": scope_file,
            "commit": commit, "files": rows}


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
