#!/usr/bin/env python3
"""Validate the fixed HSBM pilot closure; optional offline selection replay."""
import argparse
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "results/research/hsbm-pilot-1/"
ITEM = "HSBM-PILOT-1"
FREEZE = "fe61bdf4de7beef3dc1a86b3e247ea1f4b591489"
TIP = "4c544ed4099c8227f07d5de77ad1e69fb0740a27"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite(value, name):
    require(isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and value >= 0, f"invalid {name}")
    return value


def count(value, name):
    finite(value, name)
    require(isinstance(value, int), f"noninteger {name}")
    return value


def digest(data):
    return hashlib.sha256(data).hexdigest()


def validate_data(selection, ledger, result, work, requests):
    """Pure checks also used by adversarial fixtures, without changing evidence."""
    for value in (selection, ledger, result, work, requests):
        require(value.get("item_id") == ITEM, "wrong item identity")
    chosen = selection["selected"]
    require(len(chosen) == 6, "expected six frozen selections")
    selected = {r["commit"]: r["arm"] for r in chosen}
    require(len(selected) == 6, "duplicate selected commit")
    require(list(selected.values()).count("SIGNAL") == 4
            and list(selected.values()).count("CONTROL") == 2, "wrong arm counts")
    rows = ledger["rows"]
    require(len(rows) == 6 and len({r["commit"] for r in rows}) == 6,
            "expected six unique ledger rows")
    require({r["commit"]: r["arm"] for r in rows} == selected,
            "ledger does not match frozen selections and arms")
    for row in rows:
        boundaries = row["boundaries"]
        require(isinstance(boundaries, list) and 1 <= len(boundaries) <= 3,
                "boundary candidate cap or empty analysis")
        require(all(isinstance(b, dict) and b for b in boundaries), "empty boundary")
        require(bool(row.get("decision")), "missing row decision")
    candidates = ledger["actionable_candidates"]
    require(isinstance(candidates, list) and len(candidates) <= 2,
            "actionable candidate cap")
    require(len({c["id"] for c in candidates}) == len(candidates)
            and all(c["id"] for c in candidates), "duplicate or empty candidate ID")
    require(len({c["commit"] for c in candidates}) == len(candidates)
            and all(c["commit"] in selected for c in candidates),
            "candidate commits must be distinct selected commits")
    require(all(isinstance(c.get("fresh_commit_candidate"), bool) for c in candidates),
            "candidate freshness must be explicit boolean")
    fresh_count = sum(c["fresh_commit_candidate"] for c in candidates)
    outcome = result["outcome"]
    require(outcome in {"SUCCESS", "NEGATIVE", "BOUNDED_UNRESOLVED"}, "invalid outcome")
    require(outcome != "SUCCESS" or fresh_count == 2,
            "success requires two fresh actionable source commits")
    require(outcome != "NEGATIVE" or fresh_count < 2,
            "negative contradicts two actionable candidates")
    start = finite(work["start_monotonic"], "start monotonic")
    end = finite(work["end_monotonic"], "end monotonic")
    active = finite(work["active_seconds"], "active seconds")
    require(end >= start and abs((end - start) - active) <= 0.01,
            "active duration mismatch")
    require(active <= 7200, "active time cap exceeded")
    utc_start = datetime.fromisoformat(work["started_at"])
    utc_end = datetime.fromisoformat(work["completed_at"])
    require(utc_start.utcoffset() is not None and utc_end.utcoffset() is not None,
            "UTC interval needs timezone-aware endpoints")
    utc_elapsed = (utc_end - utc_start).total_seconds()
    require(utc_elapsed >= 0 and abs(utc_elapsed - active) <= 2,
            "UTC/monotonic interval disagreement")
    charges = sum(count(r["charged_requests"], "request charge") for r in requests["requests"])
    require(charges == requests["charged_source_setup_requests"] and charges >= 4,
            "setup request charge mismatch or erased initial cost")
    require(len({r["id"] for r in requests["requests"]}) == len(requests["requests"]),
            "duplicate request ID")
    require(requests["cap"] == 8 and charges <= 8, "source request cap exceeded")
    counts = result["research_counts"]
    require(count(counts["source_setup_requests"], "source setup count") == charges,
            "result/request accounting disagreement")
    for kind in ("builds", "checkers", "proofs", "mutations", "new_exports", "external_research_writes"):
        require(count(counts[kind], kind) == 0, f"prohibited {kind}")
    successor = result["next_item"]
    require(bool(successor["id"]) and successor["id"] != ITEM
            and successor["status"] == "READY" and successor["started"] is False,
            "successor must be a different READY unstarted item")


