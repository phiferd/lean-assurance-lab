#!/usr/bin/env python3
"""Capture pure mocked runner and queue-policy tests before input freeze."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "results/research/survivor-cache-1"
RUNNER_CODE = [
    "lib/survivor_cache_runner.py",
    "scripts/execute-survivor-cache",
    "tests/test_survivor_cache_runner.py",
    "lib/cvc_process.py",
    "lib/cvc_signal_retry.py",
    "lib/cvc_prep.py",
    "lib/survivor_let_payload.py",
    "lib/research_queue.py",
    "lib/research_queue_v2.py",
    "lib/research_queue_v3.py",
]


def binding(path: Path) -> dict:
    raw = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(raw).hexdigest()}


def run(label: str, pattern: str) -> tuple[dict, int]:
    log = BASE / f"{label}.log"
    if log.exists():
        raise SystemExit("refuse to overwrite focused log: " + str(log))
    command = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", pattern, "-v"]
    started = datetime.now(timezone.utc).isoformat()
    process = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, check=False)
    log.write_text(process.stdout, encoding="utf-8")
    matches = re.findall(r"^Ran ([0-9]+) tests? in ", process.stdout, flags=re.MULTILINE)
    if process.returncode or len(matches) != 1 or not re.search(r"^OK$", process.stdout, flags=re.MULTILINE):
        raise SystemExit(f"{label} failed; retained {log}")
    return ({"label": label, "command": command, "started_at": started,
             "ended_at": datetime.now(timezone.utc).isoformat(), "returncode": process.returncode,
             "test_count": int(matches[0]), "log": binding(log)}, int(matches[0]))


def main() -> None:
    if sys.argv[1:] in (["--runner-repair-r2"], ["--runner-repair-r3"]):
        revision = sys.argv[1].rsplit("-", 1)[-1]
        receipt_path = BASE / f"focused-test-receipt-{revision}.json"
        if receipt_path.exists():
            raise SystemExit("focused repair receipt already frozen")
        runner, runner_count = run(f"focused-runner-tests-{revision}", "test_survivor_cache_runner.py")
        receipt = {
            "schema_version": 1,
            "item_id": "SURVIVOR-CACHE-1",
            "status": "PASS",
            "test_count": runner_count,
            "real_process_launches": 0,
            "tooling_inputs": [binding(ROOT / path) for path in RUNNER_CODE],
            "logs": [runner["log"]],
            "run": runner,
            "limits": "All launch/process functions were mocked; no Cargo, checker, test binary or inert process was invoked.",
        }
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"runner_tests": runner_count, "status": "PASS", "revision": revision}))
        return
    if sys.argv[1:]:
        raise SystemExit("usage: capture-focused.py [--runner-repair-r2|--runner-repair-r3]")
    receipt_path = BASE / "focused-test-receipt.json"
    policy_path = BASE / "queue-policy-test-receipt.json"
    if receipt_path.exists() or policy_path.exists():
        raise SystemExit("focused receipts already frozen")
    runner, runner_count = run("focused-runner-tests", "test_survivor_cache_runner.py")
    policy, policy_count = run("focused-queue-tests", "test_research_queue*.py")
    tooling = [binding(ROOT / path) for path in RUNNER_CODE]
    receipt = {
        "schema_version": 1,
        "item_id": "SURVIVOR-CACHE-1",
        "status": "PASS",
        "test_count": runner_count,
        "real_process_launches": 0,
        "tooling_inputs": tooling,
        "logs": [runner["log"]],
        "run": runner,
        "limits": "All launch/process functions were mocked; no Cargo, checker, test binary or inert process was invoked.",
    }
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    policy_path.write_text(json.dumps({
        "schema_version": 1,
        "item_id": "SURVIVOR-CACHE-1",
        "status": "PASS",
        "test_count": policy_count,
        "run": policy,
        "inputs": [binding(ROOT / path) for path in [
            "lib/research_queue.py", "lib/research_queue_v2.py", "lib/research_queue_v3.py",
            "scripts/validate-research-queue", "tests/test_research_queue.py",
            "tests/test_research_queue_v2.py", "tests/test_research_queue_v3.py",
        ]],
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"runner_tests": runner_count, "queue_tests": policy_count, "status": "PASS"}))


if __name__ == "__main__":
    main()
