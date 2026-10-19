#!/usr/bin/python3
"""Retained, task-local observer outside the proof workspace."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

case=Path('/out')/os.environ['LAL_CASE']
case.mkdir(exist_ok=True)
args=sys.argv[1:]
cmd=args[args.index('--')+1:]
exe=shutil.which(cmd[0]) or cmd[0]
event={'event':'invoked','case':case.name,'argv':cmd,'executable_sha256':sha(exe),
       'time_ns':time.time_ns()}
is_export='lean4export' in Path(cmd[0]).name
if is_export:
    event['module']=cmd[1]
if 'nanoda' in Path(cmd[0]).name:
    config=json.loads(Path(cmd[-1]).read_text())
    artifact=Path(config['export_file_path'])
    event['config']=config
    event['artifact_sha256']=sha(artifact)
    shutil.copyfile(artifact,case/'solution.ndjson')
    (case/'nanoda-config.json').write_text(json.dumps(config,indent=2)+'\n')
with (case/'executions.jsonl').open('a') as f: f.write(json.dumps(event)+'\n')
if is_export:
    artifact=case/('challenge.ndjson' if cmd[1].startswith('ComparatorChallenges.') else 'solution-export.ndjson')
    with artifact.open('wb') as f:
        result=subprocess.run(['/opt/bin/landrun',*args],stdout=f)
    with artifact.open('rb') as f: shutil.copyfileobj(f,sys.stdout.buffer)
    sys.stdout.buffer.flush()
    event.update(artifact_sha256=sha(artifact),artifact_bytes=artifact.stat().st_size)
else:
    result=subprocess.run(['/opt/bin/landrun',*args])
event.update(event='completed',exit_code=result.returncode,time_ns=time.time_ns())
with (case/'executions.jsonl').open('a') as f: f.write(json.dumps(event)+'\n')
raise SystemExit(result.returncode)