def git_bytes(root, revision, path):
    return subprocess.check_output(["git", "-C", str(root), "show", f"{revision}:{path}"])


def safe_path(root, name):
    path = (root / name).resolve()
    require(not Path(name).is_absolute() and path.is_relative_to(root.resolve()),
            "binding escapes repository")
    return path


def validate(root=ROOT, reproduce_selection=False):
    root = Path(root)
    def read(name):
        return json.loads((root / PREFIX / name).read_text())
    frozen_names = [PREFIX + name for name in
                    ("entry-lock.json", "source-lock.json", "selection.json", "work-record.json")]
    frozen_names.append("scripts/hsbm-pilot")
    for name in frozen_names:
        require((root / name).read_bytes() == git_bytes(root, FREEZE, name),
                f"frozen input changed: {name}")
    entry = read("entry-lock.json")
    for binding in entry["bindings"]:
        require(digest(git_bytes(root, entry["base_commit"], binding["path"])) == binding["sha256"],
                f"entry historical binding mismatch: {binding['path']}")
    source = read("source-lock.json")
    frozen_requests = json.loads(git_bytes(root, FREEZE, PREFIX + "requests.json"))
    requests = read("requests.json")
    require(requests["requests"][:len(frozen_requests["requests"])] == frozen_requests["requests"],
            "historical source request events changed")
    selection = read("selection.json")
    require(source["tip"] == selection["tip"] == TIP and source["tree"] == selection["tip_tree"],
            "source tip/tree mismatch")
    require(source["semantic_inspection_before_freeze"] is False
            and selection["semantic_inspection_started"] is False, "preinspection freeze missing")
    require(source["population_and_descendants"] == "selection.json", "selection path changed")
    bundle = safe_path(root, PREFIX + source["history_bundle"])
    require(digest(bundle.read_bytes()) == source["history_bundle_sha256"], "bundle hash mismatch")
    require(digest((root / PREFIX / "selection.json").read_bytes()) == source["selection_sha256"],
            "selection hash mismatch")
    require(digest((root / "scripts/hsbm-pilot").read_bytes()) == source["tool_sha256"], "tool hash mismatch")
    manifest = read("artifact-bindings.json")["bindings"]
    names = [b["path"] for b in manifest]
    require(len(names) == len(set(names)), "duplicate artifact binding")
    required = {PREFIX + n for n in ("result.json", "ledger.json", "work-closure.json", "requests.json", source["history_bundle"])}
    require(required <= set(names), "closure manifest missing required artifacts")
    for binding in manifest:
        require(digest(safe_path(root, binding["path"]).read_bytes()) == binding["sha256"],
                f"artifact hash mismatch: {binding['path']}")
    work = read("work-closure.json")
    entry_work = read("work-record.json")
    require(work["started_at"] == entry_work["started_at"]
            and work["start_monotonic"] == entry_work["start_monotonic"], "work clock reset")
    validate_data(selection, read("ledger.json"), read("result.json"), work, requests)
    if reproduce_selection:
        with tempfile.TemporaryDirectory(prefix="hsbm-offline-replay-") as temporary:
            target = Path(temporary) / "source"
            subprocess.run(["git", "clone", "--quiet", "--no-checkout", str(bundle), str(target)], check=True)
            tool = Path(temporary) / "hsbm-pilot"
            tool.write_bytes(git_bytes(root, FREEZE, "scripts/hsbm-pilot"))
            subprocess.run([sys.executable, str(tool), "--repo", str(target), "--tip", TIP,
                            "--output", str(root / PREFIX / "selection.json"), "--check"], check=True)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reproduce-selection", action="store_true")
    args = parser.parse_args()
    try:
        validate(reproduce_selection=args.reproduce_selection)
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"FAIL: {error}")
    print("PASS: HSBM-PILOT-1 closure and frozen history" + ("; offline selection reproduced" if args.reproduce_selection else ""))
