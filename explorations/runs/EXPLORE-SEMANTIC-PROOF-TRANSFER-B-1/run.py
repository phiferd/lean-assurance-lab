#!/usr/bin/env python3
"""Run one fixed, supervised E0 real-proof transfer sample."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.metamorphic_pilot_runner_v3 import run_supervised  # noqa: E402
from lib.metamorphic_pilot_runner import classify as classify_official  # noqa: E402
from lib.lazy_reduction_pilot import classify as classify_lazy  # noqa: E402

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "selection.json").read_text())
ENV = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C", "LL_KAM_MODE": "3"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def revision(path: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=path, text=True).strip()


def preflight() -> tuple[Path, Path, Path, int]:
    q = json.loads((ROOT / "config/research-queue.json").read_text())
    campaign = "E0-SEMANTIC-ASSURANCE-SCREENING-1"
    if q["selected_item"] != campaign or next(x for x in q["items"] if x["id"] == campaign)["status"] != "ACTIVE":
        raise ValueError("campaign is not selected ACTIVE")
    rows = [json.loads(x) for x in (ROOT / "explorations/ledger.jsonl").read_text().splitlines()]
    if not any(x["id"] == CONFIG["trial_id"] and x["event"] == "start" for x in rows):
        raise ValueError("trial start is not appended")
    for rel, expected in CONFIG["files"].items():
        path = ROOT / rel
        if not path.is_file() or sha(path) != expected:
            raise ValueError(f"input identity differs: {rel}")
    for rel, expected in CONFIG["revisions"].items():
        if revision(ROOT / rel) != expected:
            raise ValueError(f"source revision differs: {rel}")
    sample = ROOT / CONFIG["sample"]
    official = ROOT / CONFIG["official_binary"]
    lazy = ROOT / CONFIG["lazy_binary"]
    declarations = sum(any(key in json.loads(line) for key in ("axiom", "def", "thm", "opaque", "quot", "inductive")) for line in sample.read_text().splitlines())
    if declarations != CONFIG["declaration_count"]:
        raise ValueError("declaration count differs")
    return sample, official, lazy, declarations


def main() -> None:
    sample, official, lazy, declarations = preflight()
    attempts = sorted(HERE.glob("attempt-[0-9][0-9][0-9][0-9]"))
    directory = HERE / f"attempt-{len(attempts)+1:04d}"
    directory.mkdir(exist_ok=False)
    plan = [
        ("official", [str(official), str(sample)]),
        ("subst", [str(lazy), "--engine", "subst", "--jobs", "1", str(sample)]),
        ("kam", [str(lazy), "--engine", "kam", "--jobs", "1", str(sample)]),
    ]
    result = {"trial_id": CONFIG["trial_id"], "sample": CONFIG["sample"], "sample_sha256": sha(sample),
              "started_at": datetime.now(timezone.utc).isoformat(), "status": "RUNNING", "cells": []}
    write(directory / "result.json", result)
    try:
        for profile, argv in plan:
            raw = directory / profile
            receipt = run_supervised(argv=argv, cwd=ROOT, stdin=None, env=ENV,
                                     timeout_seconds=120, memory_bytes=2147483648, raw_prefix=raw)
            stdout = Path(str(raw) + ".stdout").read_bytes()
            stderr = Path(str(raw) + ".stderr").read_bytes()
            if profile == "official":
                verdict, reason = classify_official("official-lean-4.33.0", receipt, stdout, stderr)
                observation = {"verdict": verdict, "reason": reason}
            else:
                observation = classify_lazy(receipt, stdout, stderr, declarations)
            cell = {"profile": profile, "argv": argv, "receipt": receipt, "observation": observation}
            result["cells"].append(cell)
            write(directory / "result.json", result)
            if receipt["memory_monitor_error"] or receipt["timed_out"] or receipt["memory_exceeded"] or not receipt["cleanup_complete"]:
                raise RuntimeError(f"process control failure on {profile}; launches paused")
            if profile == "official" and verdict != "ACCEPT":
                raise RuntimeError("fresh official control did not accept; launches paused")
        result["status"] = "COMPLETE"
    except BaseException as exc:
        result["status"] = "REPAIR_PAUSE"
        result["error"] = f"{type(exc).__name__}: {exc}"
        write(directory / "result.json", result)
        raise
    result["finished_at"] = datetime.now(timezone.utc).isoformat()
    write(directory / "result.json", result)
    print(json.dumps({"attempt": str(directory.relative_to(ROOT)), "status": result["status"],
                      "observations": [x["observation"] for x in result["cells"]]}, sort_keys=True))


if __name__ == "__main__":
    main()
