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


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results/research/resource-envelope-pilot-1"
SCIENCE = BASE / "scientific-manifest.json"
EXECUTION = BASE / "execution-manifest.json"
PRECONSTRUCTION_REVIEW = BASE / "independent-preconstruction-review.json"
LIVE_PLAN = ROOT / "docs/research/RESOURCE_ENVELOPE_PILOT_1_PLAN.md"
PLAN_SNAPSHOT = BASE / "source/plan-at-freeze.md"

SCIENTIFIC_PATHS = (
    "results/research/resource-envelope-pilot-1/source/plan-at-freeze.md",
    "results/research/resource-envelope-pilot-1/source-reuse-review.md",
    "results/research/resource-envelope-pilot-1/protocol.md",
    "results/research/resource-envelope-pilot-1/independent-source-formula-review.json",
    "results/research/resource-envelope-pilot-1/independent-auditor-review-r3.json",
    "lib/resource_envelope_producer.py",
    "lib/resource_envelope_audit.py",
    "tests/test_resource_envelope_producer.py",
    "tests/test_resource_envelope_audit.py",
)
EXECUTION_PATHS = (
    "results/research/resource-envelope-pilot-1/nanoda-single-check.json",
    "results/research/resource-envelope-pilot-1/smoke-fixture-contract.json",
    "lib/resource_envelope_supervisor.py",
    "lib/resource_envelope_control.py",
    "lib/resource_envelope_construct.py",
    "lib/resource_envelope_observe.py",
    "tests/test_resource_envelope_supervisor.py",
    "tests/test_resource_envelope_control.py",
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
LAKEFILE = ("name = \"ResourceEnvelopePilot1\"\n"
            "defaultTargets = [\"ResourceEnvelopePilot1\"]\n\n"
            "[[lean_lib]]\nname = \"ResourceEnvelopePilot1\"\n").encode("ascii")
LEAN_TOOLCHAIN = b"leanprover/lean4:v4.29.1\n"
EMPTY_EXPORT = (b'{"meta":{"exporter":{"name":"lean4export","version":"3.1.0"},'
                b'"format":{"version":"3.1.0"},"lean":{"githash":'
                b'"f72c35b3f637c8c6571d353742168ab66cc22c00","version":"4.29.1"}}}\n')


class GateError(ValueError):
    pass


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


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
    """Bind exact executable/runtime/control bytes after science is committed."""
    _active_frontier()
    _committed(SCIENCE)
    science = _read(SCIENCE)
    for row in science["scientific_inputs"]:
        _check_binding(row, committed=True)
    for row in science["source_files"]:
        _check_binding(row, committed=False)
    for path in (ROOT / relative for relative in EXECUTION_PATHS):
        _committed(path)
    _source_revisions()
    if len(EMPTY_EXPORT) != 173:
        raise GateError("empty baseline metadata differs")
    runtime = [ROOT / EXPORTER_BINARY, ROOT / OFFICIAL_BINARY,
               ROOT / NANODA_BINARY, TOOLCHAIN / "lake", TOOLCHAIN / "lean",
               Path(sys.executable), Path("/bin/ps"), *LEAN_RUNTIME_LIBRARIES]
    for path in runtime:
        binding(path)
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
        "status": "FROZEN_BEFORE_SELECTED_INPUT_CONSTRUCTION",
        "scientific_manifest": binding(SCIENCE),
        "execution_inputs": [binding(ROOT / relative) for relative in EXECUTION_PATHS],
        "runtime": [binding(path) for path in runtime],
        "runtime_platform": {"system": platform.system(),
                             "release": platform.release(),
                             "machine": platform.machine(),
                             "python_version": sys.version},
        "limits": LIMITS,
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
