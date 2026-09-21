"""Persistent-execution research queue policy.

Version 4 removes attempt/session/build/checker budgets from unfinished work.
Historical completed records retain their original budget objects and semantics.
Per-process safety controls belong in item protocols and cannot terminate work.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from lib import research_queue_v3
from lib.research_queue import ROOT
from lib.research_queue_v2 import validate_queue as validate_v2
from lib.research_queue_v3 import _json, _review

_LEGACY_LOAD_QUEUE = research_queue_v3.load_queue
_LEGACY_HANDOFF_STATUS = research_queue_v3.handoff_status

POLICY = {
    "engineering_failures": "REPAIR_AND_CONTINUE",
    "attempt_caps": "NONE",
    "accounting": "OBSERVABILITY_ONLY",
    "process_safety_limits": "NONTERMINAL_PER_PROCESS_CONTROLS",
    "terminal_conditions": [
        "SCIENTIFIC_QUESTION_ANSWERED",
        "OWNER_STOP",
        "REQUIRED_EXTERNAL_AUTHORITY_OR_INPUT_UNAVAILABLE",
        "SCIENTIFIC_INPUT_INVALIDATED",
        "REQUIRED_CAPABILITY_UNAVAILABLE_AFTER_FEASIBLE_REPAIRS",
    ],
}


def handoff_status(data: dict[str, Any]) -> str:
    if data["schema_version"] == 4:
        return data["handoff"]["status"]
    return _LEGACY_HANDOFF_STATUS(data)


def queue_digest(data: dict[str, Any]) -> str:
    """Bind the full v4 queue except its reference to the strategic review."""
    payload = {name: value for name, value in data.items() if name != "strategic_review"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode("utf-8")).hexdigest()


def validate_queue(data: Any, root: Path = ROOT, *, require_ready: bool = False) -> None:
    root = Path(root).resolve()
    required = {
        "schema_version", "frontier_id", "plan", "updated_at", "selected_item",
        "items", "handoff", "strategic_review", "execution_policy",
    }
    if (not isinstance(data, dict) or set(data) != required
        or type(data.get("schema_version")) is not int or data["schema_version"] != 4):
        raise ValueError("invalid v4 research queue fields or schema_version")
    if data["execution_policy"] != POLICY:
        raise ValueError("v4 execution_policy must prohibit terminal attempt budgets")

    predecessor = copy.deepcopy(data)
    predecessor.pop("strategic_review")
    predecessor.pop("execution_policy")
    predecessor["schema_version"] = 2
    for index, item in enumerate(predecessor["items"]):
        original = data["items"][index]
        if original.get("status") == "COMPLETE":
            if original.get("budget") is None:
                item["budget"] = {"max_sessions": 1, "session_minutes": 1, "checker_launches": 0}
            elif not isinstance(original.get("budget"), dict):
                raise ValueError("completed items must retain a historical budget object or a v4 null budget")
        else:
            if original.get("budget") is not None:
                raise ValueError("unfinished v4 items must not have an attempt budget")
            item["budget"] = {"max_sessions": 1, "session_minutes": 1, "checker_launches": 0}
    validate_v2(predecessor, root, require_ready=False)
    review_path = root / data["strategic_review"]["path"]
    try:
        review = json.loads(review_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"could not inspect v4 strategic review: {error}") from error
    if any(blocker.get("kind") == "BUDGET"
           for candidate in review.get("candidates", [])
           for blocker in candidate.get("blockers", [])):
        raise ValueError("v4 strategic review cannot use an attempt budget as a blocker")
    _review(data, root)
    if handoff_status(data) == "PAUSED":
        by_id = {row["item_id"]: row for row in review["candidates"]}
        if by_id[data["selected_item"]]["disposition"] != "BLOCKED":
            raise ValueError("PAUSED v4 selection must have evidence-bound blockers")
        local = next(row for row in review["categories"]
                     if row["category"] == "LOCAL_BLOCKER_REMOVAL")
        if any(by_id[item_id]["disposition"] != "BLOCKED" for item_id in local["candidate_ids"]):
            raise ValueError("PAUSED v4 review must document blockers to local blocker-removal work")
    if require_ready and handoff_status(data) == "PAUSED":
        raise ValueError("queue is PAUSED; no executable item; " + data["handoff"]["required_decision"])


def load_queue(root: Path = ROOT, *, require_ready: bool = False) -> dict[str, Any]:
    root = Path(root).resolve()
    data = _json(root / "config" / "research-queue.json")
    if data.get("schema_version") == 4:
        validate_queue(data, root, require_ready=require_ready)
        return data
    return _LEGACY_LOAD_QUEUE(root, require_ready=require_ready)


# Some historical modules import the frozen v3 path as their live queue entry
# point. Keep the v3 source bytes unchanged while making those later imports
# schema-compatible. Legacy schemas still execute the captured v3 loader.
research_queue_v3.load_queue = load_queue
