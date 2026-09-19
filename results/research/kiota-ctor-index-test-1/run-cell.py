#!/usr/bin/env python3
"""Run one committed, exact-input Kiota regression-test reservation."""
from __future__ import annotations

import fcntl
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.cvc_process import atomic, run_process

BASE = ROOT / "results/research/kiota-ctor-index-test-1"
ITEM = "KIOTA-CTOR-INDEX-TEST-1"
CELLS = ("001-focused", "002-full")
MAX_ACTIVE = 5400
MAX_BUILDS = 2
MAX_TESTS = 3
TIMEOUT = 120


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(test: bool, message: str) -> None:
    if not test:
        raise ValueError(message)


def tree_manifest(path: Path) -> tuple[int, str]:
    files = sorted(candidate for candidate in path.rglob("*") if candidate.is_file())
    rows = "".join(
        f"{candidate.relative_to(path).as_posix()}\t{digest(candidate.read_bytes())}\t{candidate.stat().st_size}\n"
        for candidate in files
    ).encode()
    return len(files), digest(rows)


def verify_dependencies() -> None:
    lock = json.loads((BASE / "dependency-lock.json").read_text())
    for package in lock["packages"]:
        count, manifest = tree_manifest(Path(package["source_root"]))
        require(count == package["files"] and manifest == package["manifest_sha256"],
                "dependency source mismatch: " + package["name"])


def verify_source(manifest: dict) -> None:
    source = Path(manifest["cwd"])
    package = json.loads((BASE / "patch-package.json").read_text())
    source_lock = json.loads((BASE / "source-lock.json").read_text())
    archive = ROOT / source_lock["archive"]["path"]
    additions = {row["target_path"]: row for row in package["fixture_copies"]}
    with tarfile.open(archive, "r:gz") as bundle:
        members = [member for member in bundle.getmembers() if member.isfile()]
        prefix = source_lock["archive"]["top_level"]
        archived = {member.name[len(prefix):]: member for member in members
                    if member.name.startswith(prefix)}
        expected = set(archived) | set(additions)
        actual = {candidate.relative_to(source).as_posix()
                  for candidate in source.rglob("*") if candidate.is_file()}
        require(actual == expected, "patched source file inventory mismatch")
        for relative, member in archived.items():
            raw = bundle.extractfile(member).read()
            current = (source / relative).read_bytes()
            if relative == package["code_patch"]["target_path"]:
                require(digest(current) == package["code_patch"]["patched_sha256"]
                        and len(current) == package["code_patch"]["patched_bytes"],
                        "patched test source mismatch")
            else:
                require(current == raw, "unexpected source modification: " + relative)
        for relative, row in additions.items():
            current = (source / relative).read_bytes()
            original = (ROOT / row["source_path"]).read_bytes()
            require(current == original and digest(current) == row["sha256"]
                    and len(current) == row["bytes"], "fixture copy mismatch: " + relative)


def main() -> int:
    require(len(sys.argv) == 2 and sys.argv[1] in CELLS, "fixed cell ID required")
    cell = sys.argv[1]
    manifest_path = BASE / "execution" / (cell + "-manifest.json")
    raw = manifest_path.read_bytes()
    relative = str(manifest_path.relative_to(ROOT))
    require(subprocess.check_output(["git", "show", "HEAD:" + relative], cwd=ROOT) == raw,
            "manifest must be committed")
    manifest = json.loads(raw)
    require(manifest["item_id"] == ITEM and manifest["cell_id"] == cell,
            "wrong cell identity")
    for row in manifest["bindings"]:
        path = Path(row["path"])
        if not path.is_absolute():
            path = ROOT / path
        require(path.stat().st_size == row["bytes"] and digest(path.read_bytes()) == row["sha256"],
                "binding mismatch: " + str(path))
    for name in manifest["absent_paths"]:
        require(not Path(name).exists(), "unbound Cargo configuration: " + name)
    verify_dependencies()
    verify_source(manifest)
    source = Path(manifest["cwd"])
    work = json.loads((BASE / "work-record.json").read_text())
    elapsed = time.monotonic() - work["start_monotonic"]
    utc_elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(work["started_at"])).total_seconds()
    require(elapsed >= 0 and abs(elapsed - utc_elapsed) <= 2, "paired item clock disagreement")
    remaining = MAX_ACTIVE - elapsed
    require(remaining >= manifest["timeout_seconds"] and manifest["timeout_seconds"] == TIMEOUT,
            "remaining active time / process ceiling")
    account_path = BASE / "execution/accounting.json"
    prior_dirs = [path for path in (BASE / "execution").iterdir() if path.is_dir()]
    require(account_path.exists() or not prior_dirs, "missing accounting after reservation")
    account = json.loads(account_path.read_text()) if account_path.exists() else {
        "builds": 0, "test_processes": 0, "reservations": [], "pending": None
    }
    require(account["builds"] == account["test_processes"] == len(account["reservations"]),
            "reservation count mismatch")
    require(account["pending"] is None and account["builds"] < MAX_BUILDS
            and account["test_processes"] < MAX_TESTS, "unreconciled process or exhausted budget")
    require(not any(row["cell_id"] == cell for row in account["reservations"]),
            "cannot reuse a reservation")
    directory = BASE / "execution" / cell
    directory.mkdir(exist_ok=False)
    reservation = {
        "cell_id": cell,
        "manifest_sha256": digest(raw),
        "build_number": account["builds"] + 1,
        "test_number": account["test_processes"] + 1,
        "active_seconds_at_reservation": elapsed,
        "remaining_active_seconds": remaining,
        "status": "RESERVED"
    }
    account["builds"] += 1
    account["test_processes"] += 1
    account["reservations"].append(reservation)
    account["pending"] = cell
    atomic(account_path, account)
    receipt = run_process(manifest["argv"], source, manifest["environment"], directory,
                          TIMEOUT, deadline_monotonic=work["start_monotonic"] + MAX_ACTIVE)
    reservation["receipt"] = str((directory / "supervisor.json").relative_to(ROOT))
    reservation["status"] = receipt["status"]
    if receipt["cleanup_completed"] and not receipt["deadline_exceeded"] \
            and receipt["status"] in ("COMPLETE", "FAILED"):
        account["pending"] = None
    atomic(account_path, account)
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["status"] == "COMPLETE" and receipt["returncode"] == 0 else 1


if __name__ == "__main__":
    (BASE / "execution").mkdir(exist_ok=True)
    with (BASE / "execution/.launch.lock").open("a") as owner_lock:
        fcntl.flock(owner_lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        raise SystemExit(main())
