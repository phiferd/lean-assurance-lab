"""One-shot, receipt-preserving confirmation of the one-worker panic distinction."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil

from lib.cvc_prep import bind, committed, require, safe
from lib.cvc_process import atomic, now, sha
from lib.metamorphic_pilot_runner import run_supervised


ROOT = Path(__file__).resolve().parents[1]
ITEM = "CHILD-PANIC-CONFIRMATION-1"
BASE = "results/research/child-panic-confirmation-1"
RUN = BASE + "/run-0001"
MANIFEST = "config/child-panic-confirmation-0001.json"
PLAN = "docs/research/CHILD_PANIC_CONFIRMATION_PLAN.md"
SOURCE_LOCK = "results/research/alt-survivors-2026-09-08/source-lock.json"
README = "results/research/source-provenance-intake-1/evidence/README.md"
MUTATION = "mutations/nanoda-gen-2bdfe18a9ec2.json"
CONTROL = "corpus/controls/nanoda-gen-21ef4d1d32a1-matching-let-control.ndjson"
CANDIDATE = "corpus/generated/nanoda-gen-21ef4d1d32a1-let-value-type-mismatch.ndjson"
CONTROL_CONFIG = "results/research/survivor-thread-one-child-panic-regression-1/configs/control.json"
CANDIDATE_CONFIG = "results/research/survivor-thread-one-child-panic-regression-1/configs/candidate.json"
RUNTIME = "results/research/survivor-thread-one-child-panic-regression-1/runtime-binding.json"
WORK = BASE + "/work-record.json"
SUCCESS = b"Checked 1 declarations with no errors\n"
MEMORY = 2_147_483_648


def load(path: Path | str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def binding(path: Path) -> dict[str, str]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)}


def classify(cell: str, receipt: dict, stdout: bytes, stderr: bytes) -> str:
    if (receipt["memory_monitor_error"] is not None or receipt["memory_monitor_samples"] <= 0
            or receipt["maximum_observed_rss_bytes"] <= 0 or receipt["memory_exceeded"]
            or receipt["timed_out"] or not receipt["cleanup_complete"]):
        return "INFRASTRUCTURE_FAILURE"
    if receipt["exit_code"] == 0 and stdout == SUCCESS and stderr == b"":
        return "ACCEPT"
    if receipt["exit_code"] == 101 and stdout == b"":
        direct = (b"thread 'main'" in stderr and b"assertion failed: self.def_eq(u, v)" in stderr
                  and b"A thread in `check_all_declars` panicked while being joined" not in stderr)
        worker = (b"thread 'thread_0'" in stderr and b"assertion failed: self.def_eq(u, v)" in stderr
                  and b"A thread in `check_all_declars` panicked while being joined" in stderr)
        if cell == "candidate-baseline" and direct:
            return "DIRECT_ASSERTION_REFUSAL"
        if cell == "candidate-mutant" and worker:
            return "WORKER_PANIC_JOIN_REFUSAL"
    return "UNEXPECTED"


def validate() -> dict:
    manifest = load(ROOT / MANIFEST)
    require(manifest["schema_version"] == 1 and manifest["item_id"] == ITEM, "manifest identity differs")
    for name, expected in (
        (SOURCE_LOCK, "fb8ddc20e941aed1f56288ce83a83016e718d8abdf9756b34b96384236fdd472"),
        (README, "4442003879ac4ac7d455df1db16e0c5646652e6c9b44451f5d877345b8ff65d2"),
        (MUTATION, "565dade1407732bed722b3db2758f77e6a3a8a3cd079ce526974d91b8347aca6"),
        (CONTROL, "63ef460ca2aac739482c983457cd14309f4d7149ecd2c0d79d53fe2a410c9f16"),
        (CANDIDATE, "52e75d78c948d466e90fb203e7a04192dde4273c7319d44fc261fd2b3b6beeac"),
        (CONTROL_CONFIG, "cb2f6e6a34082bb607f26ba8e612c27d4d6cb3e2c1f923a8a40e45dc325934a6"),
        (CANDIDATE_CONFIG, "73a9e4414b5a001ba6ff24ae5f20957bf901a31c6e977f09c1a5e62e648bf909"),
        (RUNTIME, "185e0fe0a420ada25d7c8833aa694b4202b238044905621bc10c9e7f601291b3"),
    ):
        require(manifest["inputs"][name] == {"path": name, "sha256": expected}, "input binding differs")
        bind(ROOT, manifest["inputs"][name])
    for row in manifest["tooling"]:
        bind(ROOT, row)
    work = load(bind(ROOT, manifest["work_record"]))
    require(work["item_id"] == ITEM and work["status"] == "ACTIVE", "work record differs")
    return manifest


def gate(manifest: dict) -> None:
    from lib.research_queue_v3 import load_queue
    queue = load_queue(ROOT, require_ready=True)
    item = next(row for row in queue["items"] if row["id"] == ITEM)
    require(queue["selected_item"] == ITEM and item["status"] == "ACTIVE", "item is not selected ACTIVE")
    for path in (MANIFEST, PLAN, WORK, "config/research-queue.json", "docs/RESEARCH_STATUS.md"):
        committed(ROOT, path)
    for row in list(manifest["inputs"].values()) + manifest["tooling"]:
        committed(ROOT, row["path"])


def materialize(profile: str) -> tuple[Path, Path]:
    workspace = ROOT / "external" / f"child-panic-confirmation-0001-{profile}"
    target = ROOT / "external" / f"child-panic-confirmation-0001-target-{profile}"
    require(not workspace.exists() and not target.exists(), "confirmation materialization already exists")
    lock_data = load(ROOT / SOURCE_LOCK)
    for row in lock_data["files"]:
        source = bind(ROOT, {"path": row["binding"]["path"], "sha256": row["binding"]["sha256"]})
        require(source.stat().st_size == row["binding"]["bytes"], "source byte count differs")
        output = workspace / row["source_path"]
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, output)
    shutil.copyfile(ROOT / README, workspace / "README.md")
    require(sha(workspace / "README.md") == "4442003879ac4ac7d455df1db16e0c5646652e6c9b44451f5d877345b8ff65d2",
            "README materialization differs")
    if profile == "mutant":
        tc = workspace / "src/tc.rs"
        data = tc.read_bytes()
        require(data.count(b"self.config.num_threads > 1") == 1, "mutation site differs")
        data = data.replace(b"self.config.num_threads > 1", b"self.config.num_threads >= 1", 1)
        require(hashlib.sha256(data).hexdigest() == "a2a41ceb83361d892cd260f60605338788267635baf33f19cedf43e9aa579fdb",
                "mutant tc hash differs")
        tc.write_bytes(data)
    return workspace, target


def supervise(name: str, argv: list[str], cwd: Path, env: dict[str, str], seconds: int) -> tuple[dict, bytes, bytes]:
    directory = ROOT / RUN / name
    directory.mkdir(parents=True, exist_ok=False)
    receipt = run_supervised(argv=argv, cwd=cwd, stdin=None, env=env, timeout_seconds=seconds,
                             memory_bytes=MEMORY, raw_prefix=directory / "process")
    stdout = directory / "process.stdout"
    stderr = directory / "process.stderr"
    receipt["recorded_at"] = now()
    atomic(directory / "supervisor.json", receipt)
    return receipt, stdout.read_bytes(), stderr.read_bytes()


def execute() -> dict:
    manifest = validate()
    gate(manifest)
    run_dir = safe(ROOT, RUN, exists=False)
    require(not run_dir.exists(), "refuse confirmation overwrite")
    run_dir.mkdir(parents=True)
    runtime = load(ROOT / RUNTIME)
    builds = {}
    binaries = {}
    for profile in ("baseline", "mutant"):
        workspace, target = materialize(profile)
        env = dict(runtime["environment_common"])
        env["CARGO_TARGET_DIR"] = str(target)
        receipt, stdout, stderr = supervise(
            "build-" + profile, runtime["build_argv"], workspace, env, 600)
        require(receipt["exit_code"] == 0 and not stdout and receipt["cleanup_complete"]
                and not receipt["timed_out"] and receipt["memory_monitor_error"] is None
                and receipt["memory_monitor_samples"] > 0, "build failed: " + profile)
        binary = target / "release/nanoda_bin"
        require(binary.is_file(), "missing built binary")
        binaries[profile] = binary
        builds[profile] = {"receipt": binding(ROOT / RUN / ("build-" + profile) / "supervisor.json"),
                           "binary_sha256": sha(binary)}
    cells = []
    matrix = [
        ("control-baseline", "baseline", CONTROL_CONFIG, "ACCEPT"),
        ("control-mutant", "mutant", CONTROL_CONFIG, "ACCEPT"),
        ("candidate-baseline", "baseline", CANDIDATE_CONFIG, "DIRECT_ASSERTION_REFUSAL"),
        ("candidate-mutant", "mutant", CANDIDATE_CONFIG, "WORKER_PANIC_JOIN_REFUSAL"),
    ]
    checker_env = {"LANG": "C", "PATH": "/usr/bin:/bin", "RUST_BACKTRACE": "full"}
    for cell, profile, config, expected in matrix:
        receipt, stdout, stderr = supervise(cell, [str(binaries[profile]), str(ROOT / config)], ROOT,
                                            checker_env, 30)
        actual = classify(cell, receipt, stdout, stderr)
        cells.append({"cell": cell, "expected": expected, "actual": actual,
                      "receipt": binding(ROOT / RUN / cell / "supervisor.json"),
                      "stdout": binding(ROOT / RUN / cell / "process.stdout"),
                      "stderr": binding(ROOT / RUN / cell / "process.stderr")})
    require(all(row["actual"] == row["expected"] for row in cells), "four-cell confirmation differs")
    result = {
        "schema_version": 1, "item_id": ITEM, "outcome": "SUCCESS", "generated_at": now(),
        "builds": builds, "cells": cells,
        "conclusion": "Both controls accepted. The baseline candidate failed directly on the main thread; the exact one-worker mutant failed in thread_0 and then at the parent join.",
        "claim_limit": "Operational diagnostic distinction only; both observers reject the candidate, so this is not an acceptance or soundness difference.",
    }
    atomic(ROOT / BASE / "result.json", result)
    return result


def main() -> int:
    print(json.dumps(execute(), indent=2, sort_keys=True))
    return 0
