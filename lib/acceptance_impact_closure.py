"""Strict closure validation for ACCEPTANCE-IMPACT-PILOT-1.

The validator preserves the preregistered Stage-2 classification boundary.  It
must never turn the observed official application mismatch into a post-hoc
CONSEQUENTIAL or HARMLESS classification.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ITEM = "ACCEPTANCE-IMPACT-PILOT-1"
SUCCESSOR = "RECURSOR-TYPE-TRUST-BOUNDARY-1"
BOUNDARY = "CONSTRUCTION_OR_SEMANTIC_BOUNDARY"
BASE = Path("results/research/acceptance-impact-pilot-1")
OVERALL_RESULT = BASE / "result.json"
CLOSURE = BASE / "closure.json"
REPORT = BASE / "report.md"
WORK = BASE / "work-record.json"
PROTOCOL = BASE / "protocol.json"
QUEUE = Path("config/research-queue.json")
VALIDATOR = Path("scripts/validate-acceptance-impact-pilot-closure")
TEST = Path("tests/test_acceptance_impact_closure.py")

EXPECTED_CELLS = [
    {"ordinal": 1, "cell_id": "kiota-9fa2c297::control-use",
     "profile_id": "kiota-9fa2c297", "artifact_id": "control_use"},
    {"ordinal": 2, "cell_id": "kiota-9fa2c297::candidate-use",
     "profile_id": "kiota-9fa2c297", "artifact_id": "candidate_use"},
    {"ordinal": 3, "cell_id": "official-lean-4.33.0::control-use",
     "profile_id": "official-lean-4.33.0", "artifact_id": "control_use"},
    {"ordinal": 4, "cell_id": "official-lean-4.33.0::candidate-use",
     "profile_id": "official-lean-4.33.0", "artifact_id": "candidate_use"},
]
EXPECTED_MATRIX = {
    "kiota-9fa2c297::control-use": "ACCEPT",
    "kiota-9fa2c297::candidate-use": "ACCEPT",
    "official-lean-4.33.0::control-use": "ACCEPT",
    "official-lean-4.33.0::candidate-use": "INTENDED_RECURSOR_REJECT",
}
OBSERVED_MATRIX = {
    "kiota-9fa2c297::control-use": "ACCEPT",
    "kiota-9fa2c297::candidate-use": "ACCEPT",
    "official-lean-4.33.0::control-use": "ACCEPT",
    "official-lean-4.33.0::candidate-use": "SEMANTIC_REJECT",
}

FIXED_BINDINGS = {
    "candidate": {
        "path": "corpus/acceptance-impact-pilot-1/five-app-candidate.ndjson",
        "bytes": 7260,
        "sha256": "1b962a01f4e4a7af6046bc56f3f6f0a7d2ee44484e359f9bd3e1a95302689eb7",
    },
    "control": {
        "path": "corpus/acceptance-impact-pilot-1/five-app-control.ndjson",
        "bytes": 7260,
        "sha256": "362ed70d6561a15a21e214a184745140018526ce82f9c586f93d655be6c86286",
    },
    "artifact_audit": {
        "path": "results/research/acceptance-impact-pilot-1/stage-2-artifact-audit.json",
        "bytes": 6890,
        "sha256": "55576511780da56dda66a78de20d42d03b5124f233a59ecc6b046ba9848245e5",
    },
    "execution_manifest": {
        "path": "results/research/acceptance-impact-pilot-1/stage-2-execution-manifest.json",
        "bytes": 3428,
        "sha256": "169750cc9989efb0df165f7cefeb8f4e402b07eb511744d39a79074ad8c1312d",
    },
    "stage2_run": {
        "path": "results/research/acceptance-impact-pilot-1/stage-2-run-0001/result.json",
        "bytes": 9582,
        "sha256": "b967b13e481f781a97b365a8c3556cd1fa6fe5b1a2e5508f5840d56a77f10fbb",
    },
    "events": {
        "path": "results/research/acceptance-impact-pilot-1/stage-2-run-0001/events.jsonl",
        "bytes": 7346,
        "sha256": "0c342a6a106d565c0b49b1be2d12d31ccc16467694400d2a1f464860c4219d39",
    },
    "official_candidate_stderr": {
        "path": "results/research/acceptance-impact-pilot-1/stage-2-run-0001/raw/04-official-lean-4.33.0-candidate_use.stderr",
        "bytes": 343,
        "sha256": "ce7a9a7e2c744ef35487c26c7073c7088eb3c574554eecc81e4aec4480915f6f",
    },
}

EXPECTED_RESULT_PATHS = {
    "stage_1_result": "results/research/acceptance-impact-pilot-1/stage-1-run-0001/result.json",
    "consequence_contract": "results/research/acceptance-impact-pilot-1/consequence-contract.json",
    "tooling_manifest": "results/research/acceptance-impact-pilot-1/stage-2-tooling-manifest.json",
    "artifact_audit": FIXED_BINDINGS["artifact_audit"]["path"],
    "execution_manifest": FIXED_BINDINGS["execution_manifest"]["path"],
    "stage_2_run": FIXED_BINDINGS["stage2_run"]["path"],
    "candidate_use": FIXED_BINDINGS["candidate"]["path"],
    "control_use": FIXED_BINDINGS["control"]["path"],
    "official_candidate_stderr": FIXED_BINDINGS["official_candidate_stderr"]["path"],
}

EXACT_OFFICIAL_STDERR = (
    b"uncaught exception: while replaying declaration 'LALNest.rec_1_impact':\n"
    b"(kernel) application type mismatch\n"
    b"  @LALNest.rec_1 (fun t => LALNest) (fun t => LALNest) (fun children children_ih => children_ih)\n"
    b"    (fun value value_ih => value_ih) t\n"
    b"argument has type\n"
    b"  LALNest\n"
    b"but function has type\n"
    b"  (t : LALWrap LALNest) \xe2\x86\x92 (@fun t => LALNest) t\n"
)


class ClosureError(ValueError):
    """The frozen evidence or requested closure state is invalid."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ClosureError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs,
                           parse_constant=lambda token: (_ for _ in ()).throw(
                               ClosureError(f"non-finite JSON value: {token}")))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ClosureError(f"cannot load {path}: {error}") from error
    if not isinstance(value, dict):
        raise ClosureError(f"JSON root is not an object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _safe(root: Path, relative: Any) -> Path:
    if (not isinstance(relative, str) or not relative or Path(relative).is_absolute()
            or ".." in Path(relative).parts):
        raise ClosureError("path must be repository-relative")
    root = root.resolve()
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise ClosureError(f"path escapes repository: {relative}") from error
    return path


def binding(path: Path, root: Path) -> dict[str, Any]:
    root = root.resolve()
    path = path.resolve()
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError as error:
        raise ClosureError(f"file is outside repository: {path}") from error
    if not path.is_file() or path.is_symlink():
        raise ClosureError(f"missing or linked file: {relative}")
    return {"path": relative, "bytes": path.stat().st_size, "sha256": sha256(path)}


def verify_binding(root: Path, row: Any, *, expected_path: str | None = None) -> Path:
    if (not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}
            or type(row.get("bytes")) is not int or row["bytes"] < 0
            or not isinstance(row.get("sha256"), str)
            or re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is None):
        raise ClosureError("invalid file binding")
    if expected_path is not None and row["path"] != expected_path:
        raise ClosureError(f"binding path differs: {row['path']}")
    path = _safe(root, row["path"])
    if (not path.is_file() or path.is_symlink() or path.stat().st_size != row["bytes"]
            or sha256(path) != row["sha256"]):
        raise ClosureError(f"binding differs: {row['path']}")
    return path


