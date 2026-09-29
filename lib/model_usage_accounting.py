"""Privacy-preserving aggregate accounting for retained local Codex responses.

The extractor allowlists metadata and numeric usage fields. It never copies
prompts, messages, tool arguments, reasoning, or tool output into its result.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


USAGE_FIELDS = (
    "input_tokens", "cached_input_tokens", "cache_write_input_tokens",
    "output_tokens", "reasoning_output_tokens", "total_tokens",
)


class UsageError(ValueError):
    pass


def _sha(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise UsageError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _load_lines(path: Path) -> list[dict[str, Any]]:
    rows = []
    for number, raw in enumerate(path.read_bytes().splitlines(), 1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw, object_pairs_hook=_unique,
                               parse_constant=lambda token: (_ for _ in ()).throw(
                                   UsageError(f"non-finite JSON value: {token}")))
        except (UnicodeError, json.JSONDecodeError, UsageError) as error:
            raise UsageError(f"invalid JSONL at {path.name}:{number}: {error}") from error
        if type(value) is not dict:
            raise UsageError(f"non-object JSONL row at {path.name}:{number}")
        rows.append(value)
    return rows


def _usage(value: Any) -> dict[str, int]:
    if (type(value) is not dict or set(value) != set(USAGE_FIELDS)
            or any(type(value[name]) is not int or value[name] < 0 for name in USAGE_FIELDS)):
        raise UsageError("invalid response usage counters")
    if value["cached_input_tokens"] > value["input_tokens"]:
        raise UsageError("cached input exceeds total input")
    if value["total_tokens"] != value["input_tokens"] + value["output_tokens"]:
        raise UsageError("total token counter differs from input plus output")
    return {name: value[name] for name in USAGE_FIELDS}


def extract(paths: list[Path], *, root_turn_id: str, project_root: Path,
            observed_at: str | None = None) -> dict[str, Any]:
    if not root_turn_id:
        raise UsageError("root_turn_id is required")
    if not paths or len({path.resolve() for path in paths}) != len(paths):
        raise UsageError("source paths must be nonempty and unique")
    records: dict[str, dict[str, Any]] = {}
    duplicates = 0
    source_rows = []
    models: dict[str, dict[str, int]] = defaultdict(
        lambda: {name: 0 for name in (*USAGE_FIELDS, "uncached_input_tokens", "responses")})
    timestamps = []
    for path in sorted(paths, key=lambda item: item.name):
        raw = path.read_bytes()
        rows = _load_lines(path)
        metadata = [row.get("payload") for row in rows if row.get("type") == "session_meta"]
        if len(metadata) != 1 or type(metadata[0]) is not dict:
            raise UsageError(f"expected one session_meta row: {path.name}")
        meta = metadata[0]
        if (type(meta.get("cwd")) is not str
                or Path(meta["cwd"]).resolve() != project_root.resolve()):
            raise UsageError(f"session initial cwd is outside the selected project: {path.name}")
        thread_id = meta.get("id")
        if type(thread_id) is not str or not thread_id:
            raise UsageError(f"session metadata lacks an id: {path.name}")
        turn_models: dict[str, str] = {}
        for row in rows:
            if row.get("type") != "turn_context" or type(row.get("payload")) is not dict:
                continue
            payload = row["payload"]
            turn_id, model = payload.get("turn_id"), payload.get("model")
            if type(turn_id) is str and type(model) is str:
                if turn_id in turn_models and turn_models[turn_id] != model:
                    raise UsageError(f"conflicting model identity for turn {turn_id}")
                turn_models[turn_id] = model
        matched = 0
        for row in rows:
            if row.get("type") != "token_usage_record" or type(row.get("payload")) is not dict:
                continue
            payload = row["payload"]
            if payload.get("root_turn_id") != root_turn_id:
                continue
            response_id = payload.get("response_id")
            turn_id = payload.get("turn_id")
            timestamp = row.get("timestamp")
            if (type(response_id) is not str or not response_id or type(turn_id) is not str
                    or type(timestamp) is not str):
                raise UsageError("selected token record lacks response/turn/timestamp identity")
            usage = _usage(payload.get("usage"))
            record = {"turn_id": turn_id, "timestamp": timestamp,
                      "model": turn_models.get(turn_id), "usage": usage}
            previous = records.get(response_id)
            if previous is not None:
                if previous != record:
                    raise UsageError(f"conflicting duplicate response identity: {response_id}")
                duplicates += 1
                continue
            records[response_id] = record
            timestamps.append(timestamp)
            matched += 1
        source_rows.append({"file": path.name, "bytes": len(raw), "sha256": _sha(raw),
                            "thread_id": thread_id, "matched_responses": matched})
    if not records:
        raise UsageError("no response usage records matched root_turn_id")
    totals = {name: 0 for name in (*USAGE_FIELDS, "uncached_input_tokens")}
    missing_model = 0
    for record in records.values():
        usage = record["usage"]
        uncached = usage["input_tokens"] - usage["cached_input_tokens"]
        for name in USAGE_FIELDS:
            totals[name] += usage[name]
        totals["uncached_input_tokens"] += uncached
        model = record["model"] or "UNKNOWN"
        missing_model += record["model"] is None
        models[model]["responses"] += 1
        for name in USAGE_FIELDS:
            models[model][name] += usage[name]
        models[model]["uncached_input_tokens"] += uncached
    response_digest = _sha("\n".join(sorted(records)).encode())
    return {
        "schema_version": 1,
        "scope": "RETAINED_LOCAL_CODEX_RESPONSES_FOR_ONE_ROOT_TURN",
        "root_turn_id": root_turn_id,
        "observed_at": observed_at or datetime.now(timezone.utc).isoformat(),
        "source_files": source_rows,
        "responses": len(records),
        "duplicate_observations_deduplicated": duplicates,
        "response_ids_sha256": response_digest,
        "first_response_at": min(timestamps),
        "last_response_at": max(timestamps),
        "missing_model_records": missing_model,
        "totals": totals,
        "by_model": [{"model": model, **models[model]} for model in sorted(models)],
        "coverage": {
            "included": "Response-level usage records in the explicitly supplied retained local session files whose root_turn_id matches.",
            "excluded": "Other local or account sessions, non-Codex usage, any response written after the source-file observation, and any absent or deleted local record.",
            "cwd_limit": "Selection requires the session's initial cwd to equal the project root; later directory changes and mixed-purpose sessions are not inferred.",
            "cost_limit": "No price or monetary cost is inferred. Local records contain token counters, not authoritative billing attribution.",
            "privacy": "Only allowlisted identifiers, timestamps, file metadata, model names and numeric counters are retained; conversation and tool contents are never emitted."
        }
    }
