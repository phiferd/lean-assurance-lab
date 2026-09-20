"""Static, source-only audit of pinned Rust include dependencies."""
from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
from pathlib import Path, PurePosixPath
import re

from lib.cvc_prep import bind, committed, require, safe
from lib.cvc_process import atomic, now, sha


ITEM = "SOURCE-LOCK-COMPLETENESS-AUDIT-1"
RUN = "source-lock-completeness-audit-0001"
BASE = "results/research/source-lock-completeness-audit-1"
OUT = BASE + "/run-0001"
WORK = BASE + "/work-record.json"
ENTRY = BASE + "/entry-decision.json"
MANIFEST = "config/source-lock-completeness-audit-0001.json"
PLAN = "docs/research/SOURCE_LOCK_COMPLETENESS_AUDIT_PLAN.md"
LOCK = "results/research/alt-survivors-2026-09-08/source-lock.json"
SOURCE_ROOT = "results/research/alt-survivors-2026-09-08/evidence/pinned-nanoda"
CHILD_CLOSURE = "results/research/survivor-thread-one-child-panic-regression-1/work-closure.json"
CHILD_AUDIT = "results/research/survivor-thread-one-child-panic-regression-1/source-materialization-closure-audit.json"
RECEIPT = BASE + "/focused-test-receipt.json"
INCLUDE = re.compile(r"(?P<macro>include_(?:str|bytes))!\s*\(\s*\"(?P<literal>[^\"]+)\"\s*\)")
CODE = [
    "lib/source_lock_completeness_audit.py",
    "scripts/execute-source-lock-completeness-audit",
    "scripts/validate-source-lock-completeness-audit",
    "tests/test_source_lock_completeness_audit.py",
    "lib/cvc_prep.py",
    "lib/cvc_process.py",
    "lib/research_queue_v3.py",
]
AUTHORIZATION = (
    "The owner directed immediate execution of SOURCE-LOCK-COMPLETENESS-AUDIT-1. "
    "Run only the committed source-only static audit: no network, build, checker, "
    "byte substitution, source retrieval, mutation, external action or milestone advance."
)


