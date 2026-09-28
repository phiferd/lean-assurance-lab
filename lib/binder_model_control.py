"""Exact staged gates for the BINDER-MODEL-PILOT-1 scientific corpus."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results/research/binder-model-pilot-1"
SCIENCE = BASE / "scientific-manifest.json"
EXECUTION = BASE / "execution-manifest.json"
CORPUS_LOCK = BASE / "corpus-lock.json"
REVIEW = BASE / "independent-preconstruction-review.json"
LIVE_PLAN = ROOT / "docs/research/BINDER_MODEL_PILOT_1_PLAN.md"
PLAN_SNAPSHOT = BASE / "source/plan-at-freeze.md"

SCIENTIFIC_PATHS = (
    "results/research/binder-model-pilot-1/source/plan-at-freeze.md",
    "results/research/binder-model-pilot-1/protocol.md",
    "results/research/binder-model-pilot-1/scientific-contract.json",
    "results/research/binder-model-pilot-1/source-reuse-review.json",
    "results/research/binder-model-pilot-1/source-lock.json",
    "results/research/binder-model-pilot-1/selected-input-adoption.json",
    "results/research/binder-model-pilot-1/independent-selected-input-adoption-review.json",
    "results/research/binder-model-pilot-1/independent-preconstruction-review-r1.json",
    "results/research/binder-model-pilot-1/review-evidence/prefreeze-auditor-tests-r1.py.txt",
    "lib/binder_named_model.py",
    "lib/binder_model_vectors.py",
    "lib/binder_model_audit.py",
    "tests/test_binder_named_model.py",
    "tests/test_binder_model_audit.py",
)
EXECUTION_PATHS = (
    "results/research/binder-model-pilot-1/BinderObserver.lean",
    "results/research/binder-model-pilot-1/kiota-observer/Cargo.toml",
    "results/research/binder-model-pilot-1/kiota-observer/Cargo.lock",
    "results/research/binder-model-pilot-1/kiota-observer/src/main.rs",
    "results/research/binder-model-pilot-1/bin/kiota-observer",
    "lib/binder_model_control.py",
    "lib/binder_model_execute.py",
    "lib/metamorphic_pilot_runner.py",
    "lib/metamorphic_pilot_runner_v3.py",
    "scripts/binder-model-pilot-1",
    "tests/test_binder_model_control.py",
)
SMOKE_PATHS = (
    "results/research/binder-model-pilot-1/smoke/inputs.ndjson",
    "results/research/binder-model-pilot-1/smoke/expected.ndjson",
    "results/research/binder-model-pilot-1/smoke/contexts.json",
)


class GateError(ValueError):
    pass


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def binding(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise GateError(f"missing bound file: {path}")
    try:
        rel = path.relative_to(ROOT)
        name = str(rel)
    except ValueError:
        name = str(path)
    return {"path": name, "bytes": path.stat().st_size, "sha256": sha(path)}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_new(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def canonical_record_bytes(record: Any) -> bytes:
    return json.dumps(record, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def verify_adopted_record(generated: Any, retained: Any, expected_sha256: str) -> None:
    retained_bytes = canonical_record_bytes(retained)
    if (canonical_record_bytes(generated) != retained_bytes
            or hashlib.sha256(retained_bytes).hexdigest() != expected_sha256):
        raise GateError("selected-row canonical-byte replay differs")


def committed(path: Path) -> None:
    if not path.is_file():
        raise GateError(f"missing committed input: {path}")
    try:
        rel = path.relative_to(ROOT)
    except ValueError as exc:
        raise GateError("expected repository file") from exc
    status = subprocess.run(["git", "status", "--porcelain", "--", str(rel)], cwd=ROOT,
                            capture_output=True, text=True, check=True).stdout
    if status:
        raise GateError(f"uncommitted or dirty file: {rel}")
    if subprocess.run(["git", "ls-files", "--error-unmatch", "--", str(rel)], cwd=ROOT,
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        raise GateError(f"untracked file: {rel}")


def check_bindings(rows: list[dict[str, Any]], *, require_committed: bool = True) -> None:
    for row in rows:
        path = ROOT / row["path"] if not Path(row["path"]).is_absolute() else Path(row["path"])
        if binding(path) != row:
            raise GateError(f"bound file changed: {row['path']}")
        if require_committed and path.is_relative_to(ROOT):
            committed(path)


def _source_files() -> list[Path]:
    lock = read_json(BASE / "source-lock.json")
    if lock["revision"] != "2d2a9fa31cba31abdd49543c3bb667591207577e":
        raise GateError("Kiota source revision differs")
    source = BASE / "source/kiota"
    rows = lock["files"]
    expected = {row["path"] for row in rows}
    actual = {str(path.relative_to(source)) for path in source.rglob("*") if path.is_file()}
    if expected != actual:
        raise GateError("Kiota source inventory differs")
    for row in rows:
        path = source / row["path"]
        if path.stat().st_size != row["bytes"] or sha(path) != row["sha256"]:
            raise GateError(f"Kiota source file differs: {row['path']}")
    return [source / row["path"] for row in rows]


def freeze_science() -> dict[str, Any]:
    source_files = _source_files()
    committed(LIVE_PLAN)
    paths = [ROOT / p for p in SCIENTIFIC_PATHS] + source_files
    for path in paths:
        committed(path)
    if PLAN_SNAPSHOT.read_bytes() != LIVE_PLAN.read_bytes():
        raise GateError("immutable plan snapshot differs from active plan at freeze")
    adoption = read_json(BASE / "selected-input-adoption.json")
    if adoption.get("status") != "ADOPTED_UNCHANGED_PENDING_DETERMINISTIC_REPLAY":
        raise GateError("prewritten selected inputs lack accepted unchanged adoption")
    adoption_review = read_json(BASE / "independent-selected-input-adoption-review.json")
    if adoption_review.get("verdict") != "PASS_FOR_UNCHANGED_ADOPTION":
        raise GateError("independent unchanged-adoption review absent")
    adoption_sha = sha(BASE / "selected-input-adoption.json")
    if (adoption_review.get("selected_input_adoption_sha256") != adoption_sha
            or adoption_review.get("adoption_sha256") != adoption_sha):
        raise GateError("independent unchanged-adoption hash differs")
    incident = adoption["incident"]
    snapshot = ROOT / incident["raw_snapshot_path"]
    if (sha(snapshot) != incident["raw_snapshot_sha256"]
            or snapshot.stat().st_size != incident["raw_snapshot_bytes"]):
        raise GateError("prefreeze selected-row snapshot differs")
    if adoption_review.get("snapshot_sha256") != sha(snapshot):
        raise GateError("independent selected-row snapshot hash differs")
    records = adoption["records"]
    if [row["ordinal"] for row in records] != [0, 2500, 5000, 7500]:
        raise GateError("selected-row adoption ordinals differ")
    for row in records:
        record = row["record"]
        canonical = canonical_record_bytes(record)
        if hashlib.sha256(canonical).hexdigest() != row["canonical_record_sha256"]:
            raise GateError(f"selected-row retained hash differs: {row['ordinal']}")
    if (adoption_review.get("record_ids") != [row["id"] for row in records]
            or adoption_review.get("canonical_record_sha256")
            != [row["canonical_record_sha256"] for row in records]):
        raise GateError("independent selected-row inventory differs")
    contract = read_json(BASE / "scientific-contract.json")
    if (contract["ordinal_range"] != [0, 9999] or contract["operation_counts"] != [2500] * 4
            or contract["expected_outputs_per_observer"] != 15000):
        raise GateError("scientific scope differs")
    result = {
        "schema_version": 1, "item_id": "BINDER-MODEL-PILOT-1",
        "status": "FROZEN_BEFORE_FULL_CONSTRUCTION_FOUR_PREFREEZE_ROWS_ADOPTED",
        "scientific_inputs": [binding(p) for p in paths],
        "source_revision": "2d2a9fa31cba31abdd49543c3bb667591207577e",
        "live_plan_at_freeze": binding(LIVE_PLAN),
        "immutable_plan_snapshot": binding(PLAN_SNAPSHOT),
        "fixed_vector_count": 10000, "comparison_count_per_observer": 15000,
        "construction_rule": "lib/binder_model_vectors.py:make_vector(0..9999), ordered NDJSON",
        "model": "lib/binder_named_model.py",
        "auditor": "lib/binder_model_audit.py, independent imports and negative controls",
    }
    write_new(SCIENCE, result)
    return result


def _lean_runtime() -> list[Path]:
    tc = Path("/Users/danphifer/.elan/toolchains/leanprover--lean4---v4.33.0")
    return [tc / "bin/lean", tc / "src/lean/Lean/Expr.lean",
            tc / "lib/lean/libleanshared.dylib", tc / "lib/lean/libleanshared_1.dylib",
            tc / "lib/lean/libleanshared_2.dylib", tc / "lib/lean/libInit_shared.dylib"]


def freeze_execution() -> dict[str, Any]:
    committed(SCIENCE)
    science = read_json(SCIENCE)
    check_bindings(science["scientific_inputs"])
    source_files = _source_files()
    if not source_files:
        raise GateError("empty source pin")
    paths = [ROOT / p for p in EXECUTION_PATHS + SMOKE_PATHS]
    for path in paths:
        committed(path)
    runtime = _lean_runtime() + [Path(sys.executable), Path("/opt/homebrew/bin/cargo"),
                                 Path("/opt/homebrew/bin/rustc"), Path("/bin/ps")]
    for path in runtime:
        if not path.is_file():
            raise GateError(f"runtime unavailable: {path}")
    result = {
        "schema_version": 1, "item_id": "BINDER-MODEL-PILOT-1",
        "status": "FROZEN_BEFORE_FULL_CONSTRUCTION_FOUR_PREFREEZE_ROWS_ADOPTED",
        "scientific_manifest": binding(SCIENCE),
        "tooling": [binding(p) for p in paths],
        "runtime": [binding(p) for p in runtime],
        "official_revision": "d8b18978322de05a8f3dba51ef03cf5461676c17",
        "kiota_revision": "2d2a9fa31cba31abdd49543c3bb667591207577e",
        "profiles": ["official-lean-4.33.0", "kiota-2d2a9fa"],
        "batch_size": 500, "batch_count": 20,
        "output_schema": {"exact_keys": ["id", "outputs"], "rows_per_batch": 500,
                          "stage_count": "1 for LIFT/SUBST, 2 for LIFT_COMPOSE/SUBST_COMPOSE"},
        "environment": {"LANG": "C", "PATH": "/usr/bin:/bin"},
        "process_safety": {"timeout_seconds": 180, "rss_ceiling_bytes": 3221225472,
                           "positive_rss_required": True, "cleanup_required": True,
                           "fault_policy": "PAUSE_REPAIR_RESUME_SAME_ITEM"},
        "attempt_limit": None,
        "smoke": {"case_count": 5, "stage_outputs": 7,
                  "role": "capability control outside scientific corpus"},
    }
    write_new(EXECUTION, result)
    return result


def check_frozen_inputs() -> dict[str, Any]:
    for p in (SCIENCE, EXECUTION, REVIEW):
        committed(p)
    science = read_json(SCIENCE)
    execution = read_json(EXECUTION)
    review = read_json(REVIEW)
    if binding(SCIENCE) != execution["scientific_manifest"]:
        raise GateError("scientific manifest changed")
    check_bindings(science["scientific_inputs"])
    check_bindings(execution["tooling"])
    check_bindings(execution["runtime"], require_committed=False)
    if review.get("verdict") != "PASS_FOR_CONSTRUCTION_SUBJECT_TO_ADOPTION_REPLAY":
        raise GateError("independent construction gate absent")
    if review.get("scientific_manifest_sha256") != sha(SCIENCE):
        raise GateError("review scientific binding differs")
    if review.get("execution_manifest_sha256") != sha(EXECUTION):
        raise GateError("review execution binding differs")
    return execution


def construct() -> dict[str, Any]:
    execution = check_frozen_inputs()
    from lib.binder_model_vectors import construct as generate
    from lib.binder_model_audit import audit_corpus

    attempts = BASE / "construction"
    attempts.mkdir(exist_ok=True)
    index = len(list(attempts.glob("attempt-[0-9][0-9][0-9][0-9]"))) + 1
    out = attempts / f"attempt-{index:04d}"
    out.mkdir(exist_ok=False)
    path = out / "vectors.ndjson"
    try:
        adoption = read_json(BASE / "selected-input-adoption.json")
        from lib.binder_model_vectors import make_vector
        from lib.binder_model_audit import audit_vector
        replay_rows = []
        for row in adoption["records"]:
            ordinal = row["ordinal"]
            generated = make_vector(ordinal)
            original = row["record"]
            verify_adopted_record(generated, original, row["canonical_record_sha256"])
            if audit_vector(generated)["status"] != "PASS":
                raise GateError(f"selected-row independent audit differs: {ordinal}")
            replay_rows.append({"ordinal": ordinal, "id": row["id"],
                                "canonical_record_sha256": row["canonical_record_sha256"],
                                "status": "UNCHANGED_AND_AUDITED"})
        write_new(out / "adoption-replay.json", {
            "schema_version": 1, "status": "PASS", "scientific_manifest_sha256": sha(SCIENCE),
            "execution_manifest_sha256": sha(EXECUTION),
            "adoption_sha256": sha(BASE / "selected-input-adoption.json"), "rows": replay_rows})
        generate(path)
        receipt = audit_corpus(path)
        write_new(out / "audit.json", receipt)
        if receipt.get("status") != "PASS":
            raise GateError("construction auditor returned non-PASS")
        lines = path.read_bytes().splitlines(keepends=True)
        if len(lines) != 10000 or any(not line.endswith(b"\n") for line in lines):
            raise GateError("construction count or newline differs")
        for batch in range(execution["batch_count"]):
            (out / f"batch-{batch:02d}.ndjson").write_bytes(
                b"".join(lines[batch * 500:(batch + 1) * 500]))
        verify_batch_partition(path,
                               [out / f"batch-{i:02d}.ndjson" for i in range(execution["batch_count"])])
    except Exception as exc:
        failure = {"schema_version": 1, "status": "FAILED_REPAIR_REQUIRED", "attempt": index,
                   "phase": "construct_or_audit", "error_type": type(exc).__name__,
                   "error": str(exc), "scientific_manifest_sha256": sha(SCIENCE),
                   "execution_manifest_sha256": sha(EXECUTION),
                   "partial_vectors": binding(path) if path.is_file() else None}
        write_new(out / "failure.json", failure)
        raise
    return {"attempt": index, "path": str(out.relative_to(ROOT)), "audit": receipt}


def verify_batch_partition(vectors: Path, batches: list[Path], *, batch_size: int = 500,
                           count: int = 10000) -> None:
    raw = vectors.read_bytes()
    if not raw.endswith(b"\n"):
        raise GateError("full vector stream lacks final newline")
    lines = raw.splitlines(keepends=True)
    if len(lines) != count or any(line == b"\n" or not line.endswith(b"\n") for line in lines):
        raise GateError("full vector stream count/newlines differ")
    if len(batches) * batch_size != count:
        raise GateError("batch partition cardinality differs")
    for index, path in enumerate(batches):
        expected = b"".join(lines[index * batch_size:(index + 1) * batch_size])
        if path.read_bytes() != expected:
            raise GateError(f"batch {index} is not the exact full-vector slice")


def seal_corpus(attempt: int) -> dict[str, Any]:
    execution = check_frozen_inputs()
    src = BASE / "construction" / f"attempt-{attempt:04d}"
    audit = read_json(src / "audit.json")
    if audit.get("status") != "PASS":
        raise GateError("cannot seal failed audit")
    from lib.binder_model_audit import audit_corpus
    if audit_corpus(src / "vectors.ndjson") != audit:
        raise GateError("audit replay differs")
    verify_batch_partition(src / "vectors.ndjson",
                           [src / f"batch-{i:02d}.ndjson" for i in range(execution["batch_count"])])
    dest = BASE / "corpus"
    if dest.exists():
        raise GateError("corpus already sealed")
    shutil.copytree(src, dest)
    rows = [binding(p) for p in sorted(dest.glob("*.ndjson"))] + [
        binding(dest / "audit.json"), binding(dest / "adoption-replay.json")]
    if len(rows) != execution["batch_count"] + 3:
        raise GateError("sealed corpus inventory differs")
    result = {"schema_version": 1, "item_id": "BINDER-MODEL-PILOT-1",
              "scientific_manifest_sha256": sha(SCIENCE),
              "execution_manifest_sha256": sha(EXECUTION),
              "source_attempt": attempt, "files": rows}
    write_new(CORPUS_LOCK, result)
    return result


def check_corpus_lock() -> dict[str, Any]:
    execution = check_frozen_inputs()
    committed(CORPUS_LOCK)
    lock = read_json(CORPUS_LOCK)
    if lock["scientific_manifest_sha256"] != sha(SCIENCE) or lock["execution_manifest_sha256"] != sha(EXECUTION):
        raise GateError("corpus lock binding differs")
    check_bindings(lock["files"])
    if len(lock["files"]) != execution["batch_count"] + 3:
        raise GateError("corpus file count differs")
    adoption_replay = read_json(BASE / "corpus/adoption-replay.json")
    if (adoption_replay.get("status") != "PASS" or len(adoption_replay.get("rows", [])) != 4
            or adoption_replay.get("adoption_sha256") != sha(BASE / "selected-input-adoption.json")):
        raise GateError("adoption replay differs")
    from lib.binder_model_audit import audit_corpus
    if audit_corpus(BASE / "corpus/vectors.ndjson") != read_json(BASE / "corpus/audit.json"):
        raise GateError("sealed corpus audit differs")
    verify_batch_partition(BASE / "corpus/vectors.ndjson",
                           [BASE / f"corpus/batch-{i:02d}.ndjson" for i in range(execution["batch_count"])])
    return lock
