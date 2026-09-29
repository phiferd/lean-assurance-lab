"""Staged freeze and immutable-input gates for RESOURCE-ENVELOPE-PILOT-1.

Freeze functions bind committed code and retained binaries without generating
any selected term, building an observer, or launching one.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any

from lib.resource_envelope_producer import FAMILIES, SIZES, selected_slots
from lib.resource_envelope_observe import classify


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results/research/resource-envelope-pilot-1"
SCIENCE = BASE / "scientific-manifest.json"
EXECUTION = BASE / "execution-manifest-r2.json"
PRECONSTRUCTION_REVIEW = BASE / "independent-preconstruction-review-r2.json"
ORIGINAL_EXECUTION = BASE / "execution-manifest.json"
ORIGINAL_PRECONSTRUCTION_REVIEW = BASE / "independent-preconstruction-review.json"
CONSTRUCTION_R1 = BASE / "construction-run-0001"
LIVE_PLAN = ROOT / "docs/research/RESOURCE_ENVELOPE_PILOT_1_PLAN.md"
PLAN_SNAPSHOT = BASE / "source/plan-at-freeze.md"

SCIENTIFIC_PATHS = (
    "results/research/resource-envelope-pilot-1/source/plan-at-freeze.md",
    "results/research/resource-envelope-pilot-1/source-reuse-review.md",
    "results/research/resource-envelope-pilot-1/protocol.md",
    "results/research/resource-envelope-pilot-1/independent-source-formula-review.json",
    "results/research/resource-envelope-pilot-1/independent-auditor-review-r3.json",
    "results/research/resource-envelope-pilot-1/independent-measurement-rss-attribution-correction-r1.json",
    "lib/resource_envelope_producer.py",
    "lib/resource_envelope_audit.py",
    "tests/test_resource_envelope_producer.py",
    "tests/test_resource_envelope_audit.py",
)
EXECUTION_PATHS = (
    "results/research/resource-envelope-pilot-1/nanoda-single-check.json",
    "results/research/resource-envelope-pilot-1/baseline-empty.ndjson",
    "results/research/resource-envelope-pilot-1/smoke-fixture-contract.json",
    "results/research/resource-envelope-pilot-1/review-evidence/actual-host-supervisor-preflight.py",
    "results/research/resource-envelope-pilot-1/preflight-run-0001/provenance-attestation.json",
    "results/research/resource-envelope-pilot-1/independent-preflight-review.json",
    "results/research/resource-envelope-pilot-1/independent-launch-controller-review-r1.json",
    "results/research/resource-envelope-pilot-1/independent-launch-controller-review-r2.json",
    "results/research/resource-envelope-pilot-1/independent-launch-controller-review-r3.json",
    "results/research/resource-envelope-pilot-1/execution-freeze-attempt-r1.json",
    "results/research/resource-envelope-pilot-1/independent-execution-freeze-repair-review-r1.json",
    "results/research/resource-envelope-pilot-1/independent-construction-failure-review-r1.json",
    "results/research/resource-envelope-pilot-1/independent-construction-tooling-repair-review-r2.json",
    "results/research/resource-envelope-pilot-1/review-evidence/construction-recursion-repair-r2.json",
    "results/research/resource-envelope-pilot-1/construction-run-0001/construction-failure.json",
    "results/research/resource-envelope-pilot-1/execution-manifest.json",
    "results/research/resource-envelope-pilot-1/independent-preconstruction-review.json",
    "results/research/resource-envelope-pilot-1/review-evidence/launch-prefreeze-r1-after-first-custody-edit.py.txt",
    "results/research/resource-envelope-pilot-1/review-evidence/launch-tests-prefreeze-r1.py.txt",
    "results/research/resource-envelope-pilot-1/review-evidence/launch-prefreeze-r2-before-prefix-verifier.py.txt",
    "results/research/resource-envelope-pilot-1/review-evidence/launch-tests-prefreeze-r2-before-prefix-verifier.py.txt",
    "lib/resource_envelope_supervisor.py",
    "lib/resource_envelope_control.py",
    "lib/resource_envelope_construct.py",
    "lib/resource_envelope_observe.py",
    "lib/resource_envelope_launch.py",
    "lib/resource_envelope_replay.py",
    "tests/test_resource_envelope_supervisor.py",
    "tests/test_resource_envelope_control.py",
    "tests/test_resource_envelope_launch.py",
    "tests/test_evidence_replay_portability.py",
    "scripts/resource-envelope-pilot-1",
)
SOURCE_PATHS = (
    "external/lean-kernel-arena/_build/lean4export/leanprover_lean4_v4.29.1/Main.lean",
    "external/lean-kernel-arena/_build/lean4export/leanprover_lean4_v4.29.1/Export.lean",
    "external/lean-kernel-arena/_build/lean4export/leanprover_lean4_v4.29.1/lean-toolchain",
    "external/lean-kernel-arena/_build/checkers/official/src/Main.lean",
    "external/lean-kernel-arena/_build/checkers/official/src/.lake/packages/lean4export/Export/Parse.lean",
    "external/lean-kernel-arena/_build/checkers/official/src/.lake/packages/lean4export/format_ndjson.md",
    "external/lean-kernel-arena/_build/checkers/nanoda/src/src/main.rs",
    "external/lean-kernel-arena/_build/checkers/nanoda/src/src/parser.rs",
    "external/lean-kernel-arena/_build/checkers/nanoda/src/src/tc.rs",
    "external/lean-kernel-arena/_build/checkers/nanoda/src/src/util.rs",
    "external/lean-kernel-arena/_build/checkers/nanoda/src/Cargo.lock",
)
SOURCE_REVISIONS = {
    "external/lean-kernel-arena": "37f7525b732808a49b746dc6999d53c3717db124",
    "external/lean-kernel-arena/_build/lean4export/leanprover_lean4_v4.29.1":
        "cacf989bd75f608700820f6afc595f32e7a99a4d",
    "external/lean-kernel-arena/_build/checkers/official/src/.lake/packages/lean4export":
        "f297dfe2a8557e8674fe892bb49dffe4bfadc0e9",
    "external/lean-kernel-arena/_build/checkers/nanoda/src":
        "6ae1f0cd962f081f6c423454c5da729d841236a7",
}
EXPORTER_BINARY = "external/lean-kernel-arena/_build/lean4export/leanprover_lean4_v4.29.1/.lake/build/bin/lean4export"
OFFICIAL_BINARY = "external/lean-kernel-arena/_build/checkers/official/src/.lake/build/bin/kernel"
NANODA_BINARY = "external/lean-kernel-arena/_build/checkers/nanoda/src/target/release/nanoda_bin"
TOOLCHAIN = Path("/Users/danphifer/.elan/toolchains/leanprover--lean4---v4.29.1/bin")
LEAN_REPLAY = Path("/Users/danphifer/.elan/toolchains/leanprover--lean4---v4.33.0/src/lean/Lean/Replay.lean")
LEAN_RUNTIME_LIBRARIES = tuple(
    Path(f"/Users/danphifer/.elan/toolchains/leanprover--lean4---v{version}/lib/lean/{library}")
    for version in ("4.29.1", "4.33.0")
    for library in ("libleanshared.dylib", "libleanshared_1.dylib",
                    "libleanshared_2.dylib", "libInit_shared.dylib")
)
LIMITS = {
    "build": {"timeout_seconds": 600, "memory_ceiling_bytes": 4 * 1024 ** 3},
    "export": {"timeout_seconds": 120, "memory_ceiling_bytes": 2 * 1024 ** 3},
    "checker": {"timeout_seconds": 120, "memory_ceiling_bytes": 2 * 1024 ** 3},
    "sample_interval_seconds": 0.01,
    "max_trace_gap_seconds": 1.0,
    "cleanup_seconds": 2.0,
    "ps_timeout_seconds": 0.5,
    "output_cap_bytes": 10_000_000,
}
CONSTRUCTION_RECURSION_LIMIT = 8192
LAKEFILE = ("name = \"ResourceEnvelopePilot1\"\n"
            "defaultTargets = [\"ResourceEnvelopePilot1\"]\n\n"
            f"[leanOptions]\nmaxRecDepth = {CONSTRUCTION_RECURSION_LIMIT}\n\n"
            "[[lean_lib]]\nname = \"ResourceEnvelopePilot1\"\n").encode("ascii")
LEAN_TOOLCHAIN = b"leanprover/lean4:v4.29.1\n"
OPTION_TRANSPORT_SOURCES = tuple(
    Path("/Users/danphifer/.elan/toolchains/leanprover--lean4---v4.29.1/src/lean") / path
    for path in ("Lake/Lake/CLI/Init.lean", "Lake/Lake/Load/Toml.lean",
                 "Lake/Lake/Config/Package.lean", "Lake/Lake/Config/LeanLib.lean",
                 "Lake/Lake/Config/Module.lean", "Lake/Lake/Build/Module.lean",
                 "Lean/Util/RecDepth.lean", "Init/Prelude.lean")
)
ORIGINAL_COMPLETED_IDS = ("rep1-pi-016", "rep1-pi-032", "rep1-pi-064", "rep1-pi-128")
EMPTY_EXPORT = (b'{"meta":{"exporter":{"name":"lean4export","version":"3.1.0"},'
                b'"format":{"version":"3.1.0"},"lean":{"githash":'
                b'"f72c35b3f637c8c6571d353742168ab66cc22c00","version":"4.29.1"}}}\n')


class GateError(ValueError):
    pass


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _python_invocation_identity() -> dict[str, Any]:
    """Bind the exact symlink invocation and its regular target, narrowly."""
    invocation = Path(sys.executable)
    if not invocation.is_symlink():
        raise GateError("preflight Python invocation is no longer a symlink")
    target = invocation.resolve(strict=True)
    if target.is_symlink() or not target.is_file():
        raise GateError("Python invocation does not resolve to a regular executable")
    resolved = binding(target)
    flat_bytes = invocation.read_bytes()
    if len(flat_bytes) != resolved["bytes"] or _sha(flat_bytes) != resolved["sha256"]:
        raise GateError("Python symlink bytes differ from resolved target")
    return {"invocation_path": str(invocation),
            "link_target": os.readlink(invocation),
            "resolved_target": resolved,
            "invocation_bytes": len(flat_bytes),
            "invocation_sha256": _sha(flat_bytes)}


def binding(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise GateError(f"missing/nonregular binding: {path}")
    try:
        name = path.relative_to(ROOT).as_posix()
    except ValueError:
        name = str(path)
    raw = path.read_bytes()
    return {"path": name, "bytes": len(raw), "sha256": _sha(raw)}


def _committed(path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise GateError(f"missing committed input: {path}")
    try:
        relative = path.relative_to(ROOT)
    except ValueError as exc:
        raise GateError("expected repository path") from exc
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", "--", str(relative)],
                             cwd=ROOT, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, check=False)
    dirty = subprocess.run(["git", "status", "--porcelain", "--", str(relative)],
                           cwd=ROOT, stdout=subprocess.PIPE, text=True, check=True)
    if tracked.returncode or dirty.stdout:
        raise GateError(f"input is not clean and committed: {relative}")


def _write_new(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(raw)


def _read(path: Path) -> dict[str, Any]:
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GateError(f"cannot read manifest/review {path}") from exc
    if type(row) is not dict:
        raise GateError(f"expected object: {path}")
    return row


def _check_binding(row: dict[str, Any], *, committed: bool) -> None:
    path = Path(row["path"])
    path = path if path.is_absolute() else ROOT / path
    if binding(path) != row:
        raise GateError(f"bound file changed: {row['path']}")
    if committed and path.is_relative_to(ROOT):
        _committed(path)


def _git_revision(relative: str) -> str:
    completed = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT / relative,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, check=False)
    if completed.returncode != 0:
        raise GateError(f"missing source revision: {relative}")
    return completed.stdout.strip()


def _source_revisions() -> dict[str, str]:
    for path, wanted in SOURCE_REVISIONS.items():
        if _git_revision(path) != wanted:
            raise GateError(f"source revision changed: {path}")
    return dict(SOURCE_REVISIONS)


def _active_frontier() -> None:
    queue = _read(ROOT / "config/research-queue.json")
    work = _read(BASE / "work-record.json")
    selected = [row for row in queue.get("items", [])
                if type(row) is dict and row.get("id") == "RESOURCE-ENVELOPE-PILOT-1"]
    if (queue.get("selected_item") != "RESOURCE-ENVELOPE-PILOT-1"
            or len(selected) != 1 or selected[0].get("status") != "ACTIVE"
            or work.get("item_id") != "RESOURCE-ENVELOPE-PILOT-1"
            or work.get("status") != "ACTIVE"):
        raise GateError("canonical queue/work record does not select ACTIVE resource item")
    _committed(ROOT / "config/research-queue.json")
    _committed(BASE / "work-record.json")


def freeze_science() -> dict[str, Any]:
    """Bind source/formula/auditor bytes; never call render_source."""
    _active_frontier()
    _committed(LIVE_PLAN)
    if not PLAN_SNAPSHOT.is_file() or PLAN_SNAPSHOT.read_bytes() != LIVE_PLAN.read_bytes():
        raise GateError("plan snapshot differs from live ACTIVE plan at freeze")
    paths = [ROOT / relative for relative in SCIENTIFIC_PATHS]
    for path in paths:
        _committed(path)
    if FAMILIES != ("pi", "let") or SIZES != (16, 32, 64, 128, 256, 512):
        raise GateError("scientific family/size scope changed")
    if len(selected_slots()) != 12 or len(EMPTY_EXPORT) != 173:
        raise GateError("scientific cardinality or empty metadata differs")
    row = {
        "schema_version": 1,
        "item_id": "RESOURCE-ENVELOPE-PILOT-1",
        "status": "FROZEN_BEFORE_SELECTED_INPUT_CONSTRUCTION",
        "source_revisions": _source_revisions(),
        "source_files": [binding(ROOT / name) for name in SOURCE_PATHS] + [binding(LEAN_REPLAY)],
        "scientific_inputs": [binding(path) for path in paths],
        "live_plan_at_freeze": binding(LIVE_PLAN),
        "immutable_plan_snapshot": binding(PLAN_SNAPSHOT),
        "families": list(FAMILIES), "sizes": list(SIZES),
        "case_order": [{"ordinal": ordinal, "family": family, "size": size}
                       for ordinal, family, size in selected_slots()],
        "observer_order": ["official", "nanoda"],
        "scientific_cells": 24,
        "baseline_runs_per_profile": 6,
        "case_auditor": "lib.resource_envelope_audit.audit_case/audit_corpus",
        "construction_rule": "lib.resource_envelope_producer.render_source; no RNG or replacement",
    }
    _write_new(SCIENCE, row)
    return row


def freeze_execution() -> dict[str, Any]:
    """Bind a new execution revision, retaining the first construction attempt."""
    _active_frontier()
    _committed(SCIENCE)
    science = _read(SCIENCE)
    for row in science["scientific_inputs"]:
        _check_binding(row, committed=True)
    for row in science["source_files"]:
        _check_binding(row, committed=False)
    for path in (ROOT / relative for relative in EXECUTION_PATHS):
        _committed(path)
    previous = _repair_history()
    _source_revisions()
    if len(EMPTY_EXPORT) != 173:
        raise GateError("empty baseline metadata differs")
    if (BASE / "baseline-empty.ndjson").read_bytes() != EMPTY_EXPORT:
        raise GateError("baseline file differs from exact frozen empty export")
    python_identity = _python_invocation_identity()
    runtime = [ROOT / EXPORTER_BINARY, ROOT / OFFICIAL_BINARY,
               ROOT / NANODA_BINARY, TOOLCHAIN / "lake", TOOLCHAIN / "lean",
               Path(python_identity["resolved_target"]["path"]),
               Path("/bin/ps"), Path("/bin/sh"),
               Path("/bin/sleep"), *LEAN_RUNTIME_LIBRARIES]
    for path in runtime:
        binding(path)
    for path in OPTION_TRANSPORT_SOURCES:
        binding(path)
    attestation = _read(BASE / "preflight-run-0001/provenance-attestation.json")
    if attestation.get("status") != "POST_RUN_PROVENANCE_ATTESTATION":
        raise GateError("positive direct-supervisor preflight provenance absent")
    expected_preflight_tools = [
        BASE / "review-evidence/actual-host-supervisor-preflight.py",
        ROOT / "lib/resource_envelope_supervisor.py",
        ROOT / "lib/resource_envelope_observe.py",
        Path("/bin/ps"), Path("/bin/sh"), Path("/bin/sleep")]
    flat_python = {"path": python_identity["invocation_path"],
                   "bytes": python_identity["invocation_bytes"],
                   "sha256": python_identity["invocation_sha256"]}
    expected_preflight_bindings = ([binding(path) for path in expected_preflight_tools[:3]]
                                   + [flat_python]
                                   + [binding(path) for path in expected_preflight_tools[3:]])
    if attestation.get("tooling_runtime") != expected_preflight_bindings:
        raise GateError("positive preflight did not cover current supervisor/runtime bytes")
    if (attestation.get("host") != {"system": platform.system(),
                                     "release": platform.release(),
                                     "machine": platform.machine(),
                                     "python_version": sys.version}):
        raise GateError("positive preflight host identity differs")
    preflight_files = [BASE / "preflight-run-0001" / name for name in
                       ("attempt.json", "process-receipt.json", "stdout.raw",
                        "stderr.raw", "summary.json")]
    for path in preflight_files:
        _committed(path)
    if attestation.get("attempt_files") != [binding(path) for path in preflight_files]:
        raise GateError("positive preflight raw/receipt binding differs")
    preflight_receipt = _read(BASE / "preflight-run-0001/process-receipt.json")
    preflight_stdout = (BASE / "preflight-run-0001/stdout.raw").read_bytes()
    preflight_stderr = (BASE / "preflight-run-0001/stderr.raw").read_bytes()
    disposition = classify(preflight_receipt, preflight_stdout, preflight_stderr,
                           expected_stdout=b"preflight-ok", baseline=False)
    if (disposition["status"] != "ACCEPTED" or preflight_receipt.get("sample_count", 0) <= 0
            or preflight_receipt.get("maximum_sampled_group_rss_bytes", 0) <= 0
            or not preflight_receipt.get("cleanup_complete")
            or _read(BASE / "preflight-run-0001/summary.json").get("status")
            != "PASS_POSITIVE_ACTUAL_HOST_RSS_AND_CLEANUP"):
        raise GateError("positive actual-host direct-supervisor preflight invalid")
    preflight_review = _read(BASE / "independent-preflight-review.json")
    if (preflight_review.get("verdict") != "PASS_POSITIVE_ACTUAL_HOST_PREFLIGHT"
            or preflight_review.get("preflight_provenance_sha256")
            != binding(BASE / "preflight-run-0001/provenance-attestation.json")["sha256"]
            or preflight_review.get("preflight_receipt_sha256")
            != binding(BASE / "preflight-run-0001/process-receipt.json")["sha256"]):
        raise GateError("independent positive direct-supervisor preflight review differs")
    config = _read(BASE / "nanoda-single-check.json")
    if config != {"use_stdin": True, "num_threads": 1,
                   "print_success_message": True, "print_axioms": False,
                   "unpermitted_axiom_hard_error": True,
                   "unsafe_permit_all_axioms": False,
                   "nat_extension": False, "string_extension": False}:
        raise GateError("Nanoda single-check config differs")
    smoke = _read(BASE / "smoke-fixture-contract.json")
    if (smoke.get("fixture_id") != "retained-vdtp1-pi-01"
            or smoke.get("expected_outputs") != {
                "official": "Accepted 1 declarations.\n",
                "nanoda": "Checked 1 declarations with no errors\n"}):
        raise GateError("smoke fixture contract differs")
    for key in ("input", "historical_case", "historical_independent_audit"):
        _check_binding(smoke[key], committed=True)
    prior_audit = _read(ROOT / smoke["historical_independent_audit"]["path"])
    if prior_audit.get("status") != "PASS" or prior_audit.get("case_id") != "vdtp1-pi-01":
        raise GateError("historical independent smoke audit differs")
    smoke_lines = (ROOT / smoke["input"]["path"]).read_bytes().splitlines()
    try:
        smoke_declarations = [json.loads(line)["def"] for line in smoke_lines
                              if "def" in json.loads(line)]
    except (json.JSONDecodeError, KeyError) as exc:
        raise GateError("historical smoke export malformed") from exc
    if (len(smoke_declarations) != 1
            or smoke_declarations[0].get("safety") != "safe"
            or smoke_declarations[0].get("hints") != {"regular": 1}
            or smoke_declarations[0].get("levelParams") != []):
        raise GateError("historical smoke export is not one safe definition")
    row = {
        "schema_version": 1,
        "item_id": "RESOURCE-ENVELOPE-PILOT-1",
        "status": "FROZEN_BEFORE_REPAIR_CONSTRUCTION_RETRY",
        "scientific_manifest": binding(SCIENCE),
        "execution_inputs": [binding(ROOT / relative) for relative in EXECUTION_PATHS],
        "runtime": [binding(path) for path in runtime],
        "option_transport_sources": [binding(path) for path in OPTION_TRANSPORT_SOURCES],
        "repair_history": previous,
        "python_invocation": python_identity,
        "runtime_platform": {"system": platform.system(),
                             "release": platform.release(),
                             "machine": platform.machine(),
                             "python_version": sys.version},
        "limits": LIMITS,
        "construction_recursion_max_depth": CONSTRUCTION_RECURSION_LIMIT,
        "workspace_templates": {"lakefile_toml_sha256": _sha(LAKEFILE),
                                "lakefile_toml_bytes": len(LAKEFILE),
                                "lean_toolchain_sha256": _sha(LEAN_TOOLCHAIN),
                                "lean_toolchain_bytes": len(LEAN_TOOLCHAIN)},
        "empty_export": {"bytes": len(EMPTY_EXPORT), "sha256": _sha(EMPTY_EXPORT)},
        "smoke_fixture_contract": binding(BASE / "smoke-fixture-contract.json"),
        "invocations": {
            "build": [str(TOOLCHAIN / "lake"), "build", "ResourceEnvelopePilot1"],
            "export": [str(TOOLCHAIN / "lake"), "env", str(ROOT / EXPORTER_BINARY),
                       "ResourceEnvelopePilot1", "--", "{declaration}"],
            "official": [str(ROOT / OFFICIAL_BINARY), "{export_path}"],
            "nanoda": [str(ROOT / NANODA_BINARY), str(BASE / "nanoda-single-check.json")],
        },
        "environment": {"PATH": str(TOOLCHAIN) + ":/usr/bin:/bin:/usr/sbin:/sbin",
                        "HOME": os.environ.get("HOME", ""), "LC_ALL": "C", "LANG": "C"},
        "baseline_order": "official before 3, official after 3; nanoda before 3, nanoda after 3",
        "scientific_order": "profile official then nanoda; family pi then let; size ascending",
    }
    _write_new(EXECUTION, row)
    return row


def require_construction_gate() -> tuple[dict[str, Any], dict[str, Any]]:
    _active_frontier()
    _committed(SCIENCE)
    _committed(EXECUTION)
    _committed(PRECONSTRUCTION_REVIEW)
    science, execution = _read(SCIENCE), _read(EXECUTION)
    for row in science["scientific_inputs"]:
        _check_binding(row, committed=True)
    for row in science["source_files"]:
        _check_binding(row, committed=False)
    for row in execution["execution_inputs"]:
        _check_binding(row, committed=True)
    for row in execution["runtime"]:
        _check_binding(row, committed=False)
    if execution.get("option_transport_sources") != [binding(path) for path in OPTION_TRANSPORT_SOURCES]:
        raise GateError("pinned Lake recursion-option transport sources differ")
    if execution.get("construction_recursion_max_depth") != CONSTRUCTION_RECURSION_LIMIT:
        raise GateError("construction-only recursion setting differs")
    if execution.get("repair_history") != _repair_history():
        raise GateError("original construction attempt binding differs")
    if execution.get("python_invocation") != _python_invocation_identity():
        raise GateError("Python invocation symlink or target differs from frozen execution")
    if execution["scientific_manifest"] != binding(SCIENCE):
        raise GateError("execution manifest science binding differs")
    review = _read(PRECONSTRUCTION_REVIEW)
    if (review.get("verdict") != "PASS_FOR_CONSTRUCTION"
            or review.get("scientific_manifest_sha256") != binding(SCIENCE)["sha256"]
            or review.get("execution_manifest_sha256") != binding(EXECUTION)["sha256"]):
        raise GateError("exact independent construction review absent")
    if _source_revisions() != science["source_revisions"]:
        raise GateError("source revisions differ")
    return science, execution


def _repair_history() -> dict[str, Any]:
    """Recheck the committed R1 failure and all four accepted prefix inputs."""
    core = (ORIGINAL_EXECUTION, ORIGINAL_PRECONSTRUCTION_REVIEW,
            CONSTRUCTION_R1 / "construction-failure.json",
            BASE / "independent-construction-failure-review-r1.json")
    for path in core:
        _committed(path)
    old_review = _read(ORIGINAL_PRECONSTRUCTION_REVIEW)
    old_failure = _read(CONSTRUCTION_R1 / "construction-failure.json")
    failure_review = _read(BASE / "independent-construction-failure-review-r1.json")
    if (old_review.get("verdict") != "PASS_FOR_CONSTRUCTION"
            or old_review.get("scientific_manifest_sha256") != binding(SCIENCE)["sha256"]
            or old_review.get("execution_manifest_sha256") != binding(ORIGINAL_EXECUTION)["sha256"]
            or old_failure.get("status") != "CONSTRUCTION_FAILURE_REPAIR_PAUSE"
            or old_failure.get("phase") != "build"
            or old_failure.get("case_id") != "rep1-pi-256"
            or old_failure.get("scientific_manifest") != binding(SCIENCE)
            or old_failure.get("execution_manifest") != binding(ORIGINAL_EXECUTION)
            or failure_review.get("verdict") != "REPAIR_REQUIRED_WITH_SCIENTIFIC_INPUTS_UNCHANGED"
            or {row.get("path"): row for row in failure_review.get("reviewed_inputs", [])}.get(
                binding(CONSTRUCTION_R1 / "construction-failure.json")["path"])
            != binding(CONSTRUCTION_R1 / "construction-failure.json")):
        raise GateError("original reviewed construction failure differs")
    rows = []
    for case_id in ORIGINAL_COMPLETED_IDS:
        paths = {kind: CONSTRUCTION_R1 / "staged/corpus" / folder / f"{case_id}.{suffix}"
                 for kind, folder, suffix in (("source", "sources", "lean"),
                                              ("export", "exports", "ndjson"),
                                              ("case", "cases", "json"))}
        for path in paths.values():
            _committed(path)
        rows.append({"id": case_id, **{kind: binding(path) for kind, path in paths.items()}})
    reviewed = {row.get("path"): row for row in failure_review["reviewed_inputs"]}
    if len(reviewed) != len(failure_review["reviewed_inputs"]):
        raise GateError("duplicate R1 independent-review evidence binding")
    for row in failure_review["reviewed_inputs"]:
        _check_binding(row, committed=True)
    for row in failure_review.get("source_support", []):
        _check_binding(row, committed=False)
    if (len(old_failure.get("completed_cases", [])) != len(rows)
            or [row.get("id") for row in old_failure["completed_cases"]] != list(ORIGINAL_COMPLETED_IDS)):
        raise GateError("original completed prefix differs")
    for expected, prior in zip(rows, old_failure["completed_cases"]):
        for kind in ("source", "export", "case"):
            if prior.get(kind) != expected[kind] or reviewed.get(expected[kind]["path"]) != expected[kind]:
                raise GateError("original accepted input custody differs")
    return {"original_execution_manifest": binding(ORIGINAL_EXECUTION),
            "original_preconstruction_review": binding(ORIGINAL_PRECONSTRUCTION_REVIEW),
            "failed_attempt": binding(CONSTRUCTION_R1 / "construction-failure.json"),
            "independent_failure_review": binding(BASE / "independent-construction-failure-review-r1.json"),
            "completed_prefix": rows}
