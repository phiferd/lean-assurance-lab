"""Mechanical integrity checks for the bounded CVC-1 reuse assessment.

This validator checks accounting, identity, and local content bindings.  It
does not establish the truth of a cited source, observe a search operation, or
prove transitive dependencies of an external formalization.  Offline hashes of
remote material are retrieval receipts, not remote-source authenticity proofs;
only the recorded excerpts and local artifact bindings are checked here.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from fnmatch import fnmatch
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CVC_DIR = Path("results/research/conditional-validation-contracts/cvc-1")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
TERMINAL = {"COMPLETE", "FAILED", "INACCESSIBLE"}
LIMITS = {
    "max_sessions": 3, "session_minutes": 90, "search_queries": 18,
    "primary_sources": 12, "code_inspections": 6, "builds": 0,
    "checker_launches": 0, "toolchain_installs": 0,
}
FRAGMENTS = {"UNIVERSE_EXPRESSIONS", "RECURSOR_METADATA", "DECLARATION_IMPORT"}
FINAL_FILES = {"work-record.json", "assessment.json", "report.md", "source-excerpts.json"}


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"could not load {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _path(root: Path, value: Any, label: str) -> Path:
    if not _text(value):
        raise ValueError(f"{label}: expected a non-empty repository-relative path")
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"{label}: unsafe path {value!r}")
    resolved = (root / candidate).resolve()
    if root not in (resolved, *resolved.parents):
        raise ValueError(f"{label}: escapes repository")
    return resolved


def _time(value: Any, label: str) -> datetime:
    if not _text(value):
        raise ValueError(f"{label}: missing timestamp")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{label}: invalid timestamp") from error
    if result.tzinfo is None:
        raise ValueError(f"{label}: timestamp needs a timezone")
    return result.astimezone(timezone.utc)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _evidence_refs(root: Path, refs: Any, label: str) -> None:
    if not isinstance(refs, list) or not refs:
        raise ValueError(f"{label}: evidence_refs are required")
    for ref in refs:
        path = _path(root, ref, label)
        if not path.is_file():
            raise ValueError(f"{label}: unresolved evidence reference {ref}")


def _unique_rows(rows: Any, label: str) -> dict[Any, dict[str, Any]]:
    if not isinstance(rows, list):
        raise ValueError(f"{label}: expected list")
    found: dict[Any, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or not _text(row.get("id")) and not isinstance(row.get("id"), int):
            raise ValueError(f"{label}: every row needs an id")
        key = row["id"]
        if key in found:
            raise ValueError(f"{label}: duplicate id {key!r}")
        found[key] = row
    return found


def _validate_historical_inputs(root: Path, record: dict[str, Any]) -> None:
    commit = record.get("predecessor_commit")
    if not isinstance(commit, str) or not HEX40.fullmatch(commit):
        raise ValueError("work record: predecessor_commit must be a 40-hex revision")
    inputs = record.get("inputs")
    if not isinstance(inputs, list) or not inputs:
        raise ValueError("work record: inputs must be a non-empty list")
    seen: set[str] = set()
    for binding in inputs:
        if not isinstance(binding, dict) or set(binding) != {"path", "sha256"}:
            raise ValueError("work record: invalid input binding")
        path = binding["path"]
        _path(root, path, "input binding")
        if path in seen or not isinstance(binding["sha256"], str) or not HEX64.fullmatch(binding["sha256"]):
            raise ValueError("work record: duplicate or malformed input binding")
        seen.add(path)
        result = subprocess.run(
            ["git", "-C", str(root), "show", f"{commit}:{path}"],
            capture_output=True, check=False,
        )
        if result.returncode != 0 or hashlib.sha256(result.stdout).hexdigest() != binding["sha256"]:
            raise ValueError(f"work record: historical input changed or unavailable: {path}")


def _validate_ledger(root: Path, record: dict[str, Any]) -> tuple[set[str], dict[tuple[Any, str], str]]:
    if record.get("schema_version") != 1 or record.get("item_id") != "CVC-1" or record.get("status") != "COMPLETE":
        raise ValueError("work record: expected completed schema-1 CVC-1 ledger")
    limits = record.get("limits")
    if not isinstance(limits, dict) or set(limits) != set(LIMITS) or any(
        type(limits[key]) is not int or limits[key] != expected for key, expected in LIMITS.items()
    ):
        raise ValueError("work record: limits must equal the literal CVC-1 limits")
    _validate_historical_inputs(root, record)
    sessions = _unique_rows(record.get("sessions"), "sessions")
    if not sessions or len(sessions) > LIMITS["max_sessions"]:
        raise ValueError("sessions: count is outside CVC-1 bound")
    session_windows: dict[Any, tuple[datetime, datetime]] = {}
    active_total = 0.0
    for session_id, session in sessions.items():
        if not isinstance(session_id, int) or isinstance(session_id, bool):
            raise ValueError("sessions: ids must be integers")
        start, end = _time(session.get("started_at"), "session start"), _time(session.get("ended_at"), "session end")
        if end < start:
            raise ValueError("sessions: end precedes start")
        active = session.get("active_minutes")
        if not isinstance(active, (int, float)) or isinstance(active, bool) or not math.isfinite(active) or active < 0:
            raise ValueError("sessions: active_minutes must be non-negative")
        elapsed = (end - start).total_seconds() / 60
        if active + 1e-9 < elapsed or active > LIMITS["session_minutes"]:
            raise ValueError("sessions: active minutes do not conservatively cover elapsed time")
        session_windows[session_id] = (start, end)
        active_total += active
    cumulative = record.get("cumulative_active_minutes")
    if not isinstance(cumulative, (int, float)) or isinstance(cumulative, bool) or not math.isfinite(cumulative) or abs(cumulative - active_total) > 1e-9:
        raise ValueError("work record: cumulative_active_minutes must equal session total")

    def validate_reserved(rows: Any, label: str, limit: int) -> dict[Any, dict[str, Any]]:
        indexed = _unique_rows(rows, label)
        if len(indexed) > limit:
            raise ValueError(f"{label}: exceeds CVC-1 limit")
        for row in indexed.values():
            if row.get("status") not in TERMINAL:
                raise ValueError(f"{label}: every reservation needs a terminal status")
            session_id = row.get("session")
            if session_id not in session_windows:
                raise ValueError(f"{label}: reservation refers to unknown session")
            start, end = session_windows[session_id]
            reserved = _time(row.get("reserved_at"), f"{label} reservation")
            if not start <= reserved <= end:
                raise ValueError(f"{label}: reservation lies outside session")
            for key in ("completed_at", "failed_at", "inaccessible_at", "retrieved_at"):
                if key in row and row[key] is not None:
                    observed = _time(row[key], f"{label} {key}")
                    if not reserved <= observed <= end:
                        raise ValueError(f"{label}: {key} lies outside session")
        return indexed

    validate_reserved(record.get("queries"), "queries", LIMITS["search_queries"])
    sources = validate_reserved(record.get("sources"), "sources", LIMITS["primary_sources"])
    inspections = validate_reserved(record.get("code_inspections"), "code inspections", LIMITS["code_inspections"])
    for row in _unique_rows(record.get("queries"), "queries").values():
        if not _text(row.get("query")):
            raise ValueError("queries: query text is required")
    for row in sources.values():
        if not _text(row.get("url")) or not _text(row.get("question")):
            raise ValueError("sources: URL and question are required")
        if row["status"] == "COMPLETE":
            if row.get("source_kind") not in {"PAPER", "REPOSITORY_DOCUMENT"}:
                raise ValueError("sources: complete sources need a recognized source_kind")
            if not all(_text(row.get(key)) for key in ("version", "claim", "gap")):
                raise ValueError("sources: complete sources need version, claim, and gap")
            if not isinstance(row.get("assumptions"), list) or not all(_text(value) for value in row["assumptions"]):
                raise ValueError("sources: complete sources need assumptions strings")
            if not isinstance(row.get("reviewed_sections"), list) or not row["reviewed_sections"] or not all(_text(value) for value in row["reviewed_sections"]):
                raise ValueError("sources: complete sources need reviewed sections")
            if row["source_kind"] == "PAPER":
                identity = row.get("content_identity")
                if not isinstance(identity, dict) or set(identity) != {"url", "sha256", "bytes", "retrieved_at"} or not _text(identity["url"]) or not isinstance(identity["sha256"], str) or not HEX64.fullmatch(identity["sha256"]) or type(identity["bytes"]) is not int or identity["bytes"] < 0:
                    raise ValueError("sources: paper source needs content identity receipt")
                _time(identity["retrieved_at"], "source content identity retrieval")
    inspection_files: dict[tuple[Any, str], str] = {}
    for row in inspections.values():
        if not _text(row.get("repository")) or not isinstance(row.get("revision"), str) or not HEX40.fullmatch(row["revision"]):
            raise ValueError("code inspections: repository and pinned revision are required")
        if not _text(row.get("question")) or not isinstance(row.get("declared_file_group"), list) or not row["declared_file_group"]:
            raise ValueError("code inspections: question and declared file group are required")
        if row.get("source_id") not in sources:
            raise ValueError("code inspections: source_id must link to a ledger source")
        files = row.get("files")
        if not isinstance(files, list) or (not files and row["status"] == "COMPLETE"):
            raise ValueError("code inspections: files are required")
        file_paths: set[str] = set()
        repository = row["repository"].rstrip("/")
        match = re.fullmatch(r"https://github\.com/([^/]+)/([^/]+)", repository)
        if not match:
            raise ValueError("code inspections: repository must be a GitHub repository URL")
        raw_prefix = f"https://raw.githubusercontent.com/{match.group(1)}/{match.group(2)}/{row['revision']}/"
        for file in files:
            if not isinstance(file, dict) or not _text(file.get("path")) or not _text(file.get("url")):
                raise ValueError("code inspections: malformed file binding")
            if not isinstance(file.get("sha256"), str) or not HEX64.fullmatch(file["sha256"]):
                raise ValueError("code inspections: malformed file hash")
            if not isinstance(file.get("bytes"), int) or isinstance(file["bytes"], bool) or file["bytes"] < 0:
                raise ValueError("code inspections: malformed file size")
            if file["path"] in file_paths or not any(fnmatch(file["path"], pattern) for pattern in row["declared_file_group"]):
                raise ValueError("code inspections: file is duplicate or outside declared file group")
            if file["url"] != raw_prefix + file["path"]:
                raise ValueError("code inspections: raw GitHub URL must bind repository and revision")
            file_paths.add(file["path"])
            inspection_files[(row["id"], file["path"])] = file["sha256"]
    for source in sources.values():
        if source["status"] == "COMPLETE" and source["source_kind"] == "REPOSITORY_DOCUMENT":
            inspection_ids = source.get("code_inspection_ids")
            if not isinstance(inspection_ids, list) or not inspection_ids or len(set(inspection_ids)) != len(inspection_ids):
                raise ValueError("sources: repository source needs linked complete inspection")
            for inspection_id in inspection_ids:
                inspection = inspections.get(inspection_id)
                if inspection is None or inspection["status"] != "COMPLETE" or not inspection["files"]:
                    raise ValueError("sources: repository source inspection is incomplete")
    execution = record.get("execution_counts")
    zero_execution = {"builds", "checker_launches", "toolchain_installs"}
    if not isinstance(execution, dict) or set(execution) != zero_execution or any(type(execution[key]) is not int or execution[key] != 0 for key in zero_execution):
        raise ValueError("work record: CVC-1 permits no execution")
    return set(sources), inspection_files


def _validate_excerpts(root: Path, excerpts: dict[str, Any], inspection_files: dict[tuple[Any, str], str]) -> None:
    if excerpts.get("schema_version") != 1 or excerpts.get("item_id") != "CVC-1":
        raise ValueError("source excerpts: expected schema-1 CVC-1 artifact")
    rows = excerpts.get("excerpts")
    if not isinstance(rows, list) or not rows:
        raise ValueError("source excerpts: excerpts must be non-empty")
    seen: set[Any] = set()
    required = {"id", "inspection_id", "path", "source_sha256", "start_line", "end_line", "text", "sha256"}
    for row in rows:
        if not isinstance(row, dict) or set(row) != required or not _text(row.get("id")) or row["id"] in seen:
            raise ValueError("source excerpts: malformed or duplicate excerpt id")
        if (row.get("inspection_id"), row.get("path")) not in inspection_files or inspection_files[(row["inspection_id"], row["path"])] != row.get("source_sha256"):
            raise ValueError("source excerpts: excerpt does not bind an inspected file")
        if not all(type(row.get(key)) is int and row[key] > 0 for key in ("start_line", "end_line")) or row["end_line"] < row["start_line"]:
            raise ValueError("source excerpts: invalid line interval")
        if not _text(row.get("text")) or not isinstance(row.get("sha256"), str) or not HEX64.fullmatch(row["sha256"]):
            raise ValueError("source excerpts: malformed text binding")
        if len(row["text"].splitlines()) != row["end_line"] - row["start_line"] + 1:
            raise ValueError("source excerpts: text does not cover stated line interval")
        if hashlib.sha256(row["text"].encode()).hexdigest() != row["sha256"]:
            raise ValueError("source excerpts: text hash does not match")
        seen.add(row["id"])


def _validate_assessment(root: Path, assessment: dict[str, Any], source_ids: set[str]) -> None:
    if assessment.get("schema_version") != 1 or assessment.get("item_id") != "CVC-1":
        raise ValueError("assessment: expected schema-1 CVC-1 artifact")
    if assessment.get("outcome") not in {"SUCCESS", "NEGATIVE", "BOUNDED_UNRESOLVED"} or assessment.get("decision") not in {"REUSE", "EXTEND", "BUILD_SMALL", "STOP"}:
        raise ValueError("assessment: invalid outcome or decision")
    selected = assessment.get("selected_fragment")
    if (assessment["decision"] == "STOP" and selected is not None) or (assessment["decision"] != "STOP" and selected not in FRAGMENTS):
        raise ValueError("assessment: selected fragment is inconsistent with decision")
    comparisons = assessment.get("comparisons")
    if not isinstance(comparisons, list) or {row.get("fragment_id") for row in comparisons if isinstance(row, dict)} != FRAGMENTS or len(comparisons) != 3:
        raise ValueError("assessment: comparisons must cover exactly the three fragments")
    if {row.get("rank") for row in comparisons if isinstance(row, dict)} != {1, 2, 3}:
        raise ValueError("assessment: comparisons must have ranks 1 through 3")
    for row in comparisons:
        if not isinstance(row, dict) or not _text(row.get("rationale")) or not _text(row.get("gap")):
            raise ValueError("assessment: comparisons need rationale and gap")
        _evidence_refs(root, row.get("evidence_refs"), "assessment comparison")
    if assessment["decision"] != "STOP" and next(row["fragment_id"] for row in comparisons if row["rank"] == 1) != selected:
        raise ValueError("assessment: selected fragment must rank first")
    used_sources = assessment.get("source_ids")
    if not isinstance(used_sources, list) or not used_sources or len(set(used_sources)) != len(used_sources) or not set(used_sources) <= source_ids:
        raise ValueError("assessment: source_ids must be unique ledger sources")
    recommendation = assessment.get("recommendation")
    if not isinstance(recommendation, dict) or not all(_text(recommendation.get(key)) for key in ("action", "target")):
        raise ValueError("assessment: recommendation needs action and target")
    if not isinstance(recommendation.get("priority"), int) or isinstance(recommendation["priority"], bool) or recommendation["priority"] <= 0:
        raise ValueError("assessment: recommendation priority must be positive")
    if not isinstance(recommendation.get("prerequisites"), list) or not all(_text(item) for item in recommendation["prerequisites"]):
        raise ValueError("assessment: recommendation prerequisites must be a list")
    _evidence_refs(root, assessment.get("evidence_refs"), "assessment")
    _evidence_refs(root, recommendation.get("evidence_refs"), "assessment recommendation")


def _validate_manifest(root: Path, manifest: dict[str, Any]) -> None:
    if manifest.get("schema_version") != 1 or manifest.get("item_id") != "CVC-1":
        raise ValueError("evidence manifest: expected schema-1 CVC-1 artifact")
    files = manifest.get("files")
    if not isinstance(files, list):
        raise ValueError("evidence manifest: files must be a list")
    expected = {str(CVC_DIR / name) for name in FINAL_FILES}
    found: set[str] = set()
    for binding in files:
        if not isinstance(binding, dict) or set(binding) != {"path", "sha256"}:
            raise ValueError("evidence manifest: malformed file binding")
        path = binding["path"]
        if path not in expected or path in found or not isinstance(binding["sha256"], str) or not HEX64.fullmatch(binding["sha256"]):
            raise ValueError("evidence manifest: unexpected or malformed file binding")
        target = _path(root, path, "evidence manifest")
        if not target.is_file() or _sha(target) != binding["sha256"]:
            raise ValueError(f"evidence manifest: modified or missing evidence {path}")
        found.add(path)
    if found != expected:
        raise ValueError("evidence manifest: must list every final CVC-1 result file except itself")


def validate_cvc1_assessment(root: Path) -> None:
    """Validate completed CVC-1 artifacts below *root*; raise ``ValueError`` on drift."""
    root = Path(root).resolve()
    base = root / CVC_DIR
    record = _load(base / "work-record.json")
    sources, inspection_files = _validate_ledger(root, record)
    _validate_assessment(root, _load(base / "assessment.json"), sources)
    _validate_excerpts(root, _load(base / "source-excerpts.json"), inspection_files)
    report = base / "report.md"
    if not report.is_file() or not report.read_text(encoding="utf-8").strip():
        raise ValueError("report: report.md must be non-empty")
    _validate_manifest(root, _load(base / "evidence-manifest.json"))
