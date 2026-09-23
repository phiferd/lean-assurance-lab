"""Prospective supervisor requiring positive RSS before releasing the child.

The original module remains byte-identical for previously bound experiments.
This successor reuses its monitor, backend preflight, classification and raw-path
logic. Only the start-gate condition changes: a visible process with zero RSS is
not evidence of positive resident-memory observation.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time
from typing import Any

from lib.metamorphic_pilot_runner import (
    PS, ROOT, START_GATE_PROGRAM, RunnerError, _memory_monitor, _raw_path,
    _verify_memory_monitor_backend, classify,
)


def _positive_rss_observed(state: dict[str, Any]) -> bool:
    return state["samples"] > 0 and state["maximum_observed_rss_bytes"] > 0


def run_supervised(*, argv: list[str], cwd: Path, stdin: bytes | None, env: dict[str, str],
                   timeout_seconds: int, memory_bytes: int, raw_prefix: Path) -> dict[str, Any]:
    if not PS.is_file(): raise RunnerError("/bin/ps is unavailable")
    backend = _verify_memory_monitor_backend()
    raw_prefix.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    gate_read, gate_write = os.pipe()
    try:
        process = subprocess.Popen(
            [sys.executable, "-c", START_GATE_PROGRAM, str(gate_read), *argv],
            cwd=cwd, stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
            start_new_session=True, pass_fds=(gate_read,),
        )
    except BaseException:
        os.close(gate_read)
        os.close(gate_write)
        raise
    os.close(gate_read)
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
    sample_deadline = min(start + timeout_seconds, time.monotonic() + 2)
    while (not _positive_rss_observed(monitor_state) and monitor_state["monitor_error"] is None
           and process.poll() is None and time.monotonic() < sample_deadline):
        time.sleep(0.001)
    if not _positive_rss_observed(monitor_state) and monitor_state["monitor_error"] is None:
        monitor_state["monitor_error"] = "no positive child process-group RSS sample before start-gate deadline"
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        if _positive_rss_observed(monitor_state) and monitor_state["monitor_error"] is None:
            os.write(gate_write, b"1")
    except BrokenPipeError:
        if monitor_state["monitor_error"] is None:
            monitor_state["monitor_error"] = "child start gate closed before release"
    finally:
        os.close(gate_write)
    timed_out = False
    try:
        remaining = max(0.001, timeout_seconds - (time.monotonic() - start))
        stdout, stderr = process.communicate(stdin, timeout=remaining)
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
    stdout_path = _raw_path(raw_prefix, ".stdout")
    stderr_path = _raw_path(raw_prefix, ".stderr")
    stdout_path.write_bytes(stdout)
    stderr_path.write_bytes(stderr)
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
        "memory_enforcement": "per-process-rss-process-group-monitor-v2",
        "memory_backend": backend,
        "memory_exceeded": monitor_state["memory_exceeded"],
        "memory_monitor_samples": monitor_state["samples"],
        "maximum_observed_rss_bytes": monitor_state["maximum_observed_rss_bytes"],
        "memory_monitor_error": monitor_state["monitor_error"],
        "cleanup_complete": cleanup and process_group_absent,
        "raw_prefix": str(raw_prefix.relative_to(ROOT)),
        "raw_stdout_path": str(stdout_path.relative_to(ROOT)),
        "raw_stderr_path": str(stderr_path.relative_to(ROOT)),
    }

