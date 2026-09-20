"""Bounded one-thread Nanoda child-panic regression controller.

This controller admits only the committed four-cell existing-byte protocol. It
records every reservation before process creation and preserves raw receipts.
The trusted local source tree, Rust toolchain, filesystem and operating system
are assumptions; this is provenance and process accounting, not a sandbox.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from lib.cvc_prep import append, bind, committed, lock, read_events, require, safe
from lib.cvc_process import atomic, now, sha
from lib.cvc_signal_retry import signal_retry
from lib.metamorphic_pilot_runner import run_supervised


ITEM = "SURVIVOR-THREAD-ONE-CHILD-PANIC-REGRESSION-1"
FRONTIER = "F-DISCOVERY-AND-CONFORMANCE"
RUN = "survivor-thread-one-child-panic-regression-0001-r2"
BASE = "results/research/survivor-thread-one-child-panic-regression-1"
OUT = BASE + "/run-0001-r2"
WORK = BASE + "/work-record-r2.json"
PLAN = "docs/research/SURVIVOR_THREAD_ONE_CHILD_PANIC_REGRESSION_PLAN.md"
MANIFEST = "config/survivor-thread-one-child-panic-regression-0001-r2.json"
SOURCE_LOCK = "results/research/alt-survivors-2026-09-08/source-lock.json"
MUTATION = "mutations/nanoda-gen-2bdfe18a9ec2.json"
CONTROL = "corpus/controls/nanoda-gen-21ef4d1d32a1-matching-let-control.ndjson"
CANDIDATE = "corpus/generated/nanoda-gen-21ef4d1d32a1-let-value-type-mismatch.ndjson"
ASSESSMENT = "results/research/survivor-thread-one-determinism-1/determinism-assessment.json"
ASSESSMENT_RESULT = "results/research/survivor-thread-one-determinism-1/result.json"
SOURCE = BASE + "/source-materialization.json"
RUNTIME = BASE + "/runtime-binding.json"
ENTRY = BASE + "/entry-decision.json"
RECEIPT = BASE + "/focused-test-receipt-r2.json"
REPAIR = BASE + "/tooling-repair-0001.json"

LIMITS = {
    "active_seconds": 3600,
    "sessions": 1,
    "offline_build_launches": 2,
    "offline_build_timeout_seconds": 600,
    "checker_launches": 4,
    "checker_timeout_seconds": 30,
    "memory_bytes": 2147483648,
    "lean_proof_launches": 0,
    "research_network_requests": 0,
    "new_export_byte_variants": 0,
    "new_mutation_identities": 0,
    "external_actions": 0,
}
CHECKER_ENV = {"LANG": "C", "PATH": "/usr/bin:/bin", "RUST_BACKTRACE": "full"}
SUCCESS = b"Checked 1 declarations with no errors\n"
CODE = [
    "lib/survivor_thread_one_child_panic_regression.py",
    "scripts/execute-survivor-thread-one-child-panic-regression",
    "scripts/validate-survivor-thread-one-child-panic-regression",
    "tests/test_survivor_thread_one_child_panic_regression.py",
    "lib/cvc_prep.py",
    "lib/cvc_process.py",
    "lib/metamorphic_pilot_runner.py",
    "lib/research_queue_v3.py",
]
EXPECTED_AUTHORIZATION = (
    "The owner authorized execution of SURVIVOR-THREAD-ONE-CHILD-PANIC-REGRESSION-1. "
    "Execute only the committed one-session, four-cell existing-byte protocol; preserve "
    "all process receipts, stop on an infrastructure or control failure, then close, "
    "select but do not start a successor, validate, commit and push main."
)


def load(path: Path | str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def finite(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def binding(root: Path, path: Path) -> dict[str, str]:
    return {"path": path.relative_to(root).as_posix(), "sha256": sha(path)}


def exact(root: Path, row: dict, path: str, digest: str) -> Path:
    require(row == {"path": path, "sha256": digest}, "wrong fixed binding: " + path)
    return bind(root, row)


def manifest_path(root: Path) -> Path:
    return safe(root, MANIFEST)


def _safe_created(root: Path, rel: str) -> Path:
    path = safe(root, rel, exists=False)
    require(not path.exists() and not path.is_symlink(), "refuse existing mutable output: " + rel)
    return path


def validate_source(root: Path, row: dict) -> dict:
    source = load(exact(root, row, SOURCE, row["sha256"]))
    require(source["schema_version"] == 1
            and source["kind"] == "SURVIVOR_THREAD_ONE_CHILD_PANIC_SOURCE_MATERIALIZATION"
            and source["revision"] == "6ae1f0cd962f081f6c423454c5da729d841236a7",
            "wrong source materialization")
    exact(root, source["source_lock"], SOURCE_LOCK,
          "fb8ddc20e941aed1f56288ce83a83016e718d8abdf9756b34b96384236fdd472")
    lock_data = load(root / SOURCE_LOCK)
    require(len(lock_data["files"]) == 22 and source["source_file_count"] == 22,
            "pinned source inventory differs")
    for file_row in lock_data["files"]:
        file_binding = file_row["binding"]
        path = bind(root, {"path": file_binding["path"], "sha256": file_binding["sha256"]})
        require(path.stat().st_size == file_binding["bytes"], "source byte count differs")
    baseline, mutant = source["baseline"], source["mutant"]
    require(baseline["workspace"] == "external/survivor-thread-one-child-panic-regression-0001-baseline"
            and baseline["target"] == "external/survivor-thread-one-child-panic-regression-0001-target-baseline"
            and baseline["product"] == "external/survivor-thread-one-child-panic-regression-0001-products/baseline/nanoda_bin",
            "wrong baseline paths")
    require(mutant["workspace"] == "external/survivor-thread-one-child-panic-regression-0001-mutant"
            and mutant["target"] == "external/survivor-thread-one-child-panic-regression-0001-target-mutant"
            and mutant["product"] == "external/survivor-thread-one-child-panic-regression-0001-products/mutant/nanoda_bin",
            "wrong mutant paths")
    require(baseline["tc"] == {
        "path": "results/research/alt-survivors-2026-09-08/evidence/pinned-nanoda/src/tc.rs",
        "bytes": 56602,
        "sha256": "622b5aaf04b478485ca462b4938f3576c8da20e11bdf53b32f6e8b9021403efc",
    }, "wrong baseline tc binding")
    baseline_tc = root / baseline["tc"]["path"]
    require(sha(baseline_tc) == baseline["tc"]["sha256"] and baseline_tc.stat().st_size == 56602,
            "baseline tc drift")
    exact(root, mutant["mutation_spec"], MUTATION,
          "565dade1407732bed722b3db2758f77e6a3a8a3cd079ce526974d91b8347aca6")
    patch = {"path": "src/tc.rs", "line": 147, "occurrence": 0,
             "original": "self.config.num_threads > 1",
             "mutated": "self.config.num_threads >= 1"}
    require(mutant["patch"] == patch and mutant["tc_after_patch"] == {
        "bytes": 56603,
        "sha256": "a2a41ceb83361d892cd260f60605338788267635baf33f19cedf43e9aa579fdb",
    }, "one-field mutation binding differs")
    spec = load(root / MUTATION)
    require(spec["mutation_operator"] == "REL_GT_TO_GE"
            and spec["original"] == patch["original"]
            and spec["mutated"] == "(" + patch["mutated"] + ")"
            and spec["source_file"] == patch["path"] and spec["source_span"] == "147",
            "mutation specification differs")
    return source


def validate_runtime(root: Path, row: dict) -> dict:
    runtime = load(exact(root, row, RUNTIME, row["sha256"]))
    require(runtime["schema_version"] == 1
            and runtime["kind"] == "SURVIVOR_THREAD_ONE_CHILD_PANIC_RUNTIME_BINDING",
            "runtime binding identity differs")
    prior = runtime["prior_runtime_binding"]
    exact(root, prior, "results/research/survivor-thread-config-regression-1/runtime-binding.json",
          "b885d36054cbc220579f6309e3040477c522f2409d213e3098b0b7bcf65e3cfc")
    tools = runtime["tools"]
    for name in ("cargo", "rustc"):
        tool = tools[name]
        path = Path(tool["path"])
        require(path.is_file() and not path.is_symlink() and path.stat().st_size == tool["bytes"]
                and sha(path) == tool["sha256"], "runtime tool drift: " + name)
    expected = [tools["cargo"]["path"], "build", "--release", "--locked", "--offline"]
    require(runtime["build_argv"] == expected and runtime["environment_common"]["CARGO_NET_OFFLINE"] == "true"
            and runtime["environment_common"]["RUSTC"] == tools["rustc"]["path"]
            and "HOME" not in runtime["environment_common"], "runtime invocation differs")
    return runtime


def validate_manifest(root: Path, *, launch: bool = False) -> dict:
    root = Path(root).resolve()
    manifest = load(manifest_path(root))
    expected_fields = {
        "schema_version", "item_id", "run_id", "limits", "prelaunch_active_seconds",
        "memory_bytes", "work_record", "entry_decision", "source_materialization",
        "runtime_binding", "tooling_repair", "fixed_inputs", "configs", "matrix",
        "checker_environment", "tooling_inputs", "focused_test_receipt",
    }
    require(set(manifest) == expected_fields and manifest["schema_version"] == 1
            and manifest["item_id"] == ITEM and manifest["run_id"] == RUN
            and manifest["limits"] == LIMITS and manifest["memory_bytes"] == LIMITS["memory_bytes"]
            and finite(manifest["prelaunch_active_seconds"])
            and 300 <= manifest["prelaunch_active_seconds"] <= 1800, "wrong manifest limits")
    work = load(exact(root, manifest["work_record"], WORK, manifest["work_record"]["sha256"]))
    require(work["item_id"] == ITEM and work["status"] == "ACTIVE"
            and work["authorization"] == EXPECTED_AUTHORIZATION and work["budget"] == LIMITS
            and work["research_counts"] == {
                "offline_build_launches": 0, "checker_launches": 0, "lean_proof_launches": 0,
                "research_network_requests": 0, "new_export_byte_variants": 0,
                "new_mutation_identities": 0, "external_actions": 0,
            }, "work record does not preserve prelaunch state")
    repair = load(exact(root, manifest["tooling_repair"], REPAIR,
                        manifest["tooling_repair"]["sha256"]))
    require(set(repair) == {"schema_version", "item_id", "kind", "recorded_at",
                            "classification", "original_execution_manifest", "reservation",
                            "raw_error", "no_process_evidence", "repair", "continuation"}
            and repair["item_id"] == ITEM
            and repair["kind"] == "ENGINEERING_CONTROLLER_REPAIR"
            and repair["classification"] == "MISSING_SIGNAL_RETRY_IMPORT_BEFORE_PROCESS"
            and repair["original_execution_manifest"] == {
                "path": "config/survivor-thread-one-child-panic-regression-0001.json",
                "sha256": "13858e5f15fa0a17a41113c090fe3b6ed92bb1d7b6161eb8079b235f658030ed",
            }
            and repair["repair"] == {
                "new_controller_revision": "R2",
                "change": "Import signal_retry before entering the supervised process context.",
                "scope": "Controller-only repair; no scientific input, source mutation, configuration or expected predicate changes.",
            }
            and repair["continuation"] == "A separate R2 manifest and ledger may run the original four-cell matrix because the preserved R1 reservation did not invoke Cargo or a checker.",
            "tooling repair binding differs")
    require(work["prior_controller_incident"] == manifest["tooling_repair"],
            "work record does not bind the tooling repair")
    expected_reservation = {
        "number": 1,
        "phase": "build",
        "cell": "baseline",
        "reserved_seconds": 600,
        "events": {"path": BASE + "/run-0001/execution/events.jsonl",
                   "sha256": "eda82debf9b42242abb68fcc19937a4bf5a399ab67d8a053eefa0a555e8a8427"},
        "state": {"path": BASE + "/run-0001/execution/state.json",
                  "sha256": "57c69f1fd832275ffbda1f33ec3974d6230b24b5e26f8382a07d2d6dbc9952c1"},
        "request": {"path": BASE + "/run-0001/attempts/01/request.json",
                    "sha256": "ff7c92532416df96a3195e7ae35581236b5b2103e000a0bb64f2cd8226f69396"},
    }
    require(repair["reservation"] == expected_reservation and repair["raw_error"] == {
        "path": BASE + "/run-0001/controller-error.txt",
        "sha256": "9ec7a36ad4435bfba071329f3ca93d18d5e9ca0de501939c255f0a4f1921240e",
    } and repair["no_process_evidence"] == {
        "cargo_or_checker_process_invoked": False,
        "supervisor_receipt_exists": False,
        "stdout_receipt_exists": False,
        "stderr_receipt_exists": False,
    }, "R1 reservation evidence differs")
    for row in (expected_reservation["events"], expected_reservation["state"],
                expected_reservation["request"], repair["raw_error"]):
        bind(root, row)
    decision = load(exact(root, manifest["entry_decision"], ENTRY, manifest["entry_decision"]["sha256"]))
    require(decision["item_id"] == ITEM and decision["owner_authorization"] == "Go ahead."
            and decision["one_worker_protocol"] is True, "entry decision differs")
    source = validate_source(root, manifest["source_materialization"])
    runtime = validate_runtime(root, manifest["runtime_binding"])
    expected_inputs = [
        {"path": MUTATION, "sha256": "565dade1407732bed722b3db2758f77e6a3a8a3cd079ce526974d91b8347aca6"},
        {"path": SOURCE_LOCK, "sha256": "fb8ddc20e941aed1f56288ce83a83016e718d8abdf9756b34b96384236fdd472"},
        {"path": CONTROL, "sha256": "63ef460ca2aac739482c983457cd14309f4d7149ecd2c0d79d53fe2a410c9f16"},
        {"path": CANDIDATE, "sha256": "52e75d78c948d466e90fb203e7a04192dde4273c7319d44fc261fd2b3b6beeac"},
        {"path": ASSESSMENT, "sha256": "3d00b95dd3211da3aa4a15f0cdfbe0f1feb28b771e690bf45f2c29ed7609e4e4"},
        {"path": ASSESSMENT_RESULT, "sha256": "23f9d6846fe25b5fde7f48fef7faa5999cde962e911a1067a67408aac19561a9"},
    ]
    require(manifest["fixed_inputs"] == expected_inputs, "scientific bindings differ")
    for row in expected_inputs:
        bind(root, row)
    require(manifest["checker_environment"] == CHECKER_ENV, "checker environment differs")
    require(set(manifest["configs"]) == {"control", "candidate"}, "wrong configs")
    for role, source_path in (("control", CONTROL), ("candidate", CANDIDATE)):
        config_row = manifest["configs"][role]
        require(config_row["path"] == BASE + "/configs/" + role + ".json", "wrong config path")
        config = load(bind(root, config_row))
        require(config == {
            "export_file_path": str(root / source_path), "nat_extension": True,
            "num_threads": 1, "print_axioms": False, "print_success_message": True,
            "string_extension": True, "unpermitted_axiom_hard_error": False,
            "unsafe_permit_all_axioms": True, "use_stdin": False,
        }, "one-thread configuration differs")
    expected_matrix = [
        {"id": "control-baseline", "observer": "baseline", "input": "control", "expected": "ACCEPT"},
        {"id": "control-mutant", "observer": "mutant", "input": "control", "expected": "ACCEPT"},
        {"id": "candidate-baseline", "observer": "baseline", "input": "candidate", "expected": "DIRECT_ASSERTION_REFUSAL"},
        {"id": "candidate-mutant", "observer": "mutant", "input": "candidate", "expected": "WORKER_PANIC_JOIN_REFUSAL"},
    ]
    require(manifest["matrix"] == expected_matrix, "four-cell protocol differs")
    require([row["path"] for row in manifest["tooling_inputs"]] == CODE, "tooling inventory differs")
    for row in manifest["tooling_inputs"]:
        bind(root, row)
    receipt = load(bind(root, manifest["focused_test_receipt"]))
    require(receipt["item_id"] == ITEM and receipt["status"] == "PASS"
            and receipt["real_process_launches"] == 0 and receipt["tooling_inputs"] == manifest["tooling_inputs"],
            "inert test receipt differs")
    if launch:
        gate(root, manifest)
        for row in ([manifest["work_record"], manifest["entry_decision"], manifest["source_materialization"],
                     manifest["runtime_binding"], manifest["tooling_repair"], manifest["focused_test_receipt"]]
                    + manifest["fixed_inputs"] + list(manifest["configs"].values())
                    + manifest["tooling_inputs"]):
            committed(root, row["path"])
        for path in (MANIFEST, "config/research-queue.json", "docs/RESEARCH_STATUS.md", PLAN):
            committed(root, path)
    return {"manifest": manifest, "source": source, "runtime": runtime}


def gate(root: Path, manifest: dict, charged_seconds: float = 0, reservation_seconds: float = 0):
    from lib.research_queue_v3 import load_queue
    queue = load_queue(root, require_ready=True)
    row = next((item for item in queue["items"] if item["id"] == ITEM), None)
    require(queue["frontier_id"] == FRONTIER and queue["selected_item"] == ITEM
            and row is not None and row["status"] == "ACTIVE", "item is not selected ACTIVE")
    work = load(root / WORK)
    require(work["status"] == "ACTIVE" and work["authorization"] == EXPECTED_AUTHORIZATION
            and work["budget"] == LIMITS, "unbound execution authority")
    used = work["pre_record_work_conservative_seconds"] + manifest["prelaunch_active_seconds"] + charged_seconds
    require(finite(used) and finite(reservation_seconds)
            and used + reservation_seconds <= LIMITS["active_seconds"],
            "active-time cap cannot cover reservation")
    require(not (root / BASE / "work-closure.json").exists(), "item is already closed")
    return LIMITS["active_seconds"] - used


def materialize(root: Path, source: dict) -> None:
    lock_data = load(root / SOURCE_LOCK)
    expected = {row["source_path"] for row in lock_data["files"]}
    for profile in ("baseline", "mutant"):
        workspace = root / source[profile]["workspace"]
        if workspace.exists():
            actual = {path.relative_to(workspace).as_posix() for path in workspace.rglob("*") if path.is_file()}
            require(actual == expected, "existing materialization differs")
        else:
            for file_row in lock_data["files"]:
                donor = root / file_row["binding"]["path"]
                output = workspace / file_row["source_path"]
                output.parent.mkdir(parents=True, exist_ok=True)
                if profile == "mutant" and file_row["source_path"] == "src/tc.rs":
                    data = donor.read_bytes()
                    patch = source["mutant"]["patch"]
                    lines = data.splitlines(keepends=True)
                    require(len(lines) >= patch["line"] and lines[patch["line"] - 1].count(patch["original"].encode()) == 1
                            and sum(line.count(patch["original"].encode()) for line in lines) == 1,
                            "mutation site differs")
                    changed = b"".join(lines[:patch["line"] - 1] + [
                        lines[patch["line"] - 1].replace(patch["original"].encode(), patch["mutated"].encode(), 1)
                    ] + lines[patch["line"]:])
                    expected_mutant = source["mutant"]["tc_after_patch"]
                    require(len(changed) == expected_mutant["bytes"]
                            and hashlib.sha256(changed).hexdigest() == expected_mutant["sha256"],
                            "mutant byte relation differs")
                    output.write_bytes(changed)
                else:
                    shutil.copyfile(donor, output)
                    require(sha(output) == file_row["binding"]["sha256"], "materialized source changed")


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
    lower = stderr.lower()
    if any(token in lower for token in (b"parse error", b"parser error", b"invalid json")):
        return "PARSER_IMPORT_REJECTION"
    return "CRASH"


def next_action(attempts: list[dict]):
    if not attempts:
        return ("build", "baseline")
    last = attempts[-1]
    if "terminal" not in last:
        return ("PAUSED", None)
    terminal, reservation = last["terminal"], last["reservation"]
    if terminal["engineering_pause"]:
        return ("PAUSED", None)
    if reservation["phase"] == "build":
        if terminal["status"] != "COMPLETE" or "binary" not in terminal:
            return ("STOP", None)
        return ("build", "mutant") if reservation["cell"] == "baseline" else ("checker", 0)
    cell = reservation["cell"]
    if cell < 2 and terminal["classification"] != "ACCEPT":
        return ("STOP", None)
    if cell == 2 and terminal["classification"] != "DIRECT_ASSERTION_REFUSAL":
        return ("STOP", None)
    if cell == 3:
        return ("DONE", None) if terminal["classification"] == "WORKER_PANIC_JOIN_REFUSAL" else ("STOP", None)
    return ("checker", cell + 1)


def derive(events: list[dict]) -> dict:
    require(events and events[0] == {"kind": "START", "run_id": RUN,
                                     "event_sha256": events[0]["event_sha256"],
                                     "previous_sha256": "0" * 64}, "wrong ledger start")
    attempts: list[dict] = []
    for event in events[1:]:
        if event["kind"] == "RESERVED":
            require(len(attempts) == event["number"] - 1 and (not attempts or "terminal" in attempts[-1]),
                    "invalid reservation order")
            phase, cell = event["phase"], event["cell"]
            expected_phase, expected_cell = next_action(attempts)
            require((phase, cell) == (expected_phase, expected_cell), "fixed protocol order differs")
            seconds = LIMITS["offline_build_timeout_seconds"] if phase == "build" else LIMITS["checker_timeout_seconds"]
            require(phase in {"build", "checker"} and event["reserved_seconds"] == seconds
                    and finite(event["active_seconds"])
                    and event["active_seconds"] + seconds <= LIMITS["active_seconds"], "invalid reservation")
            attempts.append({"reservation": event})
        elif event["kind"] == "TERMINAL":
            require(attempts and event["number"] == len(attempts) and "terminal" not in attempts[-1]
                    and event["status"] in {"COMPLETE", "FAILED", "TIMED_OUT", "INTERRUPTED"}
                    and finite(event["charged_seconds"]), "invalid terminal")
            attempts[-1]["terminal"] = event
        else:
            raise ValueError("unknown ledger event")
    charged = sum(row.get("terminal", {}).get("charged_seconds", row["reservation"]["reserved_seconds"])
                  for row in attempts)
    return {"attempts": attempts, "charged_seconds": charged, "next_action": next_action(attempts)}


class Ledger:
    def __init__(self, root: Path):
        self.root = root
        self.directory = root / OUT / "execution"
        self.path = self.directory / "events.jsonl"
        self.snapshot = self.directory / "state.json"

    def initialize(self):
        require(not self.directory.exists(), "refuse ledger reset")
        self.directory.mkdir(parents=True)
        append(self.path, {"kind": "START", "run_id": RUN})
        self.save()

    def save(self):
        events = read_events(self.path)
        atomic(self.snapshot, {"count": len(events), "tail": events[-1]["event_sha256"]})

    def read(self):
        events = read_events(self.path)
        snapshot = load(self.snapshot)
        require(snapshot == {"count": len(events), "tail": events[-1]["event_sha256"]}, "ledger snapshot differs")
        return events, derive(events)

    def add(self, event: dict):
        events, _ = self.read()
        derive(events + [{**event, "previous_sha256": events[-1]["event_sha256"], "event_sha256": hashlib.sha256(
            json.dumps({**event, "previous_sha256": events[-1]["event_sha256"]}, sort_keys=True,
                       separators=(",", ":")).encode()).hexdigest()}])
        append(self.path, event)
        self.save()


def _binary(state: dict, profile: str, root: Path) -> dict:
    for attempt in state["attempts"]:
        reservation, terminal = attempt["reservation"], attempt.get("terminal", {})
        if reservation["phase"] == "build" and reservation["cell"] == profile and "binary" in terminal:
            bind(root, terminal["binary"])
            return terminal["binary"]
    raise ValueError("missing built observer: " + profile)


def finish_attempt(root: Path, bundle: dict, reservation: dict) -> dict:
    directory = root / reservation["directory"]
    request = load(directory / "request.json")
    receipt = load(directory / "supervisor.json")
    require(request["request_sha256"] == receipt["request_sha256"]
            and request["argv"] == reservation["argv"] and request["cwd"] == reservation["cwd"]
            and request["env"] == reservation["env"] and request["seconds"] == reservation["reserved_seconds"],
            "request/receipt binding differs")
    stdout, stderr = directory / "process.stdout", directory / "process.stderr"
    require(stdout.is_file() and stderr.is_file()
            and receipt["stdout_sha256"] == sha(stdout) and receipt["stderr_sha256"] == sha(stderr),
            "raw output receipt differs")
    terminal = {
        "kind": "TERMINAL", "number": reservation["number"],
        "status": "COMPLETE" if receipt["exit_code"] == 0 and not receipt["timed_out"] else "FAILED",
        "returncode": receipt["exit_code"], "charged_seconds": receipt["elapsed_seconds"],
        "cleanup_completed": receipt["cleanup_complete"], "at": now(),
        "engineering_pause": receipt["memory_monitor_error"] is not None or receipt["memory_monitor_samples"] <= 0
            or receipt["maximum_observed_rss_bytes"] <= 0 or receipt["memory_exceeded"]
            or receipt["timed_out"] or not receipt["cleanup_complete"],
        "receipts": [binding(root, directory / name) for name in
                     ("request.json", "supervisor.json", "process.stdout", "process.stderr")],
    }
    if reservation["phase"] == "build":
        terminal["engineering_pause"] |= terminal["status"] != "COMPLETE"
        if not terminal["engineering_pause"]:
            profile = reservation["cell"]
            source = bundle["source"][profile]
            output = root / source["target"] / "release/nanoda_bin"
            product = root / source["product"]
            require(output.is_file() and not output.is_symlink() and not product.exists(), "build product unavailable")
            product.parent.mkdir(parents=True, exist_ok=False)
            shutil.copyfile(output, product)
            product.chmod(0o555)
            require(sha(product) == sha(output), "product copy drift")
            terminal["binary"] = binding(root, product)
    else:
        cell = bundle["manifest"]["matrix"][reservation["cell"]]["id"]
        terminal["classification"] = classify(cell, receipt, stdout.read_bytes(), stderr.read_bytes())
        terminal["engineering_pause"] |= terminal["classification"] == "INFRASTRUCTURE_FAILURE"
    return terminal


def execute(root: Path) -> dict:
    root = Path(root).resolve()
    bundle = validate_manifest(root, launch=True)
    with lock(root / OUT / "controller.lock"):
        ledger = Ledger(root)
        if not ledger.directory.exists():
            ledger.initialize()
        events, state = ledger.read()
        action, cell = state["next_action"]
        require(action not in {"PAUSED", "STOP"}, "execution stopped; preserve evidence and close")
        if action == "DONE":
            return state
        seconds = LIMITS["offline_build_timeout_seconds"] if action == "build" else LIMITS["checker_timeout_seconds"]
        remaining = gate(root, bundle["manifest"], state["charged_seconds"], seconds)
        materialize(root, bundle["source"])
        if action == "build":
            env = dict(bundle["runtime"]["environment_common"])
            env["CARGO_TARGET_DIR"] = str(root / bundle["source"][cell]["target"])
            argv = bundle["runtime"]["build_argv"]
            cwd = str(root / bundle["source"][cell]["workspace"])
        else:
            matrix = bundle["manifest"]["matrix"][cell]
            binary = _binary(state, matrix["observer"], root)
            argv = [str(root / binary["path"]), str(root / bundle["manifest"]["configs"][matrix["input"]]["path"])]
            cwd, env = str(root), CHECKER_ENV
        number = len(state["attempts"]) + 1
        directory = root / OUT / "attempts" / f"{number:02d}"
        directory.mkdir(parents=True, exist_ok=False)
        request = {"argv": argv, "cwd": cwd, "env": env, "seconds": seconds,
                   "manifest": binding(root, root / MANIFEST), "at": now(), "monotonic": time.monotonic()}
        request["request_sha256"] = hashlib.sha256(json.dumps(request, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        atomic(directory / "request.json", request)
        reservation = {
            "kind": "RESERVED", "number": number, "phase": action, "cell": cell,
            "reserved_seconds": seconds, "active_seconds": LIMITS["active_seconds"] - remaining,
            "argv": argv, "cwd": cwd, "env": env, "directory": directory.relative_to(root).as_posix(),
            "request": binding(root, directory / "request.json"), "at": now(), "monotonic": time.monotonic(),
        }
        ledger.add(reservation)
        with signal_retry():
            receipt = run_supervised(argv=argv, cwd=Path(cwd), stdin=None, env=env, timeout_seconds=seconds,
                                     memory_bytes=LIMITS["memory_bytes"], raw_prefix=directory / "process")
        receipt["request_sha256"] = request["request_sha256"]
        atomic(directory / "supervisor.json", receipt)
        ledger.add(finish_attempt(root, bundle, reservation))
        return ledger.read()[1]


def evidence(root: Path) -> dict:
    events, state = Ledger(Path(root).resolve()).read()
    for attempt in state["attempts"]:
        for row in attempt.get("terminal", {}).get("receipts", []):
            bind(Path(root).resolve(), row)
    return state


def main(validate: bool = False):
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", action="store_true")
    arguments = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = evidence(root) if arguments.evidence else validate_manifest(root) if validate else execute(root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0
