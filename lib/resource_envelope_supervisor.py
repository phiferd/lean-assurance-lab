"""Direct-process, phase-aware resource supervisor for the resource pilot.

No selected observer is launched by importing this module. The caller owns
the immutable input manifest, raw-file custody, and launch gates.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time
from typing import Any


class SupervisionError(RuntimeError):
    pass


@dataclass(frozen=True)
class SupervisedResult:
    receipt: dict[str, Any]
    stdout: bytes
    stderr: bytes


def _rss_unit() -> tuple[str, int]:
    if sys.platform == "darwin":
        return "bytes", 1
    if sys.platform.startswith("linux"):
        return "KiB", 1024
    raise SupervisionError(f"unsupported wait4 ru_maxrss unit: {sys.platform}")


def _group_snapshot(pgid: int, ps: str, ps_timeout: float) -> list[dict[str, Any]]:
    completed = subprocess.run(
        [ps, "-A", "-o", "pid=", "-o", "pgid=", "-o", "rss=", "-o", "stat="],
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False, timeout=ps_timeout,
    )
    if completed.returncode != 0 or completed.stderr:
        raise SupervisionError("ps failed: " + completed.stderr.decode("utf-8", "replace")[:400])
    members: list[dict[str, Any]] = []
    for line in completed.stdout.decode("ascii").splitlines():
        fields = line.split()
        if len(fields) != 4:
            raise SupervisionError("malformed ps line")
        pid_text, group_text, rss_text, state = fields
        if not (pid_text.isdecimal() and group_text.isdecimal() and rss_text.isdecimal()):
            raise SupervisionError("noninteger ps field")
        if int(group_text) == pgid:
            members.append({"pid": int(pid_text), "rss_bytes": int(rss_text) * 1024,
                            "state": state})
    return sorted(members, key=lambda member: member["pid"])


def _live_members(members: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [member for member in members if not member["state"].startswith("Z")]


def _signal_group(pgid: int, sig: signal.Signals) -> str | None:
    try:
        os.killpg(pgid, sig)
    except ProcessLookupError:
        return f"{sig.name}: process group disappeared before signal delivery"
    except OSError as exc:
        return f"{sig.name}: {type(exc).__name__}: {exc}"
    return None


def _cleanup_group(pgid: int, ps: str, ps_timeout: float,
                   cleanup_seconds: float) -> tuple[bool, list[str]]:
    errors: list[str] = []
    try:
        members = _live_members(_group_snapshot(pgid, ps, ps_timeout))
    except Exception as exc:
        return False, [f"cleanup snapshot: {type(exc).__name__}: {exc}"]
    if not members:
        return True, errors
    error = _signal_group(pgid, signal.SIGTERM)
    if error:
        errors.append(error)
    deadline = time.monotonic() + cleanup_seconds / 2
    while time.monotonic() < deadline:
        try:
            members = _live_members(_group_snapshot(pgid, ps, ps_timeout))
        except Exception as exc:
            return False, errors + [f"cleanup snapshot: {type(exc).__name__}: {exc}"]
        if not members:
            return not errors, errors
        time.sleep(min(0.01, max(0.0, deadline - time.monotonic())))
    error = _signal_group(pgid, signal.SIGKILL)
    if error:
        errors.append(error)
    deadline = time.monotonic() + cleanup_seconds / 2
    while time.monotonic() < deadline:
        try:
            members = _live_members(_group_snapshot(pgid, ps, ps_timeout))
        except Exception as exc:
            return False, errors + [f"cleanup snapshot: {type(exc).__name__}: {exc}"]
        if not members:
            return not errors, errors
        time.sleep(min(0.01, max(0.0, deadline - time.monotonic())))
    return False, errors + ["process group remains live after cleanup deadline"]


def run_direct(*, argv: list[str], cwd: Path, env: dict[str, str],
               stdin_bytes: bytes | None, timeout_seconds: float,
               memory_ceiling_bytes: int, sample_interval_seconds: float,
               max_trace_gap_seconds: float, cleanup_seconds: float,
               ps: str = "/bin/ps", ps_timeout_seconds: float = 0.5,
               output_cap_bytes: int = 10_000_000) -> SupervisedResult:
    """Run exactly one direct executable with one wait4 owner and raw custody.

    `run_direct` deliberately returns faults in its receipt. Its caller must
    preserve the receipt/raw bytes and pause on any monitoring or cleanup fault.
    """
    if (not argv or not Path(argv[0]).is_file() or not Path(ps).is_file()
            or timeout_seconds <= 0 or memory_ceiling_bytes <= 0
            or sample_interval_seconds <= 0 or max_trace_gap_seconds <= 0
            or cleanup_seconds <= 0 or ps_timeout_seconds <= 0
            or output_cap_bytes <= 0):
        raise SupervisionError("invalid supervisor inputs")
    unit, factor = _rss_unit()
    started_ns = time.monotonic_ns()
    process = subprocess.Popen(
        argv, cwd=cwd, env=env, stdin=subprocess.PIPE if stdin_bytes is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True,
        close_fds=True,
    )
    launched_ns = time.monotonic_ns()
    pgid = process.pid
    done = threading.Event()
    lock = threading.Lock()
    samples: list[dict[str, Any]] = []
    monitor_errors: list[str] = []
    pipe_errors: list[str] = []
    stop_reason: list[str] = []
    signal_events: list[dict[str, Any]] = []
    raw: dict[str, bytearray] = {"stdout": bytearray(), "stderr": bytearray()}
    reaped = threading.Event()
    reap_data: dict[str, Any] = {"status": None, "usage": None,
                                 "reaped_ns": None, "error": None,
                                 "fallback_waitpid_status": None}

    def request_stop(reason: str) -> None:
        with lock:
            if stop_reason or reap_data["reaped_ns"] is not None:
                return
            stop_reason.append(reason)
        signaled_ns = time.monotonic_ns()
        error = _signal_group(pgid, signal.SIGKILL)
        with lock:
            signal_events.append({"method": "killpg", "signal": "SIGKILL",
                                  "monotonic_ns": signaled_ns, "error": error})
        if error:
            with lock:
                monitor_errors.append(error)
            try:
                os.kill(process.pid, signal.SIGKILL)
                with lock:
                    signal_events.append({"method": "kill", "signal": "SIGKILL",
                                          "monotonic_ns": time.monotonic_ns(), "error": None})
            except ProcessLookupError:
                pass
            except OSError as exc:
                with lock:
                    message = f"direct kill: {type(exc).__name__}: {exc}"
                    monitor_errors.append(message)
                    signal_events.append({"method": "kill", "signal": "SIGKILL",
                                          "monotonic_ns": time.monotonic_ns(), "error": message})

    def reap_once() -> None:
        # This thread is the sole owner of wait4/waitpid for the target pid.
        try:
            pid, status, usage = os.wait4(process.pid, 0)
            when = time.monotonic_ns()
            if pid != process.pid:
                raise SupervisionError("wait4 reaped wrong child")
            with lock:
                reap_data["status"] = status
                reap_data["usage"] = usage
                reap_data["reaped_ns"] = when
        except Exception as exc:
            with lock:
                reap_data["error"] = f"wait4: {type(exc).__name__}: {exc}"
            _signal_group(pgid, signal.SIGKILL)
            try:
                os.kill(process.pid, signal.SIGKILL)
            except (ProcessLookupError, OSError):
                pass
            try:
                _, fallback_status = os.waitpid(process.pid, 0)
                with lock:
                    reap_data["fallback_waitpid_status"] = fallback_status
            except Exception as fallback_exc:
                with lock:
                    reap_data["error"] += (f"; fallback waitpid: "
                                           f"{type(fallback_exc).__name__}: {fallback_exc}")
            with lock:
                reap_data["reaped_ns"] = time.monotonic_ns()
        finally:
            reaped.set()
            done.set()

    def monitor() -> None:
        try:
            while not done.is_set() and not reaped.is_set():
                sample_started_ns = time.monotonic_ns()
                if (sample_started_ns - started_ns) / 1e9 >= timeout_seconds:
                    if reaped.wait(0.02):
                        return
                    request_stop("OBSERVED_TIME_LIMIT")
                    return
                members = _group_snapshot(pgid, ps, ps_timeout_seconds)
                sample_ended_ns = time.monotonic_ns()
                live = _live_members(members)
                if live and not reaped.is_set():
                    if not any(member["pid"] == process.pid for member in live):
                        with lock:
                            monitor_errors.append("group snapshot lacks direct target while descendants live")
                        request_stop("MONITOR_FAULT")
                        return
                    group_rss = sum(member["rss_bytes"] for member in live)
                    with lock:
                        if reap_data["reaped_ns"] is None:
                            samples.append({"monotonic_ns": sample_ended_ns,
                                            "collection_started_monotonic_ns": sample_started_ns,
                                            "collection_ended_monotonic_ns": sample_ended_ns,
                                            "collection_seconds": (sample_ended_ns - sample_started_ns) / 1e9,
                                            "elapsed_seconds": (sample_ended_ns - started_ns) / 1e9,
                                            "group_rss_bytes": group_rss,
                                            "members": live})
                    if group_rss > memory_ceiling_bytes and not reaped.is_set():
                        request_stop("OBSERVED_MEMORY_LIMIT")
                        return
                if not reaped.is_set() and (sample_ended_ns - started_ns) / 1e9 >= timeout_seconds:
                    if reaped.wait(0.02):
                        return
                    request_stop("OBSERVED_TIME_LIMIT")
                    return
                done.wait(sample_interval_seconds)
        except Exception as exc:
            with lock:
                monitor_errors.append(f"{type(exc).__name__}: {exc}")
            request_stop("MONITOR_FAULT")

    def drain(name: str, pipe: Any) -> None:
        try:
            while True:
                chunk = pipe.read(65536)
                if not chunk:
                    break
                with lock:
                    raw[name].extend(chunk)
                    too_large = len(raw[name]) > output_cap_bytes
                if too_large:
                    request_stop("OUTPUT_CAP")
        except Exception as exc:
            with lock:
                pipe_errors.append(f"{name}: {type(exc).__name__}: {exc}")
            request_stop("PIPE_FAULT")
        finally:
            pipe.close()

    def feed_stdin() -> None:
        assert process.stdin is not None and stdin_bytes is not None
        try:
            process.stdin.write(stdin_bytes)
            process.stdin.flush()
        except BrokenPipeError:
            # A nonzero/early exit is preserved by the main receipt.
            pass
        except Exception as exc:
            with lock:
                pipe_errors.append(f"stdin: {type(exc).__name__}: {exc}")
            request_stop("PIPE_FAULT")
        finally:
            process.stdin.close()

    reaper = threading.Thread(target=reap_once, name="target-wait4-owner", daemon=True)
    threads = [threading.Thread(target=monitor, name="rss-monitor", daemon=True)]
    assert process.stdout is not None and process.stderr is not None
    threads += [threading.Thread(target=drain, args=("stdout", process.stdout), daemon=True),
                threading.Thread(target=drain, args=("stderr", process.stderr), daemon=True)]
    if stdin_bytes is not None:
        threads.append(threading.Thread(target=feed_stdin, daemon=True))
    reaper.start()
    for thread in threads:
        thread.start()
    remaining = max(0.0, timeout_seconds - (time.monotonic_ns() - started_ns) / 1e9)
    reaper.join(timeout=remaining + cleanup_seconds + 2 * ps_timeout_seconds)
    if reaper.is_alive():
        request_stop("UNBOUNDED_REAP")
        # Bounded fallback if the monitor could not terminate the target.
        _signal_group(pgid, signal.SIGKILL)
        try:
            os.kill(process.pid, signal.SIGKILL)
        except (ProcessLookupError, OSError):
            pass
        reaper.join(timeout=cleanup_seconds)
    with lock:
        status = reap_data["status"]
        usage = reap_data["usage"]
        reap_error = reap_data["error"]
        reaped_ns = reap_data["reaped_ns"]
        fallback_status = reap_data["fallback_waitpid_status"]
    if reaper.is_alive():
        reap_error = (reap_error + "; " if reap_error else "") + "wait4 owner remained live"
    if reaped_ns is None:
        reaped_ns = time.monotonic_ns()
    if status is not None:
        process.returncode = os.waitstatus_to_exitcode(status)
    elif fallback_status is not None:
        process.returncode = os.waitstatus_to_exitcode(fallback_status)
    done.set()
    cleanup_ok, cleanup_errors = _cleanup_group(pgid, ps, ps_timeout_seconds, cleanup_seconds)
    cleaned_ns = time.monotonic_ns()
    for thread in threads:
        thread.join(timeout=cleanup_seconds)
    live_threads = [thread.name for thread in threads if thread.is_alive()]
    if live_threads:
        pipe_errors.append("threads did not finish: " + ",".join(live_threads))
    drained_ns = time.monotonic_ns()
    try:
        raw_child_peak = int(usage.ru_maxrss) if usage is not None else None
        child_user_cpu = float(usage.ru_utime) if usage is not None else None
        child_system_cpu = float(usage.ru_stime) if usage is not None else None
        if raw_child_peak is None or raw_child_peak <= 0:
            raise ValueError("missing/nonpositive wait4 child high-water")
        child_peak = raw_child_peak * factor
    except (AttributeError, TypeError, ValueError, OverflowError) as exc:
        reap_error = (reap_error + "; " if reap_error else "") + f"invalid wait4 usage: {type(exc).__name__}: {exc}"
        raw_child_peak = None
        child_peak = None
        child_user_cpu = None
        child_system_cpu = None
    with lock:
        trace = list(samples)
        monitor_faults = list(monitor_errors)
        pipe_faults = list(pipe_errors)
        reason = stop_reason[0] if stop_reason else None
        signals = list(signal_events)
        stdout = bytes(raw["stdout"])
        stderr = bytes(raw["stderr"])
    late_samples = [s for s in trace if s["monotonic_ns"] > reaped_ns]
    if late_samples:
        monitor_faults.append("sample timestamp after target reap")
    trace = [s for s in trace if s["monotonic_ns"] <= reaped_ns]
    points = [started_ns] + [s["monotonic_ns"] for s in trace] + [reaped_ns]
    maximum_gap = max((right - left) / 1e9 for left, right in zip(points, points[1:]))
    # A fast zero-sample execution can be a complete observation, albeit one
    # with no sampled group RSS. A long uncovered interval is a monitor fault.
    trace_gap_fault = maximum_gap > max_trace_gap_seconds
    if trace_gap_fault:
        monitor_faults.append("trace gap exceeded bound")
    if (child_peak is not None and child_peak > memory_ceiling_bytes and reason is None):
        reason = "OBSERVED_OVER_CEILING_AFTER_EXIT"
    receipt = {
        "schema_version": 1,
        "argv": argv,
        "cwd": str(cwd),
        "pid": process.pid,
        "pgid": pgid,
        "started_monotonic_ns": started_ns,
        "launched_monotonic_ns": launched_ns,
        "reaped_monotonic_ns": reaped_ns,
        "cleaned_monotonic_ns": cleaned_ns,
        "drained_monotonic_ns": drained_ns,
        "elapsed_seconds": (reaped_ns - started_ns) / 1e9,
        "launch_seconds": (launched_ns - started_ns) / 1e9,
        "cleanup_seconds": (cleaned_ns - reaped_ns) / 1e9,
        "drain_after_reap_seconds": (drained_ns - reaped_ns) / 1e9,
        "wait_status": status,
        "exit_code": process.returncode,
        "accounting_error": reap_error,
        "reap_complete": not reaper.is_alive(),
        "fallback_waitpid_status": reap_data["fallback_waitpid_status"],
        "child_ru_maxrss_raw": raw_child_peak,
        "child_ru_maxrss_unit": unit,
        "child_peak_rss_bytes": child_peak,
        "child_user_cpu_seconds": child_user_cpu,
        "child_system_cpu_seconds": child_system_cpu,
        "samples": trace,
        "sample_count": len(trace),
        "maximum_sampled_group_rss_bytes": max((s["group_rss_bytes"] for s in trace), default=None),
        "maximum_trace_gap_seconds": maximum_gap,
        "trace_gap_fault": trace_gap_fault,
        "monitor_errors": monitor_faults,
        "pipe_errors": pipe_faults,
        "cleanup_complete": cleanup_ok,
        "cleanup_errors": cleanup_errors,
        "stop_reason": reason,
        "signal_events": signals,
        "stdout_bytes": len(stdout),
        "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
        "stderr_bytes": len(stderr),
        "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
        "stdin_bytes": None if stdin_bytes is None else len(stdin_bytes),
        "stdin_sha256": None if stdin_bytes is None else hashlib.sha256(stdin_bytes).hexdigest(),
        "limits": {"timeout_seconds": timeout_seconds,
                   "memory_ceiling_bytes": memory_ceiling_bytes,
                   "sample_interval_seconds": sample_interval_seconds,
                   "max_trace_gap_seconds": max_trace_gap_seconds,
                   "cleanup_seconds": cleanup_seconds,
                   "ps_timeout_seconds": ps_timeout_seconds,
                   "output_cap_bytes": output_cap_bytes},
    }
    return SupervisedResult(receipt, stdout, stderr)
