"""Run one declared E0 matrix through retained bounded checker adapters."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib.pipeline_completeness import _supervise, process_classification, sentinel

HERE = Path(__file__).resolve().parent
ID = HERE.name
CASES = (["baseline", "invalid-first", "invalid-middle", "invalid-last"]
         if "INVALID-TARGET" in ID else
         ["baseline", "changed-proposition", "changed-name"])
BASELINE_SHA = "d9e51643e1533b667d897f8dfeaba3c6a0f6e64936b54162b414574e930b24e3"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, object: dict) -> None:
    path.write_text(json.dumps(object, indent=2, sort_keys=True) + "\n")


def main() -> None:
    start = json.loads((HERE / "start-event.json").read_text())
    assert start["id"] == ID and start["event"] == "start"
    for relative, expected in start["data"]["input_sha256"].items():
        assert digest(ROOT / relative) == expected, f"input changed: {relative}"
    assert digest(HERE / "baseline.ndjson") == BASELINE_SHA
    protocol = json.loads((ROOT / "results/research/pipeline-completeness-pilot-1/protocol.json").read_text())
    safety = json.loads((ROOT / "results/research/pipeline-completeness-pilot-2/protocol.json").read_text())["process_safety"]
    attempt = HERE / "attempt-0001"
    attempt.mkdir(exist_ok=False)
    cells = []
    for case in CASES:
        artifact = HERE / f"{case}.ndjson"
        identity = sentinel(artifact.read_bytes(), BASELINE_SHA)
        for adapter in protocol["adapters"]:
            binary = ROOT / adapter["binary"]["path"]
            assert digest(binary) == adapter["binary"]["sha256"], f"binary changed: {adapter['id']}"
            argv = [str(binary)] + ([] if adapter["id"] == "official" else ["--import"]) + [str(artifact)]
            directory = attempt / f"{case}-{adapter['id']}"
            receipt, _, _ = _supervise(directory, argv, binary.parent,
                                        {"LANG": "C", "PATH": "/usr/bin:/bin"},
                                        safety["checker_seconds_each"], safety["checker_memory_bytes_each"])
            receipt["adapter_id"] = adapter["id"]
            receipt["adapter_binary_sha256"] = digest(binary)
            receipt["artifact_sha256"] = digest(artifact)
            receipt["sentinel"] = identity
            write(directory / "supervisor.json", receipt)
            outcome = process_classification(receipt)
            cells.append({"case": case, "adapter": adapter["id"], "process_outcome": outcome,
                          "sentinel": identity["classification"],
                          "receipt": str((directory / "supervisor.json").relative_to(ROOT)),
                          "stdout": str((directory / "process.stdout").relative_to(ROOT)),
                          "stderr": str((directory / "process.stderr").relative_to(ROOT))})
            write(attempt / "result.json", {"id": ID, "cells": cells})
            if outcome in {"INFRASTRUCTURE_FAILURE", "UNKNOWN"}:
                raise RuntimeError(f"pause after process-control failure: {case}/{adapter['id']}")
            if case == "baseline" and outcome != "ACCEPT":
                raise RuntimeError(f"invalid baseline: {adapter['id']} {outcome}")


if __name__ == "__main__":
    main()
