"""Validate the complete fixed real-proof-slices observation and raw custody."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

from lib.real_proof_slices_audit import audit_case
from lib.real_proof_slices import ROOT
from lib.metamorphic_pilot_runner import classify

BASE=ROOT/"results/research/real-proof-slices-pilot-1"


class ClosureError(ValueError):
    pass


def _read(path:Path)->dict[str,Any]:
    return json.loads(path.read_text())


def _hash(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()


def validate()->dict[str,Any]:
    manifest=_read(BASE/"execution-manifest.json")
    controls=_read(BASE/"execution-controls.json")
    preflight=_read(BASE/"rss-preflight.json")
    result=_read(BASE/"execution/attempt-0001/result.json")
    if manifest.get("schema")!="real-proof-slices-execution-manifest-v1" or result.get("status")!="COMPLETE":
        raise ClosureError("execution manifest or result is incomplete")
    if (manifest["control_sha256"]!=_hash(BASE/"execution-controls.json")
            or preflight.get("status")!="PASS"
            or preflight.get("manifest_sha256")!=_hash(BASE/"execution-manifest.json")):
        raise ClosureError("execution control or RSS preflight binding differs")
    for item in manifest["tooling"]:
        if _hash(ROOT/item["path"])!=item["sha256"]:
            raise ClosureError(f"bound tooling differs: {item['path']}")
    runtime=controls["runtime"]
    if (_hash(Path(runtime["python_path"]))!=runtime["python_sha256"]
            or _hash(Path(runtime["ps_path"]))!=runtime["ps_sha256"]):
        raise ClosureError("bound host runtime differs")
    profile_map={row["id"]:row for row in controls["profiles"]}
    if set(profile_map)!={"official-lean-4.33.0","nanoda-6ae1f0c"}:
        raise ClosureError("observer profile set differs")
    for profile in profile_map.values():
        if _hash(ROOT/profile["binary"])!=profile["sha256"]:
            raise ClosureError("observer binary differs")
        if "config_sha256" in profile and _hash(ROOT/profile["cwd"]/"config.json")!=profile["config_sha256"]:
            raise ClosureError("observer configuration differs")
    pre=preflight["receipt"]
    if (pre["exit_code"]!=0 or pre["timed_out"] or pre["memory_exceeded"]
            or pre["memory_monitor_error"] or pre["memory_monitor_samples"]<=0
            or pre["maximum_observed_rss_bytes"]<=0 or not pre["cleanup_complete"]):
        raise ClosureError("actual-host RSS preflight differs")
    for suffix in ("stdout","stderr"):
        raw=ROOT/pre[f"raw_{suffix}_path"]
        if _hash(raw)!=pre[f"{suffix}_sha256"] or raw.stat().st_size!=pre[f"{suffix}_bytes"]:
            raise ClosureError("preflight raw stream custody differs")
    cases=controls["case_order"]
    if len(cases)!=12 or len(set(cases))!=12 or len(manifest["artifacts"])!=12:
        raise ClosureError("fixed twelve-case inventory differs")
    artifacts={row["case"]:row for row in manifest["artifacts"]}
    if set(artifacts)!=set(cases):raise ClosureError("artifact case set differs")
    dispositions={}
    for case in cases:
        artifact=artifacts[case];receipt=ROOT/artifact["receipt_path"]
        if _hash(receipt)!=artifact["receipt_sha256"]:raise ClosureError(f"receipt bytes differ: {case}")
        audit_case(receipt)
        row=_read(receipt)
        dispositions[case]=row["disposition"]
        if row["disposition"]=="READY":
            if _hash(ROOT/artifact["path"])!=artifact["sha256"]:raise ClosureError(f"slice differs: {case}")
        elif row["disposition"]!="OVERSIZE":
            raise ClosureError(f"unresolved non-ready case: {case}: {row['disposition']}")
    if [a["case"] for a in manifest["non_ready_cases"]]!=[c for c in cases if dispositions[c]!="READY"]:
        raise ClosureError("non-ready case projection differs")
    projected=[cell for cell in controls["matrix"] if dispositions[cell["case"]]=="READY"]
    if manifest["matrix"]!=projected or len(projected)!=18:
        raise ClosureError("exact 18-cell matrix differs")
    if len(result["cells"])!=len(projected):raise ClosureError("observed cell count differs")
    total_seconds=0.0;maximum_rss=0
    for expected,observed in zip(projected,result["cells"]):
        for key in ("ordinal","case","profile"):
            if observed.get(key)!=expected[key]:raise ClosureError(f"observed cell order differs: {key}")
        receipt=observed["process_receipt"]
        profile=profile_map[expected["profile"]]
        artifact=ROOT/artifacts[expected["case"]]["path"]
        if profile["id"]=="official-lean-4.33.0":
            expected_argv=[str(ROOT/profile["binary"]),str(artifact)]
            expected_cwd=str(ROOT)
        else:
            expected_argv=profile["argv"]
            expected_cwd=str(ROOT/profile["cwd"])
        if receipt["argv"]!=expected_argv or receipt["cwd"]!=expected_cwd:
            raise ClosureError(f"observed command/cwd differs: {expected}")
        if (observed["outcome"]!="ACCEPT" or receipt["exit_code"]!=0 or receipt["timed_out"]
                or receipt["memory_exceeded"] or receipt["memory_monitor_error"]
                or receipt["memory_monitor_samples"]<=0 or receipt["maximum_observed_rss_bytes"]<=0
                or not receipt["cleanup_complete"]):
            raise ClosureError(f"unsafe or nonaccepting observation: {expected}")
        stdout=ROOT/receipt["raw_stdout_path"];stderr=ROOT/receipt["raw_stderr_path"]
        if (_hash(stdout)!=receipt["stdout_sha256"] or _hash(stderr)!=receipt["stderr_sha256"]
                or stdout.stat().st_size!=receipt["stdout_bytes"] or stderr.stat().st_size!=receipt["stderr_bytes"]):
            raise ClosureError(f"raw stream custody differs: {expected}")
        if expected["profile"]=="official-lean-4.33.0":
            if not re.fullmatch(rb"Accepted [0-9]+ declarations[.]\n",stdout.read_bytes()) or stderr.stat().st_size:
                raise ClosureError("official success output contract differs")
        independently_classified=classify(expected["profile"],receipt,stdout.read_bytes(),stderr.read_bytes())
        if independently_classified!=(observed["outcome"],observed["reason"]):
            raise ClosureError(f"outcome classification differs: {expected}")
        total_seconds+=receipt["elapsed_seconds"]
        maximum_rss=max(maximum_rss,receipt["maximum_observed_rss_bytes"])
    return {"schema":"real-proof-slices-closure-validation-v1","item_id":"REAL-PROOF-SLICES-PILOT-1",
            "cases":12,"ready":sum(v=="READY" for v in dispositions.values()),
            "oversize":sum(v=="OVERSIZE" for v in dispositions.values()),
            "cells":18,"accepted":18,"profiles":{"official-lean-4.33.0":9,"nanoda-6ae1f0c":9},
            "process_seconds":total_seconds,"maximum_observed_rss_bytes":maximum_rss,
            "non_ready_cases":[c for c in cases if dispositions[c]!="READY"]}
