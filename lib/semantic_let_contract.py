"""Offline integrity checks for the bounded SEMANTIC-LET-CONTRACT-1 closure.

The source interpretation remains review evidence, not mechanically decided
semantic authority. Readers are injectable so tamper tests never edit evidence.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess

ITEM = "SEMANTIC-LET-CONTRACT-1"
BASE = "results/research/semantic-let-contract-1/"
ENTRY = "17399d9636365b5dd5a3e3622c2b5f04aae39719"
ZERO = ("builds", "checkers", "proofs", "mutations", "new_exports", "external_research_writes")
CANDIDATE = "corpus/generated/nanoda-gen-21ef4d1d32a1-let-value-type-mismatch.ndjson"
CONTROL = "corpus/controls/nanoda-gen-21ef4d1d32a1-matching-let-control.ndjson"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def binding(raw, row):
    require(len(raw) == row["bytes"] and digest(raw) == row["sha256"],
            f"content binding: {row['path']}")


def validate_pair(candidate, control):
    require(len(candidate) == len(control) == 601, "existing pair byte size")
    a, b = ([json.loads(line) for line in raw.splitlines()] for raw in (candidate, control))
    require(len(a) == len(b) == 13, "existing pair record count")
    require(a[:11] == b[:11], "existing pair common prefix")
    require(a[10] == {"bvar": 0, "ie": 3}, "pair body uses bound variable")
    require(a[11] == {"ie": 4, "letE": {"body": 3, "name": 2, "nondep": False,
            "type": 1, "value": 1}}, "candidate let shape")
    expected = json.loads(json.dumps(a))
    expected[11]["letE"]["value"] = 0
    expected[12]["def"]["type"] = 1
    require(a[12]["def"]["type"] == 2 and a[12]["def"]["value"] == 4,
            "candidate declaration shape")
    require(expected == b, "pair differs only in let value and declaration type")


def validate(root: Path, *, read=None, git_read=None):
    root = root.resolve()
    if read is None:
        def read(path):
            target = (root / path).resolve()
            require(target.is_relative_to(root) and target.is_file(), f"unsafe/missing path: {path}")
            return target.read_bytes()
    if git_read is None:
        def git_read(rev, path):
            require(re.fullmatch(r"[0-9a-f]{40}", rev), "exact git revision required")
            return subprocess.check_output(["git", "show", f"{rev}:{path}"], cwd=root)
    def load(name):
        return json.loads(read(BASE + name + ".json"))
    work, result, assessment, closure, preservation, lock = (
        load(n) for n in ("work-record", "result", "source-assessment", "work-closure",
                         "canonical-state-preservation", "source-lock"))
    for doc in (work, result, assessment, closure, preservation, lock):
        require(doc["item_id"] == ITEM and doc["schema_version"] == 1, "record identity")
    require(work["status"] == "COMPLETE" and work["entry_commit"] == ENTRY, "work closure/entry")
    for doc in (work, result, closure):
        require(doc["outcome"] == "SUCCESS", "bounded deliverable outcome")
    require(result["completion_kind"] == "SOURCE_QUALIFIED_MAINTAINER_QUESTION", "completion kind")
    for doc in (result, assessment, closure):
        require(doc["policy_status"] == "BOUNDED_UNRESOLVED", "unsupported policy resolution")
    for doc in (result, assessment):
        require(doc["catalog_changed"] is False and doc["authority_changed"] is False,
                "no catalog or authority promotion")
    require(assessment["proofs_launched"] == 0, "no proof launch")
    require(result["recommendation"]["external_action_status"] == "NOT_AUTHORIZED_NOT_SUBMITTED",
            "external action not authorized")
    require(read(result["recommendation"]["draft"]), "maintainer draft exists")

    entry = json.loads(git_read(ENTRY, BASE + "work-record.json"))
    queue_entry = json.loads(git_read(ENTRY, "config/research-queue.json"))
    require(entry["status"] == "ACTIVE" and queue_entry["selected_item"] == ITEM,
            "committed active selected entry")
    require(next(i for i in queue_entry["items"] if i["id"] == ITEM)["status"] == "ACTIVE",
            "entry queue item active")
    for key, value in entry.items():
        if key != "status":
            require(work[key] == value, f"entry work field changed: {key}")
    for name in ("source-lock.json", "action-rubric.json"):
        require(read(BASE + name) == git_read(ENTRY, BASE + name), f"frozen entry artifact: {name}")
    require(lock["entry_commit"] == work["base_commit"] == preservation["base_commit"], "base binding")
    for row in lock["bindings"]:
        # All entry inputs, including mutable queue/status, resolve at their bound commit.
        binding(git_read(lock["entry_commit"], row["path"]), row)
    expected_preserved = {r["path"] for r in lock["bindings"]
                          if r["path"].startswith(("config/declaration-validation", "corpus/", "results/"))}
    require({r["path"] for r in preservation["unchanged"]} == expected_preserved,
            "canonical preservation population")
    for row in preservation["unchanged"]:
        binding(git_read(preservation["base_commit"], row["path"]), row)
        binding(read(row["path"]), row)
    validate_pair(read(CANDIDATE), read(CONTROL))

    requests = assessment["requests"]
    require(assessment["requests_charged"] == len(requests) == 7, "seven charged requests")
    require(assessment["request_limit"] == work["budget"]["primary_source_GETs"] == 8,
            "eight request limit")
    require([r["ordinal"] for r in requests] == list(range(1, 8)), "request ordinals")
    require(requests[0]["status"] == "FAILED_NO_SOURCE" and
            all(r["status"] == "SUCCESS" for r in requests[1:]), "retained failure accounting")
    request_paths = [r["receipt"]["path"] for r in requests]
    require(len(set(request_paths)) == 7, "unique request receipts")
    for row in requests:
        binding(read(row["receipt"]["path"]), row["receipt"])
    sources = assessment["sources"]
    require({s["id"] for s in sources} == {"l4l-translation", "l4l-inference", "l4l-whnf",
            "l4l-context", "03-validating-proofs", "04-typechecker-header", "05-typechecker",
            "06-export-readme", "07-export-format", "manual-types"} and len(sources) == 10,
            "source population")
    for source in sources:
        raw = read(source["content"]["path"])
        binding(raw, source["content"])
        require(re.fullmatch(r"[0-9a-f]{40}", source["revision"]), "source exact revision")
        require(source["revision"] in source["url"] and source["qualification"].strip(),
                "qualified pinned source")
        if "git_blob" in source:
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            require(blob == source["git_blob"], "retained source git blob")
        if "receipt" in source:
            receipt = json.loads(read(source["receipt"]["path"]))
            require(raw == receipt["result"]["structuredContent"]["content"].encode(),
                    "connector content equals retained receipt")
            require(any(r["receipt"] == source["receipt"] and r["url"] == source["url"]
                        for r in requests), "source charged receipt")
        lines = raw.splitlines(keepends=True)
        require(source["excerpts"], "source excerpts required")
        for excerpt in source["excerpts"]:
            start, end = excerpt["start_line"], excerpt["end_line"]
            require(type(start) is int and type(end) is int and 1 <= start <= end <= len(lines),
                    "excerpt bounds")
            require(digest(b"".join(lines[start - 1:end])) == excerpt["sha256"], "excerpt digest")

    require(work["budget"]["active_seconds"] == 7200, "fixed active budget")
    counts = (result["research_counts"], work["consumed_at_closure"], closure["accounting"])
    for count in counts:
        require(count["primary_source_GETs"] == 7, "request accounting agreement")
        for field in ZERO:
            require(type(count[field]) is int and count[field] == work["budget"][field] == 0,
                    f"zero prohibited count: {field}")
    intervals = closure["intervals"]
    require(len(intervals) == 1, "continuous root interval without duplicate delegate charge")
    interval = intervals[0]
    require(interval["started_at"] == work["started_at"] and
            interval["start_monotonic"] == work["start_monotonic"] and
            interval["ended_at"] == work["completed_at"], "paired interval endpoints")
    elapsed = interval["end_monotonic"] - interval["start_monotonic"]
    utc_start, utc_end = (datetime.fromisoformat(interval[k]) for k in ("started_at", "ended_at"))
    require(utc_start.utcoffset() is not None and utc_end.utcoffset() is not None, "aware UTC clocks")
    require(math.isfinite(elapsed) and 0 <= elapsed <= 7200 and
            abs((utc_end - utc_start).total_seconds() - elapsed) <= 1,
            "paired UTC/monotonic active budget")
    for seconds in (interval["active_seconds"], closure["accounting"]["active_seconds"],
                    work["consumed_at_closure"]["active_seconds"]):
        require(math.isclose(seconds, elapsed, abs_tol=1e-6), "active accounting agreement")
    require(math.isclose(closure["accounting"]["remaining_active_seconds"], 7200 - elapsed,
                         abs_tol=1e-6), "remaining budget")
    successor = result["next_item"]
    require(successor["status"] == "READY" and successor["started"] is False and
            successor["id"] == work["next_item"] == closure["next_item"] and
            work["next_item_started"] is False and closure["next_item_started"] is False,
            "recorded successor unstarted at closure")
    # A future successor can complete or rerank without invalidating this closure.
    queue = json.loads(read("config/research-queue.json"))
    require(next(i for i in queue["items"] if i["id"] == ITEM)["status"] == "COMPLETE",
            "current item remains complete")
    return {"item_id": ITEM, "valid": True, "requests": 7, "active_seconds": elapsed}
