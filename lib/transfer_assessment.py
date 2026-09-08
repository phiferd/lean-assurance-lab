"""ALT-TRANSFER evidence/accounting integrity; no scientific eligibility oracle."""

import hashlib
import json
import math
import re
import subprocess
from datetime import datetime
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "results/research/alt-transfer-2026-09-08"
SUPPORT = {
    "lib/transfer_assessment.py", "scripts/validate-transfer-assessment",
    "tests/test_transfer_assessment.py",
    "docs/research/PROSPECTIVE_TRANSFER_ASSESSMENT_PLAN.md",
}
COUNTS = {"checker_launches", "proof_launches", "setup_build_launches",
          "scientific_byte_variants", "external_research_actions"}
ROLE = "METHOD_OR_TARGET_REVIEW_NOT_NORMATIVE_AUTHORITY"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _constant(value):
    raise ValueError(f"nonfinite JSON number: {value}")


def _float(value):
    parsed = float(value)
    require(math.isfinite(parsed), f"nonfinite JSON number: {value}")
    return parsed


def _json(raw):
    return json.loads(raw, object_pairs_hook=_pairs, parse_constant=_constant, parse_float=_float)


def _identity(record):
    require(type(record.get("schema_version")) is int and record["schema_version"] == 1
            and record.get("item_id") == "ALT-TRANSFER", "artifact identity mismatch")


def _path(root, name):
    require(isinstance(name, str) and name and "\\" not in name,
            f"invalid relative path: {name!r}")
    p = PurePosixPath(name)
    require(name != "." and not p.is_absolute() and ".." not in p.parts and p.as_posix() == name,
            f"unsafe relative path: {name}")
    target = root / name
    require(not any(p.is_symlink() for p in [target, *target.parents] if p != root.parent),
            f"symlink evidence path: {name}")
    require(target.resolve().is_relative_to(root.resolve()), f"path escapes root: {name}")
    return target


def _hash(raw, binding):
    require(type(binding.get("bytes")) is int and binding["bytes"] >= 0,
            "binding bytes must be a nonnegative integer")
    require(isinstance(binding.get("sha256"), str) and
            re.fullmatch(r"[0-9a-f]{64}", binding["sha256"]), "invalid SHA-256")
    require(len(raw) == binding["bytes"] and hashlib.sha256(raw).hexdigest() == binding["sha256"],
            f"evidence hash/size mismatch: {binding.get('path', binding.get('url'))}")


def _git(root, commit, path):
    require(isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}", commit),
            "invalid base Git commit")
    result = subprocess.run(["git", "-C", str(root), "cat-file", "blob", f"{commit}:{path}"],
                            capture_output=True, timeout=30, check=False)
    require(result.returncode == 0, f"missing historical Git evidence: {commit}:{path}")
    return result.stdout


def _number(value, label):
    require(type(value) in (int, float) and math.isfinite(value) and value >= 0,
            f"invalid finite nonnegative {label}")
    return value


def _utc(value):
    require(isinstance(value, str), "missing ended UTC timestamp")
    date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(date.utcoffset() is not None and date.utcoffset().total_seconds() == 0,
            "timestamp must be UTC")
    return date


def _zero_counts(value):
    require(isinstance(value, dict) and set(value) == COUNTS, "research counter inventory mismatch")
    require(all(type(v) is int and v == 0 for v in value.values()), "unauthorized research launch/count")


def _nonempty(value, label):
    require(isinstance(value, (str, list)) and bool(value), f"missing {label}")
    if isinstance(value, list):
        require(all(isinstance(v, str) and v.strip() for v in value), f"invalid {label}")


def _pointer(value, pointer):
    require(isinstance(pointer, str) and (pointer == "" or pointer.startswith("/")), "bad JSON pointer")
    for token in pointer[1:].split("/") if pointer else []:
        require(re.search(r"~(?![01])", token) is None, "bad JSON pointer escape")
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(value, list):
            require(re.fullmatch(r"0|[1-9][0-9]*", token) is not None, "bad JSON array index")
            value = value[int(token)]
        else:
            require(isinstance(value, dict) and token in value, "unresolved JSON pointer")
            value = value[token]


