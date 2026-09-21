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

from lib.research_queue import ROOT
from lib.research_queue_v2 import validate_queue as validate_v2
from lib.research_queue_v3 import _review, handoff_status

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
            if not isinstance(original.get("budget"), dict):
                raise ValueError("completed historical items must retain their original budget record")
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
    _review(data, root, digest_function=queue_digest)
    if require_ready and handoff_status(data) == "PAUSED":
        raise ValueError("queue is PAUSED; no executable item; " + data["handoff"]["required_decision"])


def load_queue(root: Path = ROOT, *, require_ready: bool = False) -> dict[str, Any]:
    from lib.research_queue_v3 import load_queue as load_current
    data = load_current(root, require_ready=require_ready)
    if data["schema_version"] != 4:
        raise ValueError("current queue is not schema v4")
    return data