def _fixed(root: Path, name: str) -> Path:
    return verify_binding(root, FIXED_BINDINGS[name],
                          expected_path=FIXED_BINDINGS[name]["path"])


def _committed(root: Path, paths: list[str]) -> None:
    for relative in paths:
        path = _safe(root, relative)
        completed = subprocess.run(
            ["git", "show", f"HEAD:{relative}"], cwd=root,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        if completed.returncode != 0 or completed.stdout != path.read_bytes():
            raise ClosureError(f"frozen evidence is not committed unchanged: {relative}")


def _safe_receipt(receipt: Any) -> None:
    if (not isinstance(receipt, dict) or receipt.get("timed_out") is not False
            or receipt.get("memory_exceeded") is not False
            or receipt.get("memory_monitor_error") is not None
            or type(receipt.get("memory_monitor_samples")) is not int
            or receipt["memory_monitor_samples"] <= 0
            or type(receipt.get("maximum_observed_rss_bytes")) is not int
            or receipt["maximum_observed_rss_bytes"] <= 0
            or receipt.get("cleanup_complete") is not True):
        raise ClosureError("unsafe or incomplete checker receipt")


def _raw(root: Path, receipt: dict[str, Any], stream: str) -> bytes:
    relative = receipt.get(f"raw_{stream}_path")
    path = _safe(root, relative)
    raw = path.read_bytes()
    if (len(raw) != receipt.get(f"{stream}_bytes")
            or hashlib.sha256(raw).hexdigest() != receipt.get(f"{stream}_sha256")):
        raise ClosureError(f"raw {stream} receipt differs")
    return raw


def validate_frozen_evidence(root: Path = ROOT, *, require_committed: bool = True) -> dict[str, Any]:
    root = Path(root).resolve()
    for name in FIXED_BINDINGS:
        _fixed(root, name)
    if require_committed:
        _committed(root, [row["path"] for row in FIXED_BINDINGS.values()])

    manifest = load_json(root / FIXED_BINDINGS["execution_manifest"]["path"])
    if (manifest.get("item_id") != ITEM or manifest.get("adaptive_search") is not False
            or manifest.get("cells") != EXPECTED_CELLS
            or manifest.get("expected_consequential_matrix") != EXPECTED_MATRIX
            or manifest.get("artifacts") != {
                "candidate_use": FIXED_BINDINGS["candidate"],
                "control_use": FIXED_BINDINGS["control"],
            }
            or manifest.get("audit_report") != FIXED_BINDINGS["artifact_audit"]):
        raise ClosureError("Stage-2 execution manifest differs")

    audit = load_json(root / FIXED_BINDINGS["artifact_audit"]["path"])
    structural = audit.get("structural_audit", {})
    domains = structural.get("cross_domain_distinction", {})
    if (audit.get("item_id") != ITEM or audit.get("current_checker_execution") is not False
            or structural.get("same_five_application_spine") is not True
            or domains.get("syntactically_distinct_rigid_heads") is not True
            or domains.get("counterfactual_tail_mismatch") != {
                "candidate_fifth_argument_domain": 28,
                "type_49_required_domain": 29,
                "control_fifth_argument_domain": 29,
                "type_68_required_domain": 28,
            }):
        raise ClosureError("independent artifact audit differs")

    run = load_json(root / FIXED_BINDINGS["stage2_run"]["path"])
    cells = run.get("cells")
    if (run.get("item_id") != ITEM or run.get("status") != "COMPLETE"
            or run.get("checker_attempts") != 4 or run.get("decision") != BOUNDARY
            or run.get("decision") in {"CONSEQUENTIAL_WITHIN_FIXED_USE",
                                       "HARMLESS_WITHIN_TESTED_USE"}
            or run.get("observed_matrix") != OBSERVED_MATRIX
            or not isinstance(cells, list) or len(cells) != 4
            or [row.get("cell") for row in cells] != EXPECTED_CELLS):
        raise ClosureError("Stage-2 result or boundary decision differs")

    process_seconds = 0.0
    events = []
    events_path = root / FIXED_BINDINGS["events"]["path"]
    for line in events_path.read_text(encoding="utf-8").splitlines():
        events.append(json.loads(line, object_pairs_hook=_pairs))
    if events != cells:
        raise ClosureError("Stage-2 event log differs from result cells")

    for expected_cell, row in zip(EXPECTED_CELLS, cells):
        if row.get("cell") != expected_cell:
            raise ClosureError("observed cell identity differs")
        artifact = (FIXED_BINDINGS["candidate"] if expected_cell["artifact_id"] == "candidate_use"
                    else FIXED_BINDINGS["control"])
        if row.get("artifact") != artifact:
            raise ClosureError("observed artifact binding differs")
        expected_outcome = OBSERVED_MATRIX[expected_cell["cell_id"]]
        if row.get("outcome") != expected_outcome:
            raise ClosureError("observed outcome differs")
        receipt = row.get("receipt")
        _safe_receipt(receipt)
        stdout, stderr = _raw(root, receipt, "stdout"), _raw(root, receipt, "stderr")
        process_seconds += receipt["elapsed_seconds"]
        if expected_outcome == "ACCEPT":
            if (expected_cell["profile_id"] == "kiota-9fa2c297"
                    and (receipt.get("exit_code") != 0 or stdout or stderr)):
                raise ClosureError("Kiota ACCEPT contract differs")
            if (expected_cell["profile_id"] == "official-lean-4.33.0"
                    and (receipt.get("exit_code") != 0 or stderr
                         or re.fullmatch(rb"Accepted [0-9]+ declarations[.]\n", stdout) is None)):
                raise ClosureError("official control ACCEPT contract differs")
        else:
            if (receipt.get("exit_code") != 1 or stdout or stderr != EXACT_OFFICIAL_STDERR
                    or row.get("reason") != "official semantic rejection outside the exact intended contract"):
                raise ClosureError("official candidate boundary diagnostic differs")
    if abs(process_seconds - run.get("process_seconds", -1)) > 1e-12:
        raise ClosureError("Stage-2 process accounting differs")
    if (root / FIXED_BINDINGS["official_candidate_stderr"]["path"]).read_bytes() \
            != EXACT_OFFICIAL_STDERR:
        raise ClosureError("exact 343-byte official candidate stderr differs")
    return {"manifest": manifest, "audit": audit, "run": run}


def _validate_overall_result(root: Path) -> dict[str, Any]:
    result = load_json(root / OVERALL_RESULT)
    if (result.get("schema_version") != 1 or result.get("item_id") != ITEM
            or result.get("status") != "COMPLETE" or result.get("outcome") != BOUNDARY
            or result.get("observed_matrix") != OBSERVED_MATRIX):
        raise ClosureError("overall result identity, outcome or matrix differs")
    if (result.get("frozen_expected_official_candidate") != "INTENDED_RECURSOR_REJECT"
            or result.get("falsified_expectation") != "OFFICIAL_REJECTS_BEFORE_APPENDED_USE"
            or result.get("adaptive_replacement") is not False
            or result.get("scientific_relaunches_after_observation") != 0
            or result.get("external_actions") != 0
            or not isinstance(result.get("conclusion"), str)
            or "cannot be promoted" not in result["conclusion"]
            or not isinstance(result.get("recommendation"), str)
            or SUCCESSOR not in result["recommendation"]):
        raise ClosureError("overall result boundary or non-adaptation state differs")
    bindings = result.get("evidence")
    if not isinstance(bindings, dict) or set(bindings) != set(EXPECTED_RESULT_PATHS):
        raise ClosureError("overall result binding roles differ")
    for role, expected_path in EXPECTED_RESULT_PATHS.items():
        verify_binding(root, bindings[role], expected_path=expected_path)
    support = result.get("scoped_support")
    limits = result.get("claim_limits")
    if (not isinstance(support, list) or not support
            or not isinstance(limits, list) or not limits
            or any(not isinstance(row, str) or not row for row in support + limits)):
        raise ClosureError("overall result support or limits are absent")
    support_text = " ".join(support)
    limits_text = " ".join(limits)
    for token in ("Kiota", "official", "LALNest.rec_1_impact", "LALWrap LALNest"):
        if token not in support_text:
            raise ClosureError(f"overall result support omits {token}")
    for token in ("not relabeled", "no external report"):
        if token not in limits_text.lower():
            raise ClosureError(f"overall result limits omit {token}")
    return result


def _validate_closure_and_report(root: Path) -> dict[str, Any]:
    closure = load_json(root / CLOSURE)
    required = {
        "schema_version", "item_id", "status", "outcome", "completion_boundary",
        "result", "report", "falsified_expectation", "post_hoc_promotion",
        "adaptive_replacement", "scientific_relaunches_after_observation",
        "external_actions", "successor",
    }
    if set(closure) != required:
        raise ClosureError("closure fields differ")
    if (closure.get("schema_version") != 1 or closure.get("item_id") != ITEM
            or closure.get("status") != "COMPLETE" or closure.get("outcome") != BOUNDARY
            or not isinstance(closure.get("completion_boundary"), str)
            or "fifth application" not in closure["completion_boundary"]
            or "preregistered" not in closure["completion_boundary"]
            or closure.get("result") != OVERALL_RESULT.as_posix()
            or closure.get("report") != REPORT.as_posix()
            or closure.get("falsified_expectation") != "OFFICIAL_REJECTS_BEFORE_APPENDED_USE"
            or closure.get("post_hoc_promotion") != "FORBIDDEN"
            or closure.get("adaptive_replacement") is not False
            or closure.get("scientific_relaunches_after_observation") != 0
            or closure.get("external_actions") != 0
            or closure.get("successor") != SUCCESSOR):
        raise ClosureError("closure boundary or non-adaptation state differs")
    report_path = root / REPORT
    if not report_path.is_file() or report_path.is_symlink():
        raise ClosureError("closure report is missing or linked")
    report = report_path.read_text(encoding="utf-8")
    required_text = (
        "CONSTRUCTION_OR_SEMANTIC_BOUNDARY",
        "INTENDED_RECURSOR_REJECT",
        "SEMANTIC_REJECT",
        "LALNest.rec_1_impact",
        "LALWrap LALNest",
        "ordering expectation",
        "Relabeling the item",
        "after seeing",
        "rerunning",
        "revised outcome rule",
        "No external report",
        SUCCESSOR,
    )
    for token in required_text:
        if token.lower() not in report.lower():
            raise ClosureError(f"closure report omits {token}")
    return closure


def _queue_digest(queue: dict[str, Any]) -> str:
    payload = {key: value for key, value in queue.items() if key != "strategic_review"}
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _validate_final_state(root: Path) -> None:
    work = load_json(root / WORK)
    if (work.get("item_id") != ITEM or work.get("status") != "COMPLETE"
            or work.get("current_phase") != "COMPLETE"
            or work.get("scientific_scope", {}).get("outcome_guided_replacement") is not False
            or work.get("authority", {}).get("external_writes") is not False
            or work.get("observations") != {
                "source_requests": 0,
                "build_attempts": 1,
                "checker_attempts": 8,
                "process_seconds": 17.952792873000362,
            }):
        raise ClosureError("final work-record state differs")
    closure_artifacts = {OVERALL_RESULT.as_posix(), CLOSURE.as_posix(), REPORT.as_posix()}
    validator_artifacts = {VALIDATOR.as_posix(), TEST.as_posix()}
    if not closure_artifacts.issubset(set(work.get("evidence_refs", []))):
        raise ClosureError("final work-record closure evidence is incomplete")
    protocol = load_json(root / PROTOCOL)
    if (protocol.get("item_id") != ITEM or protocol.get("status") != "COMPLETE"
            or protocol.get("current_phase") != "COMPLETE"
            or protocol.get("stage_2_observation", {}).get("observed_matrix") != OBSERVED_MATRIX
            or protocol.get("stage_2_observation", {}).get("decision") != BOUNDARY):
        raise ClosureError("final protocol state differs")

    queue = load_json(root / QUEUE)
    if (queue.get("schema_version") != 4 or queue.get("selected_item") != SUCCESSOR
            or queue.get("handoff", {}).get("status") != "EXECUTABLE"):
        raise ClosureError("final queue selection or handoff differs")
    items = queue.get("items")
    if not isinstance(items, list):
        raise ClosureError("final queue has no items")
    by_id = {row.get("id"): row for row in items if isinstance(row, dict)}
    item = by_id.get(ITEM)
    successor = by_id.get(SUCCESSOR)
    if (not isinstance(item, dict) or item.get("status") != "COMPLETE"
            or item.get("issue_urls") != [] or item.get("blocked_reason") != ""
            or not isinstance(item.get("closure"), dict)
            or item["closure"].get("outcome") != "BOUNDED_UNRESOLVED"
            or not isinstance(successor, dict) or successor.get("status") != "READY"
            or any(row.get("status") == "ACTIVE" for row in items if isinstance(row, dict))):
        raise ClosureError("final queue item or successor state differs")
    queue_refs = set(item.get("evidence_refs", []))
    closure_refs = set(item["closure"].get("evidence_refs", []))
    if not (closure_artifacts | validator_artifacts).issubset(closure_refs):
        raise ClosureError("final queue closure evidence is incomplete")
    recommendation = item["closure"].get("recommendation")
    if (not isinstance(recommendation, str) or SUCCESSOR not in recommendation
            or "external action" not in recommendation.lower()
            or not any(token in recommendation.lower() for token in ("relabel", "promot"))):
        raise ClosureError("final queue recommendation differs")
    review_binding = queue.get("strategic_review")
    review_path = verify_binding(root, {**review_binding,
                                        "bytes": (root / review_binding["path"]).stat().st_size},
                                 expected_path=review_binding.get("path")) \
        if isinstance(review_binding, dict) and set(review_binding) == {"path", "sha256"} \
        else None
    if review_path is None:
        raise ClosureError("final queue strategic-review binding differs")
    review = load_json(review_path)
    if (review.get("phase") != "CLOSURE" or review.get("stopped_item") != ITEM
            or review.get("selected_item") != SUCCESSOR
            or review.get("queue_sha256") != _queue_digest(queue)):
        raise ClosureError("final strategic review differs")


def validate(root: Path = ROOT, *, require_committed: bool = True) -> dict[str, Any]:
    root = Path(root).resolve()
    validate_frozen_evidence(root, require_committed=require_committed)
    _validate_overall_result(root)
    closure = _validate_closure_and_report(root)
    _validate_final_state(root)
    return {
        "schema_version": 1,
        "item_id": ITEM,
        "status": "PASS",
        "outcome": closure["outcome"],
        "observed_matrix": OBSERVED_MATRIX,
        "scientific_relaunches_after_observation": 0,
        "external_actions": 0,
        "successor": SUCCESSOR,
    }