def validate(root=ROOT, check_current_preservation=False):
    """Verify recorded integrity; live preservation is an explicit closure-only check."""
    root = Path(root).resolve()
    try:
        return _validate(root, check_current_preservation)
    except (KeyError, TypeError, IndexError, OSError, OverflowError, subprocess.SubprocessError) as exc:
        raise ValueError(f"malformed or unavailable transfer evidence: {exc}") from exc


def _validate(root, current):
    def read(name):
        return _json(_path(root, f"{PACKAGE}/{name}").read_bytes())

    manifest = read("evidence-manifest.json")
    _identity(manifest)
    actual = {p.relative_to(root).as_posix() for p in (root / PACKAGE).rglob("*") if p.is_file()}
    actual.discard(f"{PACKAGE}/evidence-manifest.json")
    expected = actual | SUPPORT
    paths = [b["path"] for b in manifest["files"]]
    require(len(paths) == len(set(paths)) and set(paths) == expected, "package inventory mismatch")
    for binding in manifest["files"]:
        p = _path(root, binding["path"])
        raw = p.read_bytes()
        _hash(raw, binding)
        if p.suffix == ".json":
            _json(raw)
        elif p.suffix == ".jsonl":
            for line in raw.splitlines():
                if line.strip():
                    _json(line)

    work, result = read("work-record.json"), read("result.json")
    for label, record in (("work", work), ("result", result)):
        require(type(record.get("schema_version")) is int and record["schema_version"] == 1
                and record.get("item_id") == "ALT-TRANSFER", f"{label} identity mismatch")
        _zero_counts(record["research_counts"])
        require(record.get("next_item_started") is False, "successor started")
    required = {"outcome": "SUCCESS", "scientific_status": "BOUNDED_FEASIBILITY_NO_GO",
                "phase_decision": "STOP", "gate_decision": "NO_GO",
                "execution_authorized": False, "design": None, "transfer_result": None}
    require(all(k in result and result[k] == v and type(result[k]) is type(v)
                for k, v in required.items()), "no-go result boundary changed")
    recommendation = result["recommendation"]
    for field in ("action", "target", "prerequisites", "evidence_refs"):
        _nonempty(recommendation[field], f"recommendation {field}")
    require(type(recommendation["priority"]) is int and recommendation["priority"] > 0, "invalid priority")
    require(work["status"] == "COMPLETE", "work record is not closed")
    require(work["budget"] == {"active_seconds": 5400, **dict.fromkeys(COUNTS, 0),
            "search_queries": 8, "in_depth_primary_sources": 6, "source_code_inspections": 3},
            "authorized budget changed")
    _zero_counts({key: work["budget"][key] for key in COUNTS})
    total = _number(work["entry_overhead_conservative_seconds"], "entry overhead")
    require(isinstance(work["intervals"], list) and work["intervals"], "missing work intervals")
    previous = None
    for interval in work["intervals"]:
        start, end = _utc(interval["started_at"]), _utc(interval["ended_at"])
        begin = _number(interval["started_monotonic"], "monotonic start")
        finish = _number(interval["ended_monotonic"], "monotonic end")
        require(finish >= begin and end >= start and (previous is None or start >= previous),
                "reversed or overlapping work intervals")
        require(abs((end - start).total_seconds() - (finish - begin)) <= 2,
                "UTC/monotonic duration mismatch")
        total += finish - begin
        previous = end
    active = _number(work["active_seconds"], "active seconds")
    require(active <= 5400 and math.isclose(active, total, rel_tol=0, abs_tol=1e-6),
            "active budget exceeded or accounting mismatch")
    ids = []
    for field, cap in (("searches", 8), ("source_reviews", 6), ("code_inspections", 3)):
        rows = work[field]
        require(isinstance(rows, list) and len(rows) <= cap, f"{field} cap exceeded")
        for row in rows:
            _nonempty(row["id"], "reservation ID")
            require(row.get("status") in {"RETURNED", "REVIEWED", "COMPLETE", "SUCCESS", "FAILED"},
                    "unclosed or invalid research reservation")
            ids.append(row["id"])
    require(len(ids) == len(set(ids)), "duplicate research reservation ID")

    preserved = manifest["preserved_inputs"]
    require(preserved and len({b["path"] for b in preserved}) == len(preserved), "missing/duplicate preserved inputs")
    preserved_paths = {b["path"] for b in preserved}
    for binding in preserved:
        _path(root, binding["path"])
        _hash(_git(root, work["base_commit"], binding["path"]), binding)
        if current:
            _hash(_path(root, binding["path"]).read_bytes(), binding)
    entries = work["entry_bindings"]
    require(entries and len({b["path"] for b in entries}) == len(entries), "missing/duplicate entry binding")
    for binding in entries:
        _path(root, binding["path"])
        require(binding["snapshot"] == f"{PACKAGE}/entry-snapshot/{binding['path']}", "entry snapshot path mismatch")
        _hash(_path(root, binding["snapshot"]).read_bytes(), binding)
        _hash(_git(root, work["base_commit"], binding["path"]), binding)

    local = read("local-independence-review.json")
    _identity(local)
    local_ids = [s["source_id"] for s in local["sources"]]
    require(len(local_ids) == len(set(local_ids)) and local_ids, "local source ID inventory mismatch")
    for source in local["sources"]:
        require(source["path"] in preserved_paths, "local source omitted from preserved inputs")
        require(source["snapshot"] == f"{PACKAGE}/evidence/local/{source['path']}", "local snapshot path mismatch")
        require(source["git_commit"] == work["base_commit"], "local source commit mismatch")
        raw = _path(root, source["snapshot"]).read_bytes()
        _hash(raw, source)
        _hash(_git(root, source["git_commit"], source["path"]), source)
        if source["kind"] == "JSON":
            for pointer in source.get("json_pointers", []):
                _pointer(_json(raw), pointer)

    source_document = read("sources.json")
    _identity(source_document)
    records = source_document["records"]
    source_ids = [s["id"] for s in records]
    require(len(records) == 5 and set(source_ids) == {f"S{i}" for i in range(1, 6)}, "source inventory mismatch")
    require(set(source_ids) == {s["id"] for s in work["source_reviews"]}, "source reservations mismatch")
    retrieved = {(r["url"], r.get("sha256"), r.get("bytes")) for r in read("retrievals.json")
                 if r.get("status") == "SUCCESS"}
    for source in records:
        require(source["role"] == ROLE, "source promoted to semantic authority")
        for field in ("title", "url", "version", "reviewed_on", "decision", "summary", "limitations", "locators"):
            _nonempty(source[field], f"source {field}")
        require(source["retrieval_bindings"], "missing source retrieval binding")
        for binding in source["retrieval_bindings"]:
            require(type(binding["bytes"]) is int and binding["bytes"] >= 0
                    and isinstance(binding["sha256"], str)
                    and re.fullmatch(r"[0-9a-f]{64}", binding["sha256"]), "malformed retrieval binding")
            require((binding["url"], binding["sha256"], binding["bytes"]) in retrieved,
                    "source retrieval binding missing from receipts")
    for row in work["code_inspections"]:
        require(row["source_id"] in source_ids, "unknown code-inspection source")

    assessment = read("target-assessment.json")
    _identity(assessment)
    routes = assessment["routes"]
    require(assessment["decision"] == "NO_GO" and assessment["eligible_route_ids"] == [], "route decision changed")
    require(len(routes) == 3 and {r["id"] for r in routes} == {"EXISTING-POOL", "FERRIPROVE", "LEAN4LESS"},
            "route inventory mismatch")
    refs = [*result["evidence_refs"], *recommendation["evidence_refs"]]
    for route in routes:
        require(route["eligibility"] == "NO_GO", "eligible route in no-go package")
        for field in ("reasons", "missing_prerequisites", "source_ids", "evidence_refs"):
            _nonempty(route[field], f"route {field}")
        require(set(route["source_ids"]).issubset(set(source_ids)), "unknown route source")
        refs.extend(route["evidence_refs"])
    require(refs, "missing evidence references")
    require(all(p in set(paths) | preserved_paths for p in refs), "unbound evidence reference")
    return {"status": "PASS", "scope": "EVIDENCE_AND_ACCOUNTING_INTEGRITY_ONLY",
            "gate_decision": "NO_GO", "active_seconds": active,
            "files": len(paths), "preserved_inputs": len(preserved),
            "current_preservation_checked": bool(current), "scientific_eligibility_proved": False}
