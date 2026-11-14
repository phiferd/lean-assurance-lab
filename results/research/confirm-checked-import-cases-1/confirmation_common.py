"""Shared, non-launching helpers for the checked-import E1 confirmation."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from lib.resource_envelope_supervisor import run_direct

IMAGE = "sha256:1a144bf428c8c7dd7ed1df886273b77ca331079cb17ebfb9712e1ea2ea643b73"
IMAGE_TAG = "lean-assurance-lab/checked-import-runtime:2026-11-14"
LEAN_PATH = "/opt/comparator/.lake/packages/lean4export/.lake/build/lib/lean"
PINNED = {
    "/opt/lean-fast/bin/lean": "79fb1d26fa5a39385d59fdc48a711a14b0710ca6480271acce99b4d177cea085",
    "/opt/nanoda/target/release/nanoda_bin": "5e99b44c8b371ca1aedbc1a609a391ca5ac61b834b14fa60871298affb23d962",
    "/opt/comparator/.lake/packages/lean4export/.lake/build/lib/lean/Export/Parse.olean": "c264ea4ad5e30bd90cd03a1b48d944c4a7317e53b483b99c04df8c3a6882f133",
    "/opt/comparator/.lake/packages/lean4export/Export/Parse.lean": "1f943b5cc776eece6d528937b976509c8bd57d10bc69a39b1c119bfb6d664286",
}
SUPERVISION = {
    "timeout_seconds": 145,
    "memory_ceiling_bytes": 4 * 1024**3,
    "sample_interval_seconds": 0.5,
    "max_trace_gap_seconds": 5,
    "cleanup_seconds": 10,
    "output_cap_bytes": 20 * 1024**2,
}
CONTAINER_LIMITS = {
    "memory": "12g",
    "memory_swap": "12g",
    "cpus": "4",
    "pids_limit": "512",
    "network": "none",
    "security_opt": "no-new-privileges",
    "read_only": True,
    "tmpfs": "/tmp:rw,noexec,nosuid,size=64m",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def docker() -> str:
    path = shutil.which("docker")
    if not path:
        raise RuntimeError("docker executable is unavailable")
    return path


def write_attempt(directory: Path, label: str, argv: list[str], timeout: float):
    """Run and retain one direct host process. The caller classifies its exit."""
    target = directory / label
    target.mkdir(parents=True, exist_ok=False)
    command = {"argv": argv, "timeout_seconds": timeout}
    (target / "command.json").write_text(json.dumps(command, indent=2) + "\n")
    result = run_direct(
        argv=argv,
        cwd=ROOT,
        env=dict(os.environ),
        stdin_bytes=None,
        timeout_seconds=timeout,
        memory_ceiling_bytes=SUPERVISION["memory_ceiling_bytes"],
        sample_interval_seconds=SUPERVISION["sample_interval_seconds"],
        max_trace_gap_seconds=SUPERVISION["max_trace_gap_seconds"],
        cleanup_seconds=SUPERVISION["cleanup_seconds"],
        output_cap_bytes=SUPERVISION["output_cap_bytes"],
    )
    (target / "stdout.log").write_bytes(result.stdout)
    (target / "stderr.log").write_bytes(result.stderr)
    (target / "receipt.json").write_text(json.dumps(result.receipt, indent=2) + "\n")
    return result


def require_supervision(receipt: dict, *, allow_stop: str | None = None) -> None:
    assert receipt["cleanup_complete"] and receipt["reap_complete"], receipt
    assert receipt["monitor_errors"] == [], receipt
    assert receipt["cleanup_errors"] == [], receipt
    assert receipt["pipe_errors"] == [], receipt
    assert receipt["accounting_error"] is None, receipt
    assert not receipt["trace_gap_fault"], receipt
    assert receipt["stop_reason"] == allow_stop, receipt


def container_prefix(name: str, *, auto_remove: bool = True) -> list[str]:
    args = [
        docker(), "run",
        "--name", name,
        "--network", CONTAINER_LIMITS["network"],
        "--read-only",
        "--tmpfs", CONTAINER_LIMITS["tmpfs"],
        "--memory", CONTAINER_LIMITS["memory"],
        "--memory-swap", CONTAINER_LIMITS["memory_swap"],
        "--cpus", CONTAINER_LIMITS["cpus"],
        "--pids-limit", CONTAINER_LIMITS["pids_limit"],
        "--security-opt", CONTAINER_LIMITS["security_opt"],
    ]
    if auto_remove:
        args.insert(2, "--rm")
    return args


def assert_container_absent(attempts: Path, label: str, name: str) -> None:
    result = write_attempt(attempts, label, [docker(), "container", "inspect", name], 30)
    require_supervision(result.receipt)
    if result.receipt["exit_code"] == 0:
        cleanup = write_attempt(attempts, label + "-repair-rm", [docker(), "rm", "-f", name], 30)
        require_supervision(cleanup.receipt)
        raise RuntimeError(f"container remained after {label}; repaired by forced removal")
    assert result.receipt["exit_code"] == 1, result.receipt
    assert (b"No such object" in result.stderr
            or b"No such container" in result.stderr), result.stderr


def load_manifest() -> dict:
    return json.loads((HERE / "execution-manifest.json").read_text())


def verify_file_bindings(manifest: dict) -> None:
    for path, expected in manifest["file_sha256"].items():
        actual = sha256(ROOT / path)
        if actual != expected:
            raise RuntimeError(f"file binding mismatch: {path}: {actual} != {expected}")


def read_json(path: Path):
    return json.loads(path.read_text())


def slug(text: str) -> str:
    return text.lower().replace("/", "-").replace("_", "-")


def cell_label(cell: dict) -> str:
    return f"cell-{cell['ordinal']:02d}-{slug(cell['id'])}"


def container_name(phase: str, cell: dict) -> str:
    return f"lal-cic-{phase[0]}-{cell['ordinal']:02d}-{slug(cell['family'])}-{slug(cell['source_case_id'])}-{cell['checker']}"
