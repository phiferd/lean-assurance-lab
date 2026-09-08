"""Version 2 research queue integrity and explicit non-operational handoffs.

This is an explicit successor to the byte-preserved version 1 validator used by
historical scientific tooling. Version 1 records retain their original rules.
"""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import Any

from lib.research_queue import (
    ROOT, _active_section, _list_of_files, _required_string, _safe_file,
    _validate_item, validate_queue as validate_v1,
)


def handoff_status(data: dict[str, Any]) -> str:
    """Return the execution state of an already validated queue.

    Version 1 always requires an executable item. Version 2 explicitly records
    a pause without converting a blocked item into execution authorization.
    """
    return data["handoff"]["status"] if data["schema_version"] == 2 else "EXECUTABLE"


def validate_queue(data: Any, root: Path = ROOT, *, require_ready: bool = False) -> None:
    """Raise ValueError unless *data* is a coherent bounded research queue."""
    if isinstance(data, dict) and type(data.get("schema_version")) is int and data["schema_version"] == 1:
        validate_v1(data, root)
        return
    root = Path(root).resolve()
    required = {"schema_version", "frontier_id", "plan", "updated_at", "selected_item", "items"}
    if (not isinstance(data, dict)
        or not isinstance(data.get("schema_version"), int)
        or isinstance(data["schema_version"], bool)
        or data["schema_version"] not in {1, 2}
    ):
        raise ValueError("invalid research queue fields or schema_version")
    if data["schema_version"] == 2:
        required.add("handoff")
    if set(data) != required:
        raise ValueError("invalid research queue fields or schema_version")
    if data["schema_version"] == 2:
        handoff = data["handoff"]
        if (not isinstance(handoff, dict)
            or set(handoff) != {"status", "reason", "required_decision", "evidence_refs"}
            or not isinstance(handoff["status"], str)
            or handoff["status"] not in {"EXECUTABLE", "PAUSED"}
        ):
            raise ValueError("invalid handoff fields or status")
        if handoff["status"] == "PAUSED":
            _required_string(handoff["reason"], "handoff.reason")
            _required_string(handoff["required_decision"], "handoff.required_decision")
            _list_of_files(root, handoff["evidence_refs"], "handoff.evidence_refs")
        elif any(handoff[name] != "" for name in ("reason", "required_decision")) or handoff["evidence_refs"] != []:
            raise ValueError("EXECUTABLE handoff must not retain pause fields")
    _required_string(data["frontier_id"], "frontier_id")
    _safe_file(root, data["plan"], "plan")
    try:
        dt.date.fromisoformat(_required_string(data["updated_at"], "updated_at"))
    except ValueError as error:
        raise ValueError("updated_at must be an ISO date") from error
    _required_string(data["selected_item"], "selected_item")
    items = data["items"]
    if not isinstance(items, list) or not items:
        raise ValueError("items must be a nonempty list")
    for index, item in enumerate(items):
        _validate_item(item, root, index)
    ids = [item["id"] for item in items]
    if len(set(ids)) != len(ids):
        raise ValueError("item IDs must be unique")
    priorities = [item["priority"] for item in items]
    if set(priorities) != set(range(1, len(items) + 1)):
        raise ValueError("priorities must be unique and contiguous from 1")
    by_id = {item["id"]: item for item in items}
    for item in items:
        for dependency in item["depends_on"]:
            if dependency not in by_id:
                raise ValueError(f"unknown dependency {dependency} for {item['id']}")
            if dependency == item["id"]:
                raise ValueError(f"item {item['id']} cannot depend on itself")

    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(item_id: str) -> None:
        if item_id in visiting:
            raise ValueError(f"dependency cycle at {item_id}")
        if item_id in visited:
            return
        visiting.add(item_id)
        for dependency in by_id[item_id]["depends_on"]:
            visit(dependency)
        visiting.remove(item_id)
        visited.add(item_id)
    for item_id in by_id:
        visit(item_id)

    def eligible(item: dict[str, Any]) -> bool:
        return all(
            by_id[dependency]["status"] == "COMPLETE"
            and by_id[dependency]["closure"]["outcome"] == "SUCCESS"
            for dependency in item["depends_on"]
        )

    active = [item for item in items if item["status"] == "ACTIVE"]
    if len(active) > 1:
        raise ValueError("at most one ACTIVE item is allowed")
    executable = [item for item in items if item["status"] in {"READY", "ACTIVE"}]
    for item in executable:
        if not eligible(item):
            raise ValueError(f"{item['status']} item {item['id']} has unmet dependencies")
    paused = handoff_status(data) == "PAUSED"
    if paused:
        if executable:
            raise ValueError("PAUSED queue must have no READY or ACTIVE item")
        candidates = [item for item in items if item["status"] in {"WAITING", "DEFERRED"}]
        if not candidates:
            raise ValueError("PAUSED queue requires a WAITING or DEFERRED decision item")
        expected = min(candidates, key=lambda item: item["priority"])
    else:
        candidates = active or [item for item in items if item["status"] == "READY" and eligible(item)]
        if not candidates:
            raise ValueError("queue has no eligible READY or ACTIVE item")
        expected = active[0] if active else min(candidates, key=lambda item: item["priority"])
    if data["selected_item"] != expected["id"]:
        raise ValueError(f"selected_item must be {expected['id']}")
    active_text = _active_section(root / "docs" / "RESEARCH_STATUS.md")
    for value, label in ((data["frontier_id"], "frontier_id"), (data["plan"], "plan")):
        if value not in active_text:
            raise ValueError(f"Active status section does not contain queue {label}: {value}")
    marker = rf"^Selected next item: `{re.escape(data['selected_item'])}`\.$"
    if not re.search(marker, active_text, flags=re.MULTILINE):
        raise ValueError("Active status section does not contain the selected-item marker")
    if data["schema_version"] == 2:
        markers = re.findall(r"^Queue handoff: (.+)\.$", active_text, flags=re.MULTILINE)
        if markers != [handoff_status(data)]:
            raise ValueError("Active status section does not contain the matching queue-handoff marker")
    if require_ready and paused:
        raise ValueError("queue is PAUSED; no executable item; " + data["handoff"]["required_decision"])


def load_queue(root: Path = ROOT, *, require_ready: bool = False) -> dict[str, Any]:
    """Load and validate ``config/research-queue.json`` below *root*."""
    root = Path(root).resolve()
    path = root / "config" / "research-queue.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"could not load research queue: {error}") from error
    validate_queue(data, root, require_ready=require_ready)
    return data
