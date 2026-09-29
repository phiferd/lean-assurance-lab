"""Strict raw-process reconciliation for resource baseline and science cells."""

from __future__ import annotations

import hashlib
import math
import os
import signal
from typing import Any


class ObservationError(ValueError):
    pass


def _finite(value: Any, label: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ObservationError(f"{label} must be finite numeric")
    return float(value)


def _integer(value: Any, label: str) -> int:
    if type(value) is not int:
        raise ObservationError(f"{label} must be integer")
    return value


def _raw_matches(receipt: dict[str, Any], stdout: bytes, stderr: bytes) -> None:
    for name, raw in (("stdout", stdout), ("stderr", stderr)):
        if receipt.get(f"{name}_bytes") != len(raw) or receipt.get(f"{name}_sha256") != hashlib.sha256(raw).hexdigest():
            raise ObservationError(f"{name} raw custody differs")


def _validate_accounting(receipt: dict[str, Any], stdout: bytes, stderr: bytes) -> None:
    _raw_matches(receipt, stdout, stderr)
    start = _integer(receipt.get("started_monotonic_ns"), "start")
    launch = _integer(receipt.get("launched_monotonic_ns"), "launch")
    reap = _integer(receipt.get("reaped_monotonic_ns"), "reap")
    clean = _integer(receipt.get("cleaned_monotonic_ns"), "clean")
    drain = _integer(receipt.get("drained_monotonic_ns"), "drain")
    if not start <= launch <= reap <= clean <= drain:
        raise ObservationError("process phase order differs")
    if abs(_finite(receipt.get("elapsed_seconds"), "elapsed") - (reap - start) / 1e9) > 1e-8:
        raise ObservationError("elapsed seconds differ from phase clock")
    unit = receipt.get("child_ru_maxrss_unit")
    if unit not in ("bytes", "KiB"):
        raise ObservationError("unknown child high-water unit")
    raw_peak = _integer(receipt.get("child_ru_maxrss_raw"), "child peak raw")
    peak = _integer(receipt.get("child_peak_rss_bytes"), "child peak bytes")
    if raw_peak <= 0 or peak != raw_peak * (1 if unit == "bytes" else 1024):
        raise ObservationError("child wait4 high-water conversion differs")
    wait_status = _integer(receipt.get("wait_status"), "wait status")
    try:
        decoded_exit = os.waitstatus_to_exitcode(wait_status)
    except ValueError as exc:
        raise ObservationError("invalid wait status") from exc
    if receipt.get("exit_code") != decoded_exit:
        raise ObservationError("wait status and exit code differ")
    limits = receipt.get("limits")
    if type(limits) is not dict:
        raise ObservationError("missing bound process limits")
    ceiling = _integer(limits.get("memory_ceiling_bytes"), "memory ceiling")
    timeout = _finite(limits.get("timeout_seconds"), "timeout")
    max_gap_bound = _finite(limits.get("max_trace_gap_seconds"), "trace gap bound")
    if ceiling <= 0 or timeout <= 0 or max_gap_bound <= 0:
        raise ObservationError("invalid limits")
    samples = receipt.get("samples")
    if type(samples) is not list or receipt.get("sample_count") != len(samples):
        raise ObservationError("sample count differs")
    points = [start]
    maximum = None
    for sample in samples:
        if type(sample) is not dict:
            raise ObservationError("malformed RSS sample")
        begun = _integer(sample.get("collection_started_monotonic_ns"), "sample start")
        ended = _integer(sample.get("collection_ended_monotonic_ns"), "sample end")
        timestamp = _integer(sample.get("monotonic_ns"), "sample timestamp")
        if not start <= begun <= ended == timestamp <= reap or timestamp < points[-1]:
            raise ObservationError("RSS sample time lies outside child lifetime")
        if abs(_finite(sample.get("collection_seconds"), "collection") - (ended - begun) / 1e9) > 1e-8:
            raise ObservationError("sample collection duration differs")
        members = sample.get("members")
        if type(members) is not list or not members:
            raise ObservationError("RSS sample lacks group members")
        seen: set[int] = set()
        group_sum = 0
        for member in members:
            if type(member) is not dict:
                raise ObservationError("malformed RSS group member")
            pid = _integer(member.get("pid"), "member pid")
            rss = _integer(member.get("rss_bytes"), "member RSS")
            if pid <= 0 or rss < 0 or pid in seen or not isinstance(member.get("state"), str):
                raise ObservationError("RSS group member identity differs")
            seen.add(pid)
            group_sum += rss
        if _integer(receipt.get("pid"), "target pid") not in seen:
            raise ObservationError("RSS sample lacks direct target")
        if sample.get("group_rss_bytes") != group_sum:
            raise ObservationError("sampled group RSS sum differs")
        maximum = group_sum if maximum is None else max(maximum, group_sum)
        points.append(timestamp)
    points.append(reap)
    gap = max((right - left) / 1e9 for left, right in zip(points, points[1:]))
    if abs(_finite(receipt.get("maximum_trace_gap_seconds"), "trace gap") - gap) > 1e-8:
        raise ObservationError("trace gap differs from endpoints")
    if receipt.get("trace_gap_fault") != (gap > max_gap_bound):
        raise ObservationError("trace-gap flag differs")
    if receipt.get("maximum_sampled_group_rss_bytes") != maximum:
        raise ObservationError("sampled group peak differs")


def classify(receipt: dict[str, Any], stdout: bytes, stderr: bytes,
             *, expected_stdout: bytes, baseline: bool) -> dict[str, Any]:
    """Return a disposition. Faults always precede any resource-limit label."""
    try:
        _validate_accounting(receipt, stdout, stderr)
    except ObservationError as error:
        return {"status": "REPAIR_PAUSE", "reason": f"accounting: {error}"}
    if (receipt.get("accounting_error") or not receipt.get("reap_complete")
            or receipt.get("monitor_errors") or receipt.get("pipe_errors")
            or receipt.get("cleanup_errors") or not receipt.get("cleanup_complete")
            or receipt.get("trace_gap_fault")):
        return {"status": "REPAIR_PAUSE", "reason": "monitor/accounting/pipe/cleanup control fault"}
    reason = receipt.get("stop_reason")
    exit_code = receipt.get("exit_code")
    ceiling = receipt["limits"]["memory_ceiling_bytes"]
    if reason in ("OBSERVED_TIME_LIMIT", "OBSERVED_MEMORY_LIMIT"):
        signals = receipt.get("signal_events")
        valid_signals = ([] if type(signals) is not list else [event for event in signals if
            type(event) is dict and event.get("method") in ("killpg", "kill")
            and event.get("signal") == "SIGKILL" and event.get("error") is None
            and type(event.get("monotonic_ns")) is int
            and receipt["started_monotonic_ns"] <= event["monotonic_ns"] <= receipt["reaped_monotonic_ns"]])
        if exit_code != -signal.SIGKILL or not valid_signals:
            return {"status": "REPAIR_PAUSE", "reason": "limit signal/exit attribution differs"}
        if reason == "OBSERVED_MEMORY_LIMIT" and (
                receipt["maximum_sampled_group_rss_bytes"] is None
                or receipt["maximum_sampled_group_rss_bytes"] <= ceiling):
            return {"status": "REPAIR_PAUSE", "reason": "memory limit lacks above-ceiling sample"}
        if reason == "OBSERVED_MEMORY_LIMIT" and not any(
                event["monotonic_ns"] >= sample["monotonic_ns"]
                for event in valid_signals for sample in receipt["samples"]
                if sample["group_rss_bytes"] > ceiling):
            return {"status": "REPAIR_PAUSE", "reason": "memory signal preceded above-ceiling sample"}
        if reason == "OBSERVED_TIME_LIMIT" and receipt["elapsed_seconds"] < receipt["limits"]["timeout_seconds"]:
            return {"status": "REPAIR_PAUSE", "reason": "timeout elapsed below threshold"}
        if reason == "OBSERVED_TIME_LIMIT" and not any(
                event["monotonic_ns"] - receipt["started_monotonic_ns"]
                >= receipt["limits"]["timeout_seconds"] * 1e9
                for event in valid_signals):
            return {"status": "REPAIR_PAUSE", "reason": "timeout signal preceded threshold"}
        if baseline:
            return {"status": "REPAIR_PAUSE", "reason": "baseline reached process limit"}
        return {"status": reason, "reason": "valid supervised limit evidence"}
    if reason == "OBSERVED_OVER_CEILING_AFTER_EXIT":
        if exit_code != 0 or receipt["child_peak_rss_bytes"] <= ceiling:
            return {"status": "REPAIR_PAUSE", "reason": "post-exit peak attribution differs"}
        if stdout != expected_stdout or stderr:
            return {"status": "REPAIR_PAUSE", "reason": "checker output differs despite post-exit high-water"}
        if baseline:
            return {"status": "REPAIR_PAUSE", "reason": "baseline child peak exceeded ceiling"}
        return {"status": reason, "reason": "OS child high-water above ceiling after normal exit"}
    if reason is not None:
        return {"status": "REPAIR_PAUSE", "reason": f"unclassified stop: {reason}"}
    if exit_code != 0:
        return {"status": "REPAIR_PAUSE", "reason": f"checker nonzero exit {exit_code}; diagnose"}
    if stdout != expected_stdout or stderr:
        return {"status": "REPAIR_PAUSE", "reason": "checker success output differs; diagnose"}
    return {"status": "ACCEPTED", "reason": "exact successful checker completion"}
