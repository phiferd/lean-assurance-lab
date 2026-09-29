"""Portable, read-only replay of the completed resource-envelope matrix.

The recorded host paths are historical identities. Only repository-relative
evidence is opened; no checker, Lake process, or host monitoring tool runs.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path

from lib.resource_envelope_audit import audit_corpus
from lib.resource_envelope_observe import classify
from lib.resource_envelope_producer import canonical_json
from lib.resource_envelope_replay import REL, ReplayError, _bound, _load, replay

RESULT_SHA256 = "9219251d4fa01523775da79e8aff177f32557b2e52828586c7dc15b42e4f1470"
REVIEWS = {
    "independent-preflight-review.json": (
        "PASS_POSITIVE_ACTUAL_HOST_PREFLIGHT",
        "242e9c7d1d1dafdd16e0ccb95b0cd05b62036c8b3cc26dacfa2de42c117d5c7e"),
    "independent-construction-failure-review-r1.json": (
        "REPAIR_REQUIRED_WITH_SCIENTIFIC_INPUTS_UNCHANGED",
        "8d3a55c90a68f5fb9f8beb1a10bb00f82ecb9651692ae65ba07a2a7a9d1d735b"),
    "independent-construction-failure-review-r2.json": (
        "PASS_FOR_SAME_MANIFEST_HOST_RETRY",
        "fd301ea969e801f030ea7b50cd3ad52e4cf9012d074fd51fb53ca9a44a165199"),
    "independent-preconstruction-review-r2.json": (
        "PASS_FOR_CONSTRUCTION",
        "fed75d07774b7fac61edc21f00527316e889758bf33cdf9b2cf2f8357411eb8e"),
    "independent-corpus-review.json": (
        "PASS_FOR_CORPUS_SEALING",
        "9e4b62adc3463b9d13460d9a8ebbb0d44f50ef1be5e081cc55f84700e719471f"),
    "independent-smoke-launch-review.json": (
        "PASS_FOR_SMOKE_LAUNCH",
        "4a222daf12fc1cd6551f692ab240bc0e64c17cf60ee732a52e8f6f417c721cfa"),
    "independent-smoke-result-review.json": (
        "PASS_EXACT_SMOKE_RESULTS",
        "c70b97c4435a203851c6df29a5a4bb5dd8f857c2be35cd131e5fa5e5e6a1efc1"),
    "independent-prelaunch-review.json": (
        "PASS_FOR_SCIENTIFIC_LAUNCH",
        "41559f3979ee2ec5967d550635b0fb0957a0b0311456d66d729241b5f5655203"),
    "independent-scientific-result-review.json": (
        "PASS_COMPLETE_FIXED_MATRIX",
        "f9ab6eb8054f0f16c90dae9f51759bdaeb369217a364fecfed3d1e051e4245b3"),
}


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


def _replay_reviews(root: Path, base: Path) -> None:
    """The independent reviews anchor every retained attempt's raw bindings."""
    for name, (verdict, digest) in REVIEWS.items():
        path = base / name
        _require(sha256(path.read_bytes()).hexdigest() == digest,
                 f"{name}: committed independent review differs")
        review = _load(path)
        rows = review.get("reviewed_inputs")
        _require(review.get("verdict") == verdict and type(rows) is list and rows,
                 f"{name}: review verdict or input inventory differs")
        for row in rows:
            _bound(root, row)


def _replay_construction(root: Path, base: Path, lock: dict) -> None:
    path = _bound(root, lock["construction_result"])
    _require(path == base / "construction-run-0003/construction-result.json",
             "successful construction path differs")
    result = _load(path)
    cases = result.get("cases")
    _require(result.get("status") == "CONSTRUCTED_AND_INDEPENDENTLY_AUDITED"
             and result.get("independent_audit") == lock["audit"]
             and type(cases) is list and len(cases) == 12,
             "successful construction audit differs")
    _require(_bound(root, result["canonical_index"]) == base / "corpus/index.json",
             "construction index binding differs")
    expected_ids = [f"rep1-{family}-{size:03d}"
                    for family in ("pi", "let")
                    for size in (16, 32, 64, 128, 256, 512)]
    _require([row.get("id") for row in cases] == expected_ids,
             "constructed case order differs")
    for row in cases:
        cid = row["id"]
        for kind, folder, suffix in (("source", "sources", "lean"),
                                     ("export", "exports", "ndjson"),
                                     ("case", "cases", "json")):
            staged = _bound(root, row[kind])
            canonical = base / f"corpus/{folder}/{cid}.{suffix}"
            _require(staged == base / f"construction-run-0003/staged/corpus/{folder}/{cid}.{suffix}"
                     and staged.read_bytes() == canonical.read_bytes(),
                     f"{cid}: staged/canonical {kind} differs")
        setup = _bound(root, row["build_setup"])
        _require(setup == base / f"construction-run-0003/workspaces/{cid}/"
                 ".lake/build/ir/ResourceEnvelopePilot1.setup.json"
                 and _load(setup).get("options") == {"maxRecDepth": 8192},
                 f"{cid}: construction option transport differs")
        for phase in ("build", "export"):
            process = row[f"{phase}_process"]
            _require(set(process) == {"receipt", "stdout", "stderr"},
                     f"{cid} {phase}: process schema differs")
            for kind in ("receipt", "stdout", "stderr"):
                _require(process[kind]["path"] ==
                         f"{REL.as_posix()}/construction-run-0003/processes/{cid}-{phase}."
                         + ("receipt.json" if kind == "receipt" else kind),
                         f"{cid} {phase}: process path differs")
                _bound(root, process[kind])
            receipt = _load(root / process["receipt"]["path"])
            _require(receipt.get("exit_code") == 0 and receipt.get("stop_reason") is None
                     and receipt.get("reap_complete") is True
                     and receipt.get("cleanup_complete") is True
                     and receipt.get("monitor_errors") == []
                     and receipt.get("pipe_errors") == []
                     and receipt.get("accounting_error") is None,
                     f"{cid} {phase}: construction process control differs")
            if phase == "export":
                _require((root / process["stdout"]["path"]).read_bytes()
                         == (root / row["export"]["path"]).read_bytes(),
                         f"{cid}: export raw differs from selected input")


