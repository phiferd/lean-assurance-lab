"""Fail-closed process runner for frozen representation-pilot cells."""
from __future__ import annotations

import hashlib
import json
import os
import re
import signal
import subprocess
import threading
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PS = Path("/bin/ps")


class RunnerError(ValueError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _binding(value: Any, label: str) -> Path:
    if not isinstance(value, dict) or not {"path", "sha256"}.issubset(value):
        raise RunnerError(f"invalid {label} binding")
    path = ROOT / value["path"]
    if not path.is_file() or sha256(path) != value["sha256"]:
        raise RunnerError(f"stale {label} binding: {value.get('path')}")
    return path


def _group_rss_bytes(process_group: int) -> list[int]:
    completed = subprocess.run(
        [str(PS), "-axo", "pgid=,rss="], capture_output=True, text=True,
        check=True, timeout=2,
    )
    values = []
    for line in completed.stdout.splitlines():
        fields = line.split()
        if len(fields) == 2 and int(fields[0]) == process_group:
            values.append(int(fields[1]) * 1024)
    return values


def _memory_monitor(process: subprocess.Popen[bytes], memory_bytes: int,
                    stopped: threading.Event, state: dict[str, Any]) -> None:
    try:
        while process.poll() is None:
            values = _group_rss_bytes(process.pid)
            if values:
                state["samples"] += 1
                state["maximum_observed_rss_bytes"] = max(
                    state["maximum_observed_rss_bytes"], max(values)
                )
                if any(value > memory_bytes for value in values):
                    state["memory_exceeded"] = True
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    return
            if stopped.wait(0.01):
                return
    except (OSError, subprocess.SubprocessError, ValueError) as error:
        state["monitor_error"] = f"{type(error).__name__}: {error}"
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def run_supervised(*, argv: list[str], cwd: Path, stdin: bytes | None, env: dict[str, str],
                   timeout_seconds: int, memory_bytes: int, raw_prefix: Path) -> dict[str, Any]:
    if not PS.is_file(): raise RunnerError("/bin/ps is unavailable")
    raw_prefix.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    process = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
                               start_new_session=True)
    stopped = threading.Event()
    monitor_state: dict[str, Any] = {
        "samples": 0,
        "maximum_observed_rss_bytes": 0,
        "memory_exceeded": False,
        "monitor_error": None,
    }
    monitor = threading.Thread(
        target=_memory_monitor, args=(process, memory_bytes, stopped, monitor_state), daemon=True
    )
    monitor.start()
    timed_out = False
    try:
        stdout, stderr = process.communicate(stdin, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        try: os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError: pass
        stdout, stderr = process.communicate()
    finally:
        stopped.set()
        monitor.join(timeout=3)
    if monitor.is_alive():
        monitor_state["monitor_error"] = "memory monitor did not terminate"
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    elapsed = time.monotonic() - start
    raw_prefix.with_suffix(".stdout").write_bytes(stdout)
    raw_prefix.with_suffix(".stderr").write_bytes(stderr)
    cleanup = process.poll() is not None
    try:
        os.killpg(process.pid, 0)
    except ProcessLookupError:
        process_group_absent = True
    except PermissionError:
        process_group_absent = False
    else:
        process_group_absent = False
    return {
        "argv": argv,
        "cwd": str(cwd),
        "exit_code": process.returncode,
        "timed_out": timed_out,
        "elapsed_seconds": elapsed,
        "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
        "stdout_bytes": len(stdout),
        "stderr_bytes": len(stderr),
        "metrics": {"real_seconds": elapsed},
        "memory_limit_bytes": memory_bytes,
        "memory_enforcement": "per-process-rss-process-group-monitor-v1",
        "memory_exceeded": monitor_state["memory_exceeded"],
        "memory_monitor_samples": monitor_state["samples"],
        "maximum_observed_rss_bytes": monitor_state["maximum_observed_rss_bytes"],
        "memory_monitor_error": monitor_state["monitor_error"],
        "cleanup_complete": cleanup and process_group_absent,
        "raw_prefix": str(raw_prefix.relative_to(ROOT)),
    }


def classify(profile: str, receipt: dict[str, Any], stdout: bytes, stderr: bytes) -> tuple[str, str]:
    if receipt["memory_monitor_error"]:
        return "INFRASTRUCTURE_AUDIT_FAILURE", "resident-memory observation failed"
    if receipt["memory_exceeded"]:
        return "CRASH", "resident-memory ceiling exceeded and process group was killed"
    if receipt["timed_out"]: return "TIMEOUT", "process exceeded frozen timeout"
    if not receipt["cleanup_complete"]: return "INFRASTRUCTURE_AUDIT_FAILURE", "process group cleanup not proven"
    code = receipt["exit_code"]
    combined = (stdout + b"\n" + stderr).decode(errors="replace")
    if code == 0:
        if profile == "official-lean-4.33.0":
            if not re.fullmatch(r"Accepted [0-9]+ declarations[.]\n", stdout.decode(errors="replace")) or stderr:
                return "INFRASTRUCTURE_AUDIT_FAILURE", "official success output contract failed"
        return "ACCEPT", "exit 0 under bound success contract"
    if code is not None and code < 0: return "CRASH", f"terminated by signal {-code}"
    lower = combined.lower()
    parse_markers = ("json", "parse", "back-reference", "back-ref", "format version", "expected value", "eof")
    if any(marker in lower for marker in parse_markers):
        return "PARSER_IMPORT_REJECTION", "diagnostic identifies parsing/import boundary"
    if profile == "nanoda-6ae1f0c" and code == 101:
        return "CRASH", "Rust panic exit 101 without a structured refusal protocol"
    if profile == "official-lean-4.33.0" and code == 1:
        return "SEMANTIC_REJECT", "official replay exited 1 after no identified parse diagnostic"
    return "INFRASTRUCTURE_AUDIT_FAILURE", f"unclassified nonzero exit {code}"


def _load_execution(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    try: manifest = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error: raise RunnerError(f"cannot load execution manifest: {error}") from error
    if manifest.get("schema_version") != 1 or manifest.get("gate") != "PASS":
        raise RunnerError("execution manifest gate is not PASS")
    science_path = _binding(manifest.get("scientific_manifest"), "scientific_manifest")
    _binding(manifest.get("tooling_revision"), "tooling_revision")
    science = json.loads(science_path.read_text())
    if manifest.get("maximum_matrix") != science.get("maximum_observation_matrix"):
        raise RunnerError("execution maximum matrix differs from scientific freeze")
    frozen_cells = {row["cell"]: row for row in science["maximum_observation_matrix"]}
    dispositions = manifest.get("cell_dispositions")
    if (not isinstance(dispositions, list) or {row.get("cell") for row in dispositions} != set(frozen_cells)
            or len(dispositions) != len(frozen_cells)):
        raise RunnerError("execution manifest lacks one disposition per frozen cell")
    launched = manifest.get("launch_cells")
    if not isinstance(launched, list) or not launched:
        raise RunnerError("execution manifest has no launch cells")
    for cell in launched:
        if frozen_cells.get(cell.get("cell")) != cell:
            raise RunnerError("launch cell differs from frozen matrix")
        disposition = next(row for row in dispositions if row["cell"] == cell["cell"])
        if disposition.get("disposition") != "ELIGIBLE":
            raise RunnerError("launch cell is not ELIGIBLE")
    if manifest.get("timeout_seconds") != 30 or manifest.get("memory_bytes") != 2147483648:
        raise RunnerError("execution limits differ from scientific freeze")
    for binding in manifest.get("generated_artifacts", []):
        _binding({"path": binding["path"], "sha256": binding["sha256"]}, "generated artifact")
        audit = _binding(binding["audit"], "generated audit")
        report = json.loads(audit.read_text())
        if not report.get("eligible") or report["variant"]["sha256"] != binding["sha256"]:
            raise RunnerError("generated artifact lacks eligible bound audit")
    for profile in science["observer_profiles"]:
        _binding(profile["definition"], f"{profile['id']} definition")
        _binding(profile["binary"], f"{profile['id']} binary")
        for name in ("source", "toolchain", "parser_source", "main_source", "configuration"):
            if name in profile: _binding(profile[name], f"{profile['id']} {name}")
    for original in science["originals"]:
        _binding({"path": original["path"], "sha256": original["sha256"]}, f"original {original['id']}")
    return manifest, science


def execute_manifest(path: Path) -> dict[str, Any]:
    manifest, science = _load_execution(path)
    run_dir = ROOT / manifest["run_dir"]
    if run_dir.exists(): raise RunnerError("run directory already exists")
    run_dir.mkdir(parents=True)
    lock = run_dir / "launch-owner.lock"
    lock.write_text(json.dumps({"pid": os.getpid(), "owner": manifest["launch_owner"]}) + "\n")
    variants = {(row["original"], row["transformation"]): ROOT / row["path"]
                for row in manifest["generated_artifacts"]}
    originals = {row["id"]: ROOT / row["path"] for row in science["originals"]}
    profiles = {row["id"]: row for row in science["observer_profiles"]}
    results = []
    try:
        for number, cell in enumerate(manifest["launch_cells"], 1):
            if cell["representation"] == "original": input_path = originals[cell["original"]]
            else: input_path = variants[(cell["original"], cell["representation"])]
            profile = profiles[cell["profile"]]
            raw_prefix = run_dir / "raw" / f"{number:02d}-{cell['profile']}-{cell['original']}-{cell['representation']}"
            env = {key: value for key, value in os.environ.items() if not key.startswith("KIOTA_")}
            if profile["id"].startswith("official"):
                argv = [str(ROOT / profile["binary"]["path"]), str(input_path)]
                cwd, stdin = ROOT, None
            else:
                cwd = ROOT / profile["invocation"]["cwd"]
                argv = [profile["invocation"]["argv"][0], profile["invocation"]["argv"][1]]
                stdin = input_path.read_bytes()
                profile_dir = run_dir / "profiles"
                profile_dir.mkdir(exist_ok=True)
                env["LLVM_PROFILE_FILE"] = str(profile_dir / "nanoda-%p.profraw")
            receipt = run_supervised(argv=argv, cwd=cwd, stdin=stdin, env=env,
                                     timeout_seconds=manifest["timeout_seconds"], memory_bytes=manifest["memory_bytes"],
                                     raw_prefix=raw_prefix)
            stdout = raw_prefix.with_suffix(".stdout").read_bytes()
            stderr = raw_prefix.with_suffix(".stderr").read_bytes()
            outcome, reason = classify(profile["id"], receipt, stdout, stderr)
            row = {"ordinal": number, "cell": cell, "input_path": str(input_path.relative_to(ROOT)),
                   "input_sha256": sha256(input_path), "outcome": outcome, "reason": reason, "receipt": receipt}
            results.append(row)
            with (run_dir / "events.jsonl").open("a") as output:
                output.write(json.dumps(row, sort_keys=True) + "\n")
            if outcome == "INFRASTRUCTURE_AUDIT_FAILURE":
                raise RunnerError(f"cell {cell['cell']} infrastructure/audit failure: {reason}")
    finally:
        lock.unlink(missing_ok=True)
    total = sum(row["receipt"]["elapsed_seconds"] for row in results)
    result = {"schema_version": 1, "execution_manifest": str(path.relative_to(ROOT)), "cells": results,
              "checker_attempts": len(results), "process_seconds": total,
              "status": "COMPLETE" if len(results) == len(manifest["launch_cells"]) else "INCOMPLETE"}
    (run_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result
