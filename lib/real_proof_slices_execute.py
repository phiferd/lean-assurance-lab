"""Exact, supervised observation of the fixed real-proof-slice matrix."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from lib.metamorphic_pilot_runner_v3 import run_supervised
from lib.metamorphic_pilot_runner import classify
from lib.real_proof_slices import ROOT, PROTOCOL_PATH, SCIENTIFIC_PATH, RECEIPTS, committed

BASE=ROOT/"results/research/real-proof-slices-pilot-1"
CONTROL=BASE/"execution-controls.json"
MANIFEST=BASE/"execution-manifest.json"
PREFLIGHT=BASE/"rss-preflight.json"
PROCESS=BASE/"execution"
PRODUCER=ROOT/"lib/real_proof_slices.py"
AUDITOR=ROOT/"lib/real_proof_slices_audit.py"
RUNNER=ROOT/"lib/metamorphic_pilot_runner_v3.py"
THIS=ROOT/"lib/real_proof_slices_execute.py"
ENVIRONMENT={"LANG":"C","PATH":"/usr/bin:/bin"}


class ExecutionError(ValueError):
    pass


def file_hash(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()


def write_json(path:Path,value:Any)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")


def load(path:Path)->dict[str,Any]:
    return json.loads(path.read_text())


def _profiles(protocol:dict[str,Any])->list[dict[str,Any]]:
    source=ROOT/"external/lean-kernel-arena/_build/lean4export/leanprover_lean4_v4.29.1"
    if subprocess.check_output(["git","rev-parse","HEAD"],cwd=source,text=True).strip()!=protocol["source_contract"]["exporter_source_revision"]:
        raise ExecutionError("exporter source revision differs")
    if file_hash(source/"format_ndjson.md")!=protocol["source_contract"]["format_spec_sha256"]:
        raise ExecutionError("format specification differs")
    rows=[]
    for p in protocol["observer_profiles"]:
        if p["id"]=="official-lean-4.33.0":
            checkout=ROOT/"external/lean-kernel-arena/_build/checkers/official/src"
            importer=checkout/".lake/packages/lean4export"
            if subprocess.check_output(["git","rev-parse","HEAD"],cwd=checkout,text=True).strip()!=p["source_revision"]:
                raise ExecutionError("official source revision differs")
            if subprocess.check_output(["git","rev-parse","HEAD"],cwd=importer,text=True).strip()!=p["importer_revision"]:
                raise ExecutionError("official importer revision differs")
        elif p["id"]=="nanoda-6ae1f0c":
            checkout=ROOT/"external/lean-kernel-arena/_build/checkers/nanoda/src"
            if subprocess.check_output(["git","rev-parse","HEAD"],cwd=checkout,text=True).strip()!=p["source_revision"]:
                raise ExecutionError("nanoda source revision differs")
        else:
            raise ExecutionError("unexpected observer profile")
        binary=ROOT/p["binary"]
        if not binary.is_file() or file_hash(binary)!=p["sha256"]:
            raise ExecutionError(f"observer binary differs: {p['id']}")
        if "config_sha256" in p:
            config=ROOT/p["cwd"]/"config.json"
            if file_hash(config)!=p["config_sha256"]:raise ExecutionError(f"observer config differs: {p['id']}")
        rows.append(p)
    return rows


def freeze_control()->dict[str,Any]:
    protocol=load(PROTOCOL_PATH); science=load(SCIENTIFIC_PATH)
    if science["protocol_sha256"]!=file_hash(PROTOCOL_PATH):raise ExecutionError("scientific protocol hash differs")
    profiles=_profiles(protocol)
    cases=[f"{entry['source']}-{slot:02d}" for entry in science["sources"] for slot in range(1,5)]
    if len(cases)!=12 or len(set(cases))!=12:raise ExecutionError("case set differs")
    controls={"schema":"real-proof-slices-execution-controls-v1","item_id":protocol["item_id"],
              "protocol_sha256":file_hash(PROTOCOL_PATH),"scientific_manifest_sha256":file_hash(SCIENTIFIC_PATH),
              "case_order":cases,"profile_order":[p["id"] for p in profiles],"profiles":profiles,
              "matrix":[{"ordinal":i+1,"case":case,"profile":p["id"]}
                        for i,(p,case) in enumerate((p,c) for p in profiles for c in cases)],
              "safety":protocol["execution_controls"],
              "runtime":{"python_path":sys.executable,"python_sha256":file_hash(Path(sys.executable)),
                         "ps_path":"/bin/ps","ps_sha256":file_hash(Path("/bin/ps")),
                         "environment":ENVIRONMENT},
              "tooling_paths":[str(path.relative_to(ROOT)) for path in (PRODUCER,AUDITOR,RUNNER,THIS)],
              "artifact_policy":"final exact artifact hashes are bound in a separately committed execution-manifest after construction and before launch"}
    write_json(CONTROL,controls)
    return controls


def freeze_execution()->dict[str,Any]:
    for path in (PROTOCOL_PATH,SCIENTIFIC_PATH,CONTROL,PRODUCER,AUDITOR,RUNNER,THIS):committed(path)
    control=load(CONTROL); protocol=load(PROTOCOL_PATH)
    if control["protocol_sha256"]!=file_hash(PROTOCOL_PATH) or control["scientific_manifest_sha256"]!=file_hash(SCIENTIFIC_PATH):
        raise ExecutionError("control input binding differs")
    _profiles(protocol)
    from lib.real_proof_slices_audit import audit_case
    artifacts=[]
    for case in control["case_order"]:
        receipt=RECEIPTS/f"{case}.json"
        if not receipt.is_file():raise ExecutionError(f"missing receipt {case}")
        result=audit_case(receipt)
        row=load(receipt)
        if row["case"]!=case:raise ExecutionError(f"case receipt differs {case}")
        artifact={"case":case,"disposition":row["disposition"],"receipt_path":str(receipt.relative_to(ROOT)),"receipt_sha256":file_hash(receipt)}
        if row["disposition"]=="READY":
            path=ROOT/row["output_path"]
            if not path.is_file() or file_hash(path)!=row["output_sha256"]:raise ExecutionError(f"artifact differs {case}")
            artifact.update({"path":row["output_path"],"sha256":row["output_sha256"],"bytes":path.stat().st_size})
        artifacts.append(artifact)
    manifest={"schema":"real-proof-slices-execution-manifest-v1","item_id":control["item_id"],
              "control_sha256":file_hash(CONTROL),"protocol_sha256":file_hash(PROTOCOL_PATH),
              "scientific_manifest_sha256":file_hash(SCIENTIFIC_PATH),
              "tooling":[{"path":p,"sha256":file_hash(ROOT/p)} for p in control["tooling_paths"]],
              "artifacts":artifacts,"matrix":[cell for cell in control["matrix"] if next(a for a in artifacts if a["case"]==cell["case"])["disposition"]=="READY"],
              "non_ready_cases":[a for a in artifacts if a["disposition"]!="READY"]}
    write_json(MANIFEST,manifest)
    return manifest


def rss_preflight()->dict[str,Any]:
    for path in (PROTOCOL_PATH,SCIENTIFIC_PATH,CONTROL,MANIFEST,PRODUCER,AUDITOR,RUNNER,THIS):committed(path)
    protocol=load(PROTOCOL_PATH);safety=protocol["execution_controls"]
    control=load(CONTROL)
    if (control["runtime"]["python_path"]!=sys.executable or
        control["runtime"]["python_sha256"]!=file_hash(Path(sys.executable)) or
        control["runtime"]["ps_sha256"]!=file_hash(Path("/bin/ps"))):
        raise ExecutionError("runtime identity differs")
    raw=BASE/"preflight/raw"
    receipt=run_supervised(argv=[sys.executable,"-c","import time; time.sleep(0.1)"],cwd=ROOT,stdin=None,env=ENVIRONMENT,
                           timeout_seconds=5,memory_bytes=safety["per_process_memory_bytes"],raw_prefix=raw)
    if (receipt["memory_monitor_error"] or receipt["memory_monitor_samples"]<=0 or receipt["maximum_observed_rss_bytes"]<=0
            or receipt["timed_out"] or not receipt["cleanup_complete"] or receipt["exit_code"]!=0):
        write_json(PREFLIGHT,{"status":"FAILED","receipt":receipt})
        raise ExecutionError("actual-host RSS preflight failed")
    result={"status":"PASS","receipt":receipt,"manifest_sha256":file_hash(MANIFEST)}
    write_json(PREFLIGHT,result)
    return result


def execute()->dict[str,Any]:
    for path in (PROTOCOL_PATH,SCIENTIFIC_PATH,CONTROL,MANIFEST,PRODUCER,AUDITOR,RUNNER,THIS,PREFLIGHT):committed(path)
    manifest=load(MANIFEST);control=load(CONTROL);protocol=load(PROTOCOL_PATH);preflight=load(PREFLIGHT)
    if manifest["control_sha256"]!=file_hash(CONTROL) or preflight["status"]!="PASS" or preflight["manifest_sha256"]!=file_hash(MANIFEST):
        raise ExecutionError("launch binding or RSS preflight differs")
    for item in manifest["tooling"]:
        if file_hash(ROOT/item["path"])!=item["sha256"]:raise ExecutionError("tooling revision differs")
    if (control["runtime"]["python_path"]!=sys.executable or
        control["runtime"]["python_sha256"]!=file_hash(Path(sys.executable)) or
        control["runtime"]["ps_sha256"]!=file_hash(Path("/bin/ps")) or
        control["runtime"]["environment"]!=ENVIRONMENT):
        raise ExecutionError("runtime identity differs")
    profiles={p["id"]:p for p in _profiles(protocol)}
    artifacts={a["case"]:a for a in manifest["artifacts"]}
    for a in artifacts.values():
        if file_hash(ROOT/a["receipt_path"])!=a["receipt_sha256"]:raise ExecutionError("receipt differs")
        if a["disposition"]=="READY" and file_hash(ROOT/a["path"])!=a["sha256"]:raise ExecutionError("artifact differs")
    existing=sorted(PROCESS.glob("attempt-*[0-9]")) if PROCESS.exists() else []
    number=len(existing)+1; run=PROCESS/f"attempt-{number:04d}"
    run.mkdir(parents=True,exist_ok=False)
    result={"schema":"real-proof-slices-execution-result-v1","attempt":number,"status":"RUNNING","cells":[]}
    write_json(run/"result.json",result)
    try:
        for cell in manifest["matrix"]:
            profile=profiles[cell["profile"]]; artifact=ROOT/artifacts[cell["case"]]["path"]
            if profile["id"]=="official-lean-4.33.0":
                argv=[str(ROOT/profile["binary"]),str(artifact)];cwd=ROOT;stdin=None
            elif profile["id"]=="nanoda-6ae1f0c":
                argv=profile["argv"][:] ;cwd=ROOT/profile["cwd"];stdin=artifact.read_bytes()
            else:raise ExecutionError("unexpected profile")
            raw=run/"raw"/f"{cell['ordinal']:03d}-{cell['case']}-{cell['profile']}"
            receipt=run_supervised(argv=argv,cwd=cwd,stdin=stdin,env=ENVIRONMENT,
                                  timeout_seconds=protocol["execution_controls"]["per_process_timeout_seconds"],
                                  memory_bytes=protocol["execution_controls"]["per_process_memory_bytes"],raw_prefix=raw)
            stdout=Path(str(raw)+".stdout").read_bytes();stderr=Path(str(raw)+".stderr").read_bytes()
            outcome,reason=classify(profile["id"],receipt,stdout,stderr)
            row={**cell,"outcome":outcome,"reason":reason,"process_receipt":receipt}
            result["cells"].append(row);write_json(run/"result.json",result)
            if outcome in {"INFRASTRUCTURE_AUDIT_FAILURE","TIMEOUT","CRASH"}:
                raise ExecutionError(f"repair pause required at {cell['case']} {profile['id']}: {outcome}")
        result["status"]="COMPLETE"
    except BaseException as exc:
        result["status"]="REPAIR_PAUSE";result["error"]=f"{type(exc).__name__}: {exc}"
        write_json(run/"result.json",result)
        raise
    write_json(run/"result.json",result)
    return result
