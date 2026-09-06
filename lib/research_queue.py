"""Validation for the bounded, ranked local research queue.

The queue records work selection; it does not authorize experiments or assess
scientific merit.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
KINDS = {
    "LITERATURE", "CONTRACT", "PROOF", "IMPLEMENTATION", "CONTRIBUTION",
    "MAINTENANCE", "EXPERIMENT", "OPERATIONS",
}
STATUSES = {"READY", "ACTIVE", "PLANNED", "WAITING", "DEFERRED", "COMPLETE"}
OUTCOMES = {"SUCCESS", "NEGATIVE", "BOUNDED_UNRESOLVED", "SUPERSEDED"}
ITEM_FIELDS = {
    "id", "priority", "title", "target", "action", "expected_value",
    "rank_rationale", "entry_gate", "completion", "stop_condition", "kind",
    "status", "depends_on", "budget", "evidence_refs", "issue_urls",
    "closure", "blocked_reason",
}


def _required_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value


def _safe_file(root: Path, value: Any, label: str) -> Path:
    path = Path(_required_string(value, label))
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{label} must be a safe relative path")
    candidate = root / path
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as error:
        raise ValueError(f"{label} is missing or escapes the repository: {value}") from error
    if not resolved.is_file():
        raise ValueError(f"{label} must name an existing file: {value}")
    return resolved


def _list_of_files(root: Path, value: Any, label: str) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a nonempty list")
    if not all(isinstance(reference, str) for reference in value):
        raise ValueError(f"{label} must contain only path strings")
    if len(set(value)) != len(value):
        raise ValueError(f"{label} must not contain duplicates")
    for index, reference in enumerate(value):
        _safe_file(root, reference, f"{label}[{index}]")


def _valid_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _active_section(status_path: Path) -> str:
    if not status_path.is_file():
        raise ValueError("docs/RESEARCH_STATUS.md is missing")
    active = False
    lines: list[str] = []
    for line in status_path.read_text(encoding="utf-8").splitlines():
        if line == "### Active":
            active = True
            continue
        if active and line.startswith("### "):
            break
        if active:
            lines.append(line)
    if not active:
        raise ValueError("docs/RESEARCH_STATUS.md has no Active section")
    return "\n".join(lines)


def _validate_item(item: Any, root: Path, index: int) -> None:
    label = f"items[{index}]"
    if not isinstance(item, dict) or set(item) != ITEM_FIELDS:
        raise ValueError(f"{label} has invalid fields")
    for name in (
        "id", "title", "target", "action", "expected_value", "rank_rationale",
        "entry_gate", "completion", "stop_condition",
    ):
        _required_string(item[name], f"{label}.{name}")
    if not isinstance(item["priority"], int) or isinstance(item["priority"], bool):
        raise ValueError(f"{label}.priority must be an integer")
    if not isinstance(item["kind"], str) or item["kind"] not in KINDS:
        raise ValueError(f"{label}.kind is invalid")
    if not isinstance(item["status"], str) or item["status"] not in STATUSES:
        raise ValueError(f"{label}.status is invalid")
    if not isinstance(item["depends_on"], list) or not all(isinstance(x, str) and x for x in item["depends_on"]):
        raise ValueError(f"{label}.depends_on must be a list of IDs")
    if len(set(item["depends_on"])) != len(item["depends_on"]):
        raise ValueError(f"{label}.depends_on contains duplicates")
    budget = item["budget"]
    if not isinstance(budget, dict) or set(budget) != {"max_sessions", "session_minutes", "checker_launches"}:
        raise ValueError(f"{label}.budget has invalid fields")
    for name, minimum in (("max_sessions", 1), ("session_minutes", 1), ("checker_launches", 0)):
        value = budget[name]
        if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
            raise ValueError(f"{label}.budget.{name} is invalid")
    _list_of_files(root, item["evidence_refs"], f"{label}.evidence_refs")
    if not isinstance(item["issue_urls"], list) or not all(_valid_url(url) for url in item["issue_urls"]):
        raise ValueError(f"{label}.issue_urls must be HTTP(S) URLs")
    if not isinstance(item["blocked_reason"], str):
        raise ValueError(f"{label}.blocked_reason must be a string")
    if item["status"] in {"WAITING", "DEFERRED"} and not item["blocked_reason"].strip():
        raise ValueError(f"{label}.blocked_reason is required")
    closure = item["closure"]
    if item["status"] != "COMPLETE":
        if closure is not None:
            raise ValueError(f"{label}.closure must be null until COMPLETE")
        return
    if not isinstance(closure, dict) or set(closure) != {"outcome", "evidence_refs", "recommendation"}:
        raise ValueError(f"{label}.closure has invalid fields")
    if not isinstance(closure["outcome"], str) or closure["outcome"] not in OUTCOMES:
        raise ValueError(f"{label}.closure.outcome is invalid")
    _list_of_files(root, closure["evidence_refs"], f"{label}.closure.evidence_refs")
    _required_string(closure["recommendation"], f"{label}.closure.recommendation")


def validate_queue(data: Any, root: Path = ROOT) -> None:
    """Raise ValueError unless *data* is a coherent bounded research queue."""
    root = Path(root).resolve()
    required = {"schema_version", "frontier_id", "plan", "updated_at", "selected_item", "items"}
    if (
        not isinstance(data, dict)
        or set(data) != required
        or not isinstance(data.get("schema_version"), int)
        or isinstance(data["schema_version"], bool)
        or data["schema_version"] != 1
    ):
        raise ValueError("invalid research queue fields or schema_version")
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


def load_queue(root: Path = ROOT) -> dict[str, Any]:
    """Load and validate ``config/research-queue.json`` below *root*."""
    root = Path(root).resolve()
    path = root / "config" / "research-queue.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"could not load research queue: {error}") from error
    validate_queue(data, root)
    return data
