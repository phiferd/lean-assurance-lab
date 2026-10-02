#!/usr/bin/env python3
"""Retain one supervised host command and its raw streams for the eta E0 screen."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib.resource_envelope_supervisor import run_direct


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=900)
    parser.add_argument("argv", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    argv = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
    if not argv:
        parser.error("missing command after --")

    result = run_direct(
        argv=argv,
        cwd=args.cwd.resolve(),
        env=dict(os.environ),
        stdin_bytes=None,
        timeout_seconds=args.timeout,
        memory_ceiling_bytes=4 * 1024**3,
        sample_interval_seconds=1,
        max_trace_gap_seconds=5,
        cleanup_seconds=10,
        output_cap_bytes=20 * 1024**2,
    )
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    (output / "receipt.json").write_text(
        json.dumps(result.receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "stdout.log").write_bytes(result.stdout)
    (output / "stderr.log").write_bytes(result.stderr)
    return 0 if result.receipt.get("exit_code") == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
