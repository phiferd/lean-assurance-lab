#!/usr/bin/env python3
"""Run one retained preparation or scientific command under project supervision."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib.resource_envelope_supervisor import run_direct


def main() -> int:
    if len(sys.argv) < 5 or sys.argv[2] != "--cwd" or "--" not in sys.argv[4:]:
        raise SystemExit("usage: run-supervised.py ATTEMPT --cwd DIR -- COMMAND [ARG ...]")
    attempt = sys.argv[1]
    separator = sys.argv.index("--", 4)
    cwd = Path(sys.argv[3]).resolve()
    argv = sys.argv[separator + 1 :]
    if not argv:
        raise SystemExit("command is required")
    executable = shutil.which(argv[0], path=os.environ.get("PATH"))
    if executable is None:
        raise SystemExit(f"executable not found: {argv[0]}")
    argv[0] = executable

    folder = Path(__file__).resolve().parent / "attempts" / attempt
    folder.mkdir(parents=True, exist_ok=False)
    inputs: dict[str, str] = {}
    for arg in argv:
        path = Path(arg)
        if path.is_file():
            resolved = path.resolve()
            inputs[str(resolved)] = hashlib.sha256(resolved.read_bytes()).hexdigest()
    (folder / "inputs.json").write_text(json.dumps(inputs, indent=2, sort_keys=True) + "\n")
    (folder / "command.json").write_text(
        json.dumps({"argv": argv, "cwd": str(cwd)}, indent=2, sort_keys=True) + "\n"
    )

    result = run_direct(
        argv=argv,
        cwd=cwd,
        env=dict(os.environ),
        stdin_bytes=None,
        timeout_seconds=3600,
        memory_ceiling_bytes=12 * 1024**3,
        sample_interval_seconds=1,
        max_trace_gap_seconds=30,
        cleanup_seconds=15,
        output_cap_bytes=40 * 1024**2,
    )
    (folder / "stdout.log").write_bytes(result.stdout)
    (folder / "stderr.log").write_bytes(result.stderr)
    (folder / "receipt.json").write_text(
        json.dumps(result.receipt, indent=2, sort_keys=True) + "\n"
    )
    summary_keys = [
        "exit_code",
        "elapsed_seconds",
        "cleanup_complete",
        "accounting_error",
        "monitor_errors",
        "termination_reason",
        "peak_sampled_group_memory_bytes",
    ]
    print(json.dumps({key: result.receipt.get(key) for key in summary_keys}, sort_keys=True))
    print(result.stdout.decode(errors="replace")[-8000:])
    print(result.stderr.decode(errors="replace")[-4000:], file=sys.stderr)
    if (
        not result.receipt.get("cleanup_complete")
        or result.receipt.get("accounting_error")
        or result.receipt.get("monitor_errors")
    ):
        raise SystemExit("CONTROL FAULT: pause launches")
    return result.receipt.get("exit_code") or 0


if __name__ == "__main__":
    raise SystemExit(main())
