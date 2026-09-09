"""Finite zero-thread Nanoda baseline/mutant regression controller.

The controller has no command override and admits only the committed fixed pair.
Trusted local source, the filesystem, and the operating system are assumptions;
this is process accounting and provenance control, not a hostile-code sandbox.
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
from lib.cvc_process import atomic, now, run_process, sha
from lib.cvc_signal_retry import signal_retry


ITEM = "SURVIVOR-THREAD-CONFIG-REGRESSION-1"
FRONTIER = "F-SURVIVOR-THREAD-CONFIG-REGRESSION"
RUN = "survivor-thread-config-regression-0001"
BASE = "results/research/survivor-thread-config-regression-1"
OUT = BASE + "/run-0001"
WORK = BASE + "/work-record.json"
PRELAUNCH_WORK = BASE + "/prelaunch-work-record.json"
PLAN = "docs/research/SURVIVOR_THREAD_CONFIG_REGRESSION_PLAN.md"
MANIFEST = "config/survivor-thread-config-regression-0001.json"
SOURCE_LOCK = "results/research/alt-survivors-2026-09-08/source-lock.json"
MUTATION = "mutations/nanoda-gen-93b21593b0d8.json"
CANDIDATE = "corpus/generated/nanoda-gen-21ef4d1d32a1-let-value-type-mismatch.ndjson"
CONTROL = "corpus/controls/nanoda-gen-21ef4d1d32a1-matching-let-control.ndjson"
PRIOR_COMPARISON = "results/mutants/nanoda-gen-21ef4d1d32a1/augmented-comparison-v2.json"
ASSESSMENT = "results/research/survivor-thread-config-reachability-1/dispatch-assessment.json"
ASSESSMENT_RESULT = "results/research/survivor-thread-config-reachability-1/result.json"
RUNTIME = BASE + "/runtime-binding.json"
SOURCE = BASE + "/source-materialization.json"

LIMITS = {
    "active_seconds": 7200,
    "sessions": 2,
    "offline_build_launches": 2,
    "offline_build_timeout_seconds": 180,
    "checker_launches": 4,
    "checker_timeout_seconds": 30,
    "lean_proof_launches": 0,
    "research_network_requests": 0,
    "new_export_byte_variants": 0,
    "new_mutation_identities": 0,
    "external_actions": 0,
}
CODE = [
    "lib/survivor_thread_config_regression.py",
    "scripts/execute-survivor-thread-config-regression",
    "scripts/validate-survivor-thread-config-regression",
    "tests/test_survivor_thread_config_regression.py",
    "lib/cvc_process.py",
    "lib/cvc_signal_retry.py",
    "lib/cvc_prep.py",
    "lib/survivor_let_payload.py",
    "lib/research_queue_v3.py",
]
SCIENCE_KEYS = [
    "entry_decision", "prelaunch_work_record", "source_materialization",
    "runtime_binding", "fixed_inputs", "configs", "matrix", "checker_environment",
]
EXPECTED_AUTHORIZATION = (
    "The owner explicitly requested execution of the next plan. Execute only "
    "SURVIVOR-THREAD-CONFIG-REGRESSION-1 through its bounded fixed-pair stop, "
    "update durable state, select but do not start a successor, validate, commit and push main."
)
SUCCESS = b"Checked 1 declarations with no errors\n"
CHECKER_ENV = {"PATH": "/usr/bin:/bin", "LANG": "C", "RUST_BACKTRACE": "full"}
INTERPRETABLE = {"ACCEPT", "TYPECHECK_REFUSAL"}


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def binding(root, path):
    path = Path(path)
    return {"path": path.relative_to(root).as_posix(), "sha256": sha(path)}


def finite(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def manifest_path(root, name):
    require(re.fullmatch(r"config/survivor-thread-config-regression-0001(?:-r[2-9][0-9]*)?\.json", name),
            "wrong manifest path")
    return safe(root, name)


def gate(root, manifest, charged_seconds=0, reservation_seconds=0):
    from lib.research_queue_v3 import load_queue

    queue = load_queue(root, require_ready=True)
    row = next((item for item in queue["items"] if item["id"] == ITEM), None)
    require(queue["frontier_id"] == FRONTIER and queue["selected_item"] == ITEM
            and row is not None and row["status"] == "ACTIVE", "G1: item not selected ACTIVE")
    work = load(root / WORK)
    require(work["item_id"] == ITEM and work["status"] == "ACTIVE"
            and work["authorization"] == EXPECTED_AUTHORIZATION
            and work["budget"] == LIMITS, "G1: exact execution authority absent")
    require(work["research_counts"] == {
        "offline_build_launches": 0, "checker_launches": 0, "lean_proof_launches": 0,
        "research_network_requests": 0, "new_export_byte_variants": 0,
        "new_mutation_identities": 0, "external_actions": 0,
    }, "G1: prelaunch research counts changed")
    used = (work["pre_record_work_conservative_seconds"]
            + manifest["prelaunch_active_seconds"] + charged_seconds)
    require(finite(used) and finite(reservation_seconds)
            and used + reservation_seconds <= LIMITS["active_seconds"],
            "active-time cap cannot cover reservation")
    require(not (root / BASE / "work-closure.json").exists(), "item work already closed")
    return LIMITS["active_seconds"] - used


def _exact_binding(root, row, path, digest):
    require(row == {"path": path, "sha256": digest}, "wrong fixed binding: " + path)
    bind(root, row)


def validate_source(root, row):
    require(row["path"] == SOURCE, "wrong source materialization path")
    source = load(bind(root, row))
    require(source["schema_version"] == 1
            and source["kind"] == "SURVIVOR_THREAD_CONFIG_SOURCE_MATERIALIZATION"
            and source["revision"] == "6ae1f0cd962f081f6c423454c5da729d841236a7"
            and source["source_file_count"] == 22, "wrong source materialization identity")
    _exact_binding(root, source["source_lock"], SOURCE_LOCK,
                   "fb8ddc20e941aed1f56288ce83a83016e718d8abdf9756b34b96384236fdd472")
    lock_data = load(root / SOURCE_LOCK)
    require(lock_data["revision"] == source["revision"] and len(lock_data["files"]) == 22,
            "source lock differs")
    for locked in lock_data["files"]:
        path = bind(root, {"path": locked["binding"]["path"],
                           "sha256": locked["binding"]["sha256"]})
        require(path.stat().st_size == locked["binding"]["bytes"], "source byte count differs")
    readme = source["readme"]
    path = bind(root, {"path": readme["path"], "sha256": readme["sha256"]})
    require(path.stat().st_size == readme["bytes"] == 6517, "README identity differs")
    baseline = source["baseline"]
    require(baseline["workspace"] == "external/survivor-thread-config-regression-0001-baseline"
            and baseline["target"] == "external/survivor-thread-config-regression-0001-target-baseline"
            and baseline["product"] == "external/survivor-thread-config-regression-0001-products/baseline/nanoda_bin",
            "baseline materialization paths differ")
    tc = baseline["tc"]
    path = bind(root, {"path": tc["path"], "sha256": tc["sha256"]})
    require(path.stat().st_size == tc["bytes"] == 56602
            and tc["sha256"] == "622b5aaf04b478485ca462b4938f3576c8da20e11bdf53b32f6e8b9021403efc",
            "baseline tc identity differs")
    mutant = source["mutant"]
    require(mutant["workspace"] == "external/survivor-thread-config-regression-0001-mutant"
            and mutant["target"] == "external/survivor-thread-config-regression-0001-target-mutant"
            and mutant["product"] == "external/survivor-thread-config-regression-0001-products/mutant/nanoda_bin",
            "mutant materialization paths differ")
    _exact_binding(root, mutant["mutation_spec"], MUTATION,
                   "b4c04dcf5b1b7335a282d228d4279ee792995f1132db5553f426b05971816d71")
    spec = load(root / MUTATION)
    expected_patch = {"path": "src/tc.rs", "line": 147, "occurrence": 0,
                      "original": "self.config.num_threads > 1",
                      "mutated": "!(self.config.num_threads > 1)"}
    require(mutant["patch"] == expected_patch
            and spec["source_file"] == expected_patch["path"]
            and int(spec["source_span"]) == expected_patch["line"]
            and spec["replace_occurrence"] == 0
            and spec["original"] == expected_patch["original"]
            and spec["mutated"] == expected_patch["mutated"], "mutation plan differs")
    require(mutant["tc_after_patch"] == {
        "bytes": 56605,
        "sha256": "3bd5c0da63537eb640f77f26ffd3cb64f62905fb1e80a9d3c0d7934f83d83e0e",
    }, "planned mutant tc identity differs")
    return source


def validate_runtime(root, row):
    require(row["path"] == RUNTIME, "wrong runtime binding path")
    runtime = load(bind(root, row))
    require(runtime["schema_version"] == 1
            and runtime["kind"] == "SURVIVOR_THREAD_CONFIG_RUNTIME_BINDING"
            and runtime["cargo_home"] == "external/survivor-let-reuse-0001-cargo-home",
            "wrong runtime identity")
    prior = runtime["prior_runtime_manifest"]
    p = root / prior["path"]
    require(prior == {"path": "results/research/survivor-let-reuse-1/runtime-manifest.json",
                      "bytes": 1223198,
                      "sha256": "aa9fec0e5065c1035ef08f3de61d96f0efc34707033aacc5ffa6cc46ff8d29bb"}
            and p.is_file() and p.stat().st_size == prior["bytes"] and sha(p) == prior["sha256"],
            "prior runtime manifest differs")
    expected_tools = {
        "cargo": ("/opt/homebrew/Cellar/rust/1.98.0/bin/cargo", 31148800,
                  "7dd84b082024c09872d9686922d1537b730a8a06bdd990dd75a6d5186c08dbcd"),
        "rustc": ("/opt/homebrew/Cellar/rust/1.98.0/bin/rustc", 341440,
                  "1f9bb25ccda465e30e4eec0d7338725963297793f341de3394d870fbae0c6cc3"),
    }
    for name, (tool_path, size, digest) in expected_tools.items():
        tool = runtime["tools"][name]
        p = Path(tool["path"])
        require(tool["path"] == tool_path and tool["bytes"] == size and tool["sha256"] == digest
                and isinstance(tool["version"], str) and p.is_file() and not p.is_symlink()
                and p.stat().st_size == size and sha(p) == digest, "runtime tool differs: " + name)
    require(runtime["build_argv"] == [expected_tools["cargo"][0], "build", "--release",
                                      "--locked", "--offline"], "build command differs")
    require(runtime["environment_common"] == {
        "CARGO_HOME": str(root / "external/survivor-let-reuse-0001-cargo-home"),
        "CARGO_NET_OFFLINE": "true", "LANG": "C",
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/Cellar/rust/1.98.0/bin",
        "RUSTC": expected_tools["rustc"][0], "RUST_BACKTRACE": "full",
    } and "HOME" not in runtime["environment_common"], "build environment differs")
    return runtime


def validate_manifest(root, name=MANIFEST, launch=False, payload=True):
    root = Path(root).resolve()
    manifest = load(manifest_path(root, name))
    expected = {"schema_version", "item_id", "run_id", "limits", "prelaunch_active_seconds",
                "entry_decision", "prelaunch_work_record", "source_materialization",
                "runtime_binding", "fixed_inputs", "configs", "matrix", "checker_environment",
                "tooling_inputs", "focused_test_receipt"}
    require(set(manifest) == expected and manifest["schema_version"] == 1
            and manifest["item_id"] == ITEM and manifest["run_id"] == RUN
            and manifest["limits"] == LIMITS
            and finite(manifest["prelaunch_active_seconds"])
            and 300 <= manifest["prelaunch_active_seconds"] <= 6000, "wrong manifest or limits")
    required = {
        "entry_decision": BASE + "/entry-decision.json",
        "prelaunch_work_record": PRELAUNCH_WORK,
        "source_materialization": SOURCE,
        "runtime_binding": RUNTIME,
    }
    for key, path in required.items():
        require(manifest[key]["path"] == path, "wrong bound path: " + key)
        bind(root, manifest[key])
    decision = load(root / manifest["entry_decision"]["path"])
    prelaunch = load(root / manifest["prelaunch_work_record"]["path"])
    require(decision["item_id"] == ITEM and decision["owner_authorization"] == "Execute the next plan."
            and prelaunch["item_id"] == ITEM and prelaunch["status"] == "ACTIVE"
            and prelaunch["authorization"] == EXPECTED_AUTHORIZATION
            and prelaunch["budget"] == LIMITS, "execution decision or authority differs")
    expected_fixed = [
        {"path": MUTATION, "sha256": "b4c04dcf5b1b7335a282d228d4279ee792995f1132db5553f426b05971816d71"},
        {"path": SOURCE_LOCK, "sha256": "fb8ddc20e941aed1f56288ce83a83016e718d8abdf9756b34b96384236fdd472"},
        {"path": CONTROL, "sha256": "63ef460ca2aac739482c983457cd14309f4d7149ecd2c0d79d53fe2a410c9f16"},
        {"path": CANDIDATE, "sha256": "52e75d78c948d466e90fb203e7a04192dde4273c7319d44fc261fd2b3b6beeac"},
        {"path": PRIOR_COMPARISON, "sha256": "1a1221c86690b5a4e183d9c7953d648c41a648eac0df94d06fadc5b3c4dde493"},
        {"path": ASSESSMENT, "sha256": "416eab29fbbb439ae801b0f1899eba25511549d7c015b7448015496a6864c29e"},
        {"path": ASSESSMENT_RESULT, "sha256": "8071aa9cea7d111b28efa7247aabb4a2642557f44b23e0c44f3fced5845a07f2"},
    ]
    require(manifest["fixed_inputs"] == expected_fixed, "fixed scientific identities differ")
    for row in expected_fixed:
        bind(root, row)
    source = validate_source(root, manifest["source_materialization"])
    validate_runtime(root, manifest["runtime_binding"])
    require(manifest["checker_environment"] == CHECKER_ENV, "checker environment differs")
    require(set(manifest["configs"]) == {"control", "candidate"}, "wrong config roles")
    for role, input_path in (("control", CONTROL), ("candidate", CANDIDATE)):
        row = manifest["configs"][role]
        require(row["path"] == BASE + "/configs/" + role + ".json", "wrong config path")
        config = load(bind(root, row))
        require(config == {
            "export_file_path": str(root / input_path), "nat_extension": True,
            "num_threads": 0, "print_axioms": False, "print_success_message": True,
            "string_extension": True, "unpermitted_axiom_hard_error": False,
            "unsafe_permit_all_axioms": True, "use_stdin": False,
        }, "zero-thread config differs")
    expected_matrix = [
        {"id": "control-baseline", "observer": "baseline", "input": "control", "expected": "ACCEPT"},
        {"id": "control-mutant", "observer": "mutant", "input": "control", "expected": "ACCEPT"},
        {"id": "candidate-baseline", "observer": "baseline", "input": "candidate", "expected": "TYPECHECK_REFUSAL"},
        {"id": "candidate-mutant", "observer": "mutant", "input": "candidate", "expected": "ACCEPT"},
    ]
    require(manifest["matrix"] == expected_matrix, "matrix or expected outcomes differ")
    require([row["path"] for row in manifest["tooling_inputs"]] == CODE,
            "incomplete tooling binding")
    all_rows = (manifest["fixed_inputs"] + list(manifest["configs"].values())
                + manifest["tooling_inputs"] + [manifest[key] for key in required]
                + [manifest["focused_test_receipt"]])
    for row in all_rows:
        bind(root, row)
        if launch:
            committed(root, row["path"])
    receipt = load(bind(root, manifest["focused_test_receipt"]))
    require(receipt["status"] == "PASS" and receipt["tooling_inputs"] == manifest["tooling_inputs"]
            and receipt["test_count"] >= 20 and receipt["real_process_launches"] == 0,
            "focused tests do not bind current tooling")
    if name != MANIFEST:
        first = load(manifest_path(root, MANIFEST))
        require(all(manifest[key] == first[key] for key in SCIENCE_KEYS)
                and manifest["limits"] == first["limits"]
                and manifest["prelaunch_active_seconds"] >= first["prelaunch_active_seconds"],
                "repair manifest changes science, authority, or budget")
    if payload:
        from lib.survivor_let_payload import verify
        verify(root, require_commit=launch)
    if launch:
        gate(root, manifest)
        for path in (name, "config/research-queue.json", "docs/RESEARCH_STATUS.md", PLAN):
            committed(root, path)
    return manifest


def next_action(attempts, repairs):
    if not attempts:
        return ("build", "baseline")
    last = attempts[-1]
    if "terminal" not in last:
        return ("PAUSED", None)
    if repairs and repairs[-1]["after_number"] == len(attempts):
        return (repairs[-1]["phase"], repairs[-1].get("cell"))
    reservation, terminal = last["reservation"], last["terminal"]
    if terminal.get("engineering_pause") or not terminal.get("cleanup_completed"):
        return ("PAUSED", None)
    if reservation["phase"] == "build":
        if terminal["status"] != "COMPLETE" or not terminal.get("binary"):
            return ("PAUSED", None)
        return (("build", "mutant") if reservation["cell"] == "baseline" else ("checker", 0))
    cell = reservation["cell"]
    if cell < 2 and terminal["classification"] != "ACCEPT":
        return ("STOP", None)
    if cell >= 2 and terminal["classification"] not in INTERPRETABLE:
        return ("PAUSED", None)
    return ("DONE", None) if cell == 3 else ("checker", cell + 1)


def derive(events):
    require(events and events[0]["kind"] == "START" and events[0]["run_id"] == RUN,
            "missing start")
    attempts, repairs = [], []
    for event in events[1:]:
        if event["kind"] == "RESERVED":
            require(not attempts or "terminal" in attempts[-1], "unreconciled reservation")
            require(event["number"] == len(attempts) + 1, "nonconsecutive reservation")
            phase = event["phase"]
            require(phase in {"build", "checker"}, "unknown process phase")
            limit, seconds = ((2, 180) if phase == "build" else (4, 30))
            require(sum(row["reservation"]["phase"] == phase for row in attempts) < limit
                    and event["reserved_seconds"] == seconds, "reservation cap")
            require(next_action(attempts, repairs) == (phase, event.get("cell")),
                    "launch violates fixed build/control/candidate order")
            require(finite(event["active_seconds"])
                    and event["active_seconds"] + seconds <= LIMITS["active_seconds"],
                    "invalid active budget reservation")
            attempts.append({"reservation": event})
        elif event["kind"] == "TERMINAL":
            require(attempts and "terminal" not in attempts[-1]
                    and event["number"] == len(attempts), "terminal without latest reservation")
            require(event["status"] in {"COMPLETE", "FAILED", "TIMED_OUT", "INTERRUPTED"}
                    and finite(event["charged_seconds"]), "invalid terminal")
            attempts[-1]["terminal"] = event
        elif event["kind"] == "REPAIR":
            require(attempts and "terminal" in attempts[-1]
                    and event["after_number"] == len(attempts)
                    and (not repairs or repairs[-1]["after_number"] != len(attempts))
                    and next_action(attempts, repairs) == ("PAUSED", None), "invalid repair")
            require(event["phase"] == attempts[-1]["reservation"]["phase"]
                    and event.get("cell") == attempts[-1]["reservation"].get("cell"),
                    "repair changes fixed action")
            repairs.append(event)
        else:
            raise ValueError("unknown ledger event")
    charged = sum(attempt.get("terminal", {}).get(
        "charged_seconds", attempt["reservation"]["reserved_seconds"]) for attempt in attempts)
    return {"attempts": attempts, "repairs": repairs,
            "next_action": next_action(attempts, repairs), "charged_seconds": charged}


class Ledger:
    def __init__(self, root):
        self.root = Path(root)
        self.directory = self.root / OUT / "execution"
        self.path = self.directory / "events.jsonl"
        self.snapshot = self.directory / "state.json"

    def initialize(self):
        require(not self.directory.exists(), "refuse reset of run directory")
        self.directory.mkdir(parents=True)
        append(self.path, {"kind": "START", "run_id": RUN, "at": now(),
                           "monotonic": time.monotonic()})
        self.save()

    def save(self):
        events = read_events(self.path)
        atomic(self.snapshot, {"count": len(events), "tail": events[-1]["event_sha256"]})

    def read(self):
        events = read_events(self.path)
        snapshot = load(self.snapshot)
        require(type(snapshot["count"]) is int and 1 <= snapshot["count"] <= len(events)
                and events[snapshot["count"] - 1]["event_sha256"] == snapshot["tail"],
                "ledger truncation/reset")
        return events, derive(events)

    def add(self, event):
        events, _ = self.read()
        derive(events + [event])
        append(self.path, event)
        self.save()


def classify(cell, receipt, stdout, stderr):
    if receipt["status"] == "TIMED_OUT":
        return "TIMEOUT"
    if (not receipt.get("cleanup_completed") or receipt.get("deadline_exceeded")
            or receipt.get("error")):
        return "INDETERMINATE"
    if receipt["status"] == "COMPLETE" and receipt["returncode"] == 0 \
            and stdout == SUCCESS and stderr == b"":
        return "ACCEPT"
    if (cell.startswith("candidate-") and receipt["status"] == "FAILED"
            and receipt["returncode"] == 101 and stdout == b""
            and b"panicked at src/tc.rs:921:71:" in stderr
            and b"assertion failed: self.def_eq(u, v)" in stderr
            and b"::infer\n" in stderr and b"::check_declar\n" in stderr):
        return "TYPECHECK_REFUSAL"
    lowered = stderr.lower()
    if any(token in lowered for token in
           (b"parse error", b"parser error", b"failed to parse", b"invalid json")):
        return "PARSE_ERROR"
    if b"unsupported" in lowered:
        return "UNSUPPORTED"
    if receipt["returncode"] != 0 or b"panicked at" in stderr:
        return "CRASH"
    return "INDETERMINATE"


def _copy_exact(source, destination, expected_sha):
    require(source.is_file() and not source.is_symlink() and sha(source) == expected_sha,
            "source changed during materialization")
    if destination.exists():
        require(destination.is_file() and not destination.is_symlink()
                and sha(destination) == expected_sha, "existing materialization differs")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name("." + destination.name + ".tmp")
    require(not temporary.exists(), "stale materialization temporary")
    shutil.copyfile(source, temporary)
    require(sha(temporary) == expected_sha, "copy changed bytes")
    os.replace(temporary, destination)


def materialize(root, manifest):
    source = validate_source(root, manifest["source_materialization"])
    lock_data = load(root / SOURCE_LOCK)
    expected_paths = {row["source_path"] for row in lock_data["files"]} | {"README.md"}
    for profile in ("baseline", "mutant"):
        workspace = root / source[profile]["workspace"]
        workspace.mkdir(parents=True, exist_ok=True)
        for row in lock_data["files"]:
            rel = row["source_path"]
            donor = root / row["binding"]["path"]
            destination = workspace / rel
            if profile == "mutant" and rel == "src/tc.rs":
                data = donor.read_bytes()
                patch = source["mutant"]["patch"]
                lines = data.splitlines(keepends=True)
                original = patch["original"].encode()
                mutated = patch["mutated"].encode()
                require(len(lines) >= patch["line"] and lines[patch["line"] - 1].count(original) == 1
                        and sum(line.count(original) for line in lines) == 1, "mutation site differs")
                lines[patch["line"] - 1] = lines[patch["line"] - 1].replace(original, mutated, 1)
                changed = b"".join(lines)
                expected = source["mutant"]["tc_after_patch"]
                require(len(changed) == expected["bytes"]
                        and hashlib.sha256(changed).hexdigest() == expected["sha256"],
                        "mutant bytes differ from frozen plan")
                if destination.exists():
                    require(destination.is_file() and not destination.is_symlink()
                            and destination.read_bytes() == changed, "existing mutant differs")
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    temporary = destination.with_name("." + destination.name + ".tmp")
                    require(not temporary.exists(), "stale mutant temporary")
                    temporary.write_bytes(changed)
                    os.replace(temporary, destination)
            else:
                _copy_exact(donor, destination, row["binding"]["sha256"])
        readme = source["readme"]
        _copy_exact(root / readme["path"], workspace / "README.md", readme["sha256"])
        actual = {path.relative_to(workspace).as_posix() for path in workspace.rglob("*")
                  if path.is_file()}
        require(actual == expected_paths, "materialized source inventory differs")
    return source


def process_absent(directory):
    marker = directory / "process.json"
    require(marker.is_file(), "unknown child identity; reconciliation required")
    process = load(marker)
    for pid, group in ((process["pid"], True), (process["supervisor_pid"], False)):
        try:
            (os.killpg if group else os.kill)(pid, 0)
        except ProcessLookupError:
            continue
        except PermissionError as error:
            raise ValueError("cannot establish process absence") from error
        raise ValueError("process or group still present")


def finish_attempt(root, reservation):
    directory = root / reservation["directory"]
    receipt = load(directory / "supervisor.json")
    request = load(directory / "request.json")
    require(receipt["request_sha256"] == request["request_sha256"], "wrong supervisor request")
    require(request["argv"] == reservation["argv"] and request["cwd"] == reservation["cwd"]
            and request["env"] == reservation["env"]
            and request["seconds"] == reservation["reserved_seconds"], "request differs from reservation")
    require(receipt["stdout_sha256"] == sha(directory / "stdout")
            and receipt["stderr_sha256"] == sha(directory / "stderr"), "raw output drift")
    require(finite(receipt["charged_seconds"])
            and receipt["monotonic_ended"] >= receipt["monotonic_started"]
            and abs(receipt["charged_seconds"]
                    - (receipt["monotonic_ended"] - receipt["monotonic_started"])) < .1,
            "invalid process accounting")
    terminal = {
        "kind": "TERMINAL", "number": reservation["number"],
        "status": receipt["status"], "returncode": receipt["returncode"],
        "charged_seconds": receipt["charged_seconds"],
        "cleanup_completed": receipt["cleanup_completed"], "at": now(),
        "engineering_pause": bool(receipt.get("error") or not receipt["cleanup_completed"]
                                  or receipt["deadline_exceeded"]),
        "receipts": [binding(root, directory / name)
                     for name in ("request.json", "supervisor.json", "stdout", "stderr")],
    }
    if reservation["phase"] == "build":
        terminal["engineering_pause"] |= receipt["status"] != "COMPLETE"
        if receipt["status"] == "COMPLETE" and not terminal["engineering_pause"]:
            manifest = load(root / reservation["manifest"]["path"])
            source = load(root / manifest["source_materialization"]["path"])
            profile = reservation["cell"]
            output = root / source[profile]["target"] / "release/nanoda_bin"
            product = root / source[profile]["product"]
            require(output.is_file() and not output.is_symlink(), "missing selected build output")
            require(not product.exists(), "immutable build product already exists")
            product.parent.mkdir(parents=True, exist_ok=False)
            shutil.copyfile(output, product)
            product.chmod(0o555)
            require(sha(product) == sha(output), "build product changed during copy")
            terminal["binary"] = binding(root, product)
    else:
        manifest = load(root / reservation["manifest"]["path"])
        cell = manifest["matrix"][reservation["cell"]]["id"]
        terminal["classification"] = classify(
            cell, receipt, (directory / "stdout").read_bytes(), (directory / "stderr").read_bytes())
        terminal["engineering_pause"] |= terminal["classification"] not in INTERPRETABLE
        if reservation["cell"] < 2:
            terminal["engineering_pause"] = False if terminal["classification"] != "INDETERMINATE" else True
    return terminal


def _historical_file(root, commit, path):
    return subprocess.check_output(["git", "show", commit + ":" + path], cwd=root)


def verify_attempts(root, events, live=False):
    state = derive(events)
    for attempt in state["attempts"]:
        reservation = attempt["reservation"]
        bind(root, reservation["manifest"])
        require(reservation["directory"] == OUT + "/attempts/" + f"{reservation['number']:02d}",
                "wrong attempt directory")
        manifest = load(root / reservation["manifest"]["path"])
        for row in manifest["tooling_inputs"] + [manifest["focused_test_receipt"]]:
            require(hashlib.sha256(_historical_file(root, reservation["commit"], row["path"])).hexdigest()
                    == row["sha256"], "historical tooling mismatch")
        if "terminal" not in attempt:
            continue
        terminal = attempt["terminal"]
        for row in terminal["receipts"]:
            bind(root, row)
        directory = root / reservation["directory"]
        raw = load(directory / "supervisor.json")
        request = load(directory / "request.json")
        require(terminal["status"] == raw["status"]
                and terminal["returncode"] == raw["returncode"]
                and terminal["charged_seconds"] == raw["charged_seconds"]
                and terminal["cleanup_completed"] == raw["cleanup_completed"], "terminal differs from raw")
        canonical = {key: value for key, value in request.items() if key != "request_sha256"}
        require(hashlib.sha256(json.dumps(canonical, sort_keys=True).encode()).hexdigest()
                == request["request_sha256"] == raw["request_sha256"], "request checksum differs")
        require(request["argv"] == reservation["argv"] and request["cwd"] == reservation["cwd"]
                and request["env"] == reservation["env"]
                and request["seconds"] == reservation["reserved_seconds"], "request drift")
        require(sha(directory / "stdout") == raw["stdout_sha256"]
                and sha(directory / "stderr") == raw["stderr_sha256"], "raw output checksum differs")
        if terminal.get("binary") and live:
            bind(root, terminal["binary"])
        if reservation["phase"] == "checker":
            cell = manifest["matrix"][reservation["cell"]]
            require(reservation["cwd"] == str(root) and reservation["env"] == CHECKER_ENV
                    and reservation["argv"][1] == str(root / manifest["configs"][cell["input"]]["path"]),
                    "checker command drift")
            current = next(row for row in manifest["tooling_inputs"]
                           if row["path"] == "lib/survivor_thread_config_regression.py")
            if sha(root / current["path"]) == current["sha256"]:
                normalized = classify(cell["id"], raw, (directory / "stdout").read_bytes(),
                                      (directory / "stderr").read_bytes())
            else:
                namespace = {"__name__": "historical_survivor_thread_config_normalizer"}
                code = _historical_file(root, reservation["commit"], current["path"])
                exec(compile(code, "<historical normalizer>", "exec"), namespace)
                normalized = namespace["classify"](
                    cell["id"], raw, (directory / "stdout").read_bytes(),
                    (directory / "stderr").read_bytes())
            require(terminal["classification"] == normalized, "normalized outcome drift")
    return state


def _binary(state, profile, root):
    for attempt in state["attempts"]:
        reservation = attempt["reservation"]
        if (reservation["phase"] == "build" and reservation["cell"] == profile
                and attempt.get("terminal", {}).get("binary")):
            row = attempt["terminal"]["binary"]
            bind(root, row)
            return row
    raise ValueError("missing attributable " + profile + " build")


def execute(root, name=MANIFEST, repair_record=None, reconcile=False):
    root = Path(root).resolve()
    manifest = validate_manifest(root, name, launch=True)
    with lock(root / OUT / "controller.lock"):
        ledger = Ledger(root)
        if not ledger.directory.exists():
            ledger.initialize()
        events, state = ledger.read()
        verify_attempts(root, events, live=True)
        if reconcile:
            require(state["attempts"] and "terminal" not in state["attempts"][-1],
                    "no orphan to reconcile")
            reservation = state["attempts"][-1]["reservation"]
            process_absent(root / reservation["directory"])
            ledger.add(finish_attempt(root, reservation))
            return ledger.read()[1]
        if repair_record:
            path = safe(root, repair_record)
            require(path.parent == root / OUT / "repairs", "repair record outside fixed run")
            committed(root, repair_record)
            record = load(path)
            require(name != MANIFEST and record["item_id"] == ITEM
                    and record["ledger_tail"] == events[-1]["event_sha256"]
                    and record["manifest"] == binding(root, root / name)
                    and record["reason"], "unbound repair")
            require(state["attempts"] and "terminal" in state["attempts"][-1],
                    "orphan requires reconciliation")
            reservation = state["attempts"][-1]["reservation"]
            process_absent(root / reservation["directory"])
            ledger.add({"kind": "REPAIR", "after_number": reservation["number"],
                        "phase": reservation["phase"], "cell": reservation.get("cell"),
                        "record": binding(root, path), "at": now()})
            events, state = ledger.read()
        action, cell = state["next_action"]
        require(action not in {"PAUSED", "STOP"},
                "launch paused; retain evidence and use an eligible exact repair if available")
        if action == "DONE":
            return state
        seconds = 180 if action == "build" else 30
        remaining = gate(root, manifest, state["charged_seconds"], seconds)
        source = materialize(root, manifest)
        runtime = validate_runtime(root, manifest["runtime_binding"])
        if action == "build":
            environment = dict(runtime["environment_common"])
            environment["CARGO_TARGET_DIR"] = str(root / source[cell]["target"])
            argv = runtime["build_argv"]
            cwd = str(root / source[cell]["workspace"])
        else:
            matrix = manifest["matrix"][cell]
            binary = _binary(state, matrix["observer"], root)
            argv = [str(root / binary["path"]),
                    str(root / manifest["configs"][matrix["input"]]["path"])]
            cwd, environment = str(root), manifest["checker_environment"]
        number = len(state["attempts"]) + 1
        directory = root / OUT / "attempts" / f"{number:02d}"
        directory.mkdir(parents=True, exist_ok=False)
        reservation = {
            "kind": "RESERVED", "number": number, "phase": action, "cell": cell,
            "reserved_seconds": seconds,
            "active_seconds": LIMITS["active_seconds"] - remaining,
            "at": now(), "monotonic": time.monotonic(), "argv": argv,
            "cwd": cwd, "env": environment,
            "directory": directory.relative_to(root).as_posix(),
            "manifest": binding(root, root / name),
            "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root,
                                               text=True).strip(),
        }
        ledger.add(reservation)
        with signal_retry():
            run_process(argv, cwd, environment, directory, seconds,
                        deadline_monotonic=min(reservation["monotonic"] + seconds,
                                               time.monotonic() + remaining))
        ledger.add(finish_attempt(root, reservation))
        return ledger.read()[1]


def evidence(root):
    root = Path(root).resolve()
    events, state = Ledger(root).read()
    verify_attempts(root, events)
    return state


def main(validate=False):
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=MANIFEST)
    parser.add_argument("--evidence", action="store_true")
    parser.add_argument("--repair-record")
    parser.add_argument("--reconcile", action="store_true")
    arguments = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = (evidence(root) if arguments.evidence else
              validate_manifest(root, arguments.manifest) if validate else
              execute(root, arguments.manifest, arguments.repair_record, arguments.reconcile))
    print(json.dumps(result, indent=2))
    return 0