def _replay_smoke(root: Path, base: Path, smoke: dict, execution: dict,
                  historical_root: str, limits: dict,
                  science_ref: dict, execution_ref: dict) -> None:
    manifest_path = _bound(root, smoke["smoke_manifest"])
    attempt_path = _bound(root, smoke["attempt_result"])
    _require(manifest_path == base / "smoke-manifest.json"
             and attempt_path == base / "smoke-run-0001/smoke-result.json"
             and _load(attempt_path) == {key: value for key, value in smoke.items()
                                         if key != "attempt_result"},
             "smoke manifest or attempt result differs")
    manifest = _load(manifest_path)
    _require(manifest.get("status") == "FROZEN_BEFORE_SMOKE_LAUNCH"
             and manifest.get("scientific_manifest") == science_ref
             and manifest.get("execution_manifest") == execution_ref,
             "smoke manifest binding differs")
    _require(manifest.get("fixture_contract") == execution["smoke_fixture_contract"]
             and [row.get("id") for row in manifest.get("profiles", [])]
                 == ["official", "nanoda"]
             and manifest.get("excluded_from_scientific_cells") is True
             and manifest.get("excluded_from_baseline_runs") is True,
             "smoke profile contract differs")
    _bound(root, manifest["input"])
    _require([row.get("profile") for row in smoke["profiles"]]
             == ["official", "nanoda"], "smoke profile order differs")
    ledger = (base / "smoke-run-0001/ledger.ndjson").read_bytes()
    _require(ledger == b"".join(canonical_json(row) for row in smoke["profiles"]),
             "smoke ledger differs")
    previous_end = None
    for row in smoke["profiles"]:
        profile = row["profile"]
        _require(row.get("input") == manifest["input"]
                 and row.get("disposition", {}).get("status") == "ACCEPTED",
                 f"smoke {profile}: input or disposition differs")
        process = row["process"]
        _require(set(process) == {"receipt", "stdout", "stderr"},
                 f"smoke {profile}: process schema differs")
        for kind in ("receipt", "stdout", "stderr"):
            _require(process[kind]["path"] ==
                     f"{REL.as_posix()}/smoke-run-0001/processes/{profile}."
                     + ("receipt.json" if kind == "receipt" else kind),
                     f"smoke {profile}: process path differs")
            _bound(root, process[kind])
        receipt = _load(root / process["receipt"]["path"])
        stdout = (root / process["stdout"]["path"]).read_bytes()
        stderr = (root / process["stderr"]["path"]).read_bytes()
        expected_argv = [arg.replace("{export_path}",
                         historical_root + "/" + manifest["input"]["path"])
                         for arg in execution["invocations"][profile]]
        expected_stdout = (b"Accepted 1 declarations.\n" if profile == "official"
                           else b"Checked 1 declarations with no errors\n")
        disposition = classify(receipt, stdout, stderr,
                               expected_stdout=expected_stdout, baseline=False)
        _require(receipt.get("argv") == expected_argv
                 and receipt.get("cwd") == historical_root
                 and receipt.get("limits") == limits
                 and row.get("started_monotonic_ns") == receipt.get("started_monotonic_ns")
                 and receipt.get("raw_stdout_path") == process["stdout"]["path"]
                 and receipt.get("raw_stderr_path") == process["stderr"]["path"]
                 and disposition == row["disposition"]
                 and disposition["status"] == "ACCEPTED",
                 f"smoke {profile}: raw checker result differs")
        if profile == "nanoda":
            _require(receipt.get("stdin_bytes") == manifest["input"]["bytes"]
                     and receipt.get("stdin_sha256") == manifest["input"]["sha256"],
                     "smoke Nanoda stdin differs")
        else:
            _require(receipt.get("stdin_bytes") is None
                     and receipt.get("stdin_sha256") is None,
                     "smoke official stdin differs")
        start, end = receipt["started_monotonic_ns"], receipt["drained_monotonic_ns"]
        _require(previous_end is None or start >= previous_end,
                 "smoke process order overlaps")
        previous_end = end


def replay_result(root: Path) -> dict:
    root = root.resolve()
    base = root / REL
    result_path = base / "science-run-0001/science-result.json"
    _require(sha256(result_path.read_bytes()).hexdigest() == RESULT_SHA256,
             "committed scientific result differs")
    result = _load(result_path)
    _replay_reviews(root, base)
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
    _replay_construction(root, base, lock)
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
    _replay_smoke(root, base, smoke, execution, historical_root, expected_limits,
                  result["scientific_manifest"], result["execution_manifest"])
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
