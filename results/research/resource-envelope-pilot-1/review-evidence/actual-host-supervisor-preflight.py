#!/usr/bin/env python3
"""Synthetic actual-host direct-process RSS preflight; invokes no checker."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from lib.resource_envelope_control import BASE, TOOLCHAIN  # noqa: E402
from lib.resource_envelope_observe import classify  # noqa: E402
from lib.resource_envelope_supervisor import run_direct  # noqa: E402


def write_new(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)


def main() -> int:
    for number in range(1, 10000):
        attempt = BASE / f"preflight-run-{number:04d}"
        try:
            attempt.mkdir(parents=True, exist_ok=False)
            break
        except FileExistsError:
            continue
    else:
        raise RuntimeError("preflight attempt namespace exhausted")
    argv = ["/bin/sh", "-c", "sleep 0.2; printf preflight-ok"]
    env = {"PATH": str(TOOLCHAIN) + ":/usr/bin:/bin:/usr/sbin:/sbin",
           "HOME": os.environ.get("HOME", ""), "LC_ALL": "C", "LANG": "C"}
    attempted = {"schema_version": 1, "item_id": "RESOURCE-ENVELOPE-PILOT-1",
                 "phase": "synthetic_actual_host_direct_supervisor_preflight",
                 "argv": argv, "cwd": str(ROOT), "environment": env,
                 "selected_terms": 0, "checker_invocations": 0,
                 "limits": {"timeout_seconds": 2, "memory_ceiling_bytes": 100_000_000,
                            "sample_interval_seconds": 0.01,
                            "max_trace_gap_seconds": 1.0, "cleanup_seconds": 2.0,
                            "ps_timeout_seconds": 0.5, "output_cap_bytes": 10_000_000}}
    write_new(attempt / "attempt.json",
              (json.dumps(attempted, sort_keys=True, indent=2) + "\n").encode())
    try:
        result = run_direct(argv=argv, cwd=ROOT, env=env, stdin_bytes=None,
                            **attempted["limits"])
        write_new(attempt / "stdout.raw", result.stdout)
        write_new(attempt / "stderr.raw", result.stderr)
        write_new(attempt / "process-receipt.json",
                  (json.dumps(result.receipt, sort_keys=True, indent=2) + "\n").encode())
        disposition = classify(result.receipt, result.stdout, result.stderr,
                               expected_stdout=b"preflight-ok", baseline=False)
        positive = (disposition["status"] == "ACCEPTED"
                    and result.receipt["sample_count"] > 0
                    and result.receipt["maximum_sampled_group_rss_bytes"] is not None
                    and result.receipt["maximum_sampled_group_rss_bytes"] > 0
                    and result.receipt["child_peak_rss_bytes"] is not None
                    and result.receipt["child_peak_rss_bytes"] > 0)
        summary = {"schema_version": 1, "item_id": "RESOURCE-ENVELOPE-PILOT-1",
                   "status": "PASS_POSITIVE_ACTUAL_HOST_RSS_AND_CLEANUP" if positive else "FAIL_REPAIR_PAUSE",
                   "disposition": disposition,
                   "process_receipt_sha256": hashlib.sha256((attempt / "process-receipt.json").read_bytes()).hexdigest(),
                   "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(),
                   "stderr_sha256": hashlib.sha256(result.stderr).hexdigest(),
                   "sample_count": result.receipt["sample_count"],
                   "child_peak_rss_bytes": result.receipt["child_peak_rss_bytes"],
                   "maximum_sampled_group_rss_bytes": result.receipt["maximum_sampled_group_rss_bytes"],
                   "cleanup_complete": result.receipt["cleanup_complete"]}
        write_new(attempt / "summary.json", (json.dumps(summary, sort_keys=True, indent=2) + "\n").encode())
        print(json.dumps({"attempt": str(attempt.relative_to(ROOT)), **summary}, sort_keys=True))
        return 0 if positive else 2
    except Exception as exc:
        failure = {"schema_version": 1, "status": "FAIL_REPAIR_PAUSE",
                   "phase": "synthetic_actual_host_direct_supervisor_preflight",
                   "error_type": type(exc).__name__, "error": str(exc)}
        write_new(attempt / "failure.json", (json.dumps(failure, sort_keys=True, indent=2) + "\n").encode())
        raise


if __name__ == "__main__":
    raise SystemExit(main())
