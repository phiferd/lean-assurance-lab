#!/usr/bin/env python3
"""Run the fixed eight-cell LazyLean E0 screen with retained supervision."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib.lazy_reduction_pilot import classify  # noqa: E402
from lib.metamorphic_pilot_runner import run_supervised  # noqa: E402

RUN = Path("explorations/runs/EXPLORE-LAZYLEAN-SEMANTIC-EXTENSION-1")
BINARY = Path("external/lazy-reduction-conformance-pilot-1/lazylean-r1")
ENV = {"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "LANG": "C", "LC_ALL": "C", "LL_KAM_MODE": "3"}
CELLS = [
    ("delta", "control", "subst", 3),
    ("delta", "candidate", "subst", 3),
    ("delta", "control", "kam", 3),
    ("delta", "candidate", "kam", 3),
    ("iota", "control", "subst", 2),
    ("iota", "candidate", "subst", 2),
    ("iota", "control", "kam", 2),
    ("iota", "candidate", "kam", 2),
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path: Path, value: object) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    with target.open("xb") as stream:
        stream.write(raw)


def main() -> None:
    rows = []
    for index, (family, role, profile, declarations) in enumerate(CELLS, 1):
        fixture = ROOT / RUN / f"{family}-{role}.ndjson"
        before = {"path": str(fixture.relative_to(ROOT)), "bytes": fixture.stat().st_size, "sha256": digest(fixture)}
        argv = [str(ROOT / BINARY), "--engine", profile, "--jobs", "1", str(fixture)]
        prefix = ROOT / RUN / "attempt-0001" / f"{index:02d}-{profile}-{family}-{role}"
        started = datetime.now(timezone.utc).isoformat()
        receipt = run_supervised(argv=argv, cwd=ROOT, stdin=None, env=ENV,
                                 timeout_seconds=30, memory_bytes=2147483648,
                                 raw_prefix=prefix)
        stdout = Path(receipt["raw_stdout_path"]).read_bytes()
        stderr = Path(receipt["raw_stderr_path"]).read_bytes()
        observation = classify(receipt, stdout, stderr, declarations)
        after = {"path": str(fixture.relative_to(ROOT)), "bytes": fixture.stat().st_size, "sha256": digest(fixture)}
        row = {
            "cell_id": f"{profile}::{family}-{role}",
            "family": family,
            "role": role,
            "profile": profile,
            "started_at": started,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "input_before": before,
            "input_after": after,
            "receipt": receipt,
            "observation": observation,
        }
        write_new(RUN / "attempt-0001" / f"cell-{index:02d}.json", row)
        rows.append(row)

    families = {}
    for family in ["delta", "iota"]:
        selected = [row for row in rows if row["family"] == family]
        controls_accept = all(row["observation"].get("verdict") == "ACCEPT" for row in selected if row["role"] == "control")
        candidates = {row["profile"]: row for row in selected if row["role"] == "candidate"}
        kam_counter = candidates["kam"]["observation"].get("machine", {}).get(family, 0)
        safety_complete = all(
            row["receipt"].get("cleanup_complete")
            and not row["receipt"].get("timed_out")
            and not row["receipt"].get("memory_exceeded")
            and row["receipt"].get("memory_monitor_error") is None
            and row["receipt"].get("memory_monitor_samples", 0) > 0
            and row["receipt"].get("maximum_observed_rss_bytes", 0) > 0
            and row["input_before"] == row["input_after"]
            for row in selected
        )
        verdicts = {profile: row["observation"].get("verdict") for profile, row in candidates.items()}
        if controls_accept and safety_complete and kam_counter > 0 and verdicts["subst"] != verdicts["kam"]:
            outcome = "SIGNAL"
        elif controls_accept and safety_complete and kam_counter > 0 and verdicts["subst"] == verdicts["kam"]:
            outcome = "NO_SIGNAL"
        else:
            outcome = "INCONCLUSIVE"
        families[family] = {
            "outcome": outcome,
            "controls_accept": controls_accept,
            "candidate_verdicts": verdicts,
            "candidate_kam_counter": kam_counter,
            "safety_and_identity_complete": safety_complete,
        }
    write_new(RUN / "attempt-0001" / "result.json", {
        "evidence_class": "E0",
        "binary": {"path": str(BINARY), "bytes": (ROOT / BINARY).stat().st_size, "sha256": digest(ROOT / BINARY)},
        "cells": rows,
        "families": families,
    })
    print(json.dumps(families, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
