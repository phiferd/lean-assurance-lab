"""Portable, read-only replay of the completed resource-envelope matrix.

The recorded host paths are historical identities. Only repository-relative
evidence is opened; no checker, Lake process, or host monitoring tool runs.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from lib.resource_envelope_audit import audit_corpus
from lib.resource_envelope_observe import classify
from lib.resource_envelope_producer import canonical_json
from lib.resource_envelope_replay import REL, ReplayError, _bound, _load, replay


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ReplayError(message)


def _schedule() -> list[dict]:
    slots = []
    for profile in ("official", "nanoda"):
        for phase in ("before", "after"):
            if phase == "after":
                for family in ("pi", "let"):
                    for size in (16, 32, 64, 128, 256, 512):
                        slots.append({"kind": "science", "profile": profile,
                                      "family": family, "size": size,
                                      "id": f"{profile}-rep1-{family}-{size:03d}"})
            for repeat in (1, 2, 3):
                slots.append({"kind": "baseline", "profile": profile,
                              "phase": phase, "repeat": repeat,
                              "id": f"{profile}-{phase}-{repeat:02d}"})
    return slots


def replay_result(root: Path) -> dict:
    root = root.resolve()
    base = root / REL
    result_path = base / "science-run-0001/science-result.json"
    result = _load(result_path)
    _require(set(result) == {"baseline_input", "baselines", "cells", "completed_at",
                             "corpus_lock", "events", "execution_manifest", "history",
                             "independent_prelaunch_review", "item_id", "ledger",
                             "schema_version", "scientific_manifest", "segment_start_index",
                             "smoke_result", "status"}, "result schema differs")
    _require(result["item_id"] == "RESOURCE-ENVELOPE-PILOT-1"
             and result["schema_version"] == 1
             and result["status"] == "COMPLETE_FIXED_MATRIX"
             and result["history"] == [] and result["segment_start_index"] == 0,
             "result identity or history differs")
    science_path = _bound(root, result["scientific_manifest"])
    execution_path = _bound(root, result["execution_manifest"])
    lock_path = _bound(root, result["corpus_lock"])
    smoke_path = _bound(root, result["smoke_result"])
    launch_review_path = _bound(root, result["independent_prelaunch_review"])
    _require(science_path == base / "scientific-manifest.json"
             and execution_path == base / "execution-manifest-r2.json"
             and lock_path == base / "corpus-lock.json"
             and smoke_path == base / "smoke-result.json"
             and launch_review_path == base / "independent-prelaunch-review.json",
             "result points outside exact frozen inputs")
    execution, lock, smoke, launch_review = map(_load,
        (execution_path, lock_path, smoke_path, launch_review_path))
    _require(lock.get("status") == "SEALED_AFTER_INDEPENDENT_AUDIT"
             and lock.get("scientific_manifest") == result["scientific_manifest"]
             and lock.get("execution_manifest") == result["execution_manifest"],
             "corpus lock manifest differs")
    _require(lock.get("audit") == audit_corpus(base / "corpus"),
             "independent corpus audit differs")
    actual_corpus = {path.relative_to(root).as_posix()
                     for path in (base / "corpus").rglob("*") if path.is_file()}
    locked = lock.get("files")
    _require(type(locked) is list and len(locked) == len(actual_corpus)
             and {row["path"] for row in locked} == actual_corpus,
             "corpus file inventory differs")
    for row in locked:
        _bound(root, row)
    for key in ("construction_result", "independent_corpus_review"):
        _bound(root, lock[key])
    _require(smoke.get("status") == "SMOKE_EXACT_ACCEPTANCE_BOTH_PROFILES"
             and [row.get("profile") for row in smoke.get("profiles", [])]
                 == ["official", "nanoda"]
             and all(row.get("disposition", {}).get("status") == "ACCEPTED"
                     for row in smoke["profiles"]), "smoke result differs")
    smoke_review = _load(base / "independent-smoke-result-review.json")
    _require(smoke_review.get("verdict") == "PASS_EXACT_SMOKE_RESULTS"
             and smoke_review.get("smoke_result_sha256") == result["smoke_result"]["sha256"],
             "smoke review differs")
    _require(launch_review.get("verdict") == "PASS_FOR_SCIENTIFIC_LAUNCH"
             and launch_review.get("scientific_manifest_sha256") == result["scientific_manifest"]["sha256"]
             and launch_review.get("execution_manifest_sha256") == result["execution_manifest"]["sha256"]
             and launch_review.get("corpus_lock_sha256") == result["corpus_lock"]["sha256"]
             and launch_review.get("smoke_result_sha256") == result["smoke_result"]["sha256"],
             "scientific launch review differs")
    baseline = _bound(root, result["baseline_input"])
    _require(baseline == base / "baseline-empty.ndjson"
             and {k: result["baseline_input"][k] for k in ("bytes", "sha256")}
                 == execution["empty_export"], "empty baseline differs")
    ledger_path = _bound(root, result["ledger"])
    _require(ledger_path == base / "science-run-0001/ledger.ndjson",
             "matrix ledger path differs")
    ledger = ledger_path.read_bytes()
    _require(b"".join(canonical_json(row) for row in result["events"]) == ledger,
             "append-only ledger differs from result events")
    schedule = _schedule()
    events = result["events"]
    _require(type(events) is list and len(events) == 36
             and [event.get("slot") for event in events] == schedule,
             "fixed slot schedule differs")
    _require(result["baselines"] == [event["row"] for event in events
                                      if event["slot"]["kind"] == "baseline"]
             and result["cells"] == [event["row"] for event in events
                                  if event["slot"]["kind"] == "science"],
             "baseline/cell projection differs")
    # Recover the original root from the frozen Nanoda config argument without
    # opening it there. This compares recorded command strings on any checkout.
    suffix = "/results/research/resource-envelope-pilot-1/nanoda-single-check.json"
    config_arg = execution["invocations"]["nanoda"][1]
    _require(config_arg.endswith(suffix), "recorded Nanoda config identity differs")
    historical_root = config_arg[:-len(suffix)]
    limits = execution["limits"]
    expected_limits = {**limits["checker"], **{name: limits[name] for name in (
        "sample_interval_seconds", "max_trace_gap_seconds", "cleanup_seconds",
        "ps_timeout_seconds", "output_cap_bytes")}}
    seen: set[str] = set()
    previous_end = None
    samples = Counter()
    outcomes = Counter()
    for event in events:
        slot, row = event["slot"], event["row"]
        profile, sid = slot["profile"], slot["id"]
        _require(row.get("status") == "ACCEPTED" and set(row) == (
            {"baseline_id", "phase", "status", "profile", "input", "process",
             "disposition", "started_monotonic_ns"} if slot["kind"] == "baseline" else
            {"cell_id", "profile", "family", "size", "status", "input", "process",
             "disposition", "started_monotonic_ns"}), f"{sid}: row schema/status differs")
        if slot["kind"] == "baseline":
            expected_input = result["baseline_input"]
            _require(row["baseline_id"] == sid and row["phase"] == slot["phase"],
                     f"{sid}: baseline identity differs")
            expected_stdout = (b"Accepted 0 declarations.\n" if profile == "official"
                               else b"Checked 0 declarations with no errors\n")
        else:
            expected_input = next((item for item in locked if item["path"] ==
                f"{REL.as_posix()}/corpus/exports/rep1-{slot['family']}-{slot['size']:03d}.ndjson"), None)
            _require(expected_input is not None and row["cell_id"] == sid
                     and row["family"] == slot["family"] and row["size"] == slot["size"],
                     f"{sid}: scientific identity differs")
            expected_stdout = (b"Accepted 1 declarations.\n" if profile == "official"
                               else b"Checked 1 declarations with no errors\n")
        _require(row["profile"] == profile and row["input"] == expected_input,
                 f"{sid}: input binding differs")
        process = row["process"]
        _require(set(process) == {"receipt", "stdout", "stderr"},
                 f"{sid}: process schema differs")
        for kind in ("receipt", "stdout", "stderr"):
            _require(process[kind]["path"] ==
                     f"{REL.as_posix()}/science-run-0001/processes/{sid}."
                     + ("receipt.json" if kind == "receipt" else kind),
                     f"{sid}: process path differs")
            _bound(root, process[kind])
        receipt_path = process["receipt"]["path"]
        _require(receipt_path not in seen, "process receipt reused")
        seen.add(receipt_path)
        receipt = _load(root / receipt_path)
        stdout = (root / process["stdout"]["path"]).read_bytes()
        stderr = (root / process["stderr"]["path"]).read_bytes()
        expected_argv = [arg.replace("{export_path}",
                         historical_root + "/" + expected_input["path"])
                         for arg in execution["invocations"][profile]]
        _require(receipt.get("argv") == expected_argv
                 and receipt.get("cwd") == historical_root
                 and receipt.get("limits") == expected_limits
                 and receipt.get("started_monotonic_ns") == row["started_monotonic_ns"]
                 and receipt.get("raw_stdout_path") == process["stdout"]["path"]
                 and receipt.get("raw_stderr_path") == process["stderr"]["path"],
                 f"{sid}: historical process identity differs")
        if profile == "nanoda":
            _require(receipt.get("stdin_bytes") == expected_input["bytes"]
                     and receipt.get("stdin_sha256") == expected_input["sha256"],
                     f"{sid}: Nanoda stdin differs")
        else:
            _require(receipt.get("stdin_bytes") is None
                     and receipt.get("stdin_sha256") is None,
                     f"{sid}: official stdin differs")
        disposition = classify(receipt, stdout, stderr,
                               expected_stdout=expected_stdout,
                               baseline=slot["kind"] == "baseline")
        _require(disposition == row["disposition"] and disposition["status"] == "ACCEPTED",
                 f"{sid}: raw disposition differs")
        start = receipt["started_monotonic_ns"]
        end = max(receipt["drained_monotonic_ns"], receipt["cleaned_monotonic_ns"])
        _require(previous_end is None or start >= previous_end,
                 f"{sid}: overlapping process order")
        previous_end = end
        samples[profile] += receipt["sample_count"] > 0
        outcomes[(profile, slot["kind"])] += 1
    custody = replay(root)
    _require(custody["process_receipts"] == 73 and custody["raw_streams"] == 146
             and custody["preserved_accounting_faults"] == 0,
             "complete preserved process inventory differs")
    _require(dict(outcomes) == {("official", "baseline"): 6,
                                ("official", "science"): 12,
                                ("nanoda", "baseline"): 6,
                                ("nanoda", "science"): 12}
             and samples == {"official": 18, "nanoda": 0},
             "matrix count or sampling coverage differs")
    return {"status": "PASS", "science_cells": 24, "baselines": 12,
            "accepted": 36, "official_sampled_runs": 18,
            "nanoda_sampled_runs": 0, "process_receipts": custody["process_receipts"],
            "host_launches": 0}
