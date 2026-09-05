"""Strict validation primitives for input-bound local authorized runs."""
from __future__ import annotations
import hashlib, json, math, os, platform, re
import signal, time
from pathlib import Path
from typing import Any

FRONTIER="F-ECOSYSTEM-CLOSURE-AND-AUTONOMY"
PATH_RE=re.compile(r"^(?!/)(?!.*(?:^|/)\.\.(?:/|$))[A-Za-z0-9._/-]+$")
ID_RE=re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
HEX_RE=re.compile(r"^[0-9a-f]{64}$")
SHELLS={"sh","bash","zsh","fish","dash","python","python3","env","curl","wget","gh","git"}
def sha256_file(path:Path)->str:
 h=hashlib.sha256()
 with path.open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""): h.update(b)
 return h.hexdigest()
def canonical_hash(value:Any)->str: return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def positive(x): return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) and x>0
def checked_path(root:Path,name:str,exists=True)->Path:
 if not isinstance(name,str) or not PATH_RE.fullmatch(name): raise ValueError("path must be safe relative repository path")
 root=root.resolve(); p=root
 for part in Path(name).parts:
  p=p/part
  if p.is_symlink(): raise ValueError(f"symlink path component refused: {name}")
 if exists and not p.exists(): raise ValueError(f"path missing: {name}")
 try: p.resolve().relative_to(root)
 except ValueError as e: raise ValueError(f"path escapes repository: {name}") from e
 return p
def relative_path(root:Path,name:str)->Path:
 return checked_path(root,name)
def active_frontier(status:Path,frontier:str)->bool:
 active=False
 for line in status.read_text().splitlines():
  if line=="### Active": active=True; continue
  if active and line.startswith("### "): return False
  if active and re.match("^\\d+\\. \\x60"+re.escape(frontier)+"\\x60(?:\\:|\\s)",line): return True
 return False
def validate_manifest(m:dict,root:Path,authorization_path:Path,check_inputs=True)->str:
 required={"schema_version","run_id","frontier_id","governing_plan","inputs","platform","phases","total_budget_seconds","max_attempts","completion_predicate","external_actions"}
 if not isinstance(m,dict) or set(m)!=required or m.get("schema_version")!=1: raise ValueError("invalid authorized-run manifest fields")
 if not isinstance(m["run_id"],str) or not ID_RE.fullmatch(m["run_id"]): raise ValueError("invalid run_id")
 if m["frontier_id"]!=FRONTIER or m["external_actions"] is not False: raise ValueError("frontier or external-action authorization invalid")
 if not positive(m["total_budget_seconds"]): raise ValueError("total budget must be finite positive")
 if not isinstance(m["max_attempts"],int) or isinstance(m["max_attempts"],bool) or m["max_attempts"]<1: raise ValueError("max_attempts must be positive integer")
 if not isinstance(m["completion_predicate"],str) or not m["completion_predicate"].strip(): raise ValueError("completion predicate required")
 if m["platform"]!={"system":platform.system(),"machine":platform.machine()}: raise ValueError("manifest platform does not match host")
 plan=m["governing_plan"]
 if not isinstance(plan,dict) or set(plan)!={"path","sha256"} or not isinstance(plan["sha256"],str) or not HEX_RE.fullmatch(plan["sha256"]): raise ValueError("invalid governing plan")
 plan_path=checked_path(root,plan["path"])
 if not plan_path.is_file() or sha256_file(plan_path)!=plan["sha256"]: raise ValueError("governing plan changed or missing")
 if not active_frontier(root/"docs/RESEARCH_STATUS.md",FRONTIER): raise ValueError("frontier is not explicitly Active")
 if not isinstance(m["inputs"],list) or not m["inputs"]: raise ValueError("inputs required")
 paths=set()
 for row in m["inputs"]:
  if not isinstance(row,dict) or set(row)!={"path","sha256","bytes"} or not isinstance(row["sha256"],str) or not HEX_RE.fullmatch(row["sha256"]) or not isinstance(row["bytes"],int) or isinstance(row["bytes"],bool) or row["bytes"]<0: raise ValueError("invalid input binding")
  p=checked_path(root,row["path"],check_inputs); norm=str(p.relative_to(root.resolve()))
  if norm in paths: raise ValueError("duplicate normalized input path")
  paths.add(norm)
  if check_inputs and (not p.is_file() or p.stat().st_size!=row["bytes"] or sha256_file(p)!=row["sha256"]): raise ValueError(f"input changed or missing: {row['path']}")
 if not isinstance(m["phases"],list) or not m["phases"]: raise ValueError("phases required")
 ids=set()
 for phase in m["phases"]:
  if not isinstance(phase,dict) or set(phase)!={"id","command","timeout_seconds"} or not isinstance(phase.get("id"),str) or not ID_RE.fullmatch(phase["id"]) or phase["id"] in ids: raise ValueError("invalid phase id")
  ids.add(phase["id"])
  if not positive(phase["timeout_seconds"]): raise ValueError("phase timeout must be finite positive")
  cmd=phase["command"]
  if not isinstance(cmd,list) or not cmd or not all(isinstance(x,str) and x for x in cmd): raise ValueError("phase command must be argv")
  if cmd[0].split("/")[-1] in SHELLS: raise ValueError("shell, network, or publishing executable refused")
  exe=checked_path(root,cmd[0],check_inputs)
  if str(exe.relative_to(root.resolve())) not in paths: raise ValueError("command executable must be bound input")
  if check_inputs:
   if not exe.is_file() or not os.access(exe,os.X_OK): raise ValueError("command executable must be executable")
   with exe.open("rb") as f:
    if f.read(2)!=b"#!": raise ValueError("command executable requires shebang")
 return canonical_hash(m)
def terminate_group(pgid:int,grace:float=1.0)->None:
 try: os.killpg(pgid,signal.SIGTERM)
 except ProcessLookupError: return
 deadline=time.monotonic()+grace
 while time.monotonic()<deadline:
  try: os.killpg(pgid,0)
  except ProcessLookupError: return
  except PermissionError: break
  time.sleep(.03)
 try: os.killpg(pgid,signal.SIGKILL)
 except (ProcessLookupError,PermissionError): pass
