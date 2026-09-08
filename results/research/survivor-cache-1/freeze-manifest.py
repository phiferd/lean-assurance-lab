#!/usr/bin/env python3
"""Freeze the exact tested cache-comparison manifest once."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.survivor_cache_runner import CODE, ENV, LIMITS  # noqa: E402

BASE = ROOT / "results/research/survivor-cache-1"
OUTPUT = ROOT / "config/survivor-cache-0001.json"


def binding(relative: str) -> dict:
    path = ROOT / relative
    raw = path.read_bytes()
    return {"path": relative, "sha256": hashlib.sha256(raw).hexdigest()}


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("scientific manifest already frozen")
    required = {
        "work_record": "results/research/survivor-cache-1/work-record.json",
        "entry_decision": "results/research/survivor-cache-1/entry-decision.json",
        "source_materialization": "results/research/survivor-cache-1/source-materialization.json",
        "runtime_manifest": "results/research/survivor-cache-1/runtime-manifest.json",
        "mutation_spec": "mutations/nanoda-gen-3365809b3c41.json",
        "source_lock": "results/research/survivor-cache-1/source-lock.json",
        "harness": "results/research/survivor-cache-1/cache-contract-tests.rs",
    }
    decision = json.loads((BASE / "entry-decision.json").read_text())
    if (decision.get("scientific_freeze_status") != "FROZEN"
            or not decision.get("source_review", {}).get("sha256")):
        raise SystemExit("source review and scientific decision must be frozen first")
    manifest = {
        "schema_version": 1,
        "item_id": "SURVIVOR-CACHE-1",
        "run_id": "survivor-cache-0001",
        "limits": LIMITS,
        **{name: binding(path) for name, path in required.items()},
        "tests": {
            "control": {"name": "tc::cache_contract_tests::control"},
            "candidate": {
                "name": "tc::cache_contract_tests::candidate",
                "failure_message": "expected checked inference to reject warmed malformed let",
                "failure_location": "src/tc.rs:1383:23",
            },
        },
        "observer_environment": ENV,
        "tooling_inputs": [binding(path) for path in CODE],
        "focused_test_receipt": binding("results/research/survivor-cache-1/focused-test-receipt.json"),
    }
    OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(binding("config/survivor-cache-0001.json")))


if __name__ == "__main__":
    main()