def load(path: Path | str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def exact(root: Path, row: dict, path: str, digest: str) -> Path:
    require(row == {"path": path, "sha256": digest}, "wrong binding: " + path)
    return bind(root, row)


def resolved_path(source_path: str, literal: str) -> str:
    """Resolve a Rust relative literal without permitting a source-root escape."""
    require(not PurePosixPath(literal).is_absolute(), "absolute include literal")
    target = posixpath.normpath(posixpath.join(posixpath.dirname(source_path), literal))
    require(target not in {".", ".."} and not target.startswith("../"), "include escapes source root")
    return target


def directives(source_path: str, data: str) -> list[dict]:
    return [{"source_path": source_path, "macro": match["macro"], "literal": match["literal"],
             "resolved_path": resolved_path(source_path, match["literal"])}
            for match in INCLUDE.finditer(data)]


def validate(root: Path, *, launch: bool = False) -> dict:
    root = Path(root).resolve()
    manifest = load(safe(root, MANIFEST))
    require(set(manifest) == {"schema_version", "item_id", "run_id", "work_record", "entry_decision",
                              "source_lock", "source_root", "child_closure", "child_audit",
                              "tooling_inputs", "focused_test_receipt"}
            and manifest["schema_version"] == 1 and manifest["item_id"] == ITEM
            and manifest["run_id"] == RUN and manifest["source_root"] == SOURCE_ROOT,
            "manifest identity differs")
    work = load(exact(root, manifest["work_record"], WORK, manifest["work_record"]["sha256"]))
    require(work["item_id"] == ITEM and work["status"] == "ACTIVE"
            and work["authorization"] == AUTHORIZATION and work["source_setup_inspections"] == 0,
            "work record differs")
    entry = load(exact(root, manifest["entry_decision"], ENTRY, manifest["entry_decision"]["sha256"]))
    require(entry["item_id"] == ITEM and entry["authorization"] == "Do the work!!"
            and entry["network_requests"] == 0 and entry["builds"] == 0 and entry["checkers"] == 0,
            "entry decision differs")
    lock_path = exact(root, manifest["source_lock"], LOCK,
                      "fb8ddc20e941aed1f56288ce83a83016e718d8abdf9756b34b96384236fdd472")
    lock_data = load(lock_path)
    require(len(lock_data["files"]) == 22 and all(row["source_path"] for row in lock_data["files"]),
            "wrong source inventory")
    exact(root, manifest["child_closure"], CHILD_CLOSURE,
          "05eb30dbf6d1c08835150007c5b71bdcb96ad9e636951309710ff40ff3791aca")
    exact(root, manifest["child_audit"], CHILD_AUDIT,
          "fd5de25fd695742706f9e9e168bf1690d5cf778dac74df9cd0189f256da43f35")
    require([row["path"] for row in manifest["tooling_inputs"]] == CODE, "tooling inventory differs")
    for row in manifest["tooling_inputs"]:
        bind(root, row)
    receipt = load(bind(root, manifest["focused_test_receipt"]))
    require(receipt["item_id"] == ITEM and receipt["status"] == "PASS"
            and receipt["real_process_launches"] == 0 and receipt["tooling_inputs"] == manifest["tooling_inputs"],
            "focused receipt differs")
    if launch:
        from lib.research_queue_v3 import load_queue
        queue = load_queue(root, require_ready=True)
        row = next((item for item in queue["items"] if item["id"] == ITEM), None)
        require(queue["selected_item"] == ITEM and row is not None and row["status"] == "ACTIVE",
                "item is not selected ACTIVE")
        for row in ([manifest["work_record"], manifest["entry_decision"], manifest["source_lock"],
                     manifest["child_closure"], manifest["child_audit"], manifest["focused_test_receipt"]]
                    + manifest["tooling_inputs"]):
            committed(root, row["path"])
        for path in (MANIFEST, "config/research-queue.json", "docs/RESEARCH_STATUS.md", PLAN):
            committed(root, path)
    return {"manifest": manifest, "lock": lock_data}


def execute(root: Path) -> dict:
    root = Path(root).resolve()
    bundle = validate(root, launch=True)
    output = safe(root, OUT + "/audit.json", exists=False)
    require(not output.exists(), "refuse audit overwrite")
    locked = {row["source_path"] for row in bundle["lock"]["files"]}
    rows: list[dict] = []
    for row in bundle["lock"]["files"]:
        source = bind(root, row["binding"])
        if not row["source_path"].endswith(".rs"):
            continue
        for directive in directives(row["source_path"], source.read_text(encoding="utf-8")):
            target = directive["resolved_path"]
            evidence = root / SOURCE_ROOT / target
            directive["locked"] = target in locked
            directive["pinned_evidence_exists"] = evidence.is_file()
            directive["disposition"] = ("LOCKED" if directive["locked"] else
                                        "MISSING_FROM_LOCK_AND_EVIDENCE" if not directive["pinned_evidence_exists"]
                                        else "MISSING_FROM_LOCK")
            rows.append(directive)
    result = {
        "schema_version": 1, "item_id": ITEM, "run_id": RUN, "generated_at": now(),
        "source_lock": bundle["manifest"]["source_lock"], "source_file_count": len(locked),
        "directives": rows,
        "missing": [row for row in rows if row["disposition"] != "LOCKED"],
        "claim_limit": "Static source-dependency inventory only; no build, checker, network or source-byte retrieval occurred.",
    }
    output.parent.mkdir(parents=True, exist_ok=False)
    atomic(output, result)
    return result


def main(validate_only: bool = False):
    parser = argparse.ArgumentParser()
    parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    value = validate(root) if validate_only else execute(root)
    print(json.dumps(value, indent=2, sort_keys=True))
    return 0
