"""Project-wide, evidence-bound stopping-point review for research queue v3.

This successor checks recorded scope, bindings and selection consistency. It
does not prove scientific merit, priority judgments or execution authority.
Version 1 and 2 queues retain their original validator semantics.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from lib.research_queue import ROOT, _required_string, _safe_file
from lib.research_queue_v2 import validate_queue as validate_v2

CATEGORIES = {
    "METHODS_AND_FRONTIERS", "UNRESOLVED_AND_SHARED_ASSETS",
    "MAINTENANCE_AND_UPSTREAM", "LITERATURE_AND_REUSE", "LOCAL_BLOCKER_REMOVAL",
}
BLOCKERS = {
    "EXTERNAL_AUTHORIZATION", "EXTERNAL_INPUT", "TECHNICAL_CAPABILITY",
    "SCIENTIFIC_GATE", "BUDGET", "NO_USEFUL_BOUNDED_QUESTION",
}
REVIEW_FIELDS = {
    "schema_version", "scope", "phase", "reviewed_at", "stopped_item",
    "selected_item", "queue_sha256", "decision", "categories", "candidates",
    "evidence_bindings",
}


def _fields(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError(f"{label} has invalid fields")
    return value


def _digest(value: Any, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError(f"{label} must be a lowercase SHA-256")
    return value


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in pairs:
        if name in result:
            raise ValueError(f"duplicate JSON key: {name}")
        result[name] = value
    return result


def _nonfinite(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"),
                          object_pairs_hook=_unique_object, parse_constant=_nonfinite)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"could not load {path}: {error}") from error


def queue_digest(data: dict[str, Any]) -> str:
    """Bind the full queue except its reference to this review (no hash cycle)."""
    payload = {name: value for name, value in data.items() if name != "strategic_review"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode("utf-8")).hexdigest()


def handoff_status(data: dict[str, Any]) -> str:
    return data["handoff"]["status"] if data["schema_version"] in {2, 3} else "EXECUTABLE"


def _review(data: dict[str, Any], root: Path) -> None:
    binding = _fields(data["strategic_review"], {"path", "sha256"}, "strategic_review")
    path = _safe_file(root, binding["path"], "strategic_review.path")
    if hashlib.sha256(path.read_bytes()).hexdigest() != _digest(binding["sha256"], "strategic_review.sha256"):
        raise ValueError("strategic review hash mismatch")
    review = _fields(_json(path), REVIEW_FIELDS, "strategic review")
    if type(review["schema_version"]) is not int or review["schema_version"] != 1:
        raise ValueError("invalid strategic review schema_version")
    if review["scope"] != "PROJECT_WIDE":
        raise ValueError("strategic review must cover PROJECT_WIDE opportunities")
    if review["phase"] not in ("ENTRY", "CLOSURE"):
        raise ValueError("invalid strategic review phase")
    if review["reviewed_at"] != data["updated_at"]:
        raise ValueError("strategic review date does not match queue")
    if _digest(review["queue_sha256"], "queue_sha256") != queue_digest(data):
        raise ValueError("strategic review queue binding is stale")
    if review["selected_item"] != data["selected_item"]:
        raise ValueError("strategic review selected_item disagrees with queue")
    _required_string(review["decision"], "strategic review decision")
    by_id = {item["id"]: item for item in data["items"]}
    if review["phase"] == "ENTRY":
        if review["stopped_item"] is not None:
            raise ValueError("ENTRY review must not claim a stopped item")
        if by_id[data["selected_item"]]["status"] != "ACTIVE":
            raise ValueError("ENTRY review requires an ACTIVE item; handoff requires CLOSURE review")
    else:
        stopped = review["stopped_item"]
        if not isinstance(stopped, str) or stopped not in by_id or by_id[stopped]["status"] != "COMPLETE":
            raise ValueError("CLOSURE review must name a completed stopped item")
        if any(item["status"] == "ACTIVE" for item in data["items"]):
            raise ValueError("CLOSURE review selects the next item without starting it")

    evidence = review["evidence_bindings"]
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("strategic review requires evidence bindings")
    bound: set[str] = set()
    for row in evidence:
        _fields(row, {"path", "sha256"}, "evidence binding")
        source = _safe_file(root, row["path"], "evidence binding path")
        if row["path"] in bound:
            raise ValueError("duplicate evidence binding")
        bound.add(row["path"])
        if hashlib.sha256(source.read_bytes()).hexdigest() != _digest(row["sha256"], "evidence sha256"):
            raise ValueError(f"strategic evidence hash mismatch: {row['path']}")
    if not {"CONSTITUTION.md", "docs/RESEARCH_WORKFLOW.md", data["plan"]}.issubset(bound):
        raise ValueError("strategic review must bind constitution, workflow and current plan")

    def refs(value: Any, label: str) -> set[str]:
        if (not isinstance(value, list) or not value
            or not all(isinstance(ref, str) for ref in value)
            or len(set(value)) != len(value) or not set(value).issubset(bound)):
            raise ValueError(f"{label} must contain unique bound evidence paths")
        return set(value)

    candidates = review["candidates"]
    if not isinstance(candidates, list) or len(candidates) < 2:
        raise ValueError("strategic review must compare at least two concrete candidates")
    considered: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        _fields(candidate, {"item_id", "disposition", "rationale", "evidence_refs", "blockers"}, "candidate")
        item_id = _required_string(candidate["item_id"], "candidate.item_id")
        if item_id not in by_id or by_id[item_id]["status"] == "COMPLETE" or item_id in considered:
            raise ValueError("candidate must name one unique unfinished queue item")
        considered[item_id] = candidate
        _required_string(candidate["rationale"], "candidate.rationale")
        if not refs(candidate["evidence_refs"], "candidate.evidence_refs").intersection(by_id[item_id]["evidence_refs"]):
            raise ValueError("candidate must bind its queue evidence")
        status = by_id[item_id]["status"]
        allowed = {"FEASIBLE": {"READY", "ACTIVE"}, "BLOCKED": {"WAITING", "PLANNED", "DEFERRED"}, "DEFERRED": {"DEFERRED"}}
        disposition = candidate["disposition"]
        if not isinstance(disposition, str) or disposition not in allowed or status not in allowed[disposition]:
            raise ValueError("candidate disposition disagrees with queue status")
        blockers = candidate["blockers"]
        if not isinstance(blockers, list):
            raise ValueError("candidate.blockers must be a list")
        if (disposition == "BLOCKED") != bool(blockers):
            raise ValueError("only BLOCKED candidates require nonempty blockers")
        for blocker in blockers:
            _fields(blocker, {"kind", "reason", "evidence_refs"}, "blocker")
            if not isinstance(blocker["kind"], str) or blocker["kind"] not in BLOCKERS:
                raise ValueError("invalid blocker kind; plan exhaustion alone is not a blocker")
            _required_string(blocker["reason"], "blocker.reason")
            refs(blocker["evidence_refs"], "blocker.evidence_refs")
    executable = {item["id"] for item in data["items"] if item["status"] in {"READY", "ACTIVE"}}
    if not (executable | {data["selected_item"]}).issubset(considered):
        raise ValueError("strategic review omits selected or executable queue candidates")

    categories = review["categories"]
    if not isinstance(categories, list):
        raise ValueError("strategic review categories must be a list")
    coverage: dict[str, list[str]] = {}
    for category in categories:
        _fields(category, {"category", "assessment", "candidate_ids"}, "category")
        name = category["category"]
        if not isinstance(name, str) or name not in CATEGORIES or name in coverage:
            raise ValueError("strategic review has an invalid or duplicate category")
        _required_string(category["assessment"], "category.assessment")
        ids = category["candidate_ids"]
        if (not isinstance(ids, list) or not all(isinstance(value, str) for value in ids)
            or len(set(ids)) != len(ids) or not set(ids).issubset(considered)):
            raise ValueError("category must reference unique assessed candidates")
        coverage[name] = ids
    if set(coverage) != CATEGORIES:
        raise ValueError("strategic review omits a project-wide category")
    if set().union(*(set(ids) for ids in coverage.values())) != set(considered):
        raise ValueError("strategic review contains an uncategorized candidate")
    if handoff_status(data) == "PAUSED":
        if considered[data["selected_item"]]["disposition"] != "BLOCKED":
            raise ValueError("PAUSED selection must have evidence-bound blockers")
        if any(considered[item_id]["disposition"] != "BLOCKED" for item_id in coverage["LOCAL_BLOCKER_REMOVAL"]):
            raise ValueError("PAUSED review must document blockers to local blocker-removal work")


def validate_queue(data: Any, root: Path = ROOT, *, require_ready: bool = False) -> None:
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 3:
        validate_v2(data, root, require_ready=require_ready)
        return
    root = Path(root).resolve()
    if "strategic_review" not in data:
        raise ValueError("v3 queue requires a strategic_review binding")
    predecessor = {name: value for name, value in data.items() if name != "strategic_review"}
    predecessor["schema_version"] = 2
    validate_v2(predecessor, root, require_ready=False)
    _review(data, root)
    if require_ready and handoff_status(data) == "PAUSED":
        raise ValueError("queue is PAUSED; no executable item; " + data["handoff"]["required_decision"])


def load_queue(root: Path = ROOT, *, require_ready: bool = False) -> dict[str, Any]:
    root = Path(root).resolve()
    path = root / "config" / "research-queue.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"could not load research queue: {error}") from error
    if isinstance(data, dict) and type(data.get("schema_version")) is int and data["schema_version"] == 3:
        data = _json(path)
    validate_queue(data, root, require_ready=require_ready)
    return data
