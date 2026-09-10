#!/usr/bin/env python3
"""Run one frozen Nanoda cache-regression cell with process-group cleanup."""

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.cvc_process import run_process  # noqa: E402

MANIFESTS = {
    "focused": ROOT / "results/research/nanoda-cache-regression-1/execution/focused-manifest.json",
    "full": ROOT / "results/research/nanoda-cache-regression-1/execution/full-suite-manifest.json",
}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in MANIFESTS:
        raise SystemExit("usage: run-cell.py {focused|full}")
    manifest = json.loads(MANIFESTS[sys.argv[1]].read_text())
    if manifest["item_id"] != "NANODA-CACHE-REGRESSION-1":
        raise ValueError("wrong item manifest")
    directory = ROOT / manifest["execution_directory"]
    directory.mkdir(parents=True, exist_ok=False)
    receipt = run_process(
        manifest["payload_invocation"],
        manifest["source"]["detached_checkout"],
        manifest["environment"],
        directory,
        manifest["timeout_seconds"],
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["status"] == "COMPLETE" and receipt["returncode"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
