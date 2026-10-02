#!/usr/bin/env python3
"""Run one frozen E1 cell after validating its committed launch manifest."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from lib.resource_envelope_supervisor import run_direct


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if len(sys.argv) != 5:
        raise SystemExit("usage: run-cell.py CELL_ID RUNNER_KEY LEAN_BINARY CELL_SOURCE")
    cell_id, runner_key, lean_arg, cell_arg = sys.argv[1:]
    lean = Path(lean_arg).resolve()
    cell = (HERE / "fixture" / cell_arg).resolve()
    manifest_path = HERE / "launch-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if sha256(Path(__file__).resolve()) != manifest["cell_runner_sha256"]:
        raise SystemExit("cell runner mismatch")
    matrix = {entry["id"]: entry for entry in manifest["matrix"]}
    if cell_id not in matrix or matrix[cell_id] != {
        "id": cell_id,
        "runner": runner_key,
        "cell": cell.name,
    }:
        raise SystemExit("cell does not match frozen matrix")
    runner = manifest["runners"][runner_key]
    if str(lean) != runner["lean_binary"]["path"] or sha256(lean) != runner["lean_binary"]["sha256"]:
        raise SystemExit("runner identity mismatch")
    for relative, digest in manifest["fixture_sources"].items():
        if sha256(ROOT / relative) != digest:
            raise SystemExit(f"fixture source mismatch: {relative}")
    for relative, digest in manifest["generated_oleans"].items():
        if sha256(ROOT / relative) != digest:
            raise SystemExit(f"generated olean mismatch: {relative}")
    if sha256(HERE / "expected.json") != manifest["expected_sha256"]:
        raise SystemExit("expected record mismatch")
    if sha256(HERE / "source-manifest.json") != manifest["source_manifest_sha256"]:
        raise SystemExit("source manifest mismatch")

    prepared = HERE / "prepared" / runner_key
    runner_lib = lean.parents[1] / "lib/lean"
    env = dict(os.environ)
    env["LEAN_PATH"] = os.pathsep.join([str(prepared), str(HERE / "fixture"), str(runner_lib)])
    local_uv = "/workspace/shared/lean-deps/lib"
    env["LD_LIBRARY_PATH"] = os.pathsep.join(
        [local_uv, str(lean.parents[1] / "lib"), env.get("LD_LIBRARY_PATH", "")]
    ).rstrip(os.pathsep)
    argv = [str(lean), "-t", "0", str(cell)]

    folder = HERE / "attempts" / cell_id
    folder.mkdir(parents=True, exist_ok=False)
    (folder / "inputs.json").write_text(
        json.dumps(
            {
                "launch_manifest_sha256": sha256(manifest_path),
                "runner_sha256": sha256(lean),
                "cell_sha256": sha256(cell),
                "prepared_olean_sha256": {
                    path.name: sha256(path) for path in sorted(prepared.glob("*.olean"))
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    (folder / "command.json").write_text(
        json.dumps({"argv": argv, "cwd": str(HERE / "fixture")}, indent=2) + "\n"
    )
    controls = manifest["cell_supervision"]
    result = run_direct(
        argv=argv,
        cwd=HERE / "fixture",
        env=env,
        stdin_bytes=None,
        timeout_seconds=controls["timeout_seconds"],
        memory_ceiling_bytes=controls["memory_ceiling_bytes"],
        sample_interval_seconds=controls["sample_interval_seconds"],
        max_trace_gap_seconds=controls["max_trace_gap_seconds"],
        cleanup_seconds=controls["cleanup_seconds"],
        output_cap_bytes=controls["output_cap_bytes"],
    )
    (folder / "stdout.log").write_bytes(result.stdout)
    (folder / "stderr.log").write_bytes(result.stderr)
    (folder / "receipt.json").write_text(
        json.dumps(result.receipt, indent=2, sort_keys=True) + "\n"
    )
    print(result.stdout.decode(errors="replace"))
    print(result.stderr.decode(errors="replace"), file=sys.stderr)
    if (
        not result.receipt.get("cleanup_complete")
        or result.receipt.get("accounting_error")
        or result.receipt.get("monitor_errors")
    ):
        raise SystemExit("CONTROL FAULT: pause launches")
    return result.receipt.get("exit_code") or 0


if __name__ == "__main__":
    raise SystemExit(main())
